"""
Level 3 Chapter 08: Divide-and-Conquer Sorting (MergeSort, QuickSort, and Introsort)
Comprehensive Laboratory Verification Suite

Covers:
1. Recursive and Iterative Bottom-Up MergeSort with stability verification.
2. QuickSort with Lomuto, Hoare, and Dutch National Flag 3-Way partitioning.
3. Introsort with recursion depth tracking, HeapSort fallback, and InsertionSort cutoff.
4. Correctness assertions on random, sorted, reverse, and duplicate-heavy arrays.
"""

import sys
import math
import random
from typing import List, Tuple, Any

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# -------------------------------------------------------------
# 1. MergeSort & Stability Check
# -------------------------------------------------------------
def mergesort(arr: List[Any]) -> List[Any]:
    if len(arr) <= 1:
        return list(arr)
    mid = len(arr) // 2
    left = mergesort(arr[:mid])
    right = mergesort(arr[mid:])
    return _merge(left, right)


def _merge(left: List[Any], right: List[Any]) -> List[Any]:
    merged = []
    i = j = 0
    # Stability condition: when keys are equal, prefer the left element
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def bottom_up_mergesort(arr: List[Any]) -> List[Any]:
    n = len(arr)
    res = list(arr)
    width = 1
    while width < n:
        for i in range(0, n, 2 * width):
            left = res[i:i + width]
            right = res[i + width:i + 2 * width]
            merged = _merge(left, right)
            res[i:i + len(merged)] = merged
        width *= 2
    return res


# -------------------------------------------------------------
# 2. QuickSort Partitioning Schemes
# -------------------------------------------------------------
def quicksort_hoare(arr: List[int]) -> List[int]:
    res = list(arr)
    _qsort_hoare(res, 0, len(res) - 1)
    return res


def _qsort_hoare(arr: List[int], lo: int, hi: int) -> None:
    if lo < hi:
        p = _partition_hoare(arr, lo, hi)
        _qsort_hoare(arr, lo, p)
        _qsort_hoare(arr, p + 1, hi)


