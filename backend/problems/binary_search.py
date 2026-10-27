
PROBLEM = {
    "id": "binary_search",
    "title": "Binary Search",
    "statement": """
Given a sorted array of N integers and a target X,
print the zero-based index of X if it exists.
Otherwise, print -1.

Input:
The first line contains N and X.
The second line contains N sorted integers.

Output:
Print the index of X, or -1 if it does not exist.
""",
    "test_cases": [
        {
            "input": "5 3\n1 2 3 4 5\n",
            "expected": "2"
        },
        {
            "input": "5 6\n1 2 3 4 5\n",
            "expected": "-1"
        },
        {
            "input": "1 7\n7\n",
            "expected": "0"
        },
        {
            "input": "4 1\n1 3 5 7\n",
            "expected": "0"
        },
        {
            "input": "4 7\n1 3 5 7\n",
            "expected": "3"
        }
    ]
}

PROBLEM_ID = PROBLEM["id"]
