
import os
import csv
import time
import uuid
from datetime import datetime

from groq import Groq
from dotenv import load_dotenv
from problems import PROBLEMS
from test_runner import evaluate_solution

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env")

client = Groq(api_key=api_key)

MODEL = "openai/gpt-oss-120b"

RESULTS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "results.csv"
)

FIELDNAMES = [
    "experiment_id",
    "timestamp",
    "problem_id",
    "problem_title",
    "model",
    "prompt",
    "status",
    "passed",
    "total",
    "score",
    "generation_latency_seconds",
    "evaluation_latency_seconds",
    "total_latency_seconds",
    "error",
    "generated_code"
]


def choose_problem():
    problems = list(PROBLEMS.values())

    print("\n========== PROMPT ARENA ==========")
    print("Choose a programming question:\n")

    for index, problem in enumerate(problems, start=1):
        print(f"{index}. {problem['title']}")

    print(f"{len(problems) + 1}. Exit")

    while True:
        choice = input("\nEnter choice: ").strip()

        if not choice.isdigit():
            print("Enter a valid number.")
            continue

        index = int(choice)

        if index == len(problems) + 1:
            return None

        if 1 <= index <= len(problems):
            return problems[index - 1]

        print("Invalid choice.")


def get_prompt():
    print("\nWrite your prompt for this question.")
    print("Type END on a new line to submit it.\n")

    lines = []

    while True:
        try:
            line = input()
        except EOFError:
            break

        if line.strip() == "END":
            break

        lines.append(line)

    return "\n".join(lines).strip()


def solve_problem(problem, prompt):
    system_prompt = f"""
You are a programming solution generator.

Solve the programming problem below according to the user's
instructions.

Problem:
{problem['statement']}

Requirements:
- Generate Python 3 code.
- Read input from standard input.
- Write the answer to standard output.
- Do not hardcode the provided examples.
- Return only executable Python code.
- Do not include Markdown fences or explanations.
"""

    start = time.perf_counter()

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    latency = round(time.perf_counter() - start, 3)
    code = response.choices[0].message.content

    if not code or not code.strip():
        raise ValueError("The model returned empty code.")

    code = code.strip()

    if code.startswith("```"):
        lines = code.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        code = "\n".join(lines).strip()

    return code, latency


def save_result(data):
    exists = (
        os.path.exists(RESULTS_FILE)
        and os.path.getsize(RESULTS_FILE) > 0
    )

    with open(
        RESULTS_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=FIELDNAMES,
            extrasaction="ignore"
        )

        if not exists:
            writer.writeheader()

        writer.writerow(data)


def run_experiment(problem, prompt):
    experiment_id = str(uuid.uuid4())[:8]
    start = time.perf_counter()

    code = ""
    generation_latency = ""
    evaluation_latency = ""
    passed = ""
    total = ""
    score = ""
    error = ""
    status = "failed"

    try:
        print("\nGenerating solution with Groq...")

        code, generation_latency = solve_problem(problem, prompt)

        print("\n========== GENERATED CODE ==========")
        print(code)
        print("====================================")

        print(f"Generation latency: {generation_latency}s")
        print("\nEvaluating with Judge0...")

        eval_start = time.perf_counter()

        result = evaluate_solution(
            code,
            problem["id"]
        )

        evaluation_latency = round(
            time.perf_counter() - eval_start, 3
        )

        passed = result["passed"]
        total = result["total"]
        score = result["score"]
        status = "success"

        print("\n========== EVALUATION ==========")
        print(f"Question: {problem['title']}")
        print(f"Passed: {passed}/{total}")
        print(f"Score: {score}%")
        print(f"Evaluation latency: {evaluation_latency}s")

        for case in result["results"]:
            label = "PASS" if case["passed"] else "FAIL"

            print(
                f"\nTest {case['test_case']}: {label}"
                f" | {case['status']}"
            )

            if not case["passed"]:
                print(f"Expected: {case['expected']!r}")
                print(f"Actual:   {case['actual']!r}")

                if case.get("compile_output"):
                    print(
                        "Compile error:",
                        case["compile_output"]
                    )

                if case.get("stderr"):
                    print("Error:", case["stderr"])

    except Exception as exception:
        error = f"{type(exception).__name__}: {exception}"
        print(f"\nExperiment failed: {error}")

    finally:
        total_latency = round(time.perf_counter() - start, 3)

        data = {
            "experiment_id": experiment_id,
            "timestamp": datetime.now().isoformat(
                timespec="seconds"
            ),
            "problem_id": problem["id"],
            "problem_title": problem["title"],
            "model": MODEL,
            "prompt": prompt,
            "status": status,
            "passed": passed,
            "total": total,
            "score": score,
            "generation_latency_seconds": generation_latency,
            "evaluation_latency_seconds": evaluation_latency,
            "total_latency_seconds": total_latency,
            "error": error,
            "generated_code": code
        }

        try:
            save_result(data)
            print(f"\nExperiment ID: {experiment_id}")
            print(f"Results saved to: {RESULTS_FILE}")
        except Exception as exception:
            print(f"Could not save results: {exception}")

    return status, score


def main():
    while True:
        problem = choose_problem()

        if problem is None:
            print("Exiting Prompt Arena.")
            break

        print("\n========== QUESTION ==========")
        print(problem["title"])
        print(problem["statement"])
        print("==============================")

        while True:
            prompt = get_prompt()

            if not prompt:
                print("Prompt cannot be empty.")
                continue

            run_experiment(problem, prompt)

            again = input(
                "\nTry another prompt on this question? (y/n): "
            ).strip().lower()

            if again != "y":
                break


if __name__ == "__main__":
    main()
