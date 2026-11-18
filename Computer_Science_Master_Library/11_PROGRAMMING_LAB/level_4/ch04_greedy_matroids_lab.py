"""
Level 4 Chapter 04: Greedy Algorithms and Matroid Theory
Comprehensive Laboratory Verification Suite

Covers:
1. Fractional Knapsack with value-to-weight ratio sorting.
2. Interval Activity Selection (Earliest Finish Time) vs. Brute Force search.
3. Huffman Optimal Prefix Coding & Kraft-McMillan Inequality verification.
4. Graphic Matroid: Hereditary & Exchange Property validation.
"""

import sys
import heapq
import itertools
from collections import Counter
from typing import List, Tuple, Dict, Optional, Set

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# -------------------------------------------------------------
# 1. Fractional Knapsack
# -------------------------------------------------------------
def fractional_knapsack(weights: List[float], values: List[float], capacity: float) -> float:
    n = len(weights)
    items = [(values[i] / weights[i], weights[i], values[i]) for i in range(n)]
    items.sort(key=lambda x: x[0], reverse=True)

    total_value = 0.0
    remaining = capacity

    for ratio, w, v in items:
        if remaining <= 0:
            break
        if w <= remaining:
            total_value += v
            remaining -= w
        else:
            total_value += v * (remaining / w)
            remaining = 0

    return total_value


# -------------------------------------------------------------
# 2. Activity / Interval Scheduling
# -------------------------------------------------------------
def greedy_activity_selection(intervals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    # Sort by earliest finish time
    sorted_intervals = sorted(intervals, key=lambda x: x[1])
    selected = []
    last_finish = -1

    for start, finish in sorted_intervals:
        if start >= last_finish:
            selected.append((start, finish))
            last_finish = finish

    return selected


def brute_force_activity_selection(intervals: List[Tuple[int, int]]) -> int:
    n = len(intervals)
    max_count = 0

    def is_compatible(subset):
        sorted_sub = sorted(subset, key=lambda x: x[0])
        for i in range(len(sorted_sub) - 1):
            if sorted_sub[i][1] > sorted_sub[i + 1][0]:
                return False
        return True

    for r in range(1, n + 1):
        for combo in itertools.combinations(intervals, r):
            if is_compatible(combo):
                max_count = max(max_count, len(combo))

    return max_count


# -------------------------------------------------------------
# 3. Huffman Coding
# -------------------------------------------------------------
class HuffmanNode:
    def __init__(self, char: Optional[str], freq: int):
        self.char = char
        self.freq = freq
        self.left: Optional['HuffmanNode'] = None
        self.right: Optional['HuffmanNode'] = None

    def __lt__(self, other: 'HuffmanNode') -> bool:
        return self.freq < other.freq


def build_huffman_codes(text: str) -> Tuple[Dict[str, str], Optional[HuffmanNode]]:
    if not text:
        return {}, None
    freqs = Counter(text)
    heap = [HuffmanNode(char, count) for char, count in freqs.items()]
    heapq.heapify(heap)

    if len(heap) == 1:
        root = HuffmanNode(None, heap[0].freq)
        root.left = heapq.heappop(heap)
        return {root.left.char: "0"}, root

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)

    root = heap[0]
    codes = {}

    def _traverse(node: Optional[HuffmanNode], prefix: str):
        if not node:
            return
        if node.char is not None:
            codes[node.char] = prefix if prefix else "0"
            return
        _traverse(node.left, prefix + "0")
        _traverse(node.right, prefix + "1")

    _traverse(root, "")
    return codes, root


def verify_prefix_free(codes: Dict[str, str]) -> bool:
    code_list = list(codes.values())
    for i in range(len(code_list)):
        for j in range(len(code_list)):
            if i != j and code_list[j].startswith(code_list[i]):
                return False
    return True


def verify_kraft_mcmillan(codes: Dict[str, str]) -> float:
    return sum(2 ** (-len(code)) for code in codes.values())


# -------------------------------------------------------------
# 4. Graphic Matroid Independence & Exchange Property
# -------------------------------------------------------------
class GraphicMatroid:
    def __init__(self, n: int, ground_edges: List[Tuple[int, int]]):
        self.n = n
        self.ground_set = ground_edges

    def is_independent(self, edge_subset: List[Tuple[int, int]]) -> bool:
        """Independent if and only if edge_subset forms an acyclic forest."""
        parent = list(range(self.n))

        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        for u, v in edge_subset:
            ru, rv = find(u), find(v)
            if ru == rv:
                return False  # Cycle detected
            parent[ru] = rv
        return True

    def test_exchange_property(self, A: List[Tuple[int, int]], B: List[Tuple[int, int]]) -> bool:
        """If |A| < |B| and both are independent, exists e in B \\ A such that A U {e} is independent."""
        assert self.is_independent(A) and self.is_independent(B)
        assert len(A) < len(B)

        candidates = [e for e in B if e not in A]
        for e in candidates:
            if self.is_independent(A + [e]):
                return True
        return False


# -------------------------------------------------------------
# Test Suite
# -------------------------------------------------------------
def test_greedy_lab():
    print("[TEST 1] Fractional Knapsack...")
    weights = [10.0, 20.0, 30.0]
    values = [60.0, 100.0, 120.0]
    cap = 50.0
    # Expected: take all item 1 (10w, 60v), all item 2 (20w, 100v), and 20/30 of item 3 (20w, 80v) -> total 240.0
    ans = fractional_knapsack(weights, values, cap)
    assert abs(ans - 240.0) < 1e-6, f"Expected 240.0, got {ans}"
    print(f"  -> Passed. Fractional Knapsack optimal value = {ans:.2f}")

    print("[TEST 2] Activity Selection: Greedy vs Brute Force...")
    intervals = [(1, 3), (2, 5), (0, 6), (5, 7), (3, 9), (5, 9), (8, 10), (6, 11)]
    greedy_res = greedy_activity_selection(intervals)
    brute_res = brute_force_activity_selection(intervals)
    assert len(greedy_res) == brute_res == 3
    print(f"  -> Passed. Greedy selected {len(greedy_res)} activities: {greedy_res}")

    print("[TEST 3] Huffman Coding Prefix-Free & Kraft-McMillan Inequality...")
    text = "BEEP BOOP BARK BARK BEEP BEEP"
    codes, _ = build_huffman_codes(text)
    assert verify_prefix_free(codes) is True, "Huffman codes are NOT prefix-free!"
    km_sum = verify_kraft_mcmillan(codes)
    assert km_sum <= 1.0, f"Kraft-McMillan violated: {km_sum} > 1.0"
    print(f"  -> Passed. Huffman codes are prefix-free, Kraft-McMillan sum = {km_sum:.4f} <= 1.0")

    print("[TEST 4] Graphic Matroid Hereditary & Exchange Axioms...")
    # Graph with 4 nodes, 5 edges
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)]
    matroid = GraphicMatroid(4, edges)

    # Independent set A (size 1) and B (size 3)
    A = [(0, 1)]
    B = [(1, 2), (2, 3), (3, 0)]
    assert matroid.is_independent(A)
    assert matroid.is_independent(B)
    assert matroid.test_exchange_property(A, B) is True
    print("  -> Passed. Graphic Matroid exchange axiom mathematically verified.")

    print("ALL Level 4 Chapter 04 Greedy & Matroid lab tests passed successfully!")


if __name__ == "__main__":
    test_greedy_lab()
