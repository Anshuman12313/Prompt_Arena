
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv(
    "JUDGE0_BASE_URL",
    "https://ce.judge0.com"
).rstrip("/")

API_KEY = os.getenv("JUDGE0_API_KEY")


def execute_code(source_code, stdin="", language_id=71, timeout=30):
    headers = {"Content-Type": "application/json"}

    if API_KEY:
        headers["X-Auth-Token"] = API_KEY

    response = requests.post(
        f"{BASE_URL}/submissions",
        params={
            "base64_encoded": "false",
            "wait": "false"
        },
        json={
            "source_code": source_code,
            "language_id": language_id,
            "stdin": stdin
        },
        headers=headers,
        timeout=15
    )

    response.raise_for_status()
    token = response.json().get("token")

    if not token:
        raise RuntimeError("Judge0 did not return a submission token.")

    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        response = requests.get(
            f"{BASE_URL}/submissions/{token}",
            params={
                "base64_encoded": "false",
                "fields": (
                    "stdout,stderr,compile_output,message,"
                    "status,time,memory"
                )
            },
            headers=headers,
            timeout=15
        )

        response.raise_for_status()
        result = response.json()
        status = result.get("status", {})
        status_id = status.get("id")

        if status_id not in (1, 2):
            return result

        time.sleep(0.5)

    raise TimeoutError("Judge0 execution timed out.")


def run_code(source_code, language="python", stdin="", timeout=30):
    language_ids = {
        "python": 71,
        "cpp": 54
    }

    if language not in language_ids:
        raise ValueError(f"Unsupported language: {language}")

    return execute_code(
        source_code=source_code,
        stdin=stdin,
        language_id=language_ids[language],
        timeout=timeout
    )


def execute_python(source_code, stdin=""):
    return run_code(
        source_code=source_code,
        language="python",
        stdin=stdin
    )
