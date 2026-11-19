# University End-Semester Examination: Advanced Engineering, Formal Methods & Research (Levels 7–9)

**Course Codes:** CS701 / CS801 / CS901 (Site Reliability, Formal Verification, Distributed Systems, Type Theory, Cryptography)  
**Applicable Degrees:** B.Tech SE, BESE, MCS, MCA, M.Tech SE, MESE, Ph.D. Preparatory  
**Duration:** 3 Hours (180 Minutes)  
**Maximum Marks:** 100  
**Instructions:**
1. All questions in Section A are compulsory (20 Marks).
2. Answer any **four** questions from Section B (40 Marks).
3. Answer any **two** questions from Section C (40 Marks).
4. Mathematical proofs, formal logic derivations, and architectural specifications carry explicit marks.
5. All code and logic formalisms must adhere to rigorous academic and engineering standards.

---

## SECTION A: Objective & Conceptual Advanced Foundations (Compulsory — 10 × 2 Marks = 20 Marks)

### Q1.1
**Question:** Explain the mathematical principle of Multi-Window Multi-Burn-Rate alerting in Google Site Reliability Engineering (SRE).  
**Marking Scheme:** 1 mark for burn rate formula, 1 mark for dual-window false-alarm suppression.  
**Model Solution:**  
Burn rate $B$ is the rate at which an error budget is consumed relative to its SLO: $B = 1$ exhausts $100\%$ budget in the full period $T$ (e.g. 30 days). A burn rate $B = 14.4$ exhausts $2\%$ of the budget in 1 hour. Multi-window alerting pairs a short window (e.g. 5 minutes) with a long window (e.g. 1 hour), firing an alert only if *both* windows exceed the burn rate threshold. This ensures immediate alerting for catastrophic sustained outages while preventing transient short bursts from triggering high-priority on-call pages.

### Q1.2
**Question:** Define False Sharing in symmetric multiprocessing (SMP) and state how compiler/cache alignment directives resolve it.  
**Marking Scheme:** 1 mark for cache line ping-pong explanation, 1 mark for cache-line alignment remedy.  
**Model Solution:**  
False sharing occurs when two independent variables accessed concurrently by distinct CPU cores reside within the same 64-byte L1 cache line. Although cores operate on distinct memory addresses, writes trigger MESI/MOESI cache invalidations across the interconnect, ping-ponging the cache line between cores and degrading throughput. It is eliminated by padding variables with compiler attributes (e.g. `alignas(64)` or `__attribute__((aligned(64)))`) to isolate variables into distinct cache lines.

### Q1.3
**Question:** Contrast Partial Correctness ($\{P\} C \{Q\}$) with Total Correctness ($[P] C [Q]$) in Hoare Logic.  
**Marking Scheme:** 1 mark for partial correctness definition, 1 mark for termination requirement in total correctness.  
**Model Solution:**  
- **Partial Correctness ($\{P\} C \{Q\}$):** If precondition $P$ holds before executing command $C$, and if execution of $C$ terminates, then postcondition $Q$ will hold upon termination. It provides no guarantee that $C$ will ever terminate (e.g., infinite loops vacuously satisfy partial correctness).  
- **Total Correctness ($[P] C [Q]$):** If precondition $P$ holds before executing $C$, then execution of $C$ is mathematically guaranteed to terminate, and postcondition $Q$ will hold upon termination ($[P] C [Q] \iff \{P\} C \{Q\} \land \text{Terminates}(C, P)$).

### Q1.4
**Question:** What is the TrueTime API uncertainty bound in Google Spanner, and how does the Commit-Wait protocol enforce external consistency?  
**Marking Scheme:** 1 mark for TrueTime interval $[t.\text{earliest}, t.\text{latest}]$, 1 mark for commit-wait duration $2\epsilon$.  
**Model Solution:**  
TrueTime returns a time interval $TT.now() = [t_{earliest}, t_{latest}]$ where $t_{latest} - t_{earliest} = 2\epsilon$ ($\epsilon \approx 1-7\text{ ms}$ via GPS and atomic clocks). To enforce external consistency (linearizability), Spanner's Commit-Wait rule requires a transaction leader to pick a commit timestamp $s \ge TT.now().latest$ and wait out the uncertainty window (delaying client ACK until $TT.now().earliest > s$). This guarantees that any subsequent transaction $T_2$ starts at timestamp $s_2 > s_1$.

