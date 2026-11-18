# Level 4 Revision & Formula Sheet: Computability, Compilers & Database Internals

---

## 1. Quick Reference: Chapters 06 to 10

| Chapter | Core Focus | Key Axioms & Master Invariants | Primary Pitfalls / Edge Cases |
|:---|:---|:---|:---|
| **CH06: Turing Machines & Decidability** | Formal 7-tuple TM, Halting Problem, Rice's Thm | $\delta: Q \times \Gamma \to Q \times \Gamma \times \{L, R\}$; $A_{\text{TM}} \notin \mathcal{R}$; $\overline{A_{\text{TM}}} \notin \mathcal{RE}$ | Confusing undecidability with intractability; missing tape boundary guards |
| **CH07: Complexity Classes P vs NP** | Polynomial verification, Cook-Levin, Reductions | $L \in \mathbf{NP} \iff V(w, c)$ in $\mathcal{O}(|w|^k)$; $A \le_p B \land B \in \mathbf{P} \implies A \in \mathbf{P}$ | Reversing reduction direction ($B \le_p A$); assuming NP means "Non-Polynomial" |
| **CH08: Compiler Lexing & Parsing** | Regex to DFA, CFGs, LL(1), LR(1), ASTs | $\text{FIRST}(\alpha)$; $\text{FOLLOW}(A)$; Shift-Reduce priority rule | Left recursion causing infinite stack; shift-reduce grammar conflicts |
| **CH09: Optimization & Code Generation**| SSA Form, CFG, Liveness Analysis, Kempe Coloring | $x_3 = \phi(x_1, x_2)$; $\text{IN} = \text{USE} \cup (\text{OUT} \setminus \text{DEF})$; $\text{deg}(v) < K$ | Pointer aliasing invalidating GVN/DCE; instruction cache bloat from unrolling |
| **CH10: Database Engine Internals** | Slotted Pages, Buffer Pool CLOCK, MVCC, ARIES | $\text{Precedence DAG} \iff \text{Conflict Serializable}$; $\text{PageLSN} \le \text{FlushedLSN}$ | Write skew under snapshot isolation; deadlocks in strict 2PL; table bloat |

---

## 2. Computability & Complexity Theory Cheatsheet

### 2.1 The Chomsky & Decidability Hierarchy
```
Languages over Sigma*:
  +--------------------------------------------------------------+
  | Turing-Recognizable (RE)        -- Halting Problem (A_TM)    |
  |   +----------------------------------------------------------+
  |   | Turing-Decidable (Recursive)-- Presburger Arithmetic     |
  |   |   +------------------------------------------------------+
  |   |   | Context-Sensitive (CSG) -- Linear Bounded Automata   |
  |   |   |   +--------------------------------------------------+
  |   |   |   | Context-Free (CFG)  -- Pushdown Automata (PDA)   |
  |   |   |   |   +----------------------------------------------+
  |   |   |   |   | Regular (DFA)   -- Lexers, Finite Automata   |
  |   |   |   |   +----------------------------------------------+
  |   |   |   +--------------------------------------------------+
  |   |   +------------------------------------------------------+
  |   +----------------------------------------------------------+
  +--------------------------------------------------------------+
```

### 2.2 Complexity Classes Relationship
$$\mathbf{P} \subseteq \mathbf{NP} \subseteq \mathbf{PSPACE} = \mathbf{NPSPACE} \subseteq \mathbf{EXPTIME}$$
- **Savitch's Theorem**: $\mathbf{NSPACE}(f(n)) \subseteq \mathbf{SPACE}(f(n)^2)$.
- **Cook-Levin Theorem**: $\text{SAT}$ is NP-complete.
- **Karp's Reductions**: $\text{3-SAT} \le_p \text{CLIQUE} \le_p \text{VERTEX-COVER} \le_p \text{SET-COVER}$.
- **Approximation Ratio**: $\alpha = \max_I \frac{\text{ALG}(I)}{\text{OPT}(I)}$. Maximal matching yields a $2$-approximation for Vertex Cover.

---

## 3. Compiler Frontend & Parser Construction Formulas

### 3.1 FIRST & FOLLOW Set Invariants
- $\text{FIRST}(X) = \{a \in \Sigma \mid X \Rightarrow^* a \beta\}$
- For production $A \to X_1 X_2 \dots X_k$:
  Add non-$\epsilon$ symbols of $\text{FIRST}(X_1)$ to $\text{FIRST}(A)$. If $\epsilon \in \text{FIRST}(X_1)$, add $\text{FIRST}(X_2)$, and so on.
