import sys, os
import re
import json
from main import main 
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
    
def public_tests():
    queries = [
    "What is the overall score for taco bell?",
    "What is the overall score for In N Out?",
    "How good is the restaurant Chick-fil-A overall?",
    "What is the overall score for Krispy Kreme?",
    ]
    query_results = [3.25, 10.000, 10.000, 8.94]
    tolerances = [0.2, 0.2, 0.2, 0.15]
    contents = []
    
    for query in queries:
        with open("runtime-log.txt", "w") as f:
            sys.stdout = f
            main(query)
        with open("runtime-log.txt", "r") as f:
            contents.append(f.read())
            
    restore_prints()
    num_passed = 0
    for i, content in enumerate(contents):
        if not contains_num_with_tolerance(content, query_results[i], tolerance=tolerances[i]):
            print(TerminalColors.RED + f"Test {i+1} Failed." + TerminalColors.RESET, "Expected: ", query_results[i], "Query: ", queries[i])
        else:
            print(TerminalColors.GREEN + f"Test {i+1} Passed." + TerminalColors.RESET, "Expected: ", query_results[i], "Query: ", queries[i])
            num_passed += 1
            
    print(f"{num_passed}/{len(queries)} Tests Passed")

public_tests()