### Q1.5
**Question:** In substructural type systems, define the three structural rules: Exchange, Weakening, and Contraction.  
**Marking Scheme:** 1 mark for Weakening and Contraction definitions, 1 mark for Linear type classification.  
**Model Solution:**  
- **Exchange:** Reordering hypotheses in context ($\Gamma, x:A, y:B \vdash C \implies \Gamma, y:B, x:A \vdash C$).  
- **Weakening:** Discarding unused variables without consumption ($\Gamma \vdash C \implies \Gamma, x:A \vdash C$).  
- **Contraction:** Duplicating a variable multiple times ($\Gamma, x:A, y:A \vdash C \implies \Gamma, z:A \vdash C[z/x, z/y]$).  
A **Linear Type System** drops both Weakening and Contraction, requiring every value to be consumed *exactly once*. An **Affine Type System** drops Contraction, permitting values to be used *at most once*.

### Q1.6
**Question:** State the Curry-Howard Isomorphism correspondence for: Propositions, Proofs, Implication ($A \to B$), and Conjunction ($A \land B$).  
**Marking Scheme:** 0.5 marks per correctly mapped concept (total 2 marks).  
**Model Solution:**  
- **Proposition:** Type $A$  
- **Proof:** Program / Term $t$ of type $A$ ($t: A$)  
- **Implication ($A \to B$):** Function type $A \to B$ (takes an argument of type $A$ and returns type $B$)  
- **Conjunction ($A \land B$):** Product type / Pair $(A, B)$ (a term containing evidence for both $A$ and $B$)

### Q1.7
**Question:** State the Schwartz-Zippel Lemma and explain its role in Zero-Knowledge succinct arguments.  
**Marking Scheme:** 1 mark for lemma bound, 1 mark for polynomial identity check reduction.  
**Model Solution:**  
Let $P(x_1, \dots, x_m)$ be a non-zero polynomial of total degree $d$ over field $\mathbb{F}$. For any finite subset $S \subseteq \mathbb{F}$ with values $r_1, \dots, r_m$ chosen independently and uniformly at random from $S$:  
$$\Pr[P(r_1, \dots, r_m) = 0] \le \frac{d}{|S|}$$  
In ZKPs, checking whether two high-degree polynomials $A(x)B(x) = C(x)$ are identical across all inputs is reduced to evaluating them at a single secret random point $\tau$. If $|S| \approx 2^{256}$, the probability of an invalid proof falsely evaluating to zero is negligible ($\le d/2^{256} \approx 0$).

### Q1.8
**Question:** Express an arithmetic gate $z = x \cdot y$ as a Rank-1 Constraint System (R1CS) equation: $(A \cdot s) \cdot (B \cdot s) - (C \cdot s) = 0$.  
**Marking Scheme:** 1 mark for witness vector layout, 1 mark for linear combination vectors A, B, C.  
**Model Solution:**  
Let witness vector $s = [1, x, y, z]^T$.  
We define row vectors:  
- $A = [0, 1, 0, 0]$ (selects $x$: $A \cdot s = x$)  
- $B = [0, 0, 1, 0]$ (selects $y$: $B \cdot s = y$)  
- $C = [0, 0, 0, 1]$ (selects $z$: $C \cdot s = z$)  
Then: $(A \cdot s) \cdot (B \cdot s) - (C \cdot s) = x \cdot y - z = 0$, satisfying the R1CS constraint.

### Q1.9
**Question:** Explain the microarchitectural vulnerability exploited in Spectre Variant 1 (Bounds Check Bypass).  
**Marking Scheme:** 1 mark for branch prediction speculation, 1 mark for cache line side-channel footprint.  
**Model Solution:**  
Spectre v1 targets code like `if (x < array1_size) y = array2[array1[x] * 512];`. The attacker trains the branch predictor to expect $x < \text{size}$. Then an out-of-bounds index $x_{secret}$ is passed. The CPU speculatively executes the condition, reading secret memory byte $S = \text{array1}[x_{secret}]$ and fetching $\text{array2}[S \times 512]$ into L1 cache before the misprediction is detected and squashed. The attacker then probes $\text{array2}[k \times 512]$ access latencies using `Flush+Reload`; the single cache hit reveals secret byte $S$.

### Q1.10
**Question:** How does the Black-Scholes financial option pricing formula translate conceptually to technical debt remediation?  
**Marking Scheme:** 1 mark for principal vs interest volatility mapping, 1 mark for real options valuation.  
**Model Solution:**  
In financial options, Black-Scholes values the option to take action under market uncertainty. Refactoring technical debt is modeled as purchasing a "Call Option" to rewrite or expand an architecture in the future. The debt principal is the immediate engineering cost to refactor; the debt interest is the continuous overhead on feature velocity. High architectural volatility ($\sigma$) increases the option value of delaying complete rewrites while modularizing interfaces.

---

## SECTION B: Analytical & Algorithmic Foundations (Answer any FOUR — 4 × 10 Marks = 40 Marks)

