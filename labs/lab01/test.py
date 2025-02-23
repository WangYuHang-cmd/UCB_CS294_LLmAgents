import sys, os
import re
import json
from mymain import main 
from typing import List

class TerminalColors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    RESET = '\033[0m'

def suppress_prints() -> None:
    sys.stdout = open(os.devnull, 'w')

def restore_prints() -> None:
    sys.stdout = sys.__stdout__

def contains_num_with_tolerance(text: str, pattern: float, tolerance: float=0) -> bool:
    # Note: the test will only match numbers that have 3 or more decimal places.
    nums = re.findall(r'\d*\.\d{3}', text)
    nums = [float(num) for num in nums]
    pattern_matches = [num for num in nums if abs(num - pattern) <= tolerance]
    return len(pattern_matches) >= 1

def extract_score(content: str) -> float:
    # 提取带有3位小数的数字
    nums = re.findall(r'\d*\.\d{3}', content)
    if nums:
        return float(nums[0])
    return None

def public_tests():
    # print(os.environ.get("OPENAI_API_KEY"))

    queries = [
    "What is the overall score for taco bell?",
    "What is the overall score for In N Out?",
    "How good is the restaurant Chick-fil-A overall?",
    "What is the overall score for Krispy Kreme?",
    ]
    query_results = [3.25, 10.000, 10.000, 8.94]
    tolerances = [0.2, 0.2, 0.2, 0.15]
    contents = []
    
    original_stdout = sys.stdout
    
    for query in queries:
        with open("runtime-log.txt", "w") as f:
            sys.stdout = f
            main(query)
            
        sys.stdout = original_stdout
        
        with open("runtime-log.txt", "r") as f:
            content = f.read()
            actual_score = extract_score(content)
            print(f"\nQuery: {query}")
            print(f"Expected score: {query_results[queries.index(query)]}")
            print(f"Your score: {actual_score if actual_score is not None else 'No score found'}")
            contents.append(content)
            
    num_passed = 0
    for i, content in enumerate(contents):
        if not contains_num_with_tolerance(content, query_results[i], tolerance=tolerances[i]):
            print(TerminalColors.RED + f"Test {i+1} Failed." + TerminalColors.RESET, "Expected: ", query_results[i], "Query: ", queries[i])
        else:
            print(TerminalColors.GREEN + f"Test {i+1} Passed." + TerminalColors.RESET, "Expected: ", query_results[i], "Query: ", queries[i])
            num_passed += 1
            
    print(f"{num_passed}/{len(queries)} Tests Passed")

public_tests()
