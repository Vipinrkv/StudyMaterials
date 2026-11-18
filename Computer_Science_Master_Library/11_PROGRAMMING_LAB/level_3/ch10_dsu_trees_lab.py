"""
Level 3 Chapter 10: Disjoint Set Union (DSU) and Advanced Range Trees
Comprehensive Laboratory Verification Suite

Covers:
1. Disjoint Set Union (DSU) with Path Compression and Union by Rank.
2. Cycle detection and connected component tracking using DSU.
3. Fenwick Tree (Binary Indexed Tree) with O(n) construction and range sum queries.
4. Segment Tree supporting point updates and Range Minimum Queries (RMQ).
"""

import sys
from typing import List, Optional

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# -------------------------------------------------------------
# 1. Disjoint Set Union (DSU)
# -------------------------------------------------------------
class DisjointSetUnion:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.components = n

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            # Path compression
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False  # Already in the same component (indicates a cycle in graphs)

        # Union by rank
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1

        self.components -= 1
        return True

    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)


# -------------------------------------------------------------
# 2. Fenwick Tree (Binary Indexed Tree)
# -------------------------------------------------------------
class FenwickTree:
    """1-indexed Binary Indexed Tree for prefix and range sum queries."""
    def __init__(self, arr: List[int]):
        self.n = len(arr)
        self.tree = [0] * (self.n + 1)
        # O(n) linear construction
        for i in range(1, self.n + 1):
            self.tree[i] = arr[i - 1]
        for i in range(1, self.n + 1):
            parent = i + (i & -i)
            if parent <= self.n:
                self.tree[parent] += self.tree[i]

    def add(self, idx: int, delta: int) -> None:
        """Adds delta to 1-based index idx."""
        while idx <= self.n:
            self.tree[idx] += delta
            idx += (idx & -idx)

    def prefix_sum(self, idx: int) -> int:
        """Returns sum of elements from index 1 to idx."""
        total = 0
        while idx > 0:
            total += self.tree[idx]
            idx -= (idx & -idx)
        return total

    def range_sum(self, left: int, right: int) -> int:
        """Returns sum in 1-based interval [left, right]."""
        if left > right:
            return 0
        return self.prefix_sum(right) - self.prefix_sum(left - 1)


# -------------------------------------------------------------
# 3. Segment Tree for Range Minimum Queries (RMQ)
# -------------------------------------------------------------
class SegmentTreeRMQ:
    """Segment Tree for point update and Range Minimum Query (RMQ)."""
    def __init__(self, arr: List[int]):
        self.n = len(arr)
        self.tree = [float("inf")] * (4 * self.n)
        if self.n > 0:
            self._build(arr, 1, 0, self.n - 1)

    def _build(self, arr: List[int], node: int, l: int, r: int) -> None:
        if l == r:
            self.tree[node] = arr[l]
            return
        mid = (l + r) // 2
        self._build(arr, 2 * node, l, mid)
        self._build(arr, 2 * node + 1, mid + 1, r)
        self.tree[node] = min(self.tree[2 * node], self.tree[2 * node + 1])

    def update(self, idx: int, val: int) -> None:
        """Updates element at 0-based index idx to val."""
        self._update(1, 0, self.n - 1, idx, val)

    def _update(self, node: int, l: int, r: int, idx: int, val: int) -> None:
        if l == r:
            self.tree[node] = val
            return
        mid = (l + r) // 2
        if idx <= mid:
            self._update(2 * node, l, mid, idx, val)
        else:
            self._update(2 * node + 1, mid + 1, r, idx, val)
        self.tree[node] = min(self.tree[2 * node], self.tree[2 * node + 1])

    def query_min(self, ql: int, qr: int) -> int:
        """Returns the minimum element in 0-based range [ql, qr]."""
        return self._query(1, 0, self.n - 1, ql, qr)

    def _query(self, node: int, l: int, r: int, ql: int, qr: int) -> float:
        if ql > r or qr < l:
            return float("inf")
        if ql <= l and r <= qr:
            return self.tree[node]
        mid = (l + r) // 2
        left_min = self._query(2 * node, l, mid, ql, qr)
        right_min = self._query(2 * node + 1, mid + 1, r, ql, qr)
        return min(left_min, right_min)


# -------------------------------------------------------------
# Test Suite
# -------------------------------------------------------------
def test_dsu_trees_lab():
    print("[TEST 1] Disjoint Set Union (DSU) Connectivity & Cycle Detection...")
    dsu = DisjointSetUnion(7)
    assert dsu.components == 7

    # Build components: {0, 1, 2} and {3, 4}
    assert dsu.union(0, 1) is True
    assert dsu.union(1, 2) is True
    assert dsu.union(0, 2) is False  # Cycle detected! Edge is redundant.
    assert dsu.components == 5

    assert dsu.union(3, 4) is True
    assert dsu.components == 4

    assert dsu.connected(0, 2) is True
    assert dsu.connected(0, 3) is False
    assert dsu.connected(4, 3) is True

    # Path compression check: query 2 flattens depth
    _ = dsu.find(2)
    assert dsu.parent[2] == dsu.find(0)
    print("  -> Passed. DSU connectivity and cycle detection verified.")

    print("[TEST 2] Fenwick Tree Prefix and Range Sum Queries...")
    raw = [3, 2, -1, 6, 5, 4, -3, 3, 7, 2]
    bit = FenwickTree(raw)

    # Check prefix sums: 1-indexed
    # raw[:6] = [3, 2, -1, 6, 5, 4] -> sum = 19
    assert bit.prefix_sum(6) == 19
    # range [3, 7] in 1-based: raw[2..6] = [-1, 6, 5, 4, -3] -> sum = 11
    assert bit.range_sum(3, 7) == 11

    # Point update: add 10 to index 4 (1-based, was 6, now 16)
    bit.add(4, 10)
    assert bit.range_sum(3, 7) == 21
    assert bit.prefix_sum(4) == 20
    print("  -> Passed. Fenwick tree O(n) construction and bitwise updates verified.")

    print("[TEST 3] Segment Tree Range Minimum Query (RMQ)...")
    vals = [18, 17, 13, 19, 15, 11, 20]
    st = SegmentTreeRMQ(vals)

    # Range [0, 6] min is 11
    assert st.query_min(0, 6) == 11
    # Range [0, 3] min is 13
    assert st.query_min(0, 3) == 13
    # Range [4, 6] min is 11
    assert st.query_min(4, 6) == 11

    # Point update: index 5 was 11, change to 50
    st.update(5, 50)
    # Now range [4, 6] contains [15, 50, 20], min is 15
    assert st.query_min(4, 6) == 15
    # Overall min in [0, 6] is now 13
    assert st.query_min(0, 6) == 13
    print("  -> Passed. Segment Tree point update and RMQ queries verified.")

    print("ALL Chapter 10 DSU & Advanced Trees lab tests passed successfully!")


if __name__ == "__main__":
    test_dsu_trees_lab()