### Q2. Site Reliability Engineering: Multi-Window Multi-Burn Rate Design (10 Marks)
**Sub-questions:**
(a) For a service with a 30-day rolling SLO of 99.9% availability, compute:
1. Total allowable downtime in minutes over 30 days. (2 Marks)
2. The burn rate $B$ that exhausts 5% of the total budget in a 1-hour window. (3 Marks)
(b) Design an end-to-end Prometheus alerting rule implementation for a multi-window multi-burn-rate alert covering both a 1-hour window ($B = 14.4$) and a 5-minute window ($B = 14.4$). Explain why both must evaluate to true. (5 Marks)

**Marking Scheme & Model Solution:**  
**(a) Budget and Burn Rate Derivations:**  
1. **Total Allowable Downtime:**  
   $$\text{Budget} = 1 - 0.999 = 0.001 = 0.1\%$$  
   $$\text{Total Time} = 30 \text{ days} \times 24 \frac{\text{hours}}{\text{day}} \times 60 \frac{\text{minutes}}{\text{hour}} = 43,200 \text{ minutes}$$  
   $$\text{Allowable Downtime} = 43,200 \times 0.001 = 43.2 \text{ minutes} \quad (2,592 \text{ seconds})$$  
2. **Burn Rate for 5% Budget in 1 Hour:**  
   $$\text{Consumed Budget Fraction} = \frac{\text{Window Duration}}{\text{Total Period}} \times \text{Burn Rate}$$  
   $$0.05 = \frac{1 \text{ hour}}{720 \text{ hours}} \times B \implies B = 0.05 \times 720 = 36$$  
   *(Note: For $2\%$ consumption in 1 hour: $B = 0.02 \times 720 = 14.4$).*

**(b) Prometheus Alerting Rule Specification:**
```yaml
groups:
- name: SRE_SLO_Alerts
  rules:
  - alert: HighErrorRateBurnRate14x
    expr: |
      (
        sum(rate(http_requests_total{status=~"5.."}[1h])) 
        / 
        sum(rate(http_requests_total[1h])) 
        > (14.4 * 0.001)
      )
      and
      (
        sum(rate(http_requests_total{status=~"5.."}[5m])) 
        / 
        sum(rate(http_requests_total[5m])) 
        > (14.4 * 0.001)
      )
    for: 2m
    labels:
      severity: page
      tier: production
    annotations:
      summary: "Critical error budget burn: 14.4x consuming 2% budget in 1 hour"
      description: "Both 1-hour and 5-minute windows exceed 14.4x error budget burn rate."
```
**Rationale for Dual Windows:**  
If only the 1-hour window is checked, an alert continues paging the on-call engineer for 50 minutes after an incident is completely resolved until the error rate averages down. If only the 5-minute window is checked, a brief 30-second spike of 500 errors pages the engineer and self-resolves immediately (noisy false alarm). Requiring both to be active ensures immediate notification on severe sustained failures and instantaneous alert auto-resolution once the incident is mitigated.

---

### Q3. Formal Methods: Hoare Logic Verification of Binary Search (10 Marks)
**Sub-questions:**
Given the binary search algorithm over a sorted array $A[0..N-1]$ for target $x$:
```text
low = 0; high = N - 1; found = false;
while (low <= high and not found) {
    mid = low + (high - low) / 2;
    if (A[mid] == x) found = true;
    else if (A[mid] < x) low = mid + 1;
    else high = mid - 1;
}
```
(a) Formulate the Loop Invariant $I(low, high, found)$ and Precondition $P$. (4 Marks)  
(b) Formulate the Loop Termination Variant Function $V(low, high)$. Prove that $V$ decreases strictly monotonically on each iteration and is bounded below by 0. (3 Marks)  
(c) Prove using Hoare deduction rules that the postcondition $Q \equiv (found \implies A[mid] = x) \land (\neg found \implies \forall i \in [0, N-1], A[i] \ne x)$ holds upon loop exit. (3 Marks)

**Marking Scheme & Model Solution:**  
**(a) Precondition and Loop Invariant:**  
- **Precondition $P$:** $\forall i, j: 0 \le i \le j < N \implies A[i] \le A[j]$ (Array is sorted).  
- **Loop Invariant $I(low, high, found)$:**  
  $$I \equiv (0 \le low \le high + 1 \le N) \land (found \implies A[mid] = x) \land (\neg found \implies (\forall i < low: A[i] < x \land \forall i > high: A[i] > x))$$  
  - *Initialization:* At entry, $low = 0, high = N-1$. Subarrays $i < 0$ and $i > N-1$ are empty, so the condition holds vacuously.

