# Chapter 03: Stacks, Queues, and Deques

---

## 1. Executive Summary & Core Concept

Linear data structures like general arrays and linked lists permit insertions, deletions, and accesses at arbitrary indices. However, many of the most fundamental operations in computer systems—such as function call dispatching, undo/redo buffers, task scheduling, and network packet routing—require disciplined, restricted access patterns.

This chapter investigates the trio of restricted linear abstract data types (ADTs):
1. **Stacks (LIFO: Last-In, First-Out)**: Access is strictly confined to a single end called the **Top**. Elements are added via `push()` and removed via `pop()`. Stacks model execution environments, recursive backtracking, syntax parsing, and expression evaluation.
2. **Queues (FIFO: First-In, First-Out)**: Elements enter at the **Rear** (enqueue) and exit from the **Front** (dequeue), preserving temporal arrival ordering. Queues underpin asynchronous messaging, print spooling, and operating system scheduling.
3. **Double-Ended Queues (Deques)**: Generalized sequences permitting insertions and deletions at both the front and rear in $\mathcal{O}(1)$ time.

Beyond standard implementations, this chapter delves into high-performance systems engineering: **Circular Ring Buffers**, lockless Single-Producer Single-Consumer (SPSC) queues in operating system kernels, Dijkstra's Shunting-Yard expression parser, and **Monotonic Stacks/Queues** that solve non-trivial range queries in linear $\mathcal{O}(n)$ time.

---

## 2. Prerequisites & Cognitive Map

```mermaid
graph TD
    A[Level 2 CH04: Functions & Call Stack Activation Records] --> B[Level 2 CH07: Dynamic Heap Memory]
    B --> C[Level 3 CH01: Asymptotic Complexity]
    C --> D[Level 3 CH02: Arrays & Linked Lists]
    D --> E[Level 3 CH03: Stacks, Queues & Deques]
    E --> F[Level 3 CH04: Trees & Breadth-First / Depth-First Traversal]
    E --> G[Level 4: Lockless Concurrency & OS Ring Buffers]
```

### Required Knowledge Checklist
- Dynamic array memory allocation and geometric capacity doubling from Chapter 02.
- Singly and Doubly Linked list pointer manipulation.
- Modulo arithmetic ($a \pmod b$) and circular index calculations.

---

## 3. The "Explain Like I'm Five" (ELI5) Analogy

### The Pringles Can, The Cinema Ticket Line, and The Train Platform
- **A Stack is a Can of Pringles Potato Chips (LIFO)**:
  The factory puts chips into the can one by one through the top. The first chip placed into the can is sitting at the very bottom. When you open the can, the ONLY chip you can take is the one at the very top—the last chip that was put in! If you want the bottom chip, you MUST eat (pop) all the chips above it first.
- **A Queue is a Movie Ticket Line at a Theater (FIFO)**:
  People line up at the ticket window. The first person to arrive is the first person who gets served and walks into the theater. If a new person arrives, they must stand at the back (enqueue). Cutting the line or serving people out of order is forbidden!
- **A Circular Ring Buffer is a Rotating Sushi Carousel**:
  Instead of an infinitely long conveyor belt, the sushi bar has an oval rotating track with 20 plates. The chef puts new sushi plates on the conveyor at the `tail` pointer, and hungry customers pick up plates from the `front` pointer. As plates are taken, the empty spots rotate back around to the chef. The belt never runs out of road because it wraps around in a circle!

---

## 4. Formal Mathematical & Theoretical Foundations

### 4.1 Algebraic Specification of the Stack ADT
A stack $S$ holding elements of type $T$ is an algebraic structure defined by the signature:
- $\text{empty}: \to S$
- $\text{push}: S \times T \to S$
- $\text{pop}: S \to S \times T$
- $\text{peek}: S \to T$
- $\text{is\_empty}: S \to \text{Boolean}$

Subject to the following fundamental axioms for all $s \in S$ and $x \in T$:
$$\text{is\_empty}(\text{empty}()) = \text{True}$$
$$\text{is\_empty}(\text{push}(s, x)) = \text{False}$$
$$\text{peek}(\text{push}(s, x)) = x \quad (\text{LIFO Invariant})$$
$$\text{pop}(\text{push}(s, x)) = (s, x)$$

