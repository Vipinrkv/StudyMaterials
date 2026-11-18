"""
Level 4 Chapter 02: Minimum Spanning Trees and Network Flow
Comprehensive Laboratory Verification Suite

Covers:
1. Kruskal's Algorithm using Disjoint Set Union (DSU).
2. Prim's Algorithm using Priority Queue (Min-Heap).
3. Edmonds-Karp Maximum Flow (BFS augmenting paths).
4. Dinic's Blocking Flow Algorithm (Layered Graph).
5. Max-Flow Min-Cut duality verification.
6. Maximum Bipartite Matching reduction test.
"""

import sys
import heapq
from collections import deque
from typing import List, Tuple, Optional, Set

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# -------------------------------------------------------------
# 1. MST: Kruskal and Prim
# -------------------------------------------------------------
class DSU:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            self.parent[rx] = ry
        elif self.rank[rx] > self.rank[ry]:
            self.parent[ry] = rx
        else:
            self.parent[ry] = rx
            self.rank[rx] += 1
        return True


def kruskal_mst(n: int, edges: List[Tuple[int, int, int]]) -> Tuple[int, List[Tuple[int, int, int]]]:
    sorted_edges = sorted(edges, key=lambda x: x[2])
    dsu = DSU(n)
    mst = []
    total_weight = 0

    for u, v, w in sorted_edges:
        if dsu.union(u, v):
            mst.append((u, v, w))
            total_weight += w
            if len(mst) == n - 1:
                break
    return total_weight, mst


def prim_mst(n: int, adj: List[List[Tuple[int, int]]], src: int = 0) -> int:
    visited = [False] * n
    pq = [(0, src)]
    total_weight = 0
    edges_count = 0

    while pq and edges_count < n:
        w, u = heapq.heappop(pq)
        if visited[u]:
            continue
        visited[u] = True
        total_weight += w
        edges_count += 1

        for v, weight in adj[u]:
            if not visited[v]:
                heapq.heappush(pq, (weight, v))

    return total_weight


# -------------------------------------------------------------
# 2. Network Flow: Edmonds-Karp & Dinic
# -------------------------------------------------------------
class EdmondsKarp:
    def __init__(self, n: int):
        self.n = n
        self.capacity = [[0] * n for _ in range(n)]
        self.flow = [[0] * n for _ in range(n)]

    def add_edge(self, u: int, v: int, cap: int) -> None:
        self.capacity[u][v] += cap

    def max_flow(self, s: int, t: int) -> int:
        total_flow = 0
        while True:
            parent = [-1] * self.n
            parent[s] = s
            q = deque([s])
            while q and parent[t] == -1:
                u = q.popleft()
                for v in range(self.n):
                    if parent[v] == -1 and self.capacity[u][v] - self.flow[u][v] > 0:
                        parent[v] = u
                        q.append(v)

            if parent[t] == -1:
                break

            # Find bottleneck
            bottleneck = float("inf")
            curr = t
            while curr != s:
                p = parent[curr]
                bottleneck = min(bottleneck, self.capacity[p][curr] - self.flow[p][curr])
                curr = p

            # Augment
            curr = t
            while curr != s:
                p = parent[curr]
                self.flow[p][curr] += bottleneck
                self.flow[curr][p] -= bottleneck
                curr = p

            total_flow += bottleneck

        return total_flow

    def get_min_cut(self, s: int) -> Tuple[Set[int], Set[int], int]:
        visited = set()
        q = deque([s])
        visited.add(s)
        while q:
            u = q.popleft()
            for v in range(self.n):
                if v not in visited and self.capacity[u][v] - self.flow[u][v] > 0:
                    visited.add(v)
                    q.append(v)

        s_cut = visited
        t_cut = set(range(self.n)) - s_cut
        cut_cap = sum(self.capacity[u][v] for u in s_cut for v in t_cut)
        return s_cut, t_cut, cut_cap


