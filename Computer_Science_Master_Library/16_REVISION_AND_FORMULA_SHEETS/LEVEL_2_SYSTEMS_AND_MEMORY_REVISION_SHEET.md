# Level 2 Revision & Formula Sheet: Advanced Systems Programming & Memory Management

---

## 1. Quick Reference: Chapters 06 to 10

| Chapter | Core Focus | Key Axioms & Formulas | Primary Failure Mode |
|:---|:---|:---|:---|
| **CH06: Structs, Unions & Alignment** | Memory padding, alignment, bitfields | $\text{Off}_i = \left\lceil \frac{\text{Off}_{i-1} + S_{i-1}}{A_i} \right\rceil \times A_i$ | Information leak via uninitialized padding (`memcmp`) |
| **CH07: Dynamic Memory & Heap** | `malloc`, `realloc`, `free`, arenas | $S_{\text{alloc}} = \max\left(C_{\min}, \left\lceil \frac{S+H}{A}\right\rceil A\right)$ | Use-After-Free (UAF), Double Free, Memory Leak |
| **CH08: File I/O & Streams** | Buffered streams (`FILE*`), binary persistence | $\text{Offset} = K \times \text{sizeof}(\text{Record})$ | Looping with `while (!feof(fp))`, TOCTOU race |
| **CH09: Preprocessor & Build Systems** | Macros, headers, DAG compilation | `Timestamp(prereq) > Timestamp(target)` | Missing macro parentheses, side-effects (`i++`) |
| **CH10: Defensive Programming & Debugging** | Contracts, ASan, GDB, Valgrind | Shadow Address $= (\text{Addr} / 8) + \text{Offset}$ | Side-effects in `assert()`, Heisenbugs |

---

## 2. Memory Alignment & Offset Formulas

### 2.1 Natural Alignment Rule
$$\text{Address}(x) \equiv 0 \pmod{\text{alignof}(\text{typeof}(x))}$$

### 2.2 Struct Member Offset Calculation
$$\text{Off}_0 = 0$$
$$\text{Off}_i = \left\lceil \frac{\text{Off}_{i-1} + \text{sizeof}(M_{i-1})}{\text{alignof}(M_i)} \right\rceil \times \text{alignof}(M_i)$$

### 2.3 Total Struct Size with Tail Padding
$$A_{\text{struct}} = \max_i (\text{alignof}(M_i))$$
$$\text{sizeof}(\text{struct}) = \left\lceil \frac{\text{Off}_{last} + \text{sizeof}(M_{last})}{A_{\text{struct}}} \right\rceil \times A_{\text{struct}}$$

> **Optimization Rule**: Sort struct members in **descending order of size/alignment** ($8 \to 4 \to 2 \to 1$) to eliminate internal padding.

---

## 3. Dynamic Heap Management Patterns

### 3.1 Geometric Dynamic Array Growth
To maintain $\mathcal{O}(1)$ amortized append time, expand array capacity geometrically:
$$\text{New Capacity} = \text{Current Capacity} \times 2$$

### 3.2 Safe Reallocation Idiom
```c
void *temp = realloc(ptr, new_size);
if (temp == NULL) {
    // Handle error; original 'ptr' is still valid!
} else {
    ptr = temp;
}
```

### 3.3 Defensive Free Macro
```c
#define SAFE_FREE(p) do { free(p); (p) = NULL; } while(0)
```

---

## 4. File I/O Modes & Seeking Reference

| Mode String | Action | If File Exists | If File Missing |
|:---|:---|:---|:---|
| `"rb"` | Read binary | Opens at offset 0 | Returns `NULL` (Error) |
| `"wb"` | Write binary | **Truncates to 0 bytes!** | Creates new file |
| `"ab"` | Append binary | Opens; all writes go to EOF | Creates new file |
| `"r+b"` | Read/Write update | Opens at offset 0 | Returns `NULL` (Error) |
| `"w+b"` | Read/Write truncate | **Truncates to 0 bytes!** | Creates new file |

### Random Access Seeking (`fseek`)
- `SEEK_SET`: Offset relative to beginning of file.
- `SEEK_CUR`: Offset relative to current stream pointer.
- `SEEK_END`: Offset relative to end of file.

---

## 5. Preprocessor Best Practices & Traps

```c
// Trap: Naive Macro
#define SQUARE(x) x * x
// SQUARE(2 + 3) -> 2 + 3 * 2 + 3 = 11 (Wrong!)

// Solution: Fully Parenthesized Macro
#define SAFE_SQUARE(x) (((x) * (x)))

// Multi-statement Macro Idiom
#define DO_SOMETHING(a, b) do { \
    func1(a);                   \
    func2(b);                   \
} while(0)

// Stringification & Concatenation
#define STR(s) #s
#define GLUE(a, b) a##b
```

---

## 6. Essential Compiler & Debugging Command Reference

### Compilation with Full Diagnostics
```bash
gcc -Wall -Wextra -Werror -Wpedantic -g -O2 main.c -o app
```

### AddressSanitizer & UBSan Build
```bash
gcc -fsanitize=address,undefined -g -O1 main.c -o app_sanitized
```

### GDB Quick Cheat Sheet
- `gdb ./app`: Launch executable under GDB.
- `break function_name` / `b file.c:line`: Set breakpoint.
- `run [args]`: Execute program.
- `next` (`n`): Step over line.
- `step` (`s`): Step into function.
- `print var` (`p`): Inspect variable.
- `backtrace` (`bt`): Print call stack frames.
- `watch var`: Set hardware watchpoint on variable modification.
- `continue` (`c`): Resume execution.
- `quit` (`q`): Exit debugger.