**(b) Variant Function & Termination Proof:**  
- Let variant function $V(low, high) = high - low + 1$.  
- The loop continues only when $low \le high$, so $V(low, high) \ge 1 > 0$.  
- On each iteration:  
  - If $A[mid] == x$: $found \leftarrow true$, loop terminates immediately.  
  - If $A[mid] < x$: $low' = mid + 1$. Since $mid = \lfloor \frac{low + high}{2} \rfloor \ge low$, $low' > low$.  
    $$V' = high - low' + 1 = high - (mid + 1) + 1 = high - mid < high - low + 1 = V$$  
  - If $A[mid] > x$: $high' = mid - 1$. Since $mid \le high$, $high' < high$.  
    $$V' = high' - low + 1 = (mid - 1) - low + 1 = mid - low < high - low + 1 = V$$  
  In all non-terminating branches, $V' \le V - 1$. Because $V$ is an integer strictly decreasing on every iteration and bounded below by 0, the loop must terminate in at most $\lceil \log_2 N \rceil + 1$ steps.

**(c) Postcondition Proof:**  
Upon loop termination, the exit condition is $(\neg (low \le high) \lor found) \equiv (low > high \lor found)$.  
- Case 1: $found == true$. By the invariant, $A[mid] = x$.  
- Case 2: $found == false \land low > high$. By the invariant, all elements with indices $i < low$ satisfy $A[i] < x$ and all elements with $i > high$ satisfy $A[i] > x$.  
  Since $low > high$, every index in the array $[0, N-1]$ falls either into $i \le high < low$ or $i \ge low > high$. Thus, $\forall i \in [0, N-1]: A[i] \ne x$. Postcondition $Q$ holds unconditionally.

---

### Q4. Lock-Free Data Structures & ABA Problem (10 Marks)
**Sub-questions:**
(a) Explain the Michael-Scott non-blocking queue enqueue algorithm with a pointer diagram. (4 Marks)  
(b) Detail the **ABA Problem** in lock-free CAS operations using a concurrent stack example. (3 Marks)  
(c) Demonstrate how Tagged Pointers (generation counters / versioned pointers) eliminate the ABA vulnerability. (3 Marks)

**Marking Scheme & Model Solution:**  
**(a) Michael-Scott Non-Blocking Queue Enqueue:**
```
Initial: Head ---> [Dummy Node] <--- Tail
                    next: NULL

Step 1: Create newNode with next = NULL.
Step 2: Read tail and tail->next in a loop.
Step 3: If tail->next == NULL, attempt CAS(&tail->next, NULL, newNode).
Step 4: If CAS succeeds, advance tail: CAS(&Tail, curTail, newNode).
Step 5: If tail->next != NULL (lagging tail), help advance tail: CAS(&Tail, curTail, tail->next).
```
The algorithm uses a dummy sentinel node and 2-step CAS. If an enqueuing thread stalls after swinging `tail->next`, concurrent threads detect that `tail->next != NULL` and proactively "help" swing the global `Tail` pointer before proceeding.

**(b) The ABA Problem:**  
Consider a Lock-Free Stack: Top points to $A \to B \to C$.  
1. Thread 1 attempts `pop()`. It reads `top = A` and `next = B`. Before executing `CAS(&top, A, B)`, Thread 1 is preempted.  
2. Thread 2 pops $A$ (`top` becomes $B$).  
3. Thread 2 pops $B$ (`top` becomes $C$).  
4. Thread 2 recycles memory node $A$ and pushes it back onto the stack: `top` becomes $A \to C$.  
5. Thread 1 resumes execution and executes `CAS(&top, A, B)`.  
   Because `top` currently equals $A$, the CAS **succeeds** and sets `top = B`!  
   **Catastrophe:** Node $B$ was already freed and contains dangling pointers or garbage. The stack is corrupted.

**(c) Elimination via Tagged Pointers:**  
We pack a 64-bit pointer and a 64-bit monotonically incrementing sequence counter into a 128-bit structure operated on via double-word CAS (`CMPXCHG16B` on x86_64):
```c
typedef struct TaggedPointer {
    Node* ptr;
    uintptr_t tag; // Generation counter
} TaggedPointer;
```
- In step 1: Thread 1 reads `(ptr: A, tag: 10)`.  
- After Thread 2 pops $A$, pops $B$, and pushes $A$ back: Top has pointer $A$, but `tag` has incremented to 13: `(ptr: A, tag: 13)`.  
- When Thread 1 executes `CAS(&top, (A, 10), (B, 11))`, the CAS fails because the tags do not match ($10 \ne 13$). The ABA race condition is completely prevented.

---

