# Level 3 Revision & Formula Sheet: Core Data Structures & Asymptotic Complexity

---

## 1. Quick Reference: Chapters 01 to 05

| Chapter | Core Focus | Key Axioms & Formulas | Primary Failure Mode |
|:---|:---|:---|:---|
| **CH01: Asymptotic Analysis** | Growth rates, Master Theorem | $T(n) = a T(n/b) + f(n)$; $\log_b a$ critical exp | Confusing worst-case with Big-$\mathcal{O}$; ignoring constants |
| **CH02: Arrays & Linked Lists** | Contiguous vs Node storage | $\text{Address}(A[i]) = \text{Base} + i \cdot S$ | Pointer lost before free; cache thrashing |
| **CH03: Stacks, Queues & Deques** | LIFO, FIFO, Ring Buffers | $(x) \pmod{2^k} \equiv x \ \& \ (2^k - 1)$ | Stack underflow; modulo division bottleneck |
| **CH04: Binary Search Trees** | Binary search property, traversals | $\text{keys}(L) < \text{key}(N) < \text{keys}(R)$ | Degenerate skewed line ($h = n$) on sorted inputs |
| **CH05: AVL & Red-Black Trees** | Self-balancing tree rotations | $\text{BF} \in \{-1, 0, +1\}$; $h_{\text{AVL}} \le 1.44 \log n$ | Incomplete cascading deletion rebalancing |

---

## 2. Asymptotic Bounds & Master Theorem Summary

### 2.1 The Master Theorem Decision Matrix
For recurrence $T(n) = a T(n/b) + f(n)$:
Let $c_{\text{crit}} = \log_b a$.

1. **Case 1 (Leaves Dominate)**: If $f(n) = \mathcal{O}(n^{c_{\text{crit}} - \epsilon})$ for $\epsilon > 0 \implies \mathbf{T(n) = \Theta(n^{\log_b a})}$.
2. **Case 2 (Balanced Work)**: If $f(n) = \Theta(n^{c_{\text{crit}}} \log^k n)$ for $k \ge 0 \implies \mathbf{T(n) = \Theta(n^{\log_b a} \log^{k+1} n)}$.
3. **Case 3 (Root Dominates)**: If $f(n) = \Omega(n^{c_{\text{crit}} + \epsilon})$ for $\epsilon > 0$ and $a f(n/b) \le c f(n)$ for $c < 1 \implies \mathbf{T(n) = \Theta(f(n))}$.

---

## 3. Data Structure Operation Complexity Matrix

| Structure | Access | Search | Insert (Head) | Insert (Tail) | Delete (Known Node) | Auxiliary Space |
|:---|:---|:---|:---|:---|:---|:---|
| **Dynamic Array** | $\mathcal{O}(1)$ | $\mathcal{O}(n)$ | $\mathcal{O}(n)$ | $\mathcal{O}(1)$ amortized | $\mathcal{O}(n)$ | $\mathcal{O}(n)$ |
| **Singly Linked List**| $\mathcal{O}(n)$ | $\mathcal{O}(n)$ | $\mathcal{O}(1)$ | $\mathcal{O}(1)^*$ | $\mathcal{O}(1)^*$ | $\mathcal{O}(n)$ |
| **Doubly Linked List**| $\mathcal{O}(n)$ | $\mathcal{O}(n)$ | $\mathcal{O}(1)$ | $\mathcal{O}(1)^*$ | $\mathcal{O}(1)$ | $\mathcal{O}(n)$ |
| **Array Stack** | $\mathcal{O}(1)$ | $\mathcal{O}(n)$ | $\mathcal{O}(1)$ (top) | N/A | $\mathcal{O}(1)$ (pop) | $\mathcal{O}(n)$ |
| **Circular Queue** | $\mathcal{O}(1)$ | $\mathcal{O}(n)$ | N/A | $\mathcal{O}(1)$ (rear) | $\mathcal{O}(1)$ (front) | $\mathcal{O}(C)$ |
| **Naive BST** | $\mathcal{O}(h)$ | $\mathcal{O}(h)$ | $\mathcal{O}(h)$ | $\mathcal{O}(h)$ | $\mathcal{O}(h)$ | $\mathcal{O}(n)$ |
| **AVL Tree** | $\mathcal{O}(\log n)$ | $\mathbf{\mathcal{O}(\log n)}$ | $\mathcal{O}(\log n)$ | $\mathcal{O}(\log n)$ | $\mathcal{O}(\log n)$ | $\mathcal{O}(n)$ |
| **Red-Black Tree** | $\mathcal{O}(\log n)$ | $\mathbf{\mathcal{O}(\log n)}$ | $\mathcal{O}(\log n)$ | $\mathcal{O}(\log n)$ | $\mathcal{O}(\log n)$ | $\mathcal{O}(n)$ |
| **Skip List** | $\mathcal{O}(\log n)$ | $\mathcal{O}(\log n)$ | $\mathcal{O}(\log n)$ | $\mathcal{O}(\log n)$ | $\mathcal{O}(\log n)$ | $\mathcal{O}(n)$ |

*\*Note: Insertion/Deletion at tail/middle in linked lists is $\mathcal{O}(1)$ given an existing pointer to that location.*

---

## 4. The 4 AVL Rotations Cheat Sheet

```
Imbalance Type        Child Relative Pos          Fix / Rotation Sequence
-----------------------------------------------------------------------------------------
Left-Left (LL)        key < node->left->key       Single Right Rotation on node: RotateRight(Z)
Right-Right (RR)      key > node->right->key      Single Left Rotation on node:  RotateLeft(Z)
Left-Right (LR)       key > node->left->key       RotateLeft(Z->left), then RotateRight(Z)
Right-Left (RL)       key < node->right->key      RotateRight(Z->right), then RotateLeft(Z)
-----------------------------------------------------------------------------------------
```

---

## 5. The 5 Red-Black Invariants Checklist

1. Every node is colored either **RED** or **BLACK**.
2. The **Root** is strictly **BLACK**.
3. Every **Leaf** (NIL sentinel node) is **BLACK**.
4. If a node is **RED**, both of its children must be **BLACK** (No two consecutive RED nodes).
5. For each node, all simple paths from the node to descendant leaves contain the **same number of black nodes** (Black-Height).
- **Consequence**: Height $h \le 2 \log_2(n + 1)$.

---

## 6. Monotonic Stack & Queue Idioms

### Next Greater Element (Monotonic Decreasing Stack)
```python
def next_greater_element(nums):
    res = [-1] * len(nums)
    stack = [] # Stores indices
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            idx = stack.pop()
            res[idx] = x
        stack.append(i)
    return res
```

### Sliding Window Maximum (Monotonic Queue)
- Pop from front if index $< i - k + 1$ (out of window).
- Pop from tail while `nums[tail] <= incoming` (maintain strictly decreasing order).
- Current maximum is always at `front`.
- Runs in strict **$\mathcal{O}(n)$ linear time**.
