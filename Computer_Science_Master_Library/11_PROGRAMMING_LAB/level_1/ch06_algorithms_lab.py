"""
Practical Lab 1.6: Algorithms, Step-Tracing, and Verification
File: 11_PROGRAMMING_LAB/level_1/ch06_algorithms_lab.py
Author: Computer Science Master Library
Description: Demonstrates structured algorithm design, loop invariants,
             trace tables, and step-by-step state verification.
"""

import sys
from typing import List, Tuple, Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def linear_search_with_trace(
    arr: List[int], target: int
) -> Tuple[Optional[int], int]:
    """
    Algorithm: Linear Search
    Traces every comparison step to demonstrate the IPO cycle of a loop.
    Returns: (Found Index or None, Total Comparison Count)
    """
    print(f"--- Running Linear Search for Target: {target} ---")
    print(f"Input Array: {arr}")
    print("Step | Index | Value Inspected | Match?")
    print("-" * 42)

    comparisons = 0
    for idx, val in enumerate(arr):
        comparisons += 1
        is_match = val == target
        print(f"{comparisons:4d} | {idx:5d} | {val:15d} | {is_match}")
        if is_match:
            print(f"-> MATCH FOUND at index {idx} in {comparisons} steps!\n")
            return idx, comparisons

    print(f"-> Target {target} NOT found after {comparisons} steps.\n")
    return None, comparisons


def euclidean_gcd(a: int, b: int) -> int:
    """
    Algorithm: Euclidean Algorithm for Greatest Common Divisor (GCD)
    Mathematical principle: gcd(a, b) = gcd(b, a mod b) until b == 0.
    """
    print(f"--- Computing GCD of ({a}, {b}) using Euclid's Algorithm ---")
    step = 0
    val_a, val_b = abs(a), abs(b)

    while val_b != 0:
        step += 1
        remainder = val_a % val_b
        print(
            f"Step {step}: {val_a} = ({val_a // val_b} * {val_b}) + Remainder {remainder}"
        )
        val_a = val_b
        val_b = remainder

    print(f"-> Final GCD result: {val_a}\n")
    return val_a


def calculate_factorial(n: int) -> int:
    """
    Algorithm: Iterative Factorial (n!)
    Loop Invariant: At start of iteration i, result = (i - 1)!
    """
    if n < 0:
        raise ValueError("Factorial is undefined for negative integers.")

    print(f"--- Calculating Factorial for n = {n} ---")
    result = 1
    for i in range(1, n + 1):
        prev_result = result
        result *= i
        print(f"Iteration {i}: {prev_result} * {i} = {result}")

    print(f"-> Final {n}! = {result}\n")
    return result


if __name__ == "__main__":
    # Test 1: Linear Search
    sample_list = [18, 42, 7, 99, 53, 24, 61]
    idx1, comp1 = linear_search_with_trace(sample_list, target=99)
    assert idx1 == 3 and comp1 == 4, f"Unexpected linear search result: {idx1}, {comp1}"

    idx2, comp2 = linear_search_with_trace(sample_list, target=100)
    assert idx2 is None and comp2 == 7, (
        f"Unexpected linear search result: {idx2}, {comp2}"
    )

    # Test 2: Euclidean GCD
    gcd_res = euclidean_gcd(252, 105)
    assert gcd_res == 21, f"Expected 21, got {gcd_res}"

    # Test 3: Factorial
    fact_res = calculate_factorial(5)
    assert fact_res == 120, f"Expected 120, got {fact_res}"

    print("All algorithm lab tests executed and verified successfully.")