### 4.2 Circular Queue Index Arithmetic
Let a circular queue be backed by a fixed-size array of capacity $C$. Let `front` be the index of the first valid element, and let `rear` be the index where the next element will be inserted.
- **Enqueue Operation**:
  $$\text{rear}_{\text{new}} = (\text{rear} + 1) \pmod C$$
- **Dequeue Operation**:
  $$\text{front}_{\text{new}} = (\text{front} + 1) \pmod C$$

#### The Full vs. Empty Disambiguation Problem:
If `front == rear`, does it mean the queue is completely **empty** or completely **full**?
Two mathematical solutions exist:
1. **Count Variable**: Maintain an explicit integer variable `count` recording active elements. Queue is empty when $\text{count} = 0$, full when $\text{count} = C$.
2. **Sacrificial Slot (Capacity $C$, Max Elements $C-1$)**:
   $$\text{is\_empty} \iff \text{front} == \text{rear}$$
   $$\text{is\_full} \iff (\text{rear} + 1) \pmod C == \text{front}$$

---

## 5. Architectural & Hardware Context

```
Ring Buffer in Shared Memory / DMA Kernel Drivers
========================================================================
Array Index:     0       1       2       3       4       5       6       7
Slot Data:     [ P0 ][ P1 ][ P2 ][ P3 ][ P4 ][ ... ][ ... ][ ... ]
                 ^                               ^
                 |--- Front (Consumer reads)     |--- Rear (Producer writes)
```

### Power-of-Two Fast Modulo Masking in Silicon
In production network drivers (e.g. Linux `AF_PACKET`, DPDK) and audio pipelines, computing the modulo operator `% C` using the CPU integer division instruction (`idiv`) costs **10 to 40 CPU clock cycles**.

If the capacity $C$ is strictly constrained to be a **power of two** ($C = 2^k$, e.g. 64, 1024, 65536):
$$(x) \pmod{2^k} \equiv x \ \& \ (2^k - 1)$$
A bitwise AND (`&`) executes in a **single CPU cycle (0.3 ns)**. Modern high-frequency systems universally round ring buffer capacities to powers of two to eliminate division latency.

---

## 6. Core Syntax, Semantics & Idioms

### 6.1 Dynamic Array Stack in C
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int *data;
    size_t capacity;
    size_t top; // Index of next insertion (also represents count)
} Stack;

Stack* stack_create(size_t initial_cap) {
    Stack *s = (Stack *)malloc(sizeof(Stack));
    s->capacity = initial_cap > 0 ? initial_cap : 4;
    s->top = 0;
    s->data = (int *)malloc(s->capacity * sizeof(int));
    return s;
}

bool stack_push(Stack *s, int val) {
    if (s->top == s->capacity) {
        size_t new_cap = s->capacity * 2;
        int *new_data = (int *)realloc(s->data, new_cap * sizeof(int));
        if (!new_data) return false;
        s->data = new_data;
        s->capacity = new_cap;
    }
    s->data[s->top++] = val;
    return true;
}

bool stack_pop(Stack *s, int *out_val) {
    if (s->top == 0) return false; // Stack Underflow
    if (out_val) *out_val = s->data[--s->top];
    return true;
}

void stack_destroy(Stack *s) {
    if (s) {
        free(s->data);
        free(s);
    }
}
```

### 6.2 High-Performance Power-of-Two Circular Queue
```c
typedef struct {
    int *buffer;
    size_t mask;  // capacity - 1 (Capacity MUST be power of 2!)
    size_t head;  // Read index
    size_t tail;  // Write index
} RingBuffer;

RingBuffer* ring_create(size_t power_of_two_cap) {
    RingBuffer *rb = (RingBuffer *)malloc(sizeof(RingBuffer));
    rb->mask = power_of_two_cap - 1;
    rb->head = 0;
    rb->tail = 0;
    rb->buffer = (int *)malloc(power_of_two_cap * sizeof(int));
    return rb;
}

bool ring_enqueue(RingBuffer *rb, int val) {
    // Full condition: tail is one step behind head
    if (((rb->tail + 1) & rb->mask) == (rb->head & rb->mask)) {
        return false; // Buffer Full
    }
    rb->buffer[rb->tail & rb->mask] = val;
    rb->tail++;
    return true;
}

