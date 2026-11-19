# University End-Semester Examination: Core Computer Science & Systems Engineering (Levels 4–6)

**Course Codes:** CS401 / CS501 / CS601 (Compilers, Operating Systems, DBMS, Distributed Systems, ML)  
**Applicable Degrees:** BCS, BCA, B.Tech SE, BESE, MCS, MCA, M.Tech SE  
**Duration:** 3 Hours (180 Minutes)  
**Maximum Marks:** 100  
**Instructions:**
1. All questions in Section A are compulsory (20 Marks).
2. Answer any **four** questions from Section B (40 Marks).
3. Answer any **two** questions from Section C (40 Marks).
4. Diagrams, ASCII layout charts, and step-by-step mathematical working carry explicit marks.
5. Code snippets must adhere to standard C11 / POSIX / Python 3.10+ specifications.

---

## SECTION A: Objective & Conceptual Systems Foundations (Compulsory — 10 × 2 Marks = 20 Marks)

### Q1.1
**Question:** Explain the difference between LL(1) and LR(1) parsers in terms of parse tree construction direction and language coverage.  
**Marking Scheme:** 1 mark for direction (top-down vs bottom-up), 1 mark for language hierarchy.  
**Model Solution:**  
- **LL(1):** Constructs parse tree Top-Down from the root using leftmost derivation; predicts production with 1 token lookahead; cannot handle left recursion; recognizes deterministic context-free languages that are non-left-recursive.  
- **LR(1):** Constructs parse tree Bottom-Up from leaves to root using rightmost derivation in reverse (handle pruning); defers decisions until whole handle is accumulated on the shift-reduce stack; strictly subsumes LL(1) grammar capabilities ($LL(1) \subset LR(1)$).

### Q1.2
**Question:** Why do modern database engines store table data in B+ Trees rather than standard balanced Binary Search Trees (BST)?  
**Marking Scheme:** 1 mark for disk I/O / fanout, 1 mark for range scan sequential linking.  
**Model Solution:**  
1. **High Fanout & Low Tree Height:** Standard BSTs have a fanout of 2, requiring $\approx \log_2 N$ disk page fetches. B+ Trees have fanout $B \approx 100-1000$, keeping tree height $\le 3-4$ and bounding random I/O reads.  
2. **Sequential Leaf Pointers:** All data records reside exclusively in leaf nodes linked by bidirectional pointers, enabling $O(\log_B N + K)$ linear range scans without traversing internal nodes.

### Q1.3
**Question:** State the Write-Ahead Logging (WAL) protocol invariants in transactional database systems.  
**Marking Scheme:** 1 mark for WAL flushing before dirty page write, 1 mark for commit record before ACK.  
**Model Solution:**  
1. **Rule 1 (Undo rule):** A dirty data page in the buffer pool must not be flushed to non-volatile disk before the corresponding undo log record representing that update has been flushed to disk (`pageLSN <= flushedLSN`).  
2. **Rule 2 (Redo rule):** A transaction cannot be acknowledged as committed until its `COMMIT` log record has been synchronously flushed to non-volatile disk storage.

### Q1.4
**Question:** What is the difference between Strict Two-Phase Locking (SS2PL) and Standard Two-Phase Locking (2PL)?  
**Marking Scheme:** 1 mark for unlock timing, 1 mark for cascading abort prevention.  
**Model Solution:**  
In standard 2PL, locks can be released incrementally during the shrinking phase once all locks are acquired. In Strict 2PL (SS2PL), all exclusive (X) locks (and shared locks in Rigorous 2PL) must be held continuously until the transaction commits or aborts. This prevents cascading aborts and guarantees strict serializability.

### Q1.5
**Question:** How does the Completely Fair Scheduler (CFS) in Linux utilize `vruntime` (virtual runtime) and red-black trees to schedule tasks?  
**Marking Scheme:** 1 mark for vruntime weighting formula, 1 mark for RB-tree leftmost pick.  
**Model Solution:**  
CFS tracks elapsed execution time scaled inversely by task priority weight:  
$$\Delta \text{vruntime} = \Delta \text{physical\_time} \times \frac{\text{NICE\_0\_LOAD}}{\text{weight}}$$  
Runnable tasks are indexed in an RB-tree keyed by `vruntime`. The scheduler always picks the leftmost task (smallest `vruntime`, $O(1)$ lookup via cached pointer), ensuring perfectly fair CPU time distribution.

