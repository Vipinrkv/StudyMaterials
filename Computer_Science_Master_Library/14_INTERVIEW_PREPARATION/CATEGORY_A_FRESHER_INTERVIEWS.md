# TECHNICAL INTERVIEW PREPARATION: CATEGORY A (FRESHER & GRADUATE ENGINEER)

**Target Roles:** Graduate Software Engineer, Associate SDE, Junior Systems Developer  
**Associated Library Levels:** Level 1 (Absolute Beginner), Level 2 (Programming Foundation), Level 3 (Intermediate CS & DSA)  
**Teaching Principle:** "Teach Simply, Explain Deeply" — Zero shortcuts, memory-aware execution, and concrete code traces.

---

## 1. Interview Overview & Candidate Expectations
Interviews for graduate and junior roles evaluate solid fundamental mental models rather than obscure architectural trivia. Interviewers look for:
1. **Physical & Logical Computing Foundations:** How numbers, memory, and logic gates interact at the silicon level.
2. **Pointers, Memory Layout & Lifecycles:** Understanding stack vs. heap, struct alignment, and buffer boundaries in C/C++.
3. **Core Data Structures & Asymptotic Analysis:** Implementing lists, trees, heaps, and hash tables from scratch while reasoning about Big-O time and space.
4. **Clean Code & Defensive Programming:** Handling null pointers, off-by-one errors, and edge cases.

---

## 2. Low-Level Computing & Number Systems

### Q1: Two's Complement Representation & Integer Overflow
**Question:** Explain how signed negative integers are represented in two's complement. What happens physically when an 8-bit signed integer with value $127$ is incremented by $1$?

**Deep Explanation:**
In an $n$-bit two's complement system, the most significant bit (MSB) carries negative weight: $-2^{n-1}$. For 8 bits, the range is $[-128, 127]$.
Value $127$ in binary is `0111 1111`.
When we add $1$:
```
   0111 1111  (127)
+  0000 0001  (  1)
------------
   1000 0000  (-128 in two's complement: -2^7 = -128)
```
The CPU ALU sets the **Overflow Flag ($V$)** because adding two positive numbers yielded a negative result. In C/C++, signed integer overflow is **Undefined Behavior (UB)**, allowing optimizing compilers to assume it never occurs and prune bounds checks. In unsigned arithmetic, it wraps deterministically modulo $2^n$.

---

### Q2: Cache Locality & Row-Major Traversal
**Question:** Why does iterating through a 2D array row-by-row execute significantly faster than column-by-column in C or Python (NumPy)?

**Deep Explanation:**
Modern CPUs do not fetch single bytes from main RAM; they fetch **Cache Lines** (typically $64\text{ bytes}$).
In C and C++, 2D arrays are stored in **Row-Major Order** in contiguous memory: `A[0][0], A[0][1], A[0][2], ...`.
- **Row-Major Traversal (`A[i][j]` with inner loop `j`):** Accesses contiguous addresses. The first element loads 64 bytes into L1 cache ($16$ floats of 4 bytes). The next 15 accesses are immediate L1 cache hits ($\approx 1\text{ ns}$).
- **Column-Major Traversal (`A[i][j]` with inner loop `i`):** Each step jumps by $M \times \text{sizeof(element)}$ bytes. If $M > 16$, every single access misses the cache line, forcing memory stalls from RAM ($\approx 60\text{ to } 100\text{ ns}$).
- **Performance Impact:** Row-major access is routinely $5\times$ to $20\times$ faster due to spatial locality and CPU hardware prefetchers.

---

## 3. Pointers, Memory Management & C Foundations

### Q3: Struct Alignment, Padding, and Packing
**Question:** What is the size of the following C struct on a 64-bit architecture, and why?
```c
struct SensorData {
    char flag;      // 1 byte
    double value;   // 8 bytes
    int id;         // 4 bytes
};
```
How can we reorder the members to minimize memory usage?

**Deep Explanation:**
CPUs access memory efficiently when $k$-byte data types are aligned at memory addresses that are multiples of $k$ (natural alignment):
1. `char flag`: Placed at offset $0$. Takes 1 byte.
2. `double value`: Requires 8-byte alignment. Offsets 1 to 7 cannot be used. The compiler inserts **7 bytes of padding**. `value` resides at offsets $8$ to $15$.
3. `int id`: Requires 4-byte alignment. Placed at offsets $16$ to $19$.
4. **Tail Padding:** The overall struct size must be a multiple of the largest member's alignment ($8\text{ bytes}$). Offsets $20$ to $23$ are padded with 4 bytes.
- **Total Initial Size:** $1 + 7\text{ (pad)} + 8 + 4 + 4\text{ (pad)} = \mathbf{24\text{ bytes}}$.

**Optimized Member Order:**
```c
struct SensorDataOptimized {
    double value;   // 8 bytes (offset 0-7)
    int id;         // 4 bytes (offset 8-11)
    char flag;      // 1 byte  (offset 12)
    // 3 bytes tail padding (offset 13-15)
}; // Total: 16 bytes (33% memory savings!)
```