bool ring_dequeue(RingBuffer *rb, int *out_val) {
    if ((rb->head & rb->mask) == (rb->tail & rb->mask)) {
        return false; // Buffer Empty
    }
    if (out_val) *out_val = rb->buffer[rb->head & rb->mask];
    rb->head++;
    return true;
}
```

---

## 7. Algorithmic Applications & Deep Walkthroughs

### 7.1 Dijkstra's Shunting-Yard Algorithm (Infix to Postfix Conversion)
Computers evaluate arithmetic expressions like `3 + 4 * 2 / (1 - 5)` using **Reverse Polish Notation (Postfix)** because postfix requires zero parentheses and evaluates linearly using a single stack.

```
Token Input Stream: [ 3, +, 4, *, 2 ]
========================================================================
Step 1: Read '3' -> Output: [ 3 ]
Step 2: Read '+' -> Operator Stack: [ + ]
Step 3: Read '4' -> Output: [ 3, 4 ]
Step 4: Read '*' -> Precedence('*') > Precedence('+') -> Operator Stack: [ +, * ]
Step 5: Read '2' -> Output: [ 3, 4, 2 ]
End of Input: Pop all operators to Output -> Output: [ 3, 4, 2, *, + ]
```

### 7.2 Postfix Expression Evaluation Algorithm
```c
int evaluate_postfix(const char *expr) {
    int stack[64];
    int top = -1;

    for (int i = 0; expr[i] != '\0'; ++i) {
        char c = expr[i];
        if (c >= '0' && c <= '9') {
            stack[++top] = c - '0';
        } else if (c == '+' || c == '-' || c == '*' || c == '/') {
            int op2 = stack[top--];
            int op1 = stack[top--];
            int res = 0;
            switch(c) {
                case '+': res = op1 + op2; break;
                case '-': res = op1 - op2; break;
                case '*': res = op1 * op2; break;
                case '/': res = op1 / op2; break;
            }
            stack[++top] = res;
        }
    }
    return stack[top];
}
```

---

## 8. Visual Models & Deep Walkthroughs

### Monotonic Stack: Next Greater Element in $\mathcal{O}(n)$ Time

Given an array `arr = [2, 1, 2, 4, 3]`, find the next greater element for each index.
A naive nested loop takes $\mathcal{O}(n^2)$ time. A **Monotonic Decreasing Stack** stores indices whose values are strictly decreasing, resolving in strict $\mathcal{O}(n)$ time.

```mermaid
sequenceDiagram
    autonumber
    Note over Array,Stack: arr = [2, 1, 2, 4, 3]. Iterate right-to-left.
    Note over Stack: Processing 3: Stack empty -> Next Greater = -1. Push 3.
    Note over Stack: Processing 4: Pop 3 (since 3 <= 4). Stack empty -> Next Greater = -1. Push 4.
    Note over Stack: Processing 2: Top is 4 (4 > 2) -> Next Greater = 4. Push 2.
    Note over Stack: Processing 1: Top is 2 (2 > 1) -> Next Greater = 2. Push 1.
    Note over Stack: Processing 2: Pop 1 (1 <= 2). Top is 2 (2 <= 2, Pop 2). Top is 4 -> Next Greater = 4. Push 2.
    Note over Array: Final Result: [4, 2, 4, -1, -1]