### Q5. Zero-Knowledge Proofs: Arithmetic Circuit to R1CS to QAP (10 Marks)
**Sub-questions:**
(a) For the polynomial relation $y = x^3 + x + 5$:
1. Decompose the computation into primitive arithmetic gates (multiplication and addition). (3 Marks)
2. Define the witness vector $s$ and construct the exact R1CS constraint matrices $A, B, C$ such that $(A \cdot s) \odot (B \cdot s) = (C \cdot s)$. (4 Marks)
(b) Explain how Lagrange interpolation converts the discrete R1CS constraints at evaluation points $\{r_1, r_2, r_3, \dots\}$ into continuous polynomial vectors $A(x), B(x), C(x)$ defining a Quadratic Arithmetic Program (QAP). (3 Marks)

**Marking Scheme & Model Solution:**  
**(a) Circuit Decomposition & R1CS Matrices:**  
1. Primitive Arithmetic Gates:
   - $v_1 = x \cdot x$ ($x^2$)
   - $v_2 = v_1 \cdot x$ ($x^3$)
   - $v_3 = v_2 + x$ ($x^3 + x$)
   - $y = v_3 + 5$ ($x^3 + x + 5$)  
   Converted to strictly multiplicative gates $(A_i \cdot s) \cdot (B_i \cdot s) = (C_i \cdot s)$:  
   - Gate 1: $x \cdot x = v_1$  
   - Gate 2: $v_1 \cdot x = v_2$  
   - Gate 3: $(v_2 + x) \cdot 1 = v_3$  
   - Gate 4: $(v_3 + 5) \cdot 1 = y$  

2. Witness Vector $s$:  
   $$s = [1, \; x, \; y, \; v_1, \; v_2, \; v_3]^T$$  
   Let indices be $0: 1, \; 1: x, \; 2: y, \; 3: v_1, \; 4: v_2, \; 5: v_3$.  
   - **Gate 1 ($x \cdot x = v_1$):**  
     $A_1 = [0, 1, 0, 0, 0, 0]$, $B_1 = [0, 1, 0, 0, 0, 0]$, $C_1 = [0, 0, 0, 1, 0, 0]$  
   - **Gate 2 ($v_1 \cdot x = v_2$):**  
     $A_2 = [0, 0, 0, 1, 0, 0]$, $B_2 = [0, 1, 0, 0, 0, 0]$, $C_2 = [0, 0, 0, 0, 1, 0]$  
   - **Gate 3 ($(v_2 + x) \cdot 1 = v_3$):**  
     $A_3 = [0, 1, 0, 0, 1, 0]$, $B_3 = [1, 0, 0, 0, 0, 0]$, $C_3 = [0, 0, 0, 0, 0, 1]$  
   - **Gate 4 ($(v_3 + 5) \cdot 1 = y$):**  
     $A_4 = [5, 0, 0, 0, 0, 1]$, $B_4 = [1, 0, 0, 0, 0, 0]$, $C_4 = [0, 0, 1, 0, 0, 0]$  

**(b) Quadratic Arithmetic Program (QAP) Formulation:**  
- Select distinct field evaluation points $\{r_1, r_2, r_3, r_4\} \subset \mathbb{F}$ (e.g. $1, 2, 3, 4$).  
- For each witness column $j \in [0, 5]$, use Lagrange interpolation to find polynomials $A_j(x), B_j(x), C_j(x)$ such that:  
  $$A_j(r_i) = A[i, j], \quad B_j(r_i) = B[i, j], \quad C_j(r_i) = C[i, j]$$  
- Combine with the witness vector:  
  $$A(x) = \sum_{j=0}^5 s_j A_j(x), \quad B(x) = \sum_{j=0}^5 s_j B_j(x), \quad C(x) = \sum_{j=0}^5 s_j C_j(x)$$  
- Let vanishing polynomial $T(x) = \prod_{i=1}^4 (x - r_i) = (x - 1)(x - 2)(x - 3)(x - 4)$.  
- **QAP Divisibility Check:** The circuit is valid if and only if:  
  $$A(x) \cdot B(x) - C(x) = H(x) \cdot T(x)$$  
  for some quotient polynomial $H(x)$. This compresses four discrete vector equations into a single polynomial divisibility proof.

---

## SECTION C: Comprehensive System Design & Derivation (Answer any TWO — 2 × 20 Marks = 40 Marks)