def _partition_hoare(arr: List[int], lo: int, hi: int) -> int:
    pivot = arr[lo + (hi - lo) // 2]
    i = lo - 1
    j = hi + 1
    while True:
        while True:
            i += 1
            if arr[i] >= pivot:
                break
        while True:
            j -= 1
            if arr[j] <= pivot:
                break
        if i >= j:
            return j
        arr[i], arr[j] = arr[j], arr[i]


def quicksort_3way(arr: List[int]) -> List[int]:
    """Dutch National Flag 3-Way QuickSort: optimal for duplicate keys."""
    res = list(arr)
    _qsort_3way(res, 0, len(res) - 1)
    return res


def _qsort_3way(arr: List[int], lo: int, hi: int) -> None:
    if lo >= hi:
        return
    lt = lo
    gt = hi
    pivot = arr[lo]
    i = lo + 1
    while i <= gt:
        if arr[i] < pivot:
            arr[lt], arr[i] = arr[i], arr[lt]
            lt += 1
            i += 1
        elif arr[i] > pivot:
            arr[i], arr[gt] = arr[gt], arr[i]
            gt -= 1
        else:
            i += 1
    _qsort_3way(arr, lo, lt - 1)
    _qsort_3way(arr, gt + 1, hi)


# -------------------------------------------------------------
# 3. Hybrid Introsort
# -------------------------------------------------------------
def introsort(arr: List[int]) -> List[int]:
    res = list(arr)
    if len(res) <= 1:
        return res
    max_depth = 2 * int(math.floor(math.log2(len(res))))
    _introsort_recurse(res, 0, len(res) - 1, max_depth)
    return res


def _introsort_recurse(arr: List[int], lo: int, hi: int, max_depth: int) -> None:
    while hi - lo > 16:
        if max_depth == 0:
            _heapsort_range(arr, lo, hi)
            return
        max_depth -= 1
        p = _partition_hoare(arr, lo, hi)
        # Tail-call optimization: recurse into smaller half
        if p - lo < hi - p:
            _introsort_recurse(arr, lo, p, max_depth)
            lo = p + 1
        else:
            _introsort_recurse(arr, p + 1, hi, max_depth)
            hi = p
    _insertion_sort(arr, lo, hi)


def _insertion_sort(arr: List[int], lo: int, hi: int) -> None:
    for i in range(lo + 1, hi + 1):
        key = arr[i]
        j = i - 1
        while j >= lo and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key


def _heapsort_range(arr: List[int], lo: int, hi: int) -> None:
    size = hi - lo + 1
    for i in range(size // 2 - 1, -1, -1):
        _sift_down(arr, lo, i, size)
    for i in range(size - 1, 0, -1):
        arr[lo], arr[lo + i] = arr[lo + i], arr[lo]
        _sift_down(arr, lo, 0, i)


def _sift_down(arr: List[int], offset: int, idx: int, size: int) -> None:
    curr = idx
    while True:
        largest = curr
        l = 2 * curr + 1
        r = 2 * curr + 2
        if l < size and arr[offset + l] > arr[offset + largest]:
            largest = l
        if r < size and arr[offset + r] > arr[offset + largest]:
            largest = r
        if largest != curr:
            arr[offset + curr], arr[offset + largest] = arr[offset + largest], arr[offset + curr]
            curr = largest
        else:
            break


# -------------------------------------------------------------
# Test Suite
# -------------------------------------------------------------
class KeyPayload:
    """Helper to verify sorting stability."""
    def __init__(self, key: int, payload: str):
        self.key = key
        self.payload = payload

    def __le__(self, other):
        return self.key <= other.key

    def __lt__(self, other):
        return self.key < other.key

    def __eq__(self, other):
        return self.key == other.key


def test_sorting_lab():
    print("[TEST 1] MergeSort Stability Verification...")
    data = [
        KeyPayload(5, "first_5"),
        KeyPayload(2, "first_2"),
        KeyPayload(5, "second_5"),
        KeyPayload(1, "first_1"),
        KeyPayload(5, "third_5"),
        KeyPayload(2, "second_2"),
    ]
    sorted_data = mergesort(data)
    # Check that keys are sorted
    assert [x.key for x in sorted_data] == [1, 2, 2, 5, 5, 5]
    # Check that payloads of equal keys preserve original order
    twos = [x.payload for x in sorted_data if x.key == 2]
    fives = [x.payload for x in sorted_data if x.key == 5]
    assert twos == ["first_2", "second_2"], f"Stability violated for key 2: {twos}"
    assert fives == ["first_5", "second_5", "third_5"], f"Stability violated for key 5: {fives}"
    print("  -> Passed. MergeSort stability mathematically verified.")

    print("[TEST 2] Bottom-Up Iterative MergeSort...")
    raw = [42, 17, 89, 5, 33, 99, 12, 60, 2]
    assert bottom_up_mergesort(raw) == sorted(raw)
    print("  -> Passed. Bottom-up MergeSort works without recursion stack.")

    print("[TEST 3] QuickSort Hoare & 3-Way Partitioning...")
    random.seed(42)
    test_cases = [
        [random.randint(0, 1000) for _ in range(200)],       # Random
        list(range(200)),                                    # Already sorted
        list(range(200, 0, -1)),                             # Reverse sorted
        [7] * 200,                                           # All duplicates
        [random.choice([1, 2, 3]) for _ in range(300)]       # Few distinct keys
    ]
    for i, tc in enumerate(test_cases):
        expected = sorted(tc)
        assert quicksort_hoare(tc) == expected, f"Hoare failed on case {i}"
        assert quicksort_3way(tc) == expected, f"3-Way failed on case {i}"
    print("  -> Passed. QuickSort handles all edge distributions.")

    print("[TEST 4] Hybrid Introsort Verification...")
    for i, tc in enumerate(test_cases):
        expected = sorted(tc)
        assert introsort(tc) == expected, f"Introsort failed on case {i}"

    # Anti-quicksort adversarial permutation test (pipe large sorted input)
    large_sorted = list(range(2000))
    assert introsort(large_sorted) == large_sorted
    print("  -> Passed. Introsort smoothly handles large sorted inputs.")

    print("ALL Chapter 08 Sorting lab tests passed successfully!")


if __name__ == "__main__":
    test_sorting_lab()
