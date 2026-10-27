
from judge0_client import run_code

result = run_code(
    source_code='print(sum(map(int, input().split())))',
    language="python",
    stdin="10 20\n",
)

print("Status:", result["status"]["description"])
print("Output:", result["stdout"])
print("Error:", result["stderr"])
print("Compile error:", result["compile_output"])