### Q6. Globally Distributed ACID Transactions: TrueTime vs Calvin (20 Marks)
**Problem Statement:** Design a globally distributed relational database spanning 5 continental regions capable of executing 100,000 distributed ACID transactions per second with serializable isolation.
1. Formulate the **Google Spanner** concurrency control architecture: Two-Phase Locking (2PL) for read-write transactions, Multi-Paxos leader quorums for consensus, TrueTime commit-wait for external consistency, and lock-free read-only snapshot queries. (7 Marks)
2. Formulate the **Calvin** deterministic transaction processing architecture: Raft/Paxos sequencing layer, active replication, deterministic lock manager, and pre-ordered execution without distributed 2PC. (7 Marks)
3. Provide a rigorous architectural comparison matrix between Spanner and Calvin regarding: Two-Phase Commit overhead, handling of interactive transactions, latency sensitivity, hardware dependencies, and tail abort rates under heavy write contention. (6 Marks)

**Marking Scheme & Model Solution:**  
**(1) Google Spanner Architecture:**  
- **Replication & Consensus:** Data is partitioned into tablets and replicated across datacenters using Multi-Paxos groups. Each Paxos group has a long-lived Leader.  
- **Concurrency Control for Read-Write:** Uses strict Two-Phase Locking (SS2PL). Reads acquire shared read locks on Paxos leaders; writes acquire exclusive locks. Distributed transactions crossing multiple Paxos groups coordinate using Two-Phase Commit (2PC) over Paxos leaders.  
- **TrueTime Commit-Wait:** Leader assigns commit timestamp $s = \max(s_{local}, TT.now().latest)$. Leader waits until $TT.now().earliest > s$ before committing and releasing locks.  
- **Lock-Free Read-Only Transactions:** Read-only transactions declare timestamp $T_{read} = TT.now().latest$. They read local snapshots from any follower replica whose `safe_time` $\ge T_{read}$ with **zero locks, zero logging, and zero 2PC overhead**.

**(2) Calvin Deterministic Architecture:**  
- **Sequencer Layer:** Transactions are collected into 10ms epochs and logged via a Paxos/Raft sequence. The sequencer determines a global, immutable transaction order **before** transaction execution begins.  
- **Deterministic Lock Manager:** Transactions acquire locks strictly in sequencer order. Because all replicas process the exact same sequence of locks, deadlocks are impossible, eliminating lock graph cycle checking and deadlock aborts.  
- **Elimination of Distributed 2PC:** Since execution is 100% deterministic, if transaction $T$ does not crash due to logic error, it will commit identically across all participating worker nodes. Replicas never need to execute a distributed 2PC vote phase, eliminating the 2PC round-trip.

**(3) Comparison Matrix:**

| Dimension | Google Spanner | Calvin |
| :--- | :--- | :--- |
| **Distributed 2PC** | Requires distributed 2PC across Paxos leaders (latency = $2 \times \text{RTT}_{cross-region}$) | Completely eliminates distributed 2PC via deterministic sequencing |
| **Interactive Transactions** | Fully supports client-interactive transactions (e.g., read, pause, compute, write) | Cannot support arbitrary interactive client queries; write sets must be statically known in advance |
| **Hardware Dependency** | Strictly requires GPS antennas and atomic clock hardware in every datacenter rack | Zero specialized hardware; runs on commodity commodity cloud instances |
| **Commit-Wait Latency** | Introduces $2\epsilon$ ($2-14\text{ ms}$) artificial commit-wait stall on every write commit | Zero commit-wait; latency governed by epoch sequencing batching |
| **High Contention Behavior** | Lock contention causes cascading transaction aborts, deadlocks, and exponential backoff | Zero deadlocks, zero lock aborts under contention; transactions queue deterministically |

---

### Q7. Substructural Types, Borrow Checking & Polonius Datalog Engine (20 Marks)
**Problem Statement:** Design the static analysis engine of a modern systems programming language compiler that enforces memory safety and race-freedom without garbage collection.
1. Formulate the operational typing rules for **Linear Types** (must consume exactly once) and **Affine Types** (consume at most once). Write the inference rules using natural deduction syntax. (6 Marks)
2. Formulate the **Aliasing XOR Mutability** invariant ($\&T \text{ vs } \&\text{mut } T$). Prove why this invariant eliminates data races in concurrent multi-threaded programs. (6 Marks)
3. Detail the **Polonius Datalog-based Borrow-Checker Engine**. Define the fundamental relations:
   - `base_borrow(Origin, Point, Path)`
   - `subset(Origin1, Origin2, Point)`
   - `origin_contains_loan(Origin, Loan, Point)`
   - `loan_invalidated_at(Point, Loan)`
   Show how illegal borrows and use-after-free conditions are captured as Datalog query derivations. (8 Marks)

**Marking Scheme & Model Solution:**  
**(1) Natural Deduction Substructural Typing Rules:**  
- **Affine Consumption Rule:**  
  $$\frac{\Gamma_1 \vdash e_1 : \tau \quad \Gamma_2, x:\tau \vdash e_2 : \sigma}{\Gamma_1 \cup \Gamma_2 \vdash \text{let } x = e_1 \text{ in } e_2 : \sigma} \; (\text{Weakening allowed: } x \text{ may appear } 0 \text{ or } 1 \text{ times in } e_2)$$  
