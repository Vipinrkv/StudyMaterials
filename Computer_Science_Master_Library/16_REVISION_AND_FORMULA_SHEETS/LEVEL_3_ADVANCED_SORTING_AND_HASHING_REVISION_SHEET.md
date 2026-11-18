# Level 3 Revision & Formula Sheet: Advanced Sorting, Heaps, Hashing & Range Trees

---

## 1. Quick Reference: Chapters 06 to 10

| Chapter | Core Focus | Key Axioms & Formulas | Primary Failure Mode |
|:---|:---|:---|:---|
| **CH06: Heaps & Priority Queues** | Array-based complete binary trees | Parent: $\lfloor (i-1)/2 \rfloor$; Floyd build: $\mathcal{O}(n)$ | Breaking heap invariant; naive $\mathcal{O}(n \log n)$ insertions |
| **CH07: Hashing & Hash Tables** | $\mathcal{O}(1)$ key-value retrieval | $E[\text{probes}] \le \frac{1}{1-\alpha}$; SipHash defense | Tombstone neglect; primary clustering; hash DoS |
| **CH08: Divide-and-Conquer Sorts** | MergeSort, QuickSort, Introsort | Decision tree lower bound $\Omega(n \log n)$; $2 \log_2 n$ depth | $\mathcal{O}(n^2)$ worst-case pivot trap; stack overflow |
| **CH09: Linear Sorts & Selection** | Non-comparison sorts, order statistics | Counting: $\Theta(n+k)$; Radix: $\Theta(d(n+b))$; BFPRT $\mathcal{O}(n)$ | Unbounded $k$ memory explosion; signed integer sign bit |
| **CH10: DSU & Advanced Trees** | Dynamic equivalence & Range queries | DSU: $\mathcal{O}(\alpha(n))$; Fenwick: $i \ \& \ (-i)$; SegTree: $4n$ | 0-indexed Fenwick infinite loop; un-ranked DSU degeneration |

---

## 2. Complete Sorting & Selection Master Complexity Matrix

| Algorithm | Best-Case Time | Average-Case Time | Worst-Case Time | Auxiliary Space | In-Place? | Stable? | Primary Industry Use |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **HeapSort** | $\Theta(n \log n)$ | $\Theta(n \log n)$ | $\mathbf{\Theta(n \log n)}$ | $\mathcal{O}(1)$ | **Yes** | No | Embedded systems with fixed RAM |
| **MergeSort** | $\Theta(n \log n)$ | $\Theta(n \log n)$ | $\mathbf{\Theta(n \log n)}$ | $\mathcal{O}(n)$ | No | **Yes** | Linked lists, External disk sorting |
| **QuickSort (Hoare)** | $\Theta(n \log n)$ | $\mathbf{\Theta(n \log n)}$ | $\mathcal{O}(n^2)$ | $\mathcal{O}(\log n)$ stack | **Yes** | No | General in-memory sorting |
| **QuickSort (3-Way)** | $\mathbf{\mathcal{O}(n)}$ | $\Theta(n \log n)$ | $\mathcal{O}(n^2)$ | $\mathcal{O}(\log n)$ stack | **Yes** | No | Arrays with heavy duplicate keys |
| **Introsort** | $\Theta(n \log n)$ | $\mathbf{\Theta(n \log n)}$ | $\mathbf{\Theta(n \log n)}$ | $\mathcal{O}(\log n)$ stack | **Yes** | No | C++ `std::sort` |
| **Timsort** | $\mathbf{\mathcal{O}(n)}$ | $\Theta(n \log n)$ | $\mathbf{\Theta(n \log n)}$ | $\mathcal{O}(n)$ | No | **Yes** | Python `list.sort()`, Java `Arrays.sort` |
| **Counting Sort** | $\mathbf{\Theta(n + k)}$ | $\mathbf{\Theta(n + k)}$ | $\mathbf{\Theta(n + k)}$ | $\mathcal{O}(n + k)$ | No | **Yes** | Small integer ranges ($k \le \mathcal{O}(n)$) |
| **Radix Sort (LSD)** | $\mathbf{\Theta(d \cdot n)}$ | $\mathbf{\Theta(d \cdot n)}$ | $\mathbf{\Theta(d \cdot n)}$ | $\mathcal{O}(n + 2^r)$ | No | **Yes** | GPU sorting, HFT price-level sorting |
| **QuickSelect** | $\Theta(n)$ | $\mathbf{\Theta(n)}$ | $\mathcal{O}(n^2)$ | $\mathcal{O}(1)$ | **Yes** | No | Finding Top-$K$ / Median in-memory |
| **Median-of-Medians**| $\Theta(n)$ | $\Theta(n)$ | $\mathbf{\Theta(n)}$ | $\mathcal{O}(\log n)$ stack | **Yes** | No | Guaranteed theoretical linear selection |

---

## 3. Heaps & Priority Queues Formulas