```

Every element is pushed onto the stack exactly once and popped at most once $\implies \mathcal{O}(n)$ total amortized time!

---

## 9. Common Pitfalls, Anti-Patterns & Undefined Behavior

| Anti-Pattern / Bug | Code Example | Consequence / Fix |
|:---|:---|:---|
| **Stack Underflow** | `pop()` on empty stack | Dereferences invalid memory index `-1` or returns garbage. Always check `if (is_empty(s))`. |
| **Naive Queue Front Popping** | Shifting array on dequeue: `for(i=0;i<n;i++) a[i]=a[i+1];` | Destroys performance! Dequeue degrades to $\mathcal{O}(n)$ time. Use a Circular Queue with head pointer ($\mathcal{O}(1)$). |
| **Unchecked Recursion Stack Overflow**| Deep recursion without base case | Consumes all thread stack memory (~8 MB), triggering OS `SIGSEGV` crash. Convert to iterative dynamic stack. |
| **Modulo Division Bottleneck** | `index = (index + 1) % cap;` in hot loops | `idiv` costs 30 cycles. Use power-of-two mask: `(index + 1) & (cap - 1);`. |

---

## 10. Industrial & Production Application

### Case 1: Operating System IPC & Pipe Buffers
In Unix and Linux systems, inter-process communication pipes (`echo "data" | grep "d"`) are implemented inside the kernel using circular ring buffers (typically 64 KB). The producing process writes data to the write pointer; the consuming process reads from the read pointer. When the buffer is full, the OS kernel suspends the producer process using waitqueues until the consumer drains data, achieving synchronized lockless streaming.

### Case 2: Undo-Redo Stack Architecture in Software
Text editors (VS Code, Microsoft Word) maintain two explicit stacks:
1. **Undo Stack**: Pushes editor actions (Insert character, Delete line).
2. **Redo Stack**: When the user presses `Ctrl+Z`, the action is popped from the Undo stack, reversed, and pushed onto the Redo stack. When a new keystroke occurs, the Redo stack is wiped. Both operations execute in instantaneous $\mathcal{O}(1)$ time.

---

## 11. Benchmarks, Complexity & Performance Profiling

| Operation | Array-Backed Stack | Linked-List Stack | Circular Ring Queue | Monotonic Stack Query |
|:---|:---|:---|:---|:---|
| **Push / Enqueue** | $\mathcal{O}(1)$ amortized | $\Theta(1)$ | $\mathbf{\Theta(1)}$ (Strict worst-case) | $\mathcal{O}(1)$ amortized |
| **Pop / Dequeue** | $\mathbf{\Theta(1)}$ | $\Theta(1)$ | $\mathbf{\Theta(1)}$ (Strict worst-case) | $\mathcal{O}(1)$ amortized |
| **Peek** | $\mathbf{\Theta(1)}$ | $\Theta(1)$ | $\mathbf{\Theta(1)}$ | $\Theta(1)$ |
| **Auxiliary Memory**| $\mathcal{O}(n)$ (Contiguous buffer) | $\mathcal{O}(n)$ ($+8$ bytes ptr per node) | $\mathcal{O}(C)$ (Zero allocations) | $\mathcal{O}(n)$ |
| **Cache Line Hits**| **~99% (L1 Cache Hits)** | ~10% (Pointer Chasing) | **~99% (L1 Cache Hits)** | ~99% |

---

## 12. Security Implications & Vulnerability Analysis

### The Call Stack Return-Oriented Programming (ROP) Exploit
When a buffer overflow overwrites the execution stack, modern systems prevent running injected shellcode using Non-Executable (NX/DEP) memory flags. Attackers circumvent this using **Return-Oriented Programming (ROP)**:
- The attacker constructs a fake call stack payload consisting of a sequence of memory addresses pointing to tiny snippets of legitimate executable code followed by a `ret` instruction (called **Gadgets**).
- By chaining gadgets together, the attacker forces the CPU to pop and execute arbitrary shell instructions without ever introducing new code into memory!

#### Modern Defense: Shadow Stacks (Intel CET)
Modern Intel and AMD processors implement hardware **Control-Flow Enforcement Technology (CET)**. The CPU maintains a second, isolated **Shadow Stack** in hardware that stores return instruction pointers. If the pointer on the application stack does not match the pointer on the shadow stack when a `ret` instruction executes, the CPU raises an immediate hardware control protection exception.

---

## 13. Edge Cases & Boundary Conditions

1. **Stack Capacity 0**: If initialized with capacity 0, geometric doubling ($C \times 2$) remains 0. Always enforce initial capacity $\ge 1$ or 4.
2. **Deques Wrapping at Boundary**: When prepending to a circular deque at index 0, subtracting 1 wraps to negative numbers in naive arithmetic. Use:
   $$\text{front}_{\text{new}} = (\text{front} - 1 + C) \pmod C$$
3. **Division by Zero in Expression Parsers**: Postfix evaluation engines must explicitly check if the right-hand operand is 0 before executing `/` or `%`.

---

## 14. Comparative Analysis: Array-Backed vs Linked-List-Backed

| Evaluation Metric | Dynamic Array Implementation | Linked List Implementation |
|:---|:---|:---|
| **Memory Allocation** | Bulk allocation; amortized resizing | Node allocated on every single `push()` |
| **Single-Op Latency** | Predictable except during doubling | Completely deterministic ($\mathcal{O}(1)$ always) |
| **Cache Locality** | **Superior** (Sequential contiguous memory) | Poor (Dispersed heap blocks) |
| **Memory Footprint** | Low (Payload only + buffer) | High (Payload + 8-byte pointer per element) |
| **Best Used For** | General applications, high-throughput systems | Real-time systems forbidding reallocation pauses |

---

## 15. Emerging Paradigms, AI & Future Perspectives

1. **Lock-Free Concurrency via Atomic Ring Buffers**: Modern multi-core processing engines (e.g. LMAX Disruptor, DPDK) implement lock-free Single-Producer Single-Consumer (SPSC) circular queues using CPU atomic instructions (`atomic_load`, `atomic_store` with acquire/release memory barriers), achieving throughput of over **100 million messages per second** between CPU cores without operating system locks.
2. **AI Transformer Attention Window Management**: LLM streaming inference (e.g. vLLM) treats the Key-Value (KV) cache as a specialized circular ring buffer with paging (PagedAttention) to prevent out-of-memory crashes during long chat conversations.

---

## 16. Step-by-Step Solved Problem 1 (Foundational / Academic)

### Problem Statement
Write a C function to validate whether a string containing brackets `(`, `)`, `{`, `}`, `[`, `]` has properly balanced and nested parentheses using a stack.

### Algorithmic Strategy
1. Initialize an empty character stack.
2. Traverse each character in the string:
   - If it is an opening bracket (`(`, `{`, `[`), push it onto the stack.
   - If it is a closing bracket (`)`, `}`, `]`), check if the stack is empty. If empty, return `false`. Otherwise, pop the top bracket and verify it matches the closing bracket.
3. At the end of the string, if the stack is empty, return `true`; otherwise, return `false` (unclosed opening bracket).

### Code Implementation
```c
#include <stdbool.h>
#include <string.h>

bool is_valid_parentheses(const char *s) {
    char stack[1024];
    int top = -1;

    for (int i = 0; s[i] != '\0'; ++i) {
        char c = s[i];
        if (c == '(' || c == '{' || c == '[') {
            if (top >= 1023) return false; // Buffer overflow defense
            stack[++top] = c;
        } else if (c == ')' || c == '}' || c == ']') {
            if (top == -1) return false; // Closing without opening
            char open = stack[top--];
            if ((c == ')' && open != '(') ||
                (c == '}' && open != '{') ||
                (c == ']' && open != '[')) {
                return false; // Mismatched types
            }
        }
    }
    return top == -1; // Must have balanced all brackets
}
```

---

## 17. Step-by-Step Solved Problem 2 (Algorithmic / Systems Level)

### Problem Statement
Implement a **Min-Stack** data structure that supports `push()`, `pop()`, `top()`, and retrieving the minimum element `get_min()` in **strict $\mathcal{O}(1)$ time** and $\mathcal{O}(n)$ auxiliary space.

### Algorithmic Strategy (Dual-Stack Approach)
Maintain two stacks:
1. `main_stack`: Stores all pushed values.
2. `min_stack`: Stores the minimum value encountered up to the current depth. When pushing $x$, push $\min(x, \text{current\_min})$ onto `min_stack`.

### Code Implementation
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int *data;
    int *min_data;
    size_t capacity;
    size_t top;
} MinStack;

MinStack* min_stack_create(size_t cap) {
    MinStack *ms = (MinStack *)malloc(sizeof(MinStack));
    ms->capacity = cap;
    ms->top = 0;
    ms->data = (int *)malloc(cap * sizeof(int));
    ms->min_data = (int *)malloc(cap * sizeof(int));
    return ms;
}

void min_stack_push(MinStack *ms, int val) {
    if (ms->top >= ms->capacity) return;
    ms->data[ms->top] = val;
    if (ms->top == 0) {
        ms->min_data[ms->top] = val;
    } else {
        int prev_min = ms->min_data[ms->top - 1];
        ms->min_data[ms->top] = (val < prev_min) ? val : prev_min;
    }
    ms->top++;
}

bool min_stack_pop(MinStack *ms, int *out_val) {
    if (ms->top == 0) return false;
    ms->top--;
    if (out_val) *out_val = ms->data[ms->top];
    return true;
}

int min_stack_get_min(MinStack *ms) {
    return ms->min_data[ms->top - 1]; // O(1) Minimum retrieval!
}
```

