"""
Level 4 Chapter 01: Graph Algorithms — Representations, Traversals, and Shortest Paths
Comprehensive Laboratory Verification Suite

Covers:
1. CSR (Compressed Sparse Row) and Adjacency List representations.
2. BFS, DFS, and Kahn's Topological Sorting with cycle detection.
3. Dijkstra's Algorithm with Min-Heap for SSSP.
4. Bellman-Ford with negative cycle detection.
5. Tarjan's Strongly Connected Components (SCC) algorithm.
"""

import sys
import heapq
from collections import deque
from typing import List, Dict, Tuple, Optional, Set

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# -------------------------------------------------------------
# 1. Graph Representations: CSR Format
# -------------------------------------------------------------
class CSRGraph:
    def __init__(self, num_vertices: int, edges: List[Tuple[int, int, int]]):
        self.V = num_vertices
        self.E = len(edges)
        self.offsets = [0] * (self.V + 1)
        self.destinations = [0] * self.E
        self.weights = [0] * self.E

        # Count out-degrees
        for u, _, _ in edges:
            self.offsets[u + 1] += 1

        # Prefix sums for offsets
        for i in range(1, self.V + 1):
            self.offsets[i] += self.offsets[i - 1]

        cursor = list(self.offsets)
        for u, v, w in edges:
            pos = cursor[u]
            self.destinations[pos] = v
            self.weights[pos] = w
            cursor[u] += 1

    def get_neighbors(self, u: int) -> List[Tuple[int, int]]:
        start = self.offsets[u]
        end = self.offsets[u + 1]
        return [(self.destinations[i], self.weights[i]) for i in range(start, end)]


# -------------------------------------------------------------
# 2. Traversals & Topological Sorting
# -------------------------------------------------------------
def bfs_shortest_path(adj: List[List[int]], src: int, target: int) -> Optional[List[int]]:
    visited = {src}
    parent = {src: None}
    q = deque([src])

    while q:
        u = q.popleft()
        if u == target:
            break
        for v in adj[u]:
            if v not in visited:
                visited.add(v)
                parent[v] = u
                q.append(v)

    if target not in parent:
        return None
    path = []
    curr = target
    while curr is not None:
        path.append(curr)
        curr = parent[curr]
    path.reverse()
    return path