### Q1.6
**Question:** Explain the causality invariant of Vector Clocks: when does $V(a) < V(b)$?  
**Marking Scheme:** 1 mark for component-wise inequality, 1 mark for strict inequality condition.  
**Model Solution:**  
Event $a$ causally precedes event $b$ ($a \to b$) if and only if:  
$$\forall k \in [1, N]: V(a)[k] \le V(b)[k] \quad \land \quad \exists j \in [1, N]: V(a)[j] < V(b)[j]$$  
If neither $V(a) < V(b)$ nor $V(b) < V(a)$, then $a$ and $b$ are concurrent ($a \parallel b$).

### Q1.7
**Question:** Define the CAP theorem's Consistency ($C$) and Availability ($A$) under a network partition ($P$).  
**Marking Scheme:** 1 mark for Consistency definition, 1 mark for Availability definition under partition.  
**Model Solution:**  
Under a network partition ($P$):  
- **Consistency ($CP$):** Every read receives the most recent write or an error (system sacrifices availability on minority partition to prevent stale or conflicting reads).  
- **Availability ($AP$):** Every non-failing node returns a non-error response, but responses may not contain the most recent write (system sacrifices linearizability to remain responsive).

### Q1.8
**Question:** In a convolutional layer with input $32 \times 32 \times 3$, 16 filters of size $5 \times 5$, padding $P = 2$, stride $S = 1$, compute output spatial dimensions and parameter count (including bias).  
**Marking Scheme:** 1 mark for spatial dimensions, 1 mark for parameter count.  
**Model Solution:**  
- Output spatial dimensions:  
  $$\text{Out} = \frac{W - K + 2P}{S} + 1 = \frac{32 - 5 + 4}{1} + 1 = 32 \times 32 \times 16$$  
- Parameter count:  
  $$\text{Params} = (\text{kernel\_h} \times \text{kernel\_w} \times \text{in\_channels} + 1_{\text{bias}}) \times \text{num\_filters} = (5 \times 5 \times 3 + 1) \times 16 = 76 \times 16 = 1,216 \text{ parameters}$$.

### Q1.9
**Question:** Why does the Page Replacement "Clock" (Second-Chance) algorithm approximate LRU in $O(1)$ amortized time?  
**Marking Scheme:** 1 mark for circular pointer scan, 1 mark for reference bit inspection/reset.  
**Model Solution:**  
The Clock algorithm arranges page frames in a circular buffer with a sweeping hand. Each page has a hardware reference bit $R$:  
- If $R = 1$, the hand clears $R \leftarrow 0$ (giving a second chance) and advances.  
- If $R = 0$, the page has not been referenced since the last sweep and is immediately selected for eviction.  
This approximates Least Recently Used without requiring expensive doubly linked list pointer updates on every memory hit.

### Q1.10
**Question:** What causes the vanishing gradient problem when training deep neural networks with Sigmoid activation functions?  
**Marking Scheme:** 1 mark for maximum derivative value ($\le 0.25$), 1 mark for repeated multiplication across layers.  
**Model Solution:**  
The derivative of the Sigmoid function $\sigma(z) = \frac{1}{1 + e^{-z}}$ is $\sigma'(z) = \sigma(z)(1 - \sigma(z))$, whose maximum value is $0.25$ (at $z = 0$). In backpropagation through $L$ layers, gradients are multiplied: $\prod_{l=1}^L W_l \sigma'(z_l)$. Since $\sigma'(z) \le 0.25$, gradients decay exponentially towards zero ($0.25^L \to 0$), freezing weight updates in early layers.

---

## SECTION B: Analytical & Algorithmic Foundations (Answer any FOUR — 4 × 10 Marks = 40 Marks)

### Q2. Compiler Construction: LR(1) Parser Table & Conflicts (10 Marks)
**Sub-questions:**
Given the grammar:
1. $S \to A$
2. $A \to A + A$
3. $A \to \text{id}$
(a) Construct the augmented grammar and canonical LR(0) collection of items. (4 Marks)  
(b) Identify the shift-reduce conflict in state $I_k$ containing $\{A \to A + A \cdot, \; A \to A \cdot + A\}$. Explain how operator precedence and associativity rules resolve this conflict for left-associative addition. (6 Marks)

