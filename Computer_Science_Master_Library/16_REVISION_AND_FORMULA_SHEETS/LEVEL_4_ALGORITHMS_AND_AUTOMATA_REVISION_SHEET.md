# Level 4 Revision & Formula Sheet: Advanced Algorithms, Dynamic Programming & Automata

---

## 1. Quick Reference: Chapters 01 to 05

| Chapter | Core Focus | Key Axioms & Master Invariants | Primary Pitfalls / Edge Cases |
|:---|:---|:---|:---|
| **CH01: Graph Algorithms & Shortest Paths** | CSR graphs, Dijkstra, Bellman-Ford, Tarjan SCC | $\text{dist}[v] \le \text{dist}[u] + w(u, v)$ (Triangle Ineq.); $\text{low}[u] = \min(\text{disc}[u], \dots)$ | Dijkstra on negative edge weights; dangling edges in CSR indexing |
| **CH02: MST & Network Flow** | Kruskal, Prim, Edmonds-Karp, Dinic | $\sum_{e \in \delta^+(u)} f(e) = \sum_{e \in \delta^-(u)} f(e)$; $\text{Max Flow} = \text{Min Cut}$ | Omitting residual back-edges ($c_f(v, u) = f(u, v)$); infinite augmenting loops |
| **CH03: Dynamic Programming Paradigms** | Optimal substructure, overlapping subproblems | $dp[i][w] = \max(dp[i-1][w], v_i + dp[i-1][w - w_i])$; bitmask TSP | Forward iteration in 1D knapsack causing duplicate takes; non-DAG dependencies |
| **CH04: Greedy Algorithms & Matroids** | Greedy choice, hereditary systems, Huffman | $I_1, I_2 \in \mathcal{I}, |I_1| < |I_2| \implies \exists e \in I_2 \setminus I_1 : I_1 \cup \{e\} \in \mathcal{I}$ | Non-matroid problems with local optima trap; prefix collision in variable-length codes |
| **CH05: Automata & Formal Languages** | DFA/NFA, Chomsky Hierarchy, CYK, Pumping Lemma | $M = (Q, \Sigma, \delta, q_0, F)$; $|uv^i w| \in L \ \forall i \ge 0$; $P(A \to BC) = \mathcal{O}(n^3)$ | Non-deterministic state explosion; CFG parser assuming CNF without prior binarization |

---

## 2. Graph Algorithms & Shortest Paths Formula Matrix

### 2.1 Shortest Path Comparison Table
| Algorithm | Edge Weights | Time Complexity | Auxiliary Space | Negative Cycle Detection? |
|:---|:---|:---|:---|:---|
| **Breadth-First Search (BFS)** | Unweighted / Unit ($w=1$) | $\mathcal{O}(V + E)$ | $\mathcal{O}(V)$ | N/A |
| **Dijkstra (Fibonacci Heap)** | Non-negative ($w \ge 0$) | $\mathcal{O}(E + V \log V)$ | $\mathcal{O}(V)$ | No (Fails/Loops) |
| **Dijkstra (Binary Heap)** | Non-negative ($w \ge 0$) | $\mathcal{O}((V + E) \log V)$ | $\mathcal{O}(V)$ | No |
| **Bellman-Ford** | Arbitrary ($\mathbb{R}$) | $\mathcal{O}(V \cdot E)$ | $\mathcal{O}(V)$ | **Yes** ($V$-th iteration test) |
| **SPFA (Shortest Path Faster)**| Arbitrary ($\mathbb{R}$) | $\mathcal{O}(E)$ avg, $\mathcal{O}(V \cdot E)$ worst | $\mathcal{O}(V)$ | **Yes** (queue visit count $\ge V$) |
| **Floyd-Warshall** | All-Pairs ($\mathbb{R}$, no neg cycle) | $\mathcal{O}(V^3)$ | $\mathcal{O}(V^2)$ | **Yes** ($\text{dist}[i][i] < 0$) |
| **Johnson's Algorithm** | All-Pairs Sparse ($\mathbb{R}$) | $\mathcal{O}(V^2 \log V + V E)$ | $\mathcal{O}(V^2)$ | **Yes** (via initial Bellman-Ford step) |

### 2.2 Tarjan's Strongly Connected Components (SCC)
- **Discovery time array**: `disc[u]`
- **Low-link value**: `low[u]`
- **Rule**:
  $$\text{low}[u] = \min \begin{cases} \text{disc}[u] \\ \text{low}[v] & \text{if } (u, v) \text{ is a tree edge} \\ \text{disc}[v] & \text{if } (u, v) \text{ is a back edge and } v \in \text{stack} \end{cases}$$
- **Root Identification**: If $\text{low}[u] = \text{disc}[u]$, pop the stack until $u$ is removed; all popped nodes form one SCC.

---

## 3. Network Flow & Minimum Cut Invariants

### 3.1 Max-Flow Min-Cut Theorem
$$\max |f| = \min_{(S, T)} c(S, T) = \sum_{u \in S, v \in T} c(u, v)$$
- **Residual Capacity Definition**:
  $$c_f(u, v) = c(u, v) - f(u, v), \quad c_f(v, u) = f(u, v)$$