---

## 18. Step-by-Step Solved Problem 3 (Industry / Production Debugging)

### Production Incident Scenario
A real-time telemetry ingestion server experiences intermittent deadlocks and corrupted data packets in an inter-thread circular ring buffer.

### Defective Code Snippet
```c
void write_telemetry(RingBuffer *rb, int packet_id) {
    // FATAL FLAW: Non-atomic check-then-act with unmasked increment!
    if (rb->tail - rb->head < rb->capacity) {
        rb->buffer[rb->tail % rb->capacity] = packet_id;
        rb->tail++; // RACE CONDITION: Non-atomic write!
    }
}
```

### Root Cause Analysis
1. Two worker threads invoked `write_telemetry` simultaneously. Both read the same `rb->tail` value.
2. Both threads wrote their packet to the same buffer slot, overwriting one packet.
3. Both incremented `rb->tail`, leaving the subsequent slot uninitialized.

### Production Fix: Single-Producer Single-Consumer (SPSC) Isolation & Atomic Fences
In a concurrent ring buffer, thread access must be isolated: only the producer modifies `tail`, and only the consumer modifies `head`. Memory barriers guarantee visibility:
```c
bool spsc_ring_write(RingBuffer *rb, int packet_id) {
    size_t tail = atomic_load_explicit(&rb->tail, memory_order_relaxed);
    size_t head = atomic_load_explicit(&rb->head, memory_order_acquire);

    if ((tail - head) >= rb->capacity) {
        return false; // Queue full
    }

    rb->buffer[tail & rb->mask] = packet_id;
    atomic_store_explicit(&rb->tail, tail + 1, memory_order_release);
    return true;
}
```

---

## 19. Categorized Practice Exercises

### Beginner (Confidence Builders)
1. Implement a queue using two stacks and analyze the amortized cost of `enqueue` and `dequeue`.
2. Write a function to reverse a string using a stack.
3. Implement a circular queue using an array and write a display function that prints elements in FIFO order.

### Intermediate (Exam Level)
4. Implement an infix-to-postfix expression converter that handles operators `+`, `-`, `*`, `/`, `^`, and parentheses.
5. Solve the **Daily Temperatures** problem: given an array of daily temperatures, return an array such that `res[i]` is the number of days you have to wait for a warmer temperature, using a monotonic stack.
6. Design a Circular Deque supporting `insertFront`, `insertLast`, `deleteFront`, `deleteLast` in $\mathcal{O}(1)$ time.

### Advanced (Systems / Competitive)
7. Implement the **Sliding Window Maximum** problem: given an array of integers and a window size $k$, return the maximum element in every moving window in strict $\mathcal{O}(n)$ time using a Monotonic Double-Ended Queue (Deque).
8. Implement an unbounded lock-free SPSC (Single Producer Single Consumer) ring buffer in C11 using `<stdatomic.h>`.

---

## 20. University Exam Practice Questions (SPPU / International Style)

### Question 1 (Theory - 5 Marks)
Define Stack and Queue. Explain why circular queues are preferred over linear array queues. State the mathematical conditions for queue full and queue empty in a circular queue.

### Question 2 (Algorithm & Conversion - 5 Marks)
Convert the following infix expression into postfix using Dijkstra's Shunting Yard algorithm, showing the step-by-step state of the operator stack and output string:
$$A + B \times (C - D) / E$$

### Question 3 (Code Analysis & Defect Identification - 5 Marks)
What is wrong with the following stack pop implementation?
```c
int pop(int *stack, int top) {
    int val = stack[top];
    top--;
    return val;
}
```
Explain why `top` remains unchanged in the calling function and provide the pass-by-pointer correction.

---

## 21. Industry Interview Masterclass

### Tier A (Freshers / Campus Hiring)
- **Q**: What is the difference between a Stack and a Queue?
- **A**: A Stack is a LIFO (Last-In, First-Out) data structure where insertions and deletions happen at the same end (Top). A Queue is a FIFO (First-In, First-Out) data structure where insertions happen at one end (Rear) and deletions happen at the opposite end (Front).