**Marking Scheme & Model Solution:**  
**(a) Augmented Grammar & LR(0) Items:**  
Augmented grammar:  
0. $S' \to S \$$  
1. $S \to A$  
2. $A \to A + A$  
3. $A \to \text{id}$  

Item Sets:  
- $I_0 = \text{CLOSURE}(\{S' \to \cdot S \$\}) = \{S' \to \cdot S \$, \; S \to \cdot A, \; A \to \cdot A + A, \; A \to \cdot \text{id}\}$  
- $\text{GOTO}(I_0, S) = I_1 = \{S' \to S \cdot \$\}$  
- $\text{GOTO}(I_0, A) = I_2 = \{S \to A \cdot, \; A \to A \cdot + A\}$  
- $\text{GOTO}(I_0, \text{id}) = I_3 = \{A \to \text{id} \cdot\}$  
- $\text{GOTO}(I_2, +) = I_4 = \text{CLOSURE}(\{A \to A + \cdot A\}) = \{A \to A + \cdot A, \; A \to \cdot A + A, \; A \to \cdot \text{id}\}$  
- $\text{GOTO}(I_4, A) = I_5 = \{A \to A + A \cdot, \; A \to A \cdot + A\}$  

**(b) Shift-Reduce Conflict in $I_5$:**  
- In state $I_5$:  
  - Item $A \to A + A \cdot$ prescribes a **REDUCE** action by production 2 ($A \to A + A$).  
  - Item $A \to A \cdot + A$ prescribes a **SHIFT** action when lookahead is $+$.  
- **Conflict:** When the parser is in state $I_5$ and sees lookahead token $+$, it cannot decide whether to reduce $A + A$ or shift $+$ onto the stack.  
- **Disambiguation via Associativity:**  
  - For string `id + id + id`, if addition is **left-associative** (`(id + id) + id`), the first `id + id` must be reduced before shifting the second `+`.  
  - Precedence rule: We assign operator $+$ left-associativity. In conflict state $I_5$ with lookahead $+$, the parser favors **REDUCE** over SHIFT, generating parse tree `(A + A) + A`. (If right-associative, SHIFT would be chosen).

---

### Q3. Database Engine: MVCC Snapshot Isolation & Write Skew (10 Marks)
**Sub-questions:**
(a) Define Snapshot Isolation (SI) using transaction start timestamps $T_{start}$ and commit timestamps $T_{commit}$. Explain the First-Committer-Wins rule. (4 Marks)  
(b) Detail the classic "Doctors on Call" Write Skew anomaly under Snapshot Isolation with a step-by-step transaction timeline diagram. Prove why Snapshot Isolation does not guarantee Serializability in this scenario. (6 Marks)

**Marking Scheme & Model Solution:**  
**(a) Snapshot Isolation Semantics:**  
- When transaction $T_i$ starts, it is assigned timestamp $T_{start}$. $T_i$ reads a consistent snapshot of the database containing all versions committed prior to $T_{start}$. Modifications made by concurrent transactions active after $T_{start}$ are invisible.  
- **First-Committer-Wins (Write-Write Conflict Resolution):** If $T_i$ attempts to commit updates to item $X$, and a concurrent transaction $T_j$ has committed an update to $X$ after $T_{start}(T_i)$, $T_i$ must abort (preventing lost updates).

**(b) Doctors on Call Write Skew Anomaly:**  
- **Integrity Constraint:** At least one doctor must be on call at all times ($\sum \text{on\_call} \ge 1$).  
- **Initial State:** Dr. Alice (`on_call = true`), Dr. Bob (`on_call = true`). Count = 2.  
```text
Time    Transaction T1 (Dr. Alice)              Transaction T2 (Dr. Bob)
-----------------------------------------------------------------------------------
t1      BEGIN (T_start = 10)                    
t2                                              BEGIN (T_start = 12)
t3      SELECT count(*) WHERE on_call=true;     
        -> Returns 2 (Valid to take off)
t4                                              SELECT count(*) WHERE on_call=true;
                                                -> Returns 2 (Valid to take off)
t5      UPDATE doctors SET on_call=false        
        WHERE name = 'Alice';
t6                                              UPDATE doctors SET on_call=false
                                                WHERE name = 'Bob';
t7      COMMIT (T_commit = 15)                  
        -> Succeeds! Alice off call.
t8                                              COMMIT (T_commit = 16)
                                                -> Succeeds! Bob off call.
-----------------------------------------------------------------------------------
Final State: Alice: false, Bob: false. Count = 0 (VIOLATES INVARIANT!)
```
- **Proof of Non-Serializability:**  
  - $T_1$ modified record `Alice`; $T_2$ modified record `Bob`.  
  - Since their write sets are disjoint ($\text{WriteSet}(T_1) \cap \text{WriteSet}(T_2) = \emptyset$), the First-Committer-Wins check passes without aborting either transaction!  
  - In dependency serialization graph, $T_1$ reads state before $T_2$'s write ($T_1 \to T_2$ anti-dependency $rw$), and $T_2$ reads state before $T_1$'s write ($T_2 \to T_1$ anti-dependency $rw$). This forms a cycle $T_1 \rightleftarrows T_2$, proving the execution is **not serializable**.

---

### Q4. Distributed Systems: Raft Leader Election & Failover (10 Marks)
**Sub-questions:**
(a) Write the state transition function of a Raft node between Follower, Candidate, and Leader. Detail conditions for role elevation and demotion. (4 Marks)  
(b) Assume a 5-node cluster $\{S_1, S_2, S_3, S_4, S_5\}$. Leader $S_1$ suffers a network partition isolating $\{S_1, S_2\}$ from $\{S_3, S_4, S_5\}$. Trace the election of a new leader in the majority partition and what happens when the partition heals. (6 Marks)

**Marking Scheme & Model Solution:**  
**(a) State Transition Function:**
```
                     +----------------------------+
                     |                            |
       Timeout       v       Majority Votes       |
[Follower] -----> [Candidate] ------------> [Leader]
    ^                 |                           |
    |                 | Higher Term               | Higher Term
    +-----------------+---------------------------+
```
- **Follower $\to$ Candidate:** Election timeout expires without heartbeat from Leader or candidate vote. Increments `currentTerm`, votes for self, resets timer, sends `RequestVote(term, candidateId, lastLogIndex, lastLogTerm)`.  
- **Candidate $\to$ Leader:** Receives affirmative votes from majority of cluster ($\lfloor N/2 \rfloor + 1$). Sends immediate empty `AppendEntries` heartbeats.  
- **Leader / Candidate $\to$ Follower:** Receives RPC (`AppendEntries` or `RequestVote`) with `term > currentTerm`. Updates `currentTerm = RPC.term` and reverts to Follower.

**(b) Network Partition Trace (5 Nodes):**  
- **Partition:** Partition 1 = $\{S_1, S_2\}$ (Minority), Partition 2 = $\{S_3, S_4, S_5\}$ (Majority).
1. **Minority Partition $\{S_1, S_2\}$:** $S_1$ remains leader in term $T$, but any client write cannot be committed because $S_1$ can only replicate to $S_2$ ($2/5 < 3$ majority quorum).
2. **Majority Partition $\{S_3, S_4, S_5\}$:** Heartbeats from $S_1$ stop. Election timer expires on $S_3$.  
   $S_3$ increments term to $T+1$, votes for self, sends `RequestVote` to $S_4, S_5$.  
   $S_4$ and $S_5$ grant votes (since $S_3$'s log is up-to-date). $S_3$ collects 3 votes ($3/5$ majority) and becomes **Leader for Term $T+1$**. Client writes to $S_3$ successfully commit.
3. **Partition Heals:** Network connectivity restored.  
   $S_3$ sends `AppendEntries(term = T+1)` to $S_1$.  
   $S_1$ observes incoming `term = T+1 > currentTerm = T`.  
   $S_1$ immediately **steps down to Follower**, updates term to $T+1$. Any uncommitted log entries on $S_1, S_2$ from term $T$ are overwritten by $S_3$'s canonical log entries matching the leader's indices.

---

### Q5. Machine Learning: Rigorous Backpropagation Derivation (10 Marks)
**Sub-questions:**
For a 2-layer neural network with input $x \in \mathbb{R}^d$, hidden layer $h = \text{ReLU}(W_1 x + b_1) \in \mathbb{R}^m$, output logits $z = W_2 h + b_2 \in \mathbb{R}^k$, softmax probabilities $\hat{y} = \text{softmax}(z)$, and cross-entropy loss $\mathcal{L} = -\sum_{i=1}^k y_i \log \hat{y}_i$:
(a) Derive analytically the gradient $\frac{\partial \mathcal{L}}{\partial z_i}$ with respect to logit $z_i$. (5 Marks)  
(b) Derive the gradients $\frac{\partial \mathcal{L}}{\partial W_2}$ and $\frac{\partial \mathcal{L}}{\partial W_1}$ using matrix calculus. (5 Marks)

**Marking Scheme & Model Solution:**  
**(a) Softmax + Cross-Entropy Loss Gradient:**  
Let $\hat{y}_i = \frac{e^{z_i}}{\sum_{j=1}^k e^{z_j}}$.  
Derivative of softmax $\frac{\partial \hat{y}_c}{\partial z_i}$:  
- If $c = i$: $\frac{\partial \hat{y}_i}{\partial z_i} = \hat{y}_i (1 - \hat{y}_i)$  
- If $c \ne i$: $\frac{\partial \hat{y}_c}{\partial z_i} = -\hat{y}_c \hat{y}_i$  

Now differentiate $\mathcal{L} = -\sum_{c=1}^k y_c \log \hat{y}_c$ using chain rule:  
$$\frac{\partial \mathcal{L}}{\partial z_i} = -\sum_{c=1}^k \frac{y_c}{\hat{y}_c} \frac{\partial \hat{y}_c}{\partial z_i} = -\frac{y_i}{\hat{y}_i} \hat{y}_i (1 - \hat{y}_i) - \sum_{c \ne i} \frac{y_c}{\hat{y}_c} (-\hat{y}_c \hat{y}_i)$$  
$$= -y_i (1 - \hat{y}_i) + \sum_{c \ne i} y_c \hat{y}_i = -y_i + y_i \hat{y}_i + \hat{y}_i \sum_{c \ne i} y_c = -y_i + \hat{y}_i \left( \sum_{c=1}^k y_c \right)$$  
Since target $y$ is a one-hot distribution, $\sum_{c=1}^k y_c = 1$. Therefore:  
$$\frac{\partial \mathcal{L}}{\partial z} = \hat{y} - y$$

**(b) Layer Gradients via Matrix Calculus:**  
Let $\delta_2 = \frac{\partial \mathcal{L}}{\partial z} = (\hat{y} - y) \in \mathbb{R}^k$.  
1. **Output weights $W_2$ ($z = W_2 h + b_2$):**  
   $$\frac{\partial \mathcal{L}}{\partial W_2} = \delta_2 h^T \in \mathbb{R}^{k \times m}, \quad \frac{\partial \mathcal{L}}{\partial b_2} = \delta_2 \in \mathbb{R}^k$$  
2. **Hidden layer backpropagation:**  
   $$\frac{\partial \mathcal{L}}{\partial h} = W_2^T \delta_2 \in \mathbb{R}^m$$  
   For $a_1 = W_1 x + b_1$ and $h = \text{ReLU}(a_1)$:  
   $$\delta_1 = \frac{\partial \mathcal{L}}{\partial a_1} = \left( W_2^T \delta_2 \right) \odot \mathbb{I}(a_1 > 0)$$  
   where $\odot$ denotes element-wise Hadamard product and $\mathbb{I}$ is the indicator step function.  
3. **Input weights $W_1$:**  
   $$\frac{\partial \mathcal{L}}{\partial W_1} = \delta_1 x^T \in \mathbb{R}^{m \times d}, \quad \frac{\partial \mathcal{L}}{\partial b_1} = \delta_1 \in \mathbb{R}^m$$

---

## SECTION C: Comprehensive System Design & Derivation (Answer any TWO — 2 × 20 Marks = 40 Marks)

### Q6. ARIES Transaction Recovery Engine Architecture (20 Marks)
**Problem Statement:** You are designing the crash recovery subsystem for a transactional relational DBMS based on the ARIES (Algorithms for Recovery and Isolation Exploiting Semantics) protocol.
1. Define the roles and structures of the **Log Sequence Number (LSN)**, **Transaction Table (TT)**, and **Dirty Page Table (DPT)** with `recLSN`. (5 Marks)
2. Trace the **Three Recovery Phases**:
   - **Phase 1: Analysis** (from last checkpoint forward to end of log).
   - **Phase 2: Redo (Repeating History)** (from smallest `recLSN` forward to end of log).
   - **Phase 3: Undo** (backward rollback of loser transactions). (8 Marks)
3. Detail the exact purpose and structure of **Compensation Log Records (CLRs)**. Explain with an ASCII timeline how CLRs prevent infinite loops during crashes that occur during recovery. (7 Marks)

**Marking Scheme & Model Solution:**  
**(1) Data Structures & LSN Invariants:**  
- **LSN (Log Sequence Number):** Monotonically increasing 64-bit integer uniquely identifying every log record on disk.  
- **`pageLSN`:** Embedded in each data page header; records the LSN of the most recent log record that updated that page.  
- **Transaction Table (TT):** Tracks active transactions at crash time. Schema: `{TransID, Status (Running/Committing/Aborted), LastLSN}`.  
- **Dirty Page Table (DPT):** Tracks pages modified in memory but not yet written to disk. Schema: `{PageID, recLSN}`.  
  - **`recLSN`:** The LSN of the oldest log record that dirtied the page since it was last flushed to disk. It defines the exact lower bound where Redo must start.

**(2) Three Recovery Phases:**  
1. **Analysis Phase:**  
   - Scans log forward starting from the `CHECKPOINT_BEGIN` record up to the end of the log.  
   - Reconstructs TT and DPT:  
     - If an `UPDATE` record is found for page $P$: if $P \notin \text{DPT}$, insert $(P, \text{LSN})$. Update $\text{LastLSN}$ in TT.  
     - If a `COMMIT` record is found: set status = COMMITTED in TT.  
     - If an `END` record is found: remove transaction from TT.  
   - Output: Final active "Loser Transactions" (TT entries not committed) and minimum `recLSN` in DPT.  
2. **Redo Phase (Repeating History):**  
   - Scans log forward starting from $\min_{P \in \text{DPT}}(\text{recLSN})$ to the end of the log.  
   - Re-applies all logged changes (for both winners and losers) to restore exact pre-crash buffer state.  
   - **Redo optimization check:** Page $P$ need NOT be read or re-applied if:  
     1. Page $P$ is not in DPT, or  
     2. $\text{LSN} < \text{recLSN}$ for $P$ in DPT, or  
     3. Disk page read reveals $\text{pageLSN} \ge \text{LSN}$.  
3. **Undo Phase:**  
   - Scans backward through log, rolling back active loser transactions in TT simultaneously.  
   - Uses a max-heap of `{LastLSN}` for all loser transactions to always process the highest LSN across losers first.  
   - Undoes each update, flushes a Compensation Log Record (CLR), and updates `UndoNextLSN`.

**(3) Compensation Log Records (CLRs) & Crash During Recovery:**  
- **Structure:** `CLR = {LSN, TransID, Type = CLR, PageID, RedoInfo, UndoNextLSN}`.  
- `UndoNextLSN` points directly to the `PrevLSN` of the record currently being undone, completely skipping already undone operations.
```
Original Execution:
LSN 10: T1 modifies P1 (PrevLSN = 0)
LSN 20: T1 modifies P2 (PrevLSN = 10)
--- CRASH 1 ---

Recovery Attempt 1:
Undo LSN 20: Reverses update on P2.
Writes LSN 30: CLR for LSN 20 (UndoNextLSN = 10)
--- CRASH 2 during recovery! ---

Recovery Attempt 2:
Analysis: Sees T1 active, LastLSN = 30.
Redo: Replays LSN 10, 20, 30.
Undo:
Reads LSN 30 (CLR). Since it is a CLR, it DOES NOT undo it again!
Instead, it immediately jumps to UndoNextLSN = 10!
Undoes LSN 10, writes LSN 40: CLR for LSN 10 (UndoNextLSN = 0).
Writes LSN 50: END record for T1. Recovery finishes!
```
**Conclusion:** Without CLRs and `UndoNextLSN`, a system that crashes repeatedly during recovery could log endless undo operations, resulting in an infinite crash-recovery loop.

---

### Q7. High-Performance Asynchronous I/O: epoll vs io_uring (20 Marks)
**Problem Statement:** Design a high-throughput network event loop serving 1,000,000 concurrent TCP sockets on Linux.
1. Compare the architecture and system call mechanics of `epoll` (readiness notification) versus `io_uring` (completion ring buffer). (6 Marks)
2. Detail the memory-mapped Submission Queue (SQ) and Completion Queue (CQ) architecture of `io_uring`. Show how user-space and kernel share these ring buffers without copying. (6 Marks)
3. Explain why `io_uring` eliminates system call overhead using SQPOLL (Submission Queue Polling kernel thread). (4 Marks)
4. Write a C11/POSIX code snippet setting up an `io_uring` instance and submitting an asynchronous non-blocking vectorized read (`IORING_OP_READV`). (4 Marks)

**Marking Scheme & Model Solution:**  
**(1) Architectural Comparison:**  
- **`epoll` (Readiness Notification):** Reactor pattern. `epoll_wait` tells the application *when* a file descriptor is ready to be read/written. The application must then execute a subsequent synchronous `read()` or `write()` system call, requiring 2 system calls and 2 context switches per I/O transaction.  
- **`io_uring` (Completion Ring Buffer):** Proactor pattern. The application submits an asynchronous read/write request directly into a shared ring buffer. The kernel executes the I/O asynchronously and deposits the completed result into a completion ring buffer. Zero extra system calls required for execution.

**(2) Memory-Mapped SQ and CQ Ring Buffer Architecture:**
```
USER SPACE                                    KERNEL SPACE
+---------------------------+                 +---------------------------+
| Application Memory Buffer | <============== | Direct DMA from NIC/Disk  |
+---------------------------+   Zero-Copy     +---------------------------+
             |
             v
+-------------------------------------------------------------------------+
|                  Shared Memory-Mapped Region (mmap)                     |
|                                                                         |
|  Submission Queue (SQ) Ring:                                            |
|  [Head (Kernel Read)] ---> [Entries (SQEs)] ---> [Tail (User Write)]     |
|                                                                         |
|  Completion Queue (CQ) Ring:                                            |
|  [Head (User Read)]   ---> [Entries (CQEs)] ---> [Tail (Kernel Write)]    |
+-------------------------------------------------------------------------+
```
- Both SQ and CQ are allocated by kernel memory and mapped into the application process via `mmap()`.  
- **Lock-Free Concurrency:** Single producer / single consumer semantics using atomic index variables (`head` and `tail`). The user thread updates `sq->tail` after writing an entry; the kernel advances `sq->head` upon consuming it.

**(3) SQPOLL Kernel Thread Mode:**  
In standard mode, submitting entries requires calling `io_uring_enter()`. With `IORING_SETUP_SQPOLL`, the kernel spawns a dedicated kernel thread (`io_uring-sq`) that continuously polls the SQ ring tail. When the application writes new SQEs, the kernel thread detects them instantly and processes the I/O **without the application making any system calls whatsoever (0 sys-calls, 0 context switches)**.

**(4) io_uring Setup & Submission in C11:**
```c
#include <linux/io_uring.h>
#include <sys/syscall.h>
#include <sys/mman.h>
#include <unistd.h>
#include <string.h>
#include <stdint.h>

struct io_uring_sq {
    uint32_t *khead, *ktail, *kring_mask, *kflags, *array;
    struct io_uring_sqe *sqes;
};

// Simplified system call wrapper
int io_uring_setup(unsigned entries, struct io_uring_params *p) {
    return (int)syscall(__NR_io_uring_setup, entries, p);
}

int io_uring_enter(int fd, unsigned to_submit, unsigned min_complete, unsigned flags) {
    return (int)syscall(__NR_io_uring_enter, fd, to_submit, min_complete, flags, NULL, 0);
}

void submit_async_read(int ring_fd, struct io_uring_sq *sq, int socket_fd, void *buf, size_t len) {
    uint32_t tail = *sq->ktail;
    uint32_t index = tail & *sq->kring_mask;
    struct io_uring_sqe *sqe = &sq->sqes[index];

    memset(sqe, 0, sizeof(*sqe));
    sqe->opcode = IORING_OP_READ;
    sqe->fd = socket_fd;
    sqe->addr = (uint64_t)buf;
    sqe->len = (uint32_t)len;
    sqe->user_data = (uint64_t)socket_fd; // Tracking context

    sq->array[index] = index;
    __atomic_store_n(sq->ktail, tail + 1, __ATOMIC_RELEASE);

    // Notify kernel of 1 submitted event
    io_uring_enter(ring_fd, 1, 0, 0);
}
```

---

### Q8. Distributed Partitioned Storage Engine Design (20 Marks)
**Problem Statement:** Design a Dynamo-style decentralized, horizontally scalable distributed key-value store.
1. Formulate the **Consistent Hashing** ring topology with Virtual Nodes ($V$). Prove mathematically how virtual nodes bound data distribution variance across heterogeneous physical nodes. (6 Marks)
2. Detail the **SWIM Gossip Protocol** for failure detection using ping-req indirect probing. Explain why it achieves $O(1)$ network load per node. (6 Marks)
3. Explain multi-master replication with Sloppy Quorums ($N, R, W$) and Hinted Handoff. Show how concurrent diverging writes are tracked via Vector Clocks. (4 Marks)
4. Detail background **Anti-Entropy Synchronization using Merkle Trees**. Prove why Merkle trees detect range discrepancies in $O(\log S)$ network exchanges. (4 Marks)

**Marking Scheme & Model Solution:**  
**(1) Consistent Hashing & Virtual Nodes:**  
- The key space is mapped to a circular integer continuum $[0, 2^{128}-1]$ using MD5 or MurmurHash3.  
- Each physical node $p_i$ is mapped to $V$ virtual positions: $H(p_i \parallel 1), H(p_i \parallel 2), \dots, H(p_i \parallel V)$.  
- A key $k$ is stored on the first node encountered by scanning clockwise from $H(k)$.  
- **Variance Bound:** With 1 token per node, load varies by up to $O(\log N)$. With $V$ virtual nodes, by the Chernoff bound, the probability that any node receives load exceeding $(1+\epsilon)\bar{L}$ decays exponentially:  
  $$P(|L_i - \bar{L}| \ge \epsilon \bar{L}) \le 2e^{-\frac{\epsilon^2 V}{3}}$$  
  Setting $V \approx 100-250$ ensures maximum load imbalance across all nodes is bounded within $< 5\%$.

**(2) SWIM Failure Detection Protocol (Structured Weak-Consistency Infection-Style):**
```
   [Node A] ----------------- Direct Ping -----------------> [Target Node B] (Times out!)
      |
      +--- Ping-Req(B) ---> [Node C] --- Ping ---> [Node B]
      |
      +--- Ping-Req(B) ---> [Node D] --- Ping ---> [Node B]
```
1. Node $A$ randomly selects target $B$ from its membership list and sends `Ping`.  
2. If $B$ fails to reply within timeout $t_{ack}$, $A$ selects $k$ random peer nodes $\{C, D\}$ and sends `Ping-Req(B)`.  
3. Peers attempt to ping $B$ via alternate routes. If none succeed within $t_{indirect}$, $A$ declares $B$ `Suspect`.  
4. `Suspect` status is gossiped with an expiry timer. If $B$ does not refute within the timeout, it is marked `Dead`.  
- **$O(1)$ Load:** Each node periodically contacts a constant number ($1 + k$) of nodes per interval $T$. The probe rate per node is completely independent of total cluster size $N$.

**(3) Sloppy Quorum, Hinted Handoff & Vector Clocks:**  
- **Sloppy Quorum ($N=3, R=2, W=2$):** Quorum condition $R + W > N$ ensures read and write sets intersect in at least one up-to-date node. Under node failure, writes are accepted by the next healthy node on the ring with a `Hinted Handoff` tag, to be forwarded back when the primary recovers.  
- **Vector Clocks:** Key update carries $VC = \{N_1: v_1, N_2: v_2, \dots\}$. Divergent sibling branches ($VC_A \not< VC_B \land VC_B \not< VC_A$) are preserved and returned to the client application for domain-level conflict reconciliation (e.g. shopping cart union).

**(4) Anti-Entropy with Merkle Trees:**  
- Each node maintains a binary Merkle tree over key-value hashes in its designated key ranges. Internal nodes contain hashes of their children: $\text{Node} = H(\text{Left} \parallel \text{Right})$.  
- During synchronization between replicas $R_1$ and $R_2$:  
  1. $R_1$ and $R_2$ exchange the root hash ($O(1)$ network exchange). If roots match, replicas are 100% identical; sync terminates immediately.  
  2. If root hashes differ, they exchange children hashes. Traversal descends only along divergent tree branches.  
  - For $S$ keys partitioned into $M$ leaf buckets, locating differing key buckets requires traversing depth $\log_2 M$, sending only $2 \log_2 M$ hashes instead of transmitting millions of keys across the network.