---

### Q4: Stack vs. Heap Allocation & Dangling Pointers
**Question:** What is fundamentally flawed with the following code?
```c
int* get_counter() {
    int count = 42;
    return &count;
}
```
How do you fix it, and what are the trade-offs?

**Deep Explanation:**
The variable `count` is allocated on the **Stack Frame** of `get_counter()`. When the function returns, its stack activation record is deallocated (the stack pointer `RSP` retreats). The returned pointer points to a dead stack address: a **Dangling Pointer**. Subsequent function calls will overwrite that memory, corrupting data.

**Fix 1: Dynamic Heap Allocation:**
```c
int* get_counter() {
    int* ptr = (int*)malloc(sizeof(int));
    if (!ptr) return NULL; // Defensive allocation check
    *ptr = 42;
    return ptr; // Caller MUST free(ptr)
}
```
*Trade-off:* Heap allocation requires `malloc` overhead and risks memory leaks if the caller forgets to `free`.

**Fix 2: Caller-Allocated Buffer (Preferred Systems Idiom):**
```c
void get_counter(int* out_count) {
    if (out_count) *out_count = 42;
}
```
*Trade-off:* Zero dynamic allocation overhead; ownership remains cleanly with the caller.

---

## 4. Fundamental Algorithms & Data Structures

### Q5: Floyd's Cycle Detection Algorithm
**Question:** Given a singly linked list, prove how to detect a loop in $O(N)$ time and $O(1)$ auxiliary space. How do you find the exact entry point of the loop?

**Deep Explanation:**
Use two pointers: `slow` (advancing 1 step) and `fast` (advancing 2 steps).
1. If there is no cycle, `fast` reaches `NULL` in $O(N)$ time.
2. If there is a cycle of length $C$, once both pointers enter the loop, the relative distance between them decreases by 1 in each step. They are guaranteed to collide within $C$ steps.

**Finding the Loop Entrance:**
Let $L$ be the distance from head to loop entrance.
Let $X$ be the distance from entrance to collision point.
At collision, `slow` traveled $L + X$, and `fast` traveled $L + X + kC = 2(L + X)$.
Therefore, $L + X = kC \implies L = kC - X = (k-1)C + (C - X)$.
Distance from head to entrance ($L$) equals the distance from collision point to entrance ($C - X$).
- **Algorithm:** Move one pointer to the list head, keep the other at the collision point, and advance both 1 step at a time. The node where they meet is the **exact loop entrance**.

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def find_cycle_entrance(head: ListNode) -> ListNode:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            # Collision detected: find entrance
            ptr1 = head
            ptr2 = slow
            while ptr1 != ptr2:
                ptr1 = ptr1.next
                ptr2 = ptr2.next
            return ptr1  # Entrance node
    return None  # No cycle
```

---

### Q6: Open Addressing vs. Separate Chaining Hash Tables
**Question:** Compare Separate Chaining and Open Addressing with Linear Probing for hash collision resolution. What happens to linear probing when the load factor $\alpha > 0.7$?

**Deep Explanation:**
- **Separate Chaining:** Each bucket points to a linked list or red-black tree. Memory is non-contiguous, creating pointer indirection and L1 cache misses. Degrades gracefully as $\alpha > 1.0$.
- **Open Addressing (Linear Probing):** All keys reside directly in a contiguous flat array. When collision occurs at index $h(k)$, probe $(h(k) + i) \pmod M$.
  - *Advantage:* Outstanding cache locality.
  - *Disadvantage (Primary Clustering):* Long contiguous runs of occupied slots form. As load factor $\alpha$ approaches $0.70$, probe lengths diverge towards infinity ($O(N)$ lookup).
  - *Tombstones:* Deletions require special `TOMBSTONE` markers; otherwise, subsequent linear probes terminate prematurely upon encountering an empty slot.

---

## 5. Coding Exercise: Monotonic Stack (Next Greater Element)
**Question:** Given an array of integers, return an array where each position contains the next strictly greater element to its right, or $-1$ if none exists. Must run in $O(N)$ time.

**Solution:**
```python
from typing import List

def next_greater_elements(nums: List[int]) -> List[int]:
    n = len(nums)
    res = [-1] * n
    stack = []  # Stores indices of elements in strictly decreasing order

    for i in range(n):
        while stack and nums[i] > nums[stack[-1]]:
            prev_idx = stack.pop()
            res[prev_idx] = nums[i]
        stack.append(i)

    return res

# Verification
assert next_greater_elements([4, 5, 2, 25]) == [5, 25, 25, -1]
assert next_greater_elements([13, 7, 6, 12]) == [-1, 12, 12, -1]
```
- **Complexity:** Each index is pushed and popped at most once $\implies O(N)$ time, $O(N)$ auxiliary stack space.