- **Linear Consumption Rule:**  
  $$\frac{\Gamma_1 \vdash e_1 : \tau \quad \Gamma_2, x:\tau \vdash e_2 : \sigma \quad x \in \text{FreeVars}(e_2)}{\Gamma_1 \uplus \Gamma_2 \vdash \text{let } x = e_1 \text{ in } e_2 : \sigma} \; (\text{Context disjoint union } \uplus \text{ enforces no duplication and mandatory use})$$

**(2) Aliasing XOR Mutability ($\&T \text{ vs } \&\text{mut } T$):**  
- **Invariant:** At any program point $P$ for variable $X$:  
  Either there exist any number of immutable references ($\&T$), OR there exists exactly one mutable reference ($\&\text{mut } T$), but **never both simultaneously**.  
- **Proof of Data Race Freedom:**  
  A data race occurs if two concurrent threads access the same memory location, at least one access is a write, and no synchronization precedes them.  
  1. Suppose Thread $T_1$ writes to memory address $M$. To write, $T_1$ must possess a mutable reference `&mut T` to $M$.  
  2. By the Aliasing XOR Mutability invariant, while `&mut T` is active, no other reference (mutable or immutable) to $M$ can exist anywhere in the program.  
  3. Therefore, no other thread $T_2$ can hold a valid reference to $M$.  
  4. Consequently, no concurrent read or write can occur simultaneously with $T_1$'s write. Thus, data races are statically impossible.

**(3) Polonius Datalog Borrow-Checker Engine:**  
Polonius formulates borrow checking as reachability on a graph of CFG points and origins (lifetimes) using Datalog:
- **Base Relations:**  
  - `cfg_edge(Point1, Point2)`: CFG transition.  
  - `loan_issued_at(Origin, Loan, Point)`: Loan created at Point.  
  - `loan_invalidated_at(Point, Loan)`: Point performs an action (e.g. write/move) that conflicts with Loan.  
  - `path_accessed_at(Path, Point)`: Path is read or written.  
- **Datalog Deduction Rules:**  
```prolog
% A loan is live at a point if it was issued there
origin_contains_loan_on_entry(Origin, Loan, Point) :-
    loan_issued_at(Origin, Loan, Point).

% Transitive subset propagation
origin_contains_loan_on_entry(Origin2, Loan, Point) :-
    origin_contains_loan_on_entry(Origin1, Loan, Point),
    subset(Origin1, Origin2, Point).

% Loan liveness flows along CFG edges if origin is live
origin_contains_loan_on_entry(Origin, Loan, Point2) :-
    origin_contains_loan_on_entry(Origin, Loan, Point1),
    cfg_edge(Point1, Point2),
    origin_is_live_at(Origin, Point2).

% ILLEGAL BORROW ERROR DERIVATION:
% An error occurs if a loan is invalidated at Point while still live!
check_loan_violation(Loan, Point) :-
    loan_invalidated_at(Point, Loan),
    origin_contains_loan_on_entry(Origin, Loan, Point),
    origin_is_live_at(Origin, Point).
```
**Conclusion:** A use-after-free or conflicting mutation is detected if `check_loan_violation(Loan, Point)` produces any non-empty tuples, causing compilation failure with precise diagnostic source spans.

---

### Q8. Formal Model Checking: Peterson's Mutual Exclusion Verification (20 Marks)
**Problem Statement:** You are formally verifying Peterson's two-process mutual exclusion algorithm using exhaustive state-space model checking.
```text
Variables:
  flag = [false, false]
  turn = 0

Process 0:
  L0: flag[0] = true
  L1: turn = 1
  L2: wait until (flag[1] == false or turn == 0)
  L3: /* CRITICAL SECTION */
  L4: flag[0] = false
  L5: /* NON-CRITICAL SECTION */

Process 1:
  M0: flag[1] = true
  M1: turn = 0
  M2: wait until (flag[0] == false or turn == 1)
  M3: /* CRITICAL SECTION */
  M4: flag[1] = false
  M5: /* NON-CRITICAL SECTION */
```
1. Formulate the state tuple $S = (PC_0, PC_1, flag_0, flag_1, turn)$. (4 Marks)
2. Construct the exhaustive state-space transition graph starting from initial state $S_0 = (L_0, M_0, \text{false}, \text{false}, 0)$. (8 Marks)
3. Formulate the **Mutual Exclusion Safety Invariant** in Linear Temporal Logic (LTL) or propositional logic. Prove by state enumeration that no reachable state violates this invariant. (4 Marks)
4. Formulate the **Liveness / Starvation-Freedom Invariant** in LTL ($\square(PC_0 = L_2 \implies \lozenge PC_0 = L_3)$). Prove why Peterson's algorithm is strictly starvation-free assuming weak fairness. (4 Marks)

**Marking Scheme & Model Solution:**  
**(1) State Tuple Formalism:**  
- State $S = (PC_0, PC_1, flag_0, flag_1, turn)$ where:  
  $PC_0 \in \{L_0, L_1, L_2, L_3, L_4, L_5\}$,  
  $PC_1 \in \{M_0, M_1, M_2, M_3, M_4, M_5\}$,  
  $flag_0, flag_1 \in \{\text{false}, \text{true}\}$,  
  $turn \in \{0, 1\}$.  
- Initial state: $S_0 = (L_0, M_0, \text{false}, \text{false}, 0)$.

**(2) Reachability Analysis & Transition Sequences:**  
Consider the interleaved race where both processes attempt entry concurrently:
1. $S_0 = (L_0, M_0, F, F, 0)$  
   - $P_0$ sets flag: $S_1 = (L_1, M_0, T, F, 0)$  
   - $P_1$ sets flag: $S_2 = (L_1, M_1, T, T, 0)$  
2. Now both processes set `turn`:  
   - Branch A: $P_0$ executes $L_1$: $S_3 = (L_2, M_1, T, T, 1)$  
     Next $P_1$ executes $M_1$: $S_4 = (L_2, M_2, T, T, 0)$  
     Now check wait conditions at $S_4$:  
     - For $P_0$ at $L_2$: condition is $(flag_1 == F \lor turn == 0)$. Since $turn == 0$, **Condition is TRUE!** $P_0$ enters critical section: $S_5 = (L_3, M_2, T, T, 0)$.  
     - For $P_1$ at $M_2$: condition is $(flag_0 == F \lor turn == 1)$. Since $flag_0 == T$ and $turn == 0$, **Condition is FALSE!** $P_1$ stalls in wait loop!  
   - Branch B: $P_1$ executes $M_1$: $turn \leftarrow 0$.  
     Then $P_0$ executes $L_1$: $turn \leftarrow 1$.  
     Symmetrically, $turn == 1$, allowing $P_1$ to enter $M_3$ while $P_0$ stalls.

**(3) Mutual Exclusion Invariant & Proof:**  
- **LTL Safety Invariant:**  
  $$\square \neg (PC_0 = L_3 \land PC_1 = M_3)$$  
- **Mathematical Proof:**  
  For both to be in critical section ($PC_0 = L_3 \land PC_1 = M_3$), both must have evaluated their wait conditions to TRUE while $flag_0 = T$ and $flag_1 = T$:  
  - $P_0$ required: $turn = 0$ (since $flag_1 = T$).  
  - $P_1$ required: $turn = 1$ (since $flag_0 = T$).  
  However, variable `turn` is a scalar register that holds either 0 or 1, but never both simultaneously ($turn = 0 \land turn = 1 \iff \bot$).  
  Whichever process wrote to `turn` last overwrote the other's value. The process that wrote last inevitably sees `turn` equal to the other process's ID and is blocked.  
  Full BFS exploration over all reachable states reveals that out of all reachable states, exactly **0 states** have $(PC_0 = L_3 \land PC_1 = M_3)$. Mutual exclusion is strictly guaranteed.

**(4) Liveness & Starvation Freedom:**  
- **LTL Liveness Specification:**  
  $$\square (PC_0 = L_2 \implies \lozenge PC_0 = L_3)$$  
- **Proof under Weak Fairness:**  
  Suppose $P_0$ is waiting at $L_2$ ($PC_0 = L_2$).  
  - If $P_1$ does not want to enter ($flag_1 = F$), $P_0$'s condition $(flag_1 == F \lor turn == 0)$ is immediately satisfied, so $P_0$ enters $L_3$.  
  - If $P_1$ is also competing ($flag_1 = T$), $turn$ is either 0 or 1. If $turn == 0$, $P_0$ enters immediately.  
  - If $turn == 1$, $P_1$ enters $M_3$. When $P_1$ exits $M_3$, it executes $M_4$: setting $flag_1 = F$. At that exact moment, $P_0$'s condition becomes true and $P_0$ enters $L_3$.  
  Even if $P_1$ immediately tries to re-enter, it must execute $M_1$: setting $turn = 0$, thereby handing entry priority directly to $P_0$. Therefore, $P_0$ can be delayed for at most one critical section execution of $P_1$, proving that starvation is mathematically impossible.
