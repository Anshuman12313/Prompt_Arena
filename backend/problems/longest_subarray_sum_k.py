
PROBLEM = {
    "id": "longest_subarray_sum_k",
    "title": "Longest Subarray with Sum K",
    "statement": """
Given an array of integers and an integer K,
find the length of the longest contiguous subarray
whose sum equals K.

Input:
The first line contains N and K.
The second line contains N integers.

Output:
Print the length of the longest subarray whose sum is K.
If no such subarray exists, print 0.
""",
    "test_cases": [
        {"input": "5 5\n1 2 3 1 1\n", "expected": "2"},
        {"input": "5 3\n1 2 1 1 1\n", "expected": "2"},
        {"input": "4 0\n1 -1 2 -2\n", "expected": "4"},
        {"input": "3 10\n1 2 3\n", "expected": "0"}
    ]
}
PROBLEM_ID = PROBLEM["id"]