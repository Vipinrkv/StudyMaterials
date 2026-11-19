# University End-Semester Examination: Computer Science Foundations (Levels 1–3)

**Course Codes:** CS101 / CS201 / CS301 (Foundations of Computing, Systems & Data Structures)  
**Applicable Degrees:** BCS, BCA, B.Tech SE, BESE, MCS, MCA  
**Duration:** 3 Hours (180 Minutes)  
**Maximum Marks:** 100  
**Instructions:**
1. All questions in Section A are compulsory (20 Marks).
2. Answer any **four** questions from Section B (40 Marks).
3. Answer any **two** questions from Section C (40 Marks).
4. Diagrams, ASCII layout charts, and step-by-step mathematical working carry explicit marks.
5. Code snippets must adhere to standard C11 specifications.

---

## SECTION A: Objective & Conceptual Foundations (Compulsory — 10 × 2 Marks = 20 Marks)

### Q1.1
**Question:** Explain why two's complement representation is universally preferred over one's complement in modern ALU design.  
**Marking Scheme:** 1 mark for zero representation, 1 mark for hardware addition logic.  
**Model Solution:**  
In two's complement, there is exactly one unique representation for zero ($0000_2$), unlike one's complement which possesses both $+0$ ($0000_2$) and $-0$ ($1111_2$). Furthermore, two's complement addition does not require an end-around carry: standard binary adder circuits perform both signed addition and subtraction ($A - B = A + (\sim B + 1)$) seamlessly without conditional carry-propagation circuitry, drastically simplifying hardware logic paths.

### Q1.2
**Question:** Calculate the total memory footprint and byte padding of `struct Packet { uint8_t id; uint32_t len; uint16_t flag; };` on an LP64 x86_64 architecture.  
**Marking Scheme:** 1 mark for alignment calculation, 1 mark for total size & padding bytes.  
**Model Solution:**  
Alignment requirements: `uint8_t` (1-byte), `uint32_t` (4-byte), `uint16_t` (2-byte).  
- Offset 0: `id` (1 byte)  
- Offset 1–3: 3 bytes padding (to align `len` at 4-byte boundary)  
- Offset 4–7: `len` (4 bytes)  
- Offset 8–9: `flag` (2 bytes)  
- Offset 10–11: 2 bytes tail padding (to make total struct size a multiple of largest member alignment, 4 bytes).  
**Total size = 12 bytes** (5 bytes payload + 5 bytes padding).

### Q1.3
**Question:** Define the formal definition of Big-O asymptotic notation: $f(n) \in O(g(n))$.  
**Marking Scheme:** 1 mark for inequality, 1 mark for quantification ($\exists c > 0, n_0 > 0$).  
**Model Solution:**  
$f(n) \in O(g(n)) \iff \exists c > 0, n_0 > 0 \text{ such that } \forall n \ge n_0, \; 0 \le f(n) \le c \cdot g(n)$.

### Q1.4
**Question:** What is a cache line split, and why does an unaligned memory access degrade microarchitectural throughput?  
**Marking Scheme:** 1 mark for definition, 1 mark for pipeline impact.  
**Model Solution:**  
A cache line split occurs when a multi-byte memory operand spans across two separate 64-byte cache lines. An unaligned load/store crossing this boundary requires the L1D cache controller to issue two distinct memory transactions, execute split-lock or buffer reassembly, and occupy two L1 fill buffer entries, doubling latency and stalling speculative execution pipelines.

### Q1.5
**Question:** Differentiate between internal and external fragmentation in dynamic memory allocators.  
**Marking Scheme:** 1 mark for internal, 1 mark for external definition.  
**Model Solution:**  
- **Internal Fragmentation:** Allocated memory within a block that is unused by the application (e.g. requesting 25 bytes from an allocator that rounds up to 32-byte chunks; 7 bytes wasted inside the chunk).  
- **External Fragmentation:** Total free memory across the heap is sufficient to satisfy an allocation request, but no single contiguous free block is large enough due to interleaving active allocations.

### Q1.6
**Question:** In Floyd's Cycle-Finding Algorithm (Tortoise and Hare), prove why the two pointers must meet if a cycle exists.  
**Marking Scheme:** 1 mark for relative velocity analysis, 1 mark for modular congruency.  
**Model Solution:**  
Let the slow pointer advance at 1 step/iteration and the fast pointer at 2 steps/iteration. Once both enter the cycle of length $C$, the relative distance between them decreases by 1 step modulo $C$ each iteration ($2 - 1 \equiv 1 \pmod C$). Since the relative distance decreases strictly by 1 every tick, the gap must reach 0 within at most $C$ steps, guaranteeing they meet without infinite cycling.

### Q1.7
**Question:** Explain the purpose and operation of the Base Pointer (`%rbp`) and Stack Pointer (`%rsp`) during an x86_64 function call frame setup.  
**Marking Scheme:** 1 mark for push rbp/mov rsp, 1 mark for frame demarcation.  
**Model Solution:**  
Upon entering a function prologue:
```nasm
push %rbp          ; Saves caller's frame base pointer
mov  %rsp, %rbp    ; Establishes callee's frame anchor
sub  $N, %rsp      ; Allocates local stack frame space
```
`%rbp` provides a fixed, stable reference point for accessing local variables and parameters via constant negative/positive offsets, while `%rsp` dynamically tracks the top of the stack as registers are pushed or dynamic allocations occur.

### Q1.8
**Question:** State Master's Theorem for divide-and-conquer recurrences: $T(n) = aT(n/b) + f(n)$.  
**Marking Scheme:** 2 marks (0.5 mark for conditions, 1.5 marks for the three cases).  
**Model Solution:**  
For $a \ge 1, b > 1$:
1. If $f(n) = O(n^{\log_b a - \epsilon})$ for $\epsilon > 0$, then $T(n) = \Theta(n^{\log_b a})$.
2. If $f(n) = \Theta(n^{\log_b a} \log^k n)$ for $k \ge 0$, then $T(n) = \Theta(n^{\log_b a} \log^{k+1} n)$.
3. If $f(n) = \Omega(n^{\log_b a + \epsilon})$ for $\epsilon > 0$, and regularity condition $a f(n/b) \le c f(n)$ holds for $c < 1$, then $T(n) = \Theta(f(n))$.

### Q1.9
**Question:** Why does linear probing in open-addressed hash tables suffer from primary clustering?  
**Marking Scheme:** 1 mark for mechanism, 1 mark for probability compounding.  
**Model Solution:**  
Linear probing checks positions $(h(k) + i) \pmod M$. When collisions occur, contiguous occupied slots form runs. Any new key whose initial hash falls anywhere within or immediately preceding a run of length $L$ will inevitably be appended to that run. Thus, the probability of expanding an existing run is proportional to $(L + 1) / M$, causing long runs to grow exponentially faster than isolated slots.

### Q1.10
**Question:** Describe the exact role of the translation lookaside buffer (TLB) in virtual memory addressing.  
**Marking Scheme:** 1 mark for virtual-to-physical translation caching, 1 mark for page table walk avoidance.  
**Model Solution:**  
The TLB is an on-chip, highly associative hardware cache storing recently used Virtual Page Number (VPN) to Physical Frame Number (PFN) mappings. On a memory reference, a TLB hit translates the address in < 1 clock cycle. On a TLB miss, the hardware page table walker must traverse multi-level page tables (PML4, PDPT, PD, PT) in DRAM, taking tens of nanoseconds.

---

## SECTION B: Analytical & Algorithmic Foundations (Answer any FOUR — 4 × 10 Marks = 40 Marks)

### Q2. Memory Layout, Cache Locality & Matrix Traversal (10 Marks)
**Sub-questions:**
(a) Given a 2D array `int A[4096][4096]` stored in row-major order with 64-byte cache lines (`sizeof(int) = 4`):
1. Compute the cache miss rate for row-major traversal: `for(i) for(j) sum += A[i][j];` assuming a cold cache. (3 Marks)
2. Compute the cache miss rate for column-major traversal: `for(j) for(i) sum += A[i][j];`. (3 Marks)
(b) Write a cache-blocked (tiled) C function to multiply two $N \times N$ matrices ($C = A \times B$) to optimize L1 data cache usage. Explain how tile size $B_{tile}$ is determined based on L1 cache size $C_{L1}$. (4 Marks)

**Marking Scheme & Model Solution:**  
**(a) Traversal Miss Rates:**  
- Each cache line holds $\frac{64 \text{ bytes}}{4 \text{ bytes/int}} = 16$ consecutive integers.
1. **Row-Major (`A[i][j]`):** Elements are contiguous in memory. The first element `A[i][0]` causes a cold miss; the next 15 elements (`A[i][1..15]`) are hits within the loaded line.  
   $$\text{Miss Rate} = \frac{1}{16} = 6.25\%$$
2. **Column-Major (`A[i][j]` accessed by iterating `i` inner):** Successive accesses jump by row stride: $4096 \times 4 = 16,384 \text{ bytes} = 256 \text{ cache lines}$. Since $4096 \times 16\text{KB}$ exceeds the size of typical L1/L2 caches, every access evicts previously loaded lines.  
   $$\text{Miss Rate} = 100\%$$

**(b) Cache-Blocked Matrix Multiplication in C11:**
```c
#include <stddef.h>

void matmul_tiled(size_t n, size_t b_tile, const double* restrict A, 
                  const double* restrict B, double* restrict C) {
    for (size_t ii = 0; ii < n; ii += b_tile) {
        for (size_t jj = 0; jj < n; jj += b_tile) {
            for (size_t kk = 0; kk < n; kk += b_tile) {
                for (size_t i = ii; i < ii + b_tile && i < n; i++) {
                    for (size_t k = kk; k < kk + b_tile && k < n; k++) {
                        double rA = A[i * n + k];
                        for (size_t j = jj; j < jj + b_tile && j < n; j++) {
                            C[i * n + j] += rA * B[k * n + j];
                        }
                    }
                }
            }
        }
    }
}
```
**Tile Sizing Principle:** For a block matrix multiplication, three sub-blocks ($A_{tile}, B_{tile}, C_{tile}$) must concurrently reside in L1 data cache to eliminate capacity evictions:  
$$3 \times (B_{tile}^2 \times \text{sizeof(double)}) \le C_{L1}$$
For an L1D cache of 32 KB ($32,768$ bytes) with `sizeof(double) = 8`:
$$3 \times 8 \times B_{tile}^2 \le 32768 \implies 24 B_{tile}^2 \le 32768 \implies B_{tile}^2 \le 1365 \implies B_{tile} \approx 32$$
Choosing $B_{tile} = 32$ guarantees the entire working set fits within L1.

---

### Q3. Balanced Search Trees: AVL vs. Red-Black (10 Marks)
**Sub-questions:**
(a) Define the height-balance invariants of an AVL tree and prove by mathematical induction that the minimum number of nodes in an AVL tree of height $h$ satisfies $N(h) = N(h-1) + N(h-2) + 1$. Show that $h < 1.44 \log_2(n+2)$. (5 Marks)  
(b) Illustrate with before-and-after pointer diagrams the Left-Right double rotation (LR) required when inserting a key that violates balance factor $+2$ with left child balance factor $-1$. (5 Marks)

**Marking Scheme & Model Solution:**  
**(a) Invariant & Induction:**  
- **AVL Invariant:** For every node $u$, $|\text{height}(u.\text{left}) - \text{height}(u.\text{right})| \le 1$.  
- Let $N(h)$ be the minimum number of nodes in an AVL tree of height $h$.  
  - Base cases: $N(0) = 1$, $N(1) = 2$.  
  - Inductive step: To minimize nodes for height $h$, the root must have one subtree of height $h-1$ and the other of minimum permissible height $h-2$. Thus:  
    $$N(h) = 1 + N(h-1) + N(h-2)$$  
  - By Fibonacci identity, $N(h) = F_{h+3} - 1$.  
    Since $F_k \approx \frac{\phi^k}{\sqrt{5}}$ where $\phi = \frac{1 + \sqrt{5}}{2} \approx 1.618$:  
    $$n \ge \frac{\phi^{h+2}}{\sqrt{5}} - 1 \implies \phi^{h+2} \le \sqrt{5}(n+1)$$  
    Taking $\log_2$ on both sides:  
    $$(h+2) \log_2 \phi \le \log_2(\sqrt{5}(n+1)) \implies h \le \frac{\log_2(n+1)}{\log_2(1.618)} \approx 1.4404 \log_2 n$$  
    Hence, $h \in O(\log n)$.

**(b) Left-Right (LR) Double Rotation Diagram:**  
Trigger condition: Node $A$ has balance factor $+2$ (left-heavy), Child $B$ has balance factor $-1$ (right-heavy due to insertion in $C$).
```
Initial State (Imbalance at A):
         A (+2)
        / \
       B (-1)  T4
      / \
     T1   C (0)
         / \
        T2  T3

Step 1: Left Rotate at B:
         A (+2)
        / \
       C   T4
      / \
     B   T3
    / \
   T1  T2

Step 2: Right Rotate at A:
         C (0)
       /   \
      B     A
     / \   / \
    T1 T2 T3 T4
```
All binary search invariants are preserved: $T_1 < B < T_2 < C < T_3 < A < T_4$.

---

### Q4. Advanced Sorting Lower Bounds & Non-Comparison Algorithms (10 Marks)
**Sub-questions:**
(a) Prove mathematically using decision trees that any comparison-based sorting algorithm requires at least $\lceil \log_2(n!) \rceil \approx \Omega(n \log n)$ comparisons in the worst case. (4 Marks)  
(b) Design an in-place Radix Sort or 3-Way Radix Quicksort for strings. Analyze its time and auxiliary space complexity. (6 Marks)

**Marking Scheme & Model Solution:**  
**(a) Decision Tree Lower Bound Proof:**  
1. Any comparison-based sorting algorithm can be modeled as a binary decision tree where internal nodes represent comparisons $A[i] \le A[j]$ and leaves represent permutations.
2. For an input of $n$ distinct elements, there are $n!$ possible permutations. Every permutation must appear as at least one leaf node in the decision tree. Thus, number of leaves $L \ge n!$.
3. A binary tree of height $h$ can have at most $2^h$ leaves:  
   $$2^h \ge L \ge n! \implies h \ge \log_2(n!)$$
4. By Stirling's Approximation ($\ln(n!) = n \ln n - n + O(\ln n)$):  
   $$h \ge \log_2(n!) = \sum_{i=1}^n \log_2 i \ge \sum_{i=n/2}^n \log_2(n/2) = \frac{n}{2} (\log_2 n - 1) = \Omega(n \log n)$$  
   Since worst-case comparisons equal tree height $h$, no comparison sort can run in $o(n \log n)$.

**(b) 3-Way Radix Quicksort (Bentley-Sedgewick):**
```c
#include <stddef.h>

static inline int char_at(const char* s, size_t d) {
    return (int)((unsigned char)s[d]);
}

void quicksort_3way_string(const char** a, int lo, int hi, size_t d) {
    if (hi <= lo) return;
    int lt = lo, gt = hi;
    int v = char_at(a[lo], d);
    int i = lo + 1;

    while (i <= gt) {
        int t = char_at(a[i], d);
        if (t < v) {
            const char* tmp = a[lt]; a[lt] = a[i]; a[i] = tmp;
            lt++; i++;
        } else if (t > v) {
            const char* tmp = a[i]; a[i] = a[gt]; a[gt] = tmp;
            gt--;
        } else {
            i++;
        }
    }

    quicksort_3way_string(a, lo, lt - 1, d);
    if (v > 0) {
        quicksort_3way_string(a, lt, gt, d + 1);
    }
    quicksort_3way_string(a, gt + 1, hi, d);
}
```
**Complexity Analysis:**
- **Time Complexity:** Average case is $O(N \log N + D)$ where $D$ is total examined characters. Worst case is $O(W \cdot N^2)$ if pivots are poorly chosen.
- **Auxiliary Space:** $O(W + \log N)$ stack frame depth for recursion; operates directly on pointer array in-place without dynamic bucket allocations.

---

### Q5. Graph Algorithms: Shortest Paths & Negative Cycles (10 Marks)
**Sub-questions:**
(a) Differentiate between Dijkstra's and Bellman-Ford algorithms regarding edge weights and algorithmic paradigm. (3 Marks)  
(b) State and prove the triangle inequality relaxation condition: $d[v] \le d[u] + w(u, v)$. (3 Marks)  
(c) Write pseudo-code for the Bellman-Ford algorithm with negative cycle detection. Prove why $V-1$ iterations are sufficient to find all shortest paths in a DAG/graph without negative cycles. (4 Marks)

**Marking Scheme & Model Solution:**  
**(a) Comparison:**  
- **Dijkstra:** Greedy paradigm; requires non-negative edge weights ($w(u, v) \ge 0$); time complexity $O((V + E) \log V)$ with heap.  
- **Bellman-Ford:** Dynamic programming paradigm; handles arbitrary weights; detects negative-weight cycles; time complexity $O(V \cdot E)$.

**(b) Triangle Inequality Relaxation:**  
Let $\delta(s, v)$ be the true shortest path weight from source $s$ to $v$. For any edge $(u, v) \in E$, the shortest path from $s$ to $v$ can be no longer than the shortest path from $s$ to $u$ followed by edge $(u, v)$:  
$$\delta(s, v) \le \delta(s, u) + w(u, v)$$  
In relaxation, checking if $d[v] > d[u] + w(u, v)$ and updating monotonically drives upper bound $d[v]$ down towards $\delta(s, v)$ without ever underestimating the true shortest distance.

**(c) Bellman-Ford with Negative Cycle Detection:**
```text
Algorithm BellmanFord(G, w, s):
  For each vertex v in V:
      d[v] = INFINITY, pred[v] = NIL
  d[s] = 0

  For i = 1 to |V| - 1:
      For each edge (u, v) in E:
          If d[u] != INFINITY and d[u] + w(u, v) < d[v]:
              d[v] = d[u] + w(u, v)
              pred[v] = u

  For each edge (u, v) in E:
      If d[u] != INFINITY and d[u] + w(u, v) < d[v]:
          Return "Error: Negative Weight Cycle Detected"

  Return d, pred
```
**Sufficiency of $V-1$ iterations:** Any simple path in a graph with $|V|$ vertices contains at most $|V|-1$ edges. At iteration $k$, Bellman-Ford guarantees finding the shortest path among all paths containing $\le k$ edges. If there are no negative cycles, all shortest paths are simple. Hence, $|V|-1$ relaxations guarantee that all shortest path distances are stabilized. A further reduction in iteration $|V|$ proves the existence of a negative cycle.

---

## SECTION C: Comprehensive System Design & Derivation (Answer any TWO — 2 × 20 Marks = 40 Marks)

### Q6. High-Performance Memory Allocator Design (20 Marks)
**Problem Statement:** Design a segregated free-list dynamic memory allocator (similar to jemalloc / dlmalloc) operating on an arena of contiguous memory.
1. Detail the header and footer tag structure used for constant time $O(1)$ boundary-tag coalescing. Provide an exact C `struct` definition and memory bit layout. (6 Marks)
2. Detail the exact pointer manipulation algorithm for coalescing a newly freed block with its predecessor and successor. (6 Marks)
3. Explain segregated fit binning (size classes) and how it bounds search time to $O(1)$ while suppressing fragmentation. (4 Marks)
4. Discuss the concurrency bottleneck when multiple threads allocate from a single arena, and explain how thread-local caching (tcache) resolves it. (4 Marks)

**Marking Scheme & Model Solution:**  
**(1) Boundary-Tag Block Layout:**  
To achieve $O(1)$ coalescing, every block contains a Header and a Footer. The lowest 3 bits of the size field are used as status flags because allocations are aligned to 8 or 16 bytes:
- Bit 0: `ALLOCATED` ($1 = \text{allocated}, 0 = \text{free}$)
- Bit 1: `PREV_ALLOCATED` ($1 = \text{prev allocated}, 0 = \text{prev free}$)
```c
#include <stdint.h>
#include <stdbool.h>

typedef struct BlockHeader {
    uint32_t size_and_flags;
} BlockHeader;

typedef struct FreeBlock {
    BlockHeader header;
    struct FreeBlock* next;
    struct FreeBlock* prev;
} FreeBlock;
```
**Memory Bit Layout:**
```
+--------------------------------------------------------+
| Size of Block (32-bit uint)           | Reserved | A/F | Header (4 bytes)
+--------------------------------------------------------+
| Pointer to Next Free Block in Bin (8 bytes)            |
+--------------------------------------------------------+
| Pointer to Prev Free Block in Bin (8 bytes)            |
+--------------------------------------------------------+
| Unused Free Space Payload                              |
| ...                                                    |
+--------------------------------------------------------+
| Size of Block (Duplicate Footer)                       | Footer (4 bytes)
+--------------------------------------------------------+
```

**(2) Four-Case Constant Time $O(1)$ Coalescing Algorithm:**
```c
static inline void* coalesce(FreeBlock* b) {
    size_t size = get_size(b);
    bool prev_alloc = get_prev_alloc(b);
    BlockHeader* next_hdr = (BlockHeader*)((char*)b + size);
    bool next_alloc = get_alloc(next_hdr);

    if (prev_alloc && next_alloc) {
        insert_into_freelist(b);
        return b;
    } else if (prev_alloc && !next_alloc) {
        remove_from_freelist((FreeBlock*)next_hdr);
        size += get_size(next_hdr);
        set_size_and_alloc(b, size, false);
        set_footer(b, size);
        insert_into_freelist(b);
        return b;
    } else if (!prev_alloc && next_alloc) {
        BlockHeader* prev_ftr = (BlockHeader*)((char*)b - sizeof(BlockHeader));
        size_t prev_size = prev_ftr->size_and_flags & ~0x7;
        FreeBlock* prev_b = (FreeBlock*)((char*)b - prev_size);
        remove_from_freelist(prev_b);
        prev_size += size;
        set_size_and_alloc(prev_b, prev_size, false);
        set_footer(prev_b, prev_size);
        insert_into_freelist(prev_b);
        return prev_b;
    } else {
        remove_from_freelist((FreeBlock*)next_hdr);
        BlockHeader* prev_ftr = (BlockHeader*)((char*)b - sizeof(BlockHeader));
        size_t prev_size = prev_ftr->size_and_flags & ~0x7;
        FreeBlock* prev_b = (FreeBlock*)((char*)b - prev_size);
        remove_from_freelist(prev_b);
        size += prev_size + get_size(next_hdr);
        set_size_and_alloc(prev_b, size, false);
        set_footer(prev_b, size);
        insert_into_freelist(prev_b);
        return prev_b;
    }
}
```

**(3) Segregated Fit Binning:**  
Free blocks are partitioned into disjoint doubly linked lists (bins) categorized by power-of-two size classes (16B, 32B, 64B... up to 4KB).  
- **Search Optimization:** An allocation of size $S$ is rounded up to the nearest bin index via `31 - __builtin_clz(S)`. The first block in that bin is immediately extracted in $O(1)$ without scanning unrelated blocks.  
- **Fragmentation Suppression:** Large blocks are never split for tiny allocations, insulating large memory spans from fragmentation caused by short-lived small buffers.

**(4) Concurrency Bottleneck & Thread-Local Caching (tcache):**  
- **Bottleneck:** A global allocator lock causes severe contention under high thread counts; threads stall on lock acquisition during frequent `malloc`/`free` calls.  
- **Solution:** Thread-local caches (`tcache`) maintain small singly linked pools of hot size-class blocks per OS thread. Small allocations/frees are serviced directly from TLS with **zero atomic instructions or lock contention**. When a tcache bucket drains or overflows, it batches bulk refills from the shared arena using a single locked transaction.

---

### Q7. Compiler Intermediate Representation & Register Allocation (20 Marks)
**Problem Statement:** Consider the following high-level language basic block:
```c
a = x + y;
b = a * z;
c = x + y;
d = b + c;
return d;
```
1. Translate this basic block into Static Single Assignment (SSA) form. Explain the dominance frontier and why $\phi$-nodes are placed. (5 Marks)
2. Perform Common Subexpression Elimination (CSE) and Value Numbering on the SSA graph. (5 Marks)
3. Construct the register interference graph (RIG) for the variables in the optimized code. (5 Marks)
4. Apply Chaitin's graph coloring heuristic to allocate registers assuming a machine with only $K = 2$ general-purpose registers ($R_0, R_1$). Determine whether a register spill to stack memory is required, with full mathematical justification. (5 Marks)

**Marking Scheme & Model Solution:**  
**(1) Static Single Assignment (SSA) Representation:**  
```text
a_1 = x_0 + y_0
b_1 = a_1 * z_0
c_1 = x_0 + y_0
d_1 = b_1 + c_1
return d_1
```
- **Dominance Frontier & $\phi$-Nodes:** A node $Y$ is in the dominance frontier of $X$ ($DF(X)$) if $X$ dominates a predecessor of $Y$, but does not strictly dominate $Y$. At join points in the control flow graph where multiple paths converge, variables assigned across different paths require a $\phi$-node: $v_3 = \phi(v_1, v_2)$ to resolve the valid active definition dynamically. Within this single basic block, control flow is linear, so no $\phi$-nodes are needed.

**(2) Value Numbering & CSE:**  
We construct an expression hash map mapping `(operator, operand_val1, operand_val2) -> value_number`:
- Let `VN(x_0) = 1`, `VN(y_0) = 2`, `VN(z_0) = 3`.
- `a_1 = x_0 + y_0`: Lookup `(+, 1, 2)`. Not found. Assign `VN(a_1) = 4`. Insert `(+, 1, 2) -> 4`.
- `b_1 = a_1 * z_0`: Lookup `(*, 4, 3)`. Not found. Assign `VN(b_1) = 5`. Insert `(*, 4, 3) -> 5`.
- `c_1 = x_0 + y_0`: Lookup `(+, 1, 2)`. Found! Mapped to `VN = 4` (`a_1`).  
  **Redundant computation eliminated:** Replace all occurrences of `c_1` with `a_1`.
- `d_1 = b_1 + a_1`: Lookup `(+, 5, 4)`. Assign `VN(d_1) = 6`.

**Optimized SSA Code:**
```text
a_1 = x_0 + y_0
b_1 = a_1 * z_0
d_1 = b_1 + a_1
return d_1
```

**(3) Liveness Analysis & Register Interference Graph (RIG):**  
Assuming inputs $x_0, y_0, z_0$ are dead after their last use:
- Live ranges:
  - $a_1$: Defined at line 1, used at line 2 and line 3. Live across: `[line 1 -> line 3]`.
  - $b_1$: Defined at line 2, used at line 3. Live across: `[line 2 -> line 3]`.
  - $d_1$: Defined at line 3, used at line 4 (`return`). Live across: `[line 3 -> line 4]`.
- **Interferences:**
  - At line 3: $a_1$ and $b_1$ are simultaneously live ($b_1$ is consumed and $a_1$ is consumed).
  - Hence, edge exists between **$a_1$ and $b_1$**.
  - $d_1$ is defined after $a_1$ and $b_1$ are consumed; its live range does not overlap with $a_1$ or $b_1$.
- **Nodes in RIG:** $V = \{a_1, b_1, d_1\}$.
- **Edges in RIG:** $E = \{(a_1, b_1)\}$.

**(4) Chaitin's Graph Coloring with $K = 2$ Registers:**  
- **Degree of nodes:** $\text{deg}(a_1) = 1$, $\text{deg}(b_1) = 1$, $\text{deg}(d_1) = 0$.
- **Simplify Phase ($K = 2$):**
  1. Remove $d_1$ ($\text{deg} = 0 < 2$). Stack: `[d_1]`.
  2. Remove $b_1$ ($\text{deg} = 1 < 2$). Stack: `[d_1, b_1]`.
  3. Remove $a_1$ ($\text{deg} = 0 < 2$). Stack: `[d_1, b_1, a_1]`.
- **Select / Color Phase (Colors $\{R_0, R_1\}$):**
  1. Pop $a_1$: Assign **$R_0$**.
  2. Pop $b_1$: Neighbor $a_1$ is $R_0$. Assign **$R_1$**.
  3. Pop $d_1$: No interfering neighbors. Assign **$R_0$**.
- **Spill Analysis:** **No register spill is required!** All variables are successfully colored using only 2 registers ($R_0, R_1$) because $\max(\text{degree}) = 1 < K$.
