"""
Level 4 Chapter 03: Dynamic Programming Paradigms and Complexity Analysis
Comprehensive Laboratory Verification Suite

Covers:
1. 0/1 Knapsack: 2D matrix vs. 1D rolling array with backtracking.
2. Longest Common Subsequence (LCS) with full string reconstruction.
3. Longest Increasing Subsequence (LIS): O(n^2) vs. O(n log n) Patience Sorting.
4. Held-Karp Bitmask DP for Traveling Salesperson Problem (TSP).
"""

import sys
import bisect
import random
from typing import List, Tuple, Optional

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# -------------------------------------------------------------
# 1. 0/1 Knapsack (2D & 1D Space-Optimized)
# -------------------------------------------------------------
def knapsack_2d(weights: List[int], values: List[int], W: int) -> Tuple[int, List[int]]:
    n = len(weights)
    dp = [[0] * (W + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        wi, vi = weights[i - 1], values[i - 1]
        for w in range(W + 1):
            if wi > w:
                dp[i][w] = dp[i - 1][w]
            else:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - wi] + vi)

    # Backtracking items
    items_taken = []
    curr_w = W
    for i in range(n, 0, -1):
        if dp[i][curr_w] != dp[i - 1][curr_w]:
            items_taken.append(i - 1)
            curr_w -= weights[i - 1]

    items_taken.reverse()
    return dp[n][W], items_taken


def knapsack_1d_optimized(weights: List[int], values: List[int], W: int) -> int:
    dp = [0] * (W + 1)
    for wi, vi in zip(weights, values):
        for w in range(W, wi - 1, -1):  # Reverse scan prevents item re-use
            dp[w] = max(dp[w], dp[w - wi] + vi)
    return dp[W]


# -------------------------------------------------------------
# 2. Longest Common Subsequence (LCS)
# -------------------------------------------------------------
def lcs_with_reconstruction(X: str, Y: str) -> Tuple[int, str]:
    m, n = len(X), len(Y)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i - 1] == Y[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Reconstruct string
    lcs_chars = []
    i, j = m, n
    while i > 0 and j > 0:
        if X[i - 1] == Y[j - 1]:
            lcs_chars.append(X[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    lcs_chars.reverse()
    return dp[m][n], "".join(lcs_chars)


# -------------------------------------------------------------
# 3. Longest Increasing Subsequence (LIS)
# -------------------------------------------------------------
def lis_quadratic(arr: List[int]) -> int:
    if not arr:
        return 0
    n = len(arr)
    dp = [1] * n
    for i in range(1, n):
        for j in range(i):
            if arr[j] < arr[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)


def lis_optimal_log(arr: List[int]) -> int:
    if not arr:
        return 0
    tails = []
    for x in arr:
        idx = bisect.bisect_left(tails, x)
        if idx == len(tails):
            tails.append(x)
        else:
            tails[idx] = x
    return len(tails)


# -------------------------------------------------------------
# 4. Held-Karp Bitmask DP for TSP
# -------------------------------------------------------------
def tsp_held_karp(dist: List[List[int]]) -> Tuple[int, List[int]]:
    n = len(dist)
    num_states = 1 << n
    INF = float("inf")

    # dp[mask][u] = (cost, parent)
    dp = [[(INF, -1) for _ in range(n)] for _ in range(num_states)]
    dp[1][0] = (0, -1)

    for mask in range(1, num_states):
        for u in range(n):
            if not (mask & (1 << u)):
                continue
            curr_cost = dp[mask][u][0]
            if curr_cost == INF:
                continue

            for v in range(n):
                if mask & (1 << v):
                    continue
                next_mask = mask | (1 << v)
                new_cost = curr_cost + dist[u][v]
                if new_cost < dp[next_mask][v][0]:
                    dp[next_mask][v] = (new_cost, u)

    final_mask = (1 << n) - 1
    best_cost = INF
    last_node = -1
    for u in range(1, n):
        total = dp[final_mask][u][0] + dist[u][0]
        if total < best_cost:
            best_cost = total
            last_node = u

    # Reconstruct tour
    tour = [0]
    curr = last_node
    curr_mask = final_mask
    while curr != -1:
        tour.append(curr)
        next_curr = dp[curr_mask][curr][1]
        curr_mask ^= (1 << curr)
        curr = next_curr

    tour.reverse()
    return best_cost, tour


# -------------------------------------------------------------
# Test Suite
# -------------------------------------------------------------
def test_dp_lab():
    print("[TEST 1] 0/1 Knapsack 2D Matrix vs 1D Space-Optimized...")
    weights = [2, 3, 4, 5]
    values = [3, 4, 5, 6]
    W = 8

    val_2d, items = knapsack_2d(weights, values, W)
    val_1d = knapsack_1d_optimized(weights, values, W)

    assert val_2d == val_1d == 10, f"Knapsack mismatch: 2D={val_2d}, 1D={val_1d}"
    assert sum(weights[i] for i in items) <= W
    assert sum(values[i] for i in items) == 10
    print(f"  -> Passed. Knapsack optimal value = {val_2d}, items selected: {items}")

    print("[TEST 2] Longest Common Subsequence (LCS) Reconstruction...")
    X = "ABCBDAB"
    Y = "BDCABA"
    lcs_len, lcs_str = lcs_with_reconstruction(X, Y)
    assert lcs_len == 4, f"Expected LCS length 4, got {lcs_len}"
    assert len(lcs_str) == 4
    # Validate subsequence property
    it = iter(Y)
    assert all(c in it for c in lcs_str), f"'{lcs_str}' is not a valid subsequence of '{Y}'"
    print(f"  -> Passed. LCS length = {lcs_len}, reconstructed sequence: '{lcs_str}'")

    print("[TEST 3] Longest Increasing Subsequence: O(n^2) vs O(n log n)...")
    random.seed(42)
    test_arr = [random.randint(0, 1000) for _ in range(250)]
    lis_slow = lis_quadratic(test_arr)
    lis_fast = lis_optimal_log(test_arr)
    assert lis_slow == lis_fast, f"LIS mismatch: O(n^2)={lis_slow}, O(n log n)={lis_fast}"
    print(f"  -> Passed. LIS optimal O(n log n) matched quadratic DP (length={lis_fast}).")

    print("[TEST 4] Held-Karp Bitmask DP for Traveling Salesperson Problem...")
    # 4-city asymmetric distance matrix
    dist_matrix = [
        [0, 10, 15, 20],
        [10, 0, 35, 25],
        [15, 35, 0, 30],
        [20, 25, 30, 0]
    ]
    min_cost, tour = tsp_held_karp(dist_matrix)
    # Expected optimal tour: 0 -> 1 -> 3 -> 2 -> 0 = 10 + 25 + 30 + 15 = 80
    assert min_cost == 80, f"Expected TSP cost 80, got {min_cost}"
    assert tour[0] == 0 and tour[-1] == 0 and len(tour) == 5
    print(f"  -> Passed. Held-Karp found optimal tour {tour} with cost {min_cost}.")

    print("ALL Level 4 Chapter 03 Dynamic Programming lab tests passed successfully!")


if __name__ == "__main__":
    test_dp_lab()