### 3.1 0-Indexed Array Mapping Formulas
For node at index $i$:
$$\text{Parent}(i) = \left\lfloor \frac{i - 1}{2} \right\rfloor$$
$$\text{LeftChild}(i) = 2i + 1$$
$$\text{RightChild}(i) = 2i + 2$$
$$\text{Last Non-Leaf Node} = \left\lfloor \frac{n}{2} \right\rfloor - 1$$

### 3.2 Floyd's $\mathcal{O}(n)$ Linear Heap Construction Proof
Total swaps in building a heap of height $h = \lfloor \log_2 n \rfloor$:
$$S = \sum_{i=0}^h \frac{n}{2^{i+1}} \cdot i = \frac{n}{2} \sum_{i=0}^h \frac{i}{2^i}$$
Since $\sum_{i=0}^\infty \frac{i}{2^i} = 2$:
$$S \le \frac{n}{2} \times 2 = \mathbf{\mathcal{O}(n)}$$

---

## 4. Hashing & Open Addressing Formulas

### 4.1 Load Factor and Expected Probes
Load factor $\alpha = \frac{n}{m}$ ($n$ elements, $m$ slots).
Under the Simple Uniform Hashing Assumption (SUHA):
- **Separate Chaining**: Average chain length $= \alpha$.
  $$\text{Search Time} = \Theta(1 + \alpha)$$
- **Open Addressing (Uniform Hashing)**:
  $$E[\text{Probes}_{\text{unsuccessful}}] \le \frac{1}{1 - \alpha}$$
  $$E[\text{Probes}_{\text{successful}}] \le \frac{1}{\alpha} \ln\left(\frac{1}{1 - \alpha}\right)$$

### 4.2 Probing Function Formulations
- **Linear Probing**: $h(k, i) = (h'(k) + i) \pmod m$
- **Quadratic Probing**: $h(k, i) = (h'(k) + c_1 i + c_2 i^2) \pmod m$
- **Double Hashing**: $h(k, i) = (h_1(k) + i \cdot h_2(k)) \pmod m$ (where $\gcd(h_2(k), m) = 1$)
- **Robin Hood Hashing**: Enforces $\text{PSL}_{\text{incoming}} > \text{PSL}_{\text{incumbent}} \implies \text{Swap and sift forward}$.
- **Cuckoo Hashing**: 2 tables ($T_1[h_1(k)]$, $T_2[h_2(k)]$), strictly **2 memory lookups worst-case**.

---

## 5. DSU, Fenwick & Segment Trees Cheat Sheet

### 5.1 Disjoint Set Union (DSU)
- **Path Compression**:
  `int find(int x) { return parent[x] == x ? x : (parent[x] = find(parent[x])); }`
- **Union by Rank**:
  If $\text{rank}[r_1] < \text{rank}[r_2] \implies \text{parent}[r_1] = r_2$.
- **Amortized Complexity**: $\mathbf{\mathcal{O}(\alpha(n))}$ where $\alpha(n) \le 4$ for all $n \le 10^{80}$.

### 5.2 Fenwick Tree (Binary Indexed Tree)
- **Least Significant Bit (LSB)**: $\text{LSB}(i) = i \ \& \ (-i)$
- **Point Add (+delta)**:
  `for (; i <= n; i += (i & -i)) tree[i] += delta;`
- **Prefix Sum Query**:
  `for (; i > 0; i -= (i & -i)) sum += tree[i];`
- **Range Sum**: $\text{sum}(L, R) = \text{prefix}(R) - \text{prefix}(L - 1)$
- **Space Overhead**: Exactly $n$ integers (1-indexed).

### 5.3 Segment Tree
- **Array Size Bound**: Exactly $4n$ nodes allocated for safe power-of-two padding.
- **Child Indices**: $\text{Left} = 2 \cdot \text{node}$, $\text{Right} = 2 \cdot \text{node} + 1$.
- **Lazy Propagation Rule**: Always push down pending tags before recursing into children during both updates and queries!

---

## 6. Critical Edge Cases & Common Exam Traps

1. **QuickSort on Equal Keys**: Lomuto partitioning does not split identical keys evenly, degrading to $\mathcal{O}(n^2)$. Always use Hoare partitioning or Dutch National Flag 3-Way partitioning.
2. **Signed Integers in Radix Sort**: Negative numbers have MSB set to `1`, placing them after positive numbers. Always invert the sign bit before sorting (`x ^ 0x80000000`) and invert it back after.
3. **Fenwick Tree Zero Index Trap**: Calling `bit_add(0)` triggers $0 \ \& \ (-0) = 0$, leading to an immediate infinite loop. Fenwick trees must strictly be 1-indexed.
4. **Tombstones in Open Addressing**: Never set a deleted slot to `NULL` / `None`, as it truncates probe chains for colliding keys inserted later. Use sentinel `TOMBSTONE`.
5. **Tail-Call Elimination in QuickSort**: To prevent $\mathcal{O}(n)$ call stack overflow, always recurse into the smaller partition ($< n/2$) and handle the larger partition via a loop.
