"""
Level 3 Chapter 09: Non-Comparison Linear Sorts and Selection Algorithms
Comprehensive Laboratory Verification Suite

Covers:
1. Stable Counting Sort with key-value payload stability verification.
2. Base-256 LSD Radix Sort for unsigned and signed 32-bit integers (sign-bit XOR).
3. QuickSelect O(n) average-time order statistics.
4. BFPRT Median-of-Medians O(n) worst-case selection algorithm.
"""

import sys
import random
from typing import List, Tuple, Any

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# -------------------------------------------------------------
# 1. Stable Counting Sort
# -------------------------------------------------------------
def counting_sort_payload(pairs: List[Tuple[int, str]], max_key: int) -> List[Tuple[int, str]]:
    """Stable counting sort on non-negative integer keys."""
    count = [0] * (max_key + 1)
    for k, _ in pairs:
        count[k] += 1

    # Prefix sums
    for i in range(1, max_key + 1):
        count[i] += count[i - 1]

    # Stable backward placement
    output = [None] * len(pairs)
    for k, payload in reversed(pairs):
        count[k] -= 1
        output[count[k]] = (k, payload)

    return output


# -------------------------------------------------------------
# 2. Base-256 LSD Radix Sort (Signed & Unsigned)
# -------------------------------------------------------------
def radix_sort_u32(arr: List[int]) -> List[int]:
    """Sorts list of non-negative 32-bit integers using Base 256 LSD Radix Sort."""
    res = list(arr)
    for shift in range(0, 32, 8):
        count = [0] * 256
        for x in res:
            byte = (x >> shift) & 0xFF
            count[byte] += 1

        total = 0
        for i in range(256):
            c = count[i]
            count[i] = total
            total += c

        temp = [0] * len(res)
        for x in res:
            byte = (x >> shift) & 0xFF
            temp[count[byte]] = x
            count[byte] += 1

        res = temp
    return res


def radix_sort_signed_i32(arr: List[int]) -> List[int]:
    """Sorts list of signed 32-bit integers using sign-bit XOR transform."""
    # Step 1: XOR sign bit (0x80000000) to map [-2^31, 2^31 - 1] to [0, 2^32 - 1]
    transformed = [x ^ 0x80000000 for x in arr]
    # Step 2: Unsigned Radix Sort
    sorted_transformed = radix_sort_u32(transformed)
    # Step 3: XOR sign bit back
    return [x ^ 0x80000000 for x in sorted_transformed]


# -------------------------------------------------------------
# 3. QuickSelect: Average O(n) Selection
# -------------------------------------------------------------
def quickselect(arr: List[int], k: int) -> int:
    """Finds the k-th smallest element (0-indexed) in O(n) average time."""
    nums = list(arr)

    def _select(lo: int, hi: int, k_target: int) -> int:
        while lo <= hi:
            if lo == hi:
                return nums[lo]

            # Randomized pivot selection
            pivot_idx = random.randint(lo, hi)
            nums[pivot_idx], nums[hi] = nums[hi], nums[pivot_idx]
            pivot = nums[hi]

            # Lomuto partition
            i = lo
            for j in range(lo, hi):
                if nums[j] <= pivot:
                    nums[i], nums[j] = nums[j], nums[i]
                    i += 1
            nums[i], nums[hi] = nums[hi], nums[i]

            if i == k_target:
                return nums[i]
            elif i > k_target:
                hi = i - 1
            else:
                lo = i + 1
        return -1

    return _select(0, len(nums) - 1, k)