- $\text{FOLLOW}(B) = \{a \in \Sigma \cup \{\$\} \mid S \Rightarrow^* \alpha B a \beta\}$
  If $A \to \alpha B \beta$, everything in $\text{FIRST}(\beta)$ (except $\epsilon$) is in $\text{FOLLOW}(B)$.
  If $\beta \Rightarrow^* \epsilon$ or is empty, everything in $\text{FOLLOW}(A)$ is in $\text{FOLLOW}(B)$.

### 3.2 Parsing Grammar Classes Comparison
$$\text{LL}(1) \subset \text{SLR}(1) \subset \text{LALR}(1) \subset \text{LR}(1)$$
- **LL(1)**: 1 token lookahead, top-down leftmost derivation, no left recursion allowed.
- **LR(1)**: Bottom-up shift-reduce parser with lookahead items $[A \to \alpha \bullet \beta, a]$.
- **LALR(1)**: Merges LR(1) states with identical cores, reducing state count while preventing shift-reduce conflicts (can introduce reduce-reduce conflicts).

---

## 4. Compiler Optimization & Backend Formulas

### 4.1 Dataflow Analysis Fixed-Point Systems

| Analysis | Direction | Meet ($\sqcap$) | Transfer Function | Typical Optimization |
|:---|:---|:---|:---|:---|
| **Reaching Definitions** | Forward | $\bigcup$ (May) | $\text{OUT}[B] = \text{GEN}[B] \cup (\text{IN}[B] \setminus \text{KILL}[B])$ | Constant Propagation |
| **Available Expressions**| Forward | $\bigcap$ (Must) | $\text{OUT}[B] = \text{GEN}[B] \cup (\text{IN}[B] \setminus \text{KILL}[B])$ | Common Subexpression (CSE)|
| **Live Variables** | Backward | $\bigcup$ (May) | $\text{IN}[B] = \text{USE}[B] \cup (\text{OUT}[B] \setminus \text{DEF}[B])$ | Dead Code Elimination & RegAlloc |
| **Very Busy Expressions** | Backward | $\bigcap$ (Must) | $\text{IN}[B] = \text{USE}[B] \cup (\text{OUT}[B] \setminus \text{KILL}[B])$ | Code Hoisting |

### 4.2 Chaitin-Kempe Register Allocation
1. Build interference graph $G = (V, E)$ from live variable intervals.
2. If $\exists v \in V$ with $\text{deg}(v) < K$: push $v$ to stack and remove from graph.
3. If all $\text{deg}(v) \ge K$: select spill candidate with minimal $\frac{\text{cost}}{\text{deg}(v)}$, spill to stack frame memory.
4. Pop stack and greedily assign registers $1 \dots K$.

---

## 5. Database Engine Internals & ACID Invariants

### 5.1 Storage Architecture & Page Layout
- **Slotted Page**: Header (LSN, free space offset, slot count) $\to$ Slot directory grows down $\to$ Free space $\to$ Tuples grow up from bottom.
- **Buffer Pool CLOCK Algorithm**: Circular pointer checks unpinned frames; if reference bit is 1, clear to 0; if 0, evict frame (flushing to disk if dirty).

### 5.2 Concurrency Control & Isolation Levels
- **Conflict Serializability**: Conflicting operations: $R_i(X), W_j(X)$ or $W_i(X), W_j(X)$ ($i \neq j$).
- **Precedence Graph (Serialization Graph)**: Directed edge $T_i \to T_j$ if $T_i$ precedes and conflicts with $T_j$. Acyclic $\iff$ Conflict Serializable.
- **Strict Two-Phase Locking (SS2PL)**: Hold all exclusive locks until transaction commit/abort. Guarantees serializability and eliminates cascading aborts.

### 5.3 MVCC & Snapshot Isolation
- **Tuple Header**: `(xmin, xmax, ctid, data)`.
- **Visibility**:
  - Visible if $\text{xmin}$ committed before snapshot and $\text{xmin} \notin \text{ActiveXIDs}$.
  - Invisible if $\text{xmax}$ committed before snapshot and $\text{xmax} \notin \text{ActiveXIDs}$.
  - Prevents Dirty Reads, Non-Repeatable Reads, and Phantoms without read locks.

### 5.4 ARIES Crash Recovery (Analysis, Redo, Undo)
1. **Analysis**: Forward scan from last checkpoint to crash point. Reconstructs active transactions (Losers Set) and dirty pages in buffer pool.
2. **Redo (Repeating History)**: Forward scan from smallest unwritten `RedoLSN`. Reapplies all operations (committed and uncommitted).
3. **Undo**: Backward scan from crash point, reversing updates of all Loser transactions and logging Compensation Log Records (CLRs).