def kahn_topological_sort(n: int, edges: List[Tuple[int, int]]) -> Optional[List[int]]:
    in_degree = [0] * n
    adj: List[List[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1

    q = deque([i for i in range(n) if in_degree[i] == 0])
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                q.append(v)

    return order if len(order) == n else None  # None if cycle detected


# -------------------------------------------------------------
# 3. Shortest Path Algorithms: Dijkstra & Bellman-Ford
# -------------------------------------------------------------
def dijkstra_sssp(n: int, adj_weighted: List[List[Tuple[int, int]]], src: int) -> List[int]:
    dist = [float("inf")] * n
    dist[src] = 0
    pq = [(0, src)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj_weighted[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))

    return dist


def bellman_ford_sssp(n: int, edges: List[Tuple[int, int, int]], src: int) -> Tuple[List[int], bool]:
    dist = [float("inf")] * n
    dist[src] = 0

    # Relax |V| - 1 times
    for _ in range(n - 1):
        for u, v, w in edges:
            if dist[u] != float("inf") and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w

    # Check for negative weight cycles
    has_negative_cycle = False
    for u, v, w in edges:
        if dist[u] != float("inf") and dist[u] + w < dist[v]:
            has_negative_cycle = True
            break

    return dist, has_negative_cycle


# -------------------------------------------------------------
# 4. Tarjan's Strongly Connected Components (SCC)
# -------------------------------------------------------------
def tarjan_scc(n: int, adj: List[List[int]]) -> List[List[int]]:
    disc = [-1] * n
    low = [-1] * n
    on_stack = [False] * n
    stack = []
    timer = 0
    sccs = []

    def _dfs(u: int):
        nonlocal timer
        disc[u] = low[u] = timer
        timer += 1
        stack.append(u)
        on_stack[u] = True

        for v in adj[u]:
            if disc[v] == -1:
                _dfs(v)
                low[u] = min(low[u], low[v])
            elif on_stack[v]:
                low[u] = min(low[u], disc[v])

        if low[u] == disc[u]:
            component = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                component.append(w)
                if w == u:
                    break
            sccs.append(component)

    for i in range(n):
        if disc[i] == -1:
            _dfs(i)

    return sccs


# -------------------------------------------------------------
# Test Suite
# -------------------------------------------------------------
def test_graphs_lab():
    print("[TEST 1] CSR Graph Representation...")
    edges = [(0, 1, 10), (0, 2, 20), (1, 2, 5), (2, 3, 15)]
    csr = CSRGraph(4, edges)
    assert csr.get_neighbors(0) == [(1, 10), (2, 20)]
    assert csr.get_neighbors(1) == [(2, 5)]
    assert csr.get_neighbors(2) == [(3, 15)]
    assert csr.get_neighbors(3) == []
    print("  -> Passed. CSR layout correctly indexes contiguous edges.")

    print("[TEST 2] BFS & Kahn's Topological Sort with Cycle Detection...")
    adj = [[1, 2], [3], [3], []]
    path = bfs_shortest_path(adj, 0, 3)
    assert path in ([0, 1, 3], [0, 2, 3])

    # DAG Topological sort
    dag_edges = [(5, 2), (5, 0), (4, 0), (4, 1), (2, 3), (3, 1)]
    top_order = kahn_topological_sort(6, dag_edges)
    assert top_order is not None and len(top_order) == 6
    # Verify topological invariants: for each u -> v, u appears before v
    pos = {node: idx for idx, node in enumerate(top_order)}
    for u, v in dag_edges:
        assert pos[u] < pos[v]

    # Cyclic graph detection
    cyclic_edges = [(0, 1), (1, 2), (2, 0)]
    assert kahn_topological_sort(3, cyclic_edges) is None
    print("  -> Passed. BFS shortest path and Kahn cycle detection verified.")

    print("[TEST 3] Dijkstra vs Bellman-Ford on Positive Graph...")
    n = 5
    graph_edges = [(0, 1, 4), (0, 2, 2), (1, 2, 1), (1, 3, 2), (1, 4, 3), (2, 1, 1), (2, 3, 4), (2, 4, 5), (4, 3, 1)]
    adj_w: List[List[Tuple[int, int]]] = [[] for _ in range(n)]
    for u, v, w in graph_edges:
        adj_w[u].append((v, w))

    dijkstra_dist = dijkstra_sssp(n, adj_w, 0)
    bf_dist, has_neg = bellman_ford_sssp(n, graph_edges, 0)

    assert not has_neg
    assert dijkstra_dist == bf_dist == [0, 3, 2, 5, 6]
    print("  -> Passed. Dijkstra and Bellman-Ford agree on shortest paths.")

    print("[TEST 4] Bellman-Ford Negative Cycle Detection...")
    neg_cycle_edges = [(0, 1, 1), (1, 2, 2), (2, 3, -8), (3, 1, 1)]
    _, has_neg_cycle = bellman_ford_sssp(4, neg_cycle_edges, 0)
    assert has_neg_cycle is True
    print("  -> Passed. Negative weight cycle successfully trapped.")

    print("[TEST 5] Tarjan's Strongly Connected Components (SCC)...")
    scc_adj = [[1], [2], [0, 3], [4], [5], [3]]
    sccs = tarjan_scc(6, scc_adj)
    # Expected SCCs: {0, 1, 2} and {3, 4, 5}
    sorted_sccs = sorted([sorted(c) for c in sccs])
    assert sorted_sccs == [[0, 1, 2], [3, 4, 5]], f"Tarjan SCC mismatch: {sorted_sccs}"
    print("  -> Passed. Tarjan's algorithm correctly decomposed graph into SCCs.")

    print("ALL Level 4 Chapter 01 Graph lab tests passed successfully!")


if __name__ == "__main__":
    test_graphs_lab()