class DinicFlow:
    class Edge:
        def __init__(self, to: int, rev: int, cap: int):
            self.to = to
            self.rev = rev
            self.cap = cap
            self.flow = 0

    def __init__(self, n: int):
        self.n = n
        self.adj = [[] for _ in range(n)]
        self.level = [-1] * n
        self.ptr = [0] * n

    def add_edge(self, u: int, v: int, cap: int) -> None:
        self.adj[u].append(self.Edge(v, len(self.adj[v]), cap))
        self.adj[v].append(self.Edge(u, len(self.adj[u]) - 1, 0))

    def _bfs(self, s: int, t: int) -> bool:
        self.level = [-1] * self.n
        self.level[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for edge in self.adj[u]:
                if edge.cap - edge.flow > 0 and self.level[edge.to] == -1:
                    self.level[edge.to] = self.level[u] + 1
                    q.append(edge.to)
        return self.level[t] != -1

    def _dfs(self, u: int, t: int, pushed: int) -> int:
        if pushed == 0 or u == t:
            return pushed
        for cid in range(self.ptr[u], len(self.adj[u])):
            self.ptr[u] = cid
            edge = self.adj[u][cid]
            tr = edge.to
            if self.level[tr] != self.level[u] + 1 or edge.cap - edge.flow <= 0:
                continue
            tr_pushed = self._dfs(tr, t, min(pushed, edge.cap - edge.flow))
            if tr_pushed == 0:
                continue
            edge.flow += tr_pushed
            self.adj[tr][edge.rev].flow -= tr_pushed
            return tr_pushed
        return 0

    def max_flow(self, s: int, t: int) -> int:
        flow = 0
        while self._bfs(s, t):
            self.ptr = [0] * self.n
            while True:
                pushed = self._dfs(s, t, float("inf"))
                if pushed == 0:
                    break
                flow += pushed
        return flow


# -------------------------------------------------------------
# 3. Maximum Bipartite Matching via Max Flow
# -------------------------------------------------------------
def max_bipartite_matching(num_left: int, num_right: int, edges: List[Tuple[int, int]]) -> int:
    # Source = 0, Left = 1..num_left, Right = num_left+1..num_left+num_right, Sink = num_left+num_right+1
    source = 0
    sink = num_left + num_right + 1
    total_nodes = sink + 1

    dinic = DinicFlow(total_nodes)

    # Source to Left
    for u in range(1, num_left + 1):
        dinic.add_edge(source, u, 1)

    # Left to Right
    for u, v in edges:
        dinic.add_edge(u + 1, num_left + 1 + v, 1)

    # Right to Sink
    for v in range(1, num_right + 1):
        dinic.add_edge(num_left + v, sink, 1)

    return dinic.max_flow(source, sink)


# -------------------------------------------------------------
# Test Suite
# -------------------------------------------------------------
def test_mst_flow_lab():
    print("[TEST 1] Kruskal vs Prim Minimum Spanning Tree...")
    n = 5
    edges = [
        (0, 1, 1), (1, 3, 2), (0, 2, 3), (1, 2, 4),
        (0, 3, 4), (2, 3, 5), (2, 4, 6), (3, 4, 7)
    ]
    adj_w: List[List[Tuple[int, int]]] = [[] for _ in range(n)]
    for u, v, w in edges:
        adj_w[u].append((v, w))
        adj_w[v].append((u, w))

    kruskal_weight, mst_edges = kruskal_mst(n, edges)
    prim_weight = prim_mst(n, adj_w, 0)

    assert kruskal_weight == prim_weight == 12, f"MST weight mismatch: Kruskal={kruskal_weight}, Prim={prim_weight}"
    assert len(mst_edges) == 4
    print("  -> Passed. Kruskal and Prim produced identical MST weight (12).")

    print("[TEST 2] Edmonds-Karp & Dinic Max-Flow with Min-Cut Duality...")
    # Classic Goldberg-Tarjan network
    ek = EdmondsKarp(6)
    dinic = DinicFlow(6)

    flow_edges = [
        (0, 1, 16), (0, 2, 13), (1, 2, 10), (2, 1, 4),
        (1, 3, 12), (3, 2, 9),  (2, 4, 14), (4, 3, 7),
        (3, 5, 20), (4, 5, 4)
    ]
    for u, v, cap in flow_edges:
        ek.add_edge(u, v, cap)
        dinic.add_edge(u, v, cap)

    ek_flow = ek.max_flow(0, 5)
    dinic_flow = dinic.max_flow(0, 5)

    assert ek_flow == dinic_flow == 23, f"Max flow mismatch: EK={ek_flow}, Dinic={dinic_flow}"

    # Verify Min-Cut duality: Cut capacity must exactly equal 23!
    _, _, cut_capacity = ek.get_min_cut(0)
    assert cut_capacity == 23, f"Min-Cut capacity {cut_capacity} != Max Flow 23"
    print("  -> Passed. Edmonds-Karp, Dinic, and Min-Cut capacity agree on 23.")

    print("[TEST 3] Maximum Bipartite Matching Reduction...")
    # 4 Applicants, 4 Jobs
    # Applicant 0 -> Jobs 0, 1
    # Applicant 1 -> Jobs 0, 2
    # Applicant 2 -> Job 2
    # Applicant 3 -> Jobs 1, 3
    applicant_job_edges = [(0, 0), (0, 1), (1, 0), (1, 2), (2, 2), (3, 1), (3, 3)]
    matchings = max_bipartite_matching(4, 4, applicant_job_edges)
    assert matchings == 4, f"Expected maximum matching of 4, got {matchings}"
    print("  -> Passed. Maximum Bipartite Matching correctly reduced to Max Flow.")

    print("ALL Level 4 Chapter 02 MST & Network Flow lab tests passed successfully!")


if __name__ == "__main__":
    test_mst_flow_lab()
