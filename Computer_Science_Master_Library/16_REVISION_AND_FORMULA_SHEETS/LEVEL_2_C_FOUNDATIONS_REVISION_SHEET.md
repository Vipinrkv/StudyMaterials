# Level 2 Revision & Formula Sheet: C Foundations & Systems Mental Models

---

## 1. Quick Reference: Chapters 01 to 05

| Chapter | Core Focus | Key Axioms & Formulas | Primary Failure Mode |
|:---|:---|:---|:---|
| **CH01: Mental Models & Problem Solving** | Computational Thinking & Decomposition | State Transitions, Invariants, Inductive Proof | Misidentifying loop termination invariants |
| **CH02: C Fundamentals & Types** | Binary representation, signed/unsigned math | $2$'s complement: $-X = \sim X + 1$ | Unsigned integer underflow wrapping to $2^{32}-1$ |
| **CH03: Operators & Control Flow** | Operator precedence, short-circuiting | `&&` short-circuits on `0`; `\|\|` short-circuits on `1` | `=` (assignment) instead of `==` (equality check) |
| **CH04: Functions & Call Stack** | Activation records, stack frames, scoping | Caller $\to$ Push args $\to$ `call` (Push RIP) $\to$ Push RBP | Returning address of local stack variable (dangling pointer) |
| **CH05: Arrays, Strings & Pointers** | Contiguous memory, pointer arithmetic | $A[i][j] = \text{Base} + (i \cdot C + j) \cdot S$ | Buffer overflow (`strcpy`), missing `\0` |

---

## 2. Mathematical & Memory Addressing Formulas

### 2.1 1D Array Offset
$$\text{Address}(A[i]) = \text{Base}(A) + i \times \text{sizeof}(T)$$

### 2.2 2D Array Row-Major Offset (C Standard)
For array declared as `T M[Rows][Cols]`:
$$\text{Address}(M[i][j]) = \text{Base}(M) + (i \times \text{Cols} + j) \times \text{sizeof}(T)$$

### 2.3 2D Array Column-Major Offset (Fortran / MATLAB)
$$\text{Address}(M[i][j]) = \text{Base}(M) + (j \times \text{Rows} + i) \times \text{sizeof}(T)$$

### 2.4 Pointer Scaling Axiom
For pointer `T *p`:
$$p + k \equiv (\text{uintptr\_t})p + k \times \text{sizeof}(T)$$
$$p_2 - p_1 = \frac{(\text{uintptr\_t})p_2 - (\text{uintptr\_t})p_1}{\text{sizeof}(T)}$$

---

## 3. The C Operator Precedence Pyramid (Top to Bottom)

1. **Highest**: Parentheses `()`, Array subscript `[]`, Struct access `.`, `->`, Post-increment `++`, Post-decrement `--` *(Left to Right)*
2. **Unary Operators**: Logical NOT `!`, Bitwise NOT `~`, Pre-increment `++`, Pre-decrement `--`, Address-of `&`, Dereference `*`, `sizeof` *(Right to Left)*
3. **Multiplicative**: `*`, `/`, `%` *(Left to Right)*
4. **Additive**: `+`, `-` *(Left to Right)*
5. **Bitwise Shifts**: `<<`, `>>` *(Left to Right)*
6. **Relational**: `<`, `<=`, `>`, `>=` *(Left to Right)*
7. **Equality**: `==`, `!=` *(Left to Right)*
8. **Bitwise AND / XOR / OR**: `&` then `^` then `|` *(Left to Right)*
9. **Logical AND / OR**: `&&` then `||` *(Left to Right - Short Circuiting)*
10. **Ternary Conditional**: `? :` *(Right to Left)*
11. **Assignment**: `=`, `+=`, `-=`, etc. *(Right to Left)*
12. **Comma**: `,` *(Left to Right)*

---

## 4. Memory Segments in a C Process

```
+-------------------------------------------------------+ High Address (0xFFFFFFFF / 0x7FFFFFFFFFFF)
| Stack Segment (Grows DOWNWARDS towards low memory)    |
| - Local automatic variables, stack frames, return IPs |
|                         |                             |
|                         v                             |
|                                                       |
|                         ^                             |
|                         |                             |
| Heap Segment (Grows UPWARDS towards high memory)      |
| - Dynamic allocation (malloc, calloc, realloc)        |
+-------------------------------------------------------+
| BSS Segment (Block Started by Symbol)                 |
| - Uninitialized global and static variables (zeroed)  |
+-------------------------------------------------------+
| Data Segment (.data)                                  |
| - Initialized global and static variables             |
+-------------------------------------------------------+
| Text Segment (.text / .rodata)                        |
| - Compiled CPU machine instructions, string literals  |
+-------------------------------------------------------+ Low Address (0x00000000)
```

---

## 5. Pointer Declarations & Semantic Decoding (Clockwise/Spiral Rule)

- `int *p;` $\to$ Pointer to `int`.
- `const int *p;` $\to$ Pointer to constant `int` (Data is read-only).
- `int * const p;` $\to$ Constant pointer to `int` (Address cannot change).
- `const int * const p;` $\to$ Constant pointer to constant `int` (Neither can change).
- `int *arr[10];` $\to$ Array of 10 pointers to `int`.
- `int (*arr)[10];` $\to$ Pointer to an array of 10 integers.
- `int (*func)(int, int);` $\to$ Pointer to a function taking two ints and returning int.

---

## 6. High-Yield Exam & Interview Traps

1. **Array Decay**: `sizeof(arr)` inside a function taking `arr[]` returns the pointer size ($8$ bytes on 64-bit systems), not the total array byte footprint.
2. **Short-Circuit Side Effects**: `if (a == 0 && ++b > 0)`: If `a != 0`, `++b` is never evaluated!
3. **Integer Promotion**: Operands smaller than `int` (`char`, `short`) are implicitly promoted to `int` before arithmetic operations.
4. **Buffer Sizing for C-Strings**: Always allocate $N+1$ bytes for a string of length $N$ to store the terminating `'\0'`.
5. **Dangling Pointer**: Accessing memory through a pointer after the target object's lifetime has ended (e.g., returning address of stack local) causes undefined behavior.
