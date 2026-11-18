# Level 4 Capstone Project: AegisDB — Optimizing Transactional Storage Engine

---

## 1. Executive Summary & Architectural Overview
**AegisDB** is a production-grade, embeddable relational storage and query optimization engine designed to synthesize all ten advanced computer science disciplines mastered in Level 4:
- **Theory of Computation & Formal Grammars**: Lexical analysis and LL(1) recursive descent parsing converting declarative SQL statements into structured Concrete and Abstract Syntax Trees.
- **Compiler Optimization & Intermediate Representations**: Logical query plan optimization, Constant Folding, Dead Predicate Elimination, and Directed Acyclic Graph (DAG) query representation.
- **Advanced Graph Algorithms & Network Flow**: Transaction dependency graphs (Precedence Graphs) with cycle detection for deadlock and serializability verification.
- **Physical Database Internals**: Fixed 4096-byte Slotted Page binary layout, in-memory Buffer Pool Manager with CLOCK page replacement, and disk persistence.
- **Concurrency & Isolation**: Multi-Version Concurrency Control (MVCC) implementing Snapshot Isolation without read-locks.
- **Durability & Fault Tolerance**: Write-Ahead Logging (WAL) with ARIES-style crash recovery (Analysis, Redo, and Undo).

```
+-----------------------------------------------------------------------------------+
|                              AEGIS-DB ARCHITECTURE                                 |
+-----------------------------------------------------------------------------------+
|  [ Declarative SQL Query String ]                                                 |
|          |                                                                        |
|          v                                                                        |
|  [ FRONTEND COMPILER ]                                                            |
|    - Lexer (DFA Scanner)                                                          |
|    - Recursive Descent AST Parser (Context-Free Grammar)                          |
+-----------------------------------------------------------------------------------+
|          |                                                                        |
|          v                                                                        |
|  [ QUERY PLANNER & OPTIMIZER ]                                                    |
|    - Logical Plan DAG Builder                                                     |
|    - Constant Folding & Predicate Simplification                                  |
|    - Volcano Iterator Physical Execution Model (open / next / close)              |
+-----------------------------------------------------------------------------------+
|          |                                              |                         |
|          v                                              v                         |
|  [ CONCURRENCY & MVCC ]                      [ WRITE-AHEAD LOGGING (WAL) ]        |
|    - Snapshot Isolation (xmin, xmax)           - Append-only WAL file             |
|    - Read View Active Tx Tracking              - ARIES Crash Recovery             |
|    - Deadlock Cycle Detection                  - Repeating History + Undo Losers  |
+-----------------------------------------------------------------------------------+
|                                  |                                                |
|                                  v                                                |
|  [ BUFFER POOL MANAGER (CLOCK Eviction Policy) ]                                  |
|    - Frame Table + Page Hash Table + Pin Counts                                   |
+-----------------------------------------------------------------------------------+
|                                  |                                                |
|                                  v (Dirty Page Writes)                            |
|  [ PHYSICAL STORAGE ENGINE (Slotted Pages: 4096 Bytes, Line Pointers, Tuples) ]   |
+-----------------------------------------------------------------------------------+
```

---

## 2. Mathematical Invariants & Verification Criteria

1. **Slotted Page Invariant**:
   $$\text{FreeSpaceEnd} - \text{SlotDirectoryEnd} \ge \text{SLOT\_SIZE} + \text{RecordLength}$$
   Tuples grow upward from byte 4096; line pointer slots grow downward from byte 12. Slot IDs remain stable across in-page data compactions.

2. **MVCC Snapshot Visibility Invariant**:
   For a transaction $T_i$ with active transaction snapshot set $\mathcal{A}$ and start timestamp $t_i$:
   $$\text{Visible}(R) \iff \left( R.\text{xmin} \le t_i \land R.\text{xmin} \notin \mathcal{A} \right) \land \left( R.\text{xmax} = 0 \lor R.\text{xmax} > t_i \lor R.\text{xmax} \in \mathcal{A} \right)$$

3. **ARIES Crash Recovery Invariant**:
   $$\forall \text{ committed } T_c, \quad \text{State}(T_c) \text{ is fully restored (Redo)}$$
   $$\forall \text{ uncommitted } T_u \in \text{Losers}, \quad \text{State}(T_u) \text{ is completely reversed (Undo)}$$

4. **Query Plan Optimization Invariant**:
   $$\forall \text{ expressions } e, \quad \text{Eval}(\text{Optimize}(e)) \equiv \text{Eval}(e) \quad \text{with zero dead filter overhead}$$

---

## 3. Component Files
- `13_PROJECTS/level_4_capstone/aegis_engine.py`: Full operational implementation of the compiler frontend, optimizer, MVCC transaction coordinator, buffer pool, slotted page manager, and WAL crash recovery engine.
- `13_PROJECTS/level_4_capstone/aegis_verifier.py`: Automated testing harness running unit, integration, concurrency, and crash recovery stress tests.