# -------------------------------------------------------------
# 4. BFPRT Median-of-Medians: Worst-Case O(n) Selection
# -------------------------------------------------------------
def median_of_medians(arr: List[int], k: int) -> int:
    """Deterministic selection algorithm guaranteeing strict O(n) worst-case time."""
    nums = list(arr)

    def _bfprt(lo: int, hi: int, k_idx: int) -> int:
        n = hi - lo + 1
        if n <= 5:
            # Base case: sort directly
            sub = sorted(nums[lo:hi + 1])
            return sub[k_idx]

        # Step 1: Group into 5s and collect medians
        num_groups = (n + 4) // 5
        medians = []
        for i in range(num_groups):
            g_lo = lo + i * 5
            g_hi = min(g_lo + 4, hi)
            sub = sorted(nums[g_lo:g_hi + 1])
            medians.append(sub[len(sub) // 2])

        # Step 2: Recursively find median of medians
        mom = median_of_medians(medians, len(medians) // 2)

        # Step 3: 3-Way Partition around mom
        lt = lo
        gt = hi
        curr = lo
        while curr <= gt:
            if nums[curr] < mom:
                nums[lt], nums[curr] = nums[curr], nums[lt]
                lt += 1
                curr += 1
            elif nums[curr] > mom:
                nums[curr], nums[gt] = nums[gt], nums[curr]
                gt -= 1
            else:
                curr += 1

        count_less = lt - lo
        count_equal = gt - lt + 1

        if k_idx < count_less:
            return _bfprt(lo, lt - 1, k_idx)
        elif k_idx < count_less + count_equal:
            return mom
        else:
            return _bfprt(gt + 1, hi, k_idx - count_less - count_equal)

    return _bfprt(0, len(nums) - 1, k)


# -------------------------------------------------------------
# Test Suite
# -------------------------------------------------------------
def test_linear_sorts_lab():
    print("[TEST 1] Counting Sort Stability Verification...")
    data = [(3, "alpha"), (1, "first_1"), (4, "delta"), (1, "second_1"), (3, "beta"), (1, "third_1")]
    sorted_pairs = counting_sort_payload(data, max_key=5)
    assert [k for k, _ in sorted_pairs] == [1, 1, 1, 3, 3, 4]
    ones = [p for k, p in sorted_pairs if k == 1]
    threes = [p for k, p in sorted_pairs if k == 3]
    assert ones == ["first_1", "second_1", "third_1"], f"Stability failed on 1s: {ones}"
    assert threes == ["alpha", "beta"], f"Stability failed on 3s: {threes}"
    print("  -> Passed. Counting sort stability fully preserved.")

    print("[TEST 2] Base-256 LSD Radix Sort (Signed Integers)...")
    random.seed(12345)
    signed_test = [random.randint(-100000, 100000) for _ in range(500)]
    signed_test.extend([-2147483648, 2147483647, 0, -1, 1, -500, 500])
    expected_signed = sorted(signed_test)
    actual_signed = radix_sort_signed_i32(signed_test)
    assert actual_signed == expected_signed, "Signed Radix Sort output mismatch!"
    print("  -> Passed. Sign-bit XOR trick successfully sorts negative & positive integers.")

    print("[TEST 3] QuickSelect Order Statistics...")
    test_arr = [64, 34, 25, 12, 22, 11, 90, 42, 88, 1, 0, -5, 77]
    sorted_ref = sorted(test_arr)
    for k in range(len(test_arr)):
        expected_val = sorted_ref[k]
        selected_val = quickselect(test_arr, k)
        assert selected_val == expected_val, f"QuickSelect failed for k={k}: {selected_val} != {expected_val}"
    print("  -> Passed. QuickSelect found all order statistics correctly.")

    print("[TEST 4] BFPRT Median-of-Medians Linear Selection...")
    large_random = [random.randint(-5000, 5000) for _ in range(300)]
    large_sorted = sorted(large_random)
    test_ks = [0, len(large_random) // 4, len(large_random) // 2, 3 * len(large_random) // 4, len(large_random) - 1]
    for k in test_ks:
        mom_val = median_of_medians(large_random, k)
        assert mom_val == large_sorted[k], f"BFPRT failed at k={k}: {mom_val} != {large_sorted[k]}"
    print("  -> Passed. BFPRT Median-of-Medians found exact medians deterministically.")

    print("ALL Chapter 09 Linear Sorts & Selection lab tests passed successfully!")


if __name__ == "__main__":
    test_linear_sorts_lab()