- **Residual Graph Construction**: For every directed edge with flow $f(u, v)$, maintain a forward edge with capacity $c - f$ and a reverse edge with capacity $f$.

### 3.2 Max-Flow Algorithm Complexity
| Algorithm | Augmentation Strategy | Time Complexity | Notes |
|:---|:---|:---|:---|
| **Ford-Fulkerson** | Any augmenting path (DFS) | $\mathcal{O}(E \cdot |f^*|)$ | Pseudo-polynomial; can diverge on irrational capacities |
| **Edmonds-Karp** | Shortest augmenting path (BFS) | $\mathcal{O}(V \cdot E^2)$ | Guaranteed polynomial; at most $\mathcal{O}(V E)$ augmentations |
| **Dinic's Algorithm** | Layered BFS DAG + Blocking Flow DFS | $\mathcal{O}(V^2 E)$ (Unit network: $\mathcal{O}(E \sqrt{V})$) | De-facto competitive programming & industry standard |
| **Push-Relabel (FIFO)** | Local preflow push + node discharge | $\mathcal{O}(V^3)$ | Highly parallelizable |

---

## 4. Dynamic Programming Recurrence Catalog

### 4.1 0/1 Knapsack
- **2D Recurrence**:
  $$dp[i][w] = \max(dp[i-1][w], v_i + dp[i-1][w - w_i]) \quad \text{for } w \ge w_i$$
- **1D Space Compression**:
  $$dp[w] = \max(dp[w], v_i + dp[w - w_i]) \quad \text{iterating } w \text{ backward from } W \text{ to } w_i$$

### 4.2 Longest Common Subsequence (LCS)
$$dp[i][j] = \begin{cases} dp[i-1][j-1] + 1 & \text{if } A[i] = B[j] \\ \max(dp[i-1][j], dp[i][j-1]) & \text{if } A[i] \neq B[j] \end{cases}$$

### 4.3 Longest Increasing Subsequence (LIS) in $\mathcal{O}(n \log n)$
- Maintain array `tails[k]` = smallest tail element of all increasing subsequences of length $k+1$.
- For each $x \in A$:
  - Binary search (Patience Sorting) index $idx$ in `tails` such that $\text{tails}[idx] \ge x$.
  - Update $\text{tails}[idx] = x$. If $idx = \text{len}(\text{tails})$, append $x$.
- Final LIS length = $\text{len}(\text{tails})$.

### 4.4 Held-Karp Traveling Salesperson Problem (TSP)
$$dp[S][u] = \min_{v \in S \setminus \{u\}} \left( dp[S \setminus \{u\}][v] + \text{cost}[v][u] \right)$$
- Space: $\mathcal{O}(n \cdot 2^n)$
- Time: $\mathcal{O}(n^2 \cdot 2^n)$

---

## 5. Matroid Theory & Greedy Choice Axioms

A Matroid $M = (E, \mathcal{I})$ satisfies:
1. **Non-emptiness**: $\emptyset \in \mathcal{I}$
2. **Hereditary Property**: $A \in \mathcal{I} \land B \subseteq A \implies B \in \mathcal{I}$
3. **Exchange Property**: $A, B \in \mathcal{I} \land |A| < |B| \implies \exists x \in B \setminus A : A \cup \{x\} \in \mathcal{I}$

**Rado-Edmonds Theorem**: The greedy algorithm finds a maximum-weight independent set for all weight functions $w: E \to \mathbb{R}^+$ if and only if $(E, \mathcal{I})$ is a matroid.

**Kraft-McMillan Inequality for Prefix Codes**:
$$\sum_{i=1}^k r^{-l_i} \le 1 \quad (r = 2 \text{ for binary})$$

---

## 6. Automata & Formal Language Hierarchy

```
Chomsky Hierarchy:
+---------------------------------------------------------------------------------+
| Type 0: Unrestricted Languages          -- Turing Machines                      |
|   +-----------------------------------------------------------------------------+
|   | Type 1: Context-Sensitive Languages   -- Linear Bounded Automata (LBA)      |
|   |   +-------------------------------------------------------------------------+
|   |   | Type 2: Context-Free Languages    -- Pushdown Automata (PDA)            |
|   |   |   +---------------------------------------------------------------------+
|   |   |   | Type 3: Regular Languages     -- Deterministic Finite Automata (DFA)|
|   |   |   +---------------------------------------------------------------------+
|   |   +-------------------------------------------------------------------------+
|   +-----------------------------------------------------------------------------+
+---------------------------------------------------------------------------------+
```

### 6.1 Pumping Lemma for Regular Languages
If $L$ is regular, $\exists p \ge 1$ such that $\forall w \in L$ with $|w| \ge p$, $w = xyz$ satisfying:
1. $|y| \ge 1$
2. $|xy| \le p$
3. $\forall i \ge 0, \quad x y^i z \in L$

### 6.2 CYK Algorithm Recurrence (Grammars in Chomsky Normal Form)
For CNF rules $A \to BC$ and $A \to a$:
$$V[i, j, A] = \bigvee_{k=i}^{j-1} \bigvee_{A \to BC} (V[i, k, B] \land V[k+1, j, C])$$
- Time Complexity: $\mathcal{O}(n^3 \cdot |R|)$
- Space Complexity: $\mathcal{O}(n^2 \cdot |V|)$
