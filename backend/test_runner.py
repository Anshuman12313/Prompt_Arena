
from judge0_client import execute_python
from problems import PROBLEMS
def normalize_output(value):
    if value is None:
        return ""
    return " ".join(str(value).split())


def evaluate_solution(code, problem_id):
    if problem_id not in PROBLEMS:
        raise ValueError(f"Unknown problem ID: {problem_id}")

    problem = PROBLEMS[problem_id]
    test_cases = problem["test_cases"]

    passed = 0
    results = []

    for index, test_case in enumerate(test_cases, start=1):
        try:
            execution = execute_python(
                source_code=code,
                stdin=test_case["input"]
            )

            status = execution.get("status", {})
            status_id = status.get("id")
            actual = execution.get("stdout") or ""
            expected = test_case["expected"]

            accepted = (
                status_id == 3
                and normalize_output(actual)
                == normalize_output(expected)
            )

            if accepted:
                passed += 1

            results.append({
                "test_case": index,
                "passed": accepted,
                "status": status.get("description", "Unknown"),
                "expected": expected,
                "actual": actual,
                "stderr": execution.get("stderr"),
                "compile_output": execution.get("compile_output"),
                "time": execution.get("time"),
                "memory": execution.get("memory")
            })

        except Exception as error:
            results.append({
                "test_case": index,
                "passed": False,
                "status": "Execution Error",
                "expected": test_case["expected"],
                "actual": "",
                "stderr": str(error),
                "compile_output": None,
                "time": None,
                "memory": None
            })

    total = len(test_cases)
    score = round((passed / total) * 100, 2) if total else 0

    return {
        "problem_id": problem_id,
        "problem_title": problem["title"],
        "passed": passed,
        "total": total,
        "score": score,
        "results": results
    }