### Tier B (Mid-Level Engineers)
- **Q**: How do you implement a Queue using two Stacks, and what is the amortized complexity of its operations?
- **A**: Maintain `stack_in` and `stack_out`. To enqueue, push to `stack_in` ($\mathcal{O}(1)$). To dequeue: if `stack_out` is empty, pop all elements from `stack_in` and push them to `stack_out` (reversing their order), then pop from `stack_out`. While a single dequeue may take $\mathcal{O}(n)$ during a transfer, each element is pushed and popped at most twice, yielding an amortized cost of $\mathcal{O}(1)$ per operation.

### Tier C (Senior Systems Engineers)
- **Q**: Why are circular ring buffers universally preferred in operating system network device drivers over dynamic queues?
- **A**: Circular ring buffers use fixed-size pre-allocated contiguous memory, requiring zero dynamic memory allocation (`malloc`/`free`) in interrupt contexts where allocation is forbidden. They offer optimal cache locality, bounded deterministic latency, and can be designed lock-free for Single-Producer Single-Consumer execution using simple memory barrier fences.

### Tier D (FAANG / Core Systems & Kernel)
- **Q**: Explain how a Monotonic Queue solves the Sliding Window Maximum problem in $\mathcal{O}(n)$ time rather than $\mathcal{O}(n \cdot k)$ naive time.
- **A**: The monotonic deque maintains indices of array elements in strictly decreasing order of their values. When sliding the window:
  1. Remove indices from the front that have fallen out of the current window ($< i - k + 1$).
  2. While the deque tail holds an element smaller than the incoming element, pop it from the tail (because an older, smaller element can never be the maximum again).
  3. Push the new element index to the tail. The element at the front of the deque is guaranteed to be the maximum for the current window. Because each element enters and leaves the deque at most once, the total time across $n$ steps is $\mathcal{O}(n)$.

---

## 22. Hands-on Lab Assignment & Verification Checklist

### Lab Goal
Write a production-quality verification harness in C and Python that:
1. Implements a circular ring buffer with power-of-two bitwise masking.
2. Validates balanced bracket parsing against nested expressions.
3. Implements the Min-Stack supporting $\mathcal{O}(1)$ minimum queries.
4. Implements the Monotonic Queue sliding window maximum algorithm and verifies output correctness.

### Verification Checklist
- [x] Circular ring buffer modulo wrapping functions correctly at boundary.
- [x] Bitwise AND mask $(C - 1)$ verified identical to `% C` for power-of-two capacities.
- [x] Min-Stack maintains accurate minimums across alternating push and pop operations.
- [x] All simulation and test scripts execute with exit code 0.

---

## 23. High-Yield Quick Revision Summary

| ADT | Discipline | Primary Operations | Standard Array Implementation | Best Use Case |
|:---|:---|:---|:---|:---|
| **Stack** | LIFO | `push()`, `pop()`, `peek()` | Dynamic array with `top` index | Call stack, expression parsing, DFS |
| **Queue** | FIFO | `enqueue()`, `dequeue()` | Circular ring buffer with `head`, `tail` | Task scheduling, BFS, IPC pipes |
| **Deque** | Double-ended | `push_front/back`, `pop_front/back`| Circular buffer with 2 pointers | Sliding window maximum, work stealing |
| **Monotonic Stack**| Monotonic order | `push()` with popping violations | Standard array stack | Next Greater Element ($\mathcal{O}(n)$) |
| **Monotonic Queue**| Monotonic order | Enqueue tail pop, Dequeue head | Deque with index bounds | Sliding Window Maximum ($\mathcal{O}(n)$) |

---

## 24. Verified Academic Citations & Authoritative References

1. **Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C.** (2022). *Introduction to Algorithms* (4th ed.). MIT Press. [Chapter 10.1: Stacks and Queues, pp. 251–257].
2. **Knuth, D. E.** (1997). *The Art of Computer Programming, Volume 1: Fundamental Algorithms* (3rd ed.). Addison-Wesley. [Section 2.2.1: Stacks, Queues, and Deques].
3. **Dijkstra, E. W.** (1961). *Algol 60 Translation: An ALGOL 60 Translator for the X1 and Making a Translator for ALGOL 60*. Mathematisch Centrum, Amsterdam. [Original formulation of the Shunting-Yard algorithm].
4. **McKenney, P. E.** (2017). *Is Parallel Programming Hard, And, If So, What Can You Do About It?* [Chapter 5: Counting and Circular Buffers].
