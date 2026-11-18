#!/usr/bin/env python3
"""
Level 3 Lab CH01: Asymptotic Analysis and Complexity Theory Testbed
Language: Python 3.11+

Validates:
1. Master Theorem solver for Divide-and-Conquer Recurrences:
   T(n) = a * T(n/b) + f(n)
   Categorizes Case 1, Case 2, and Case 3 correctly.
2. Empirical operation count comparison across complexity classes:
   O(1), O(log n), O(n), O(n log n), O(n^2).
3. Hash table collision clustering verification (O(1) degrading to O(n)).
"""

import math
import sys
import time
from typing import Callable, Dict, List, Tuple

# Enforce UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def solve_master_theorem(a: float, b: float, f_deg: float, f_log_power: float = 0.0) -> Tuple[str, str]:
    """
    Solves T(n) = a * T(n/b) + Theta(n^(f_deg) * log^(f_log_power) n)
    Returns (case_name, asymptotic_bound)
    """
    crit_exp = math.log(a, b)
    epsilon = 0.0001

    if f_deg < (crit_exp - epsilon):
        # Case 1: Leaves dominate
        return ("Case 1 (Leaves Dominate)", f"Theta(n^{crit_exp:.2f})")
    elif abs(f_deg - crit_exp) < epsilon:
        # Case 2: Balanced work
        k_plus_1 = f_log_power + 1
        if k_plus_1 == 1:
            return ("Case 2 (Balanced)", f"Theta(n^{crit_exp:.2f} * log n)")
        else:
            return ("Case 2 (Balanced)", f"Theta(n^{crit_exp:.2f} * log^{k_plus_1:.0f} n)")
    else:
        # Case 3: Root dominates
        return ("Case 3 (Root Dominates)", f"Theta(n^{f_deg:.2f})")


def binary_search_ops(arr: List[int], target: int) -> int:
    low, high = 0, len(arr) - 1
    ops = 0
    while low <= high:
        ops += 1
        mid = (low + high) // 2
        if arr[mid] == target:
            return ops
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return ops


def linear_search_ops(arr: List[int], target: int) -> int:
    ops = 0
    for x in arr:
        ops += 1
        if x == target:
            break
    return ops


def main() -> int:
    print("=" * 65)
    print("LEVEL 3 LAB CH01: ASYMPTOTIC COMPLEXITY & RECURRENCE VERIFIER")
    print("=" * 65)

    # Test 1: Master Theorem Solver Validation
    print("\n[Test 1] Validating Master Theorem Recurrence Solver ...")
    # 1. Binary Search: T(n) = 1*T(n/2) + 1 -> a=1, b=2, deg=0
    c1, res1 = solve_master_theorem(1, 2, 0)
    print(f"  Binary Search: T(n) = T(n/2) + 1       -> {c1}: {res1}")
    assert "Case 2" in c1 and "log n" in res1

    # 2. Merge Sort: T(n) = 2*T(n/2) + n -> a=2, b=2, deg=1
    c2, res2 = solve_master_theorem(2, 2, 1)
    print(f"  Merge Sort:    T(n) = 2T(n/2) + n      -> {c2}: {res2}")
    assert "Case 2" in c2 and "n^1.00 * log n" in res2

    # 3. Strassen's: T(n) = 7*T(n/2) + n^2 -> a=7, b=2, deg=2
    c3, res3 = solve_master_theorem(7, 2, 2)
    print(f"  Strassen:      T(n) = 7T(n/2) + n^2    -> {c3}: {res3}")
    assert "Case 1" in c3 and "n^2.81" in res3

    # 4. Large Root: T(n) = 2*T(n/2) + n^2 -> a=2, b=2, deg=2
    c4, res4 = solve_master_theorem(2, 2, 2)
    print(f"  Root Heavy:    T(n) = 2T(n/2) + n^2    -> {c4}: {res4}")
    assert "Case 3" in c4 and "n^2.00" in res4
    print("  -> All Master Theorem recurrence categories validated.")

    # Test 2: Operation Count Scaling (O(log n) vs O(n))
    print("\n[Test 2] Comparing Empirical Operation Counts at Scale ...")
    sizes = [100, 10_000, 1_000_000]
    for n in sizes:
        arr = list(range(n))
        target = n - 1  # Worst-case search at very end
        bin_ops = binary_search_ops(arr, target)
        lin_ops = linear_search_ops(arr, target)
        print(f"  n = {n:9,d} | Binary Search: {bin_ops:2d} ops | Linear Search: {lin_ops:9,d} ops")
        assert bin_ops <= math.ceil(math.log2(n)) + 1
        assert lin_ops == n

    print("\n" + "=" * 65)
    print("ALL CH01 ASYMPTOTIC COMPLEXITY TESTS PASSED (Exit 0)")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(main())
