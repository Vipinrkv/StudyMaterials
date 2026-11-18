# Level 6 Revision & Formula Sheet: Distributed Systems, Consensus, Cryptography & ML Foundations

---

## 1. Quick Reference: Chapters 01 to 05

| Chapter | Core Focus | Key Axioms & Formulas | Primary Pitfalls / Edge Cases |
|:---|:---|:---|:---|
| **CH01: Distributed Models & Time** | Lamport Clocks, Vector Clocks, Chandy-Lamport, NTP | $a \to b \iff V_a < V_b$; $a \parallel b$; Chandy-Lamport Marker; $T = T_{\text{srv}} + \text{RTT}/2$ | Wall clock step-backs; scalar clock concurrency blindspots; non-FIFO channels |
| **CH02: Consensus & Fault Tolerance** | SMR, FLP Impossibility, Quorum Intersections, Paxos, Raft | $Q = \lfloor N/2 \rfloor + 1$; $|Q_1 \cap Q_2| \ge 1$; Raft 5 Safety Theorems; Phase 1/2 Paxos | Split-vote live-lock; asymmetric network partitions; stale follower reads |
| **CH03: Transactions & Consistency** | Linearizability, 2PC/3PC, TrueTime Commit-Wait, CRDTs | $op_1 \prec op_2$; $\text{TT.now().earliest} > s$; Semilattice $(S, \sqcup)$; $\text{Val} = \sum P - \sum N$ | 2PC coordinator lock-blocking; LWW silent data overwrite; write skew |
| **CH04: Modern Cryptography & ZKP** | Elliptic Curves, ECDSA, PS3 Nonce Attack, Schnorr ZK | $y^2 = x^3 + ax + b$; $k = \frac{\Delta z}{\Delta s}$; $g^s \equiv T \cdot Y^c$; $c = H(g \parallel Y \parallel T)$ | Nonce reuse private key leak; timing side-channels; invalid curve attacks |
| **CH05: ML Foundations & Optimization**| Jacobians, Hessians, MLE/MAP, Bias-Variance, AdamW | $\text{MSE} = \text{Bias}^2 + \text{Var} + \sigma^2$; $\hat{m}_t = \frac{m_t}{1 - \beta_1^t}$; $\theta - \eta \lambda \theta - \frac{\eta}{\sqrt{\hat{v}} + \epsilon} \hat{m}$ | Vanishing/exploding gradients; ill-conditioned ravines; standard Adam $L_2$ decay |

---

## 2. Distributed Time, Synchronization & Snapshots

### 2.1 Lamport Logical Clocks (Scalar Order)
- **Local event**: $L_i \gets L_i + 1$
- **Send event**: Attach $L_i$ to message $(m, L_i)$
- **Receive event**: $L_j \gets \max(L_j, L_m) + 1$
- **Clock Condition Invariant**:
  $$a \to b \implies L(a) < L(b) \quad (\text{Note: } L(a) < L(b) \centernot\implies a \to b)$$

### 2.2 Vector Clocks (Mattern & Fidge 1988)
- **Local event on $P_i$**: $V_i[i] \gets V_i[i] + 1$
- **Receive event on $P_j$**:
  $$\forall k: V_j[k] \gets \max(V_j[k], V_{\text{msg}}[k]), \quad V_j[j] \gets V_j[j] + 1$$
- **Exact Causality Invariant**:
  $$a \to b \iff V(a) < V(b)$$
- **Exact Concurrency Test**:
  $$a \parallel b \iff \neg(V(a) \le V(b)) \land \neg(V(b) \le V(a))$$

### 2.3 Physical Clock Synchronization
- **Cristian's Algorithm**:
  $$T_{\text{client}} = T_{\text{server}} + \frac{T_1 - T_0}{2} \quad \text{with error bound } \pm \left( \frac{\text{RTT}}{2} - \min(\text{latency}) \right)$$
- **Clock Drift Rate ($\rho$)**:
  $$1 - \rho \le \frac{dC(t)}{dt} \le 1 + \rho$$

### 2.4 Chandy-Lamport Distributed Snapshot
- **Prerequisite**: Channels must obey FIFO delivery.
- **Marker Rule**:
  - Process $P$ records local state upon first marker receipt, marks incoming channel as empty, and forwards marker to all outgoing channels.
  - While recording, any incoming messages on other channels before their markers arrive are recorded as **in-flight channel state**.

---

## 3. Consensus, Quorums & Fault Tolerance

### 3.1 Quorum Intersection Principle
For cluster of $N = 2f + 1$ nodes:
$$Q \ge \left\lfloor \frac{N}{2} \right\rfloor + 1 = f + 1$$
$$|Q_1 \cap Q_2| = |Q_1| + |Q_2| - |Q_1 \cup Q_2| \ge (f+1) + (f+1) - (2f+1) = 1$$
Any two majorities overlap in at least one witness node.

### 3.2 Raft Consensus Core Safety Invariants
1. **Election Safety**: At most one leader elected per term $T$.
2. **Leader Append-Only**: Leader never overwrites or truncates its own log entries.
3. **Log Matching Property**: Same index and term $\implies$ identical commands and identical preceding log history.
4. **Leader Completeness**: An entry committed in term $T$ is present in leaders of all terms $T' > T$.
5. **State Machine Safety**: If server applies log entry at index $i$, no server applies a different entry for index $i$.

### 3.3 Raft Candidate Voting Rule
A follower grants vote to candidate iff:
$$\left( T_{\text{cand\_last}} > T_{\text{local\_last}} \right) \lor \left( T_{\text{cand\_last}} = T_{\text{local\_last}} \land L_{\text{cand\_last}} \ge L_{\text{local\_last}} \right)$$

---

## 4. Distributed Transactions & Consistency Models

### 4.1 Consistency Models Hierarchy
$$\text{Strict Serializability} \subset \text{Linearizability} \subset \text{Sequential Consistency} \subset \text{Causal Consistency} \subset \text{Eventual Consistency}$$

- **Linearizability**: If $t_{\text{end}}(op_1) < t_{\text{start}}(op_2)$ in absolute real time, then $op_1 \prec_{\mathcal{S}} op_2$.
- **Spanner TrueTime Commit-Wait Rule**:
  $$\text{Coordinator delays commit release until: } \text{TT.now().earliest} > s_{\text{commit}}$$

### 4.2 Two-Phase Commit (2PC) Protocol
- **Phase 1 (Prepare)**: Coordinator broadcasts `PREPARE`. Participants reply `VOTE_COMMIT` (after taking locks & writing WAL) or `VOTE_ABORT`.
- **Phase 2 (Commit/Abort)**: If all vote `VOTE_COMMIT`, coordinator writes `GLOBAL_COMMIT` and broadcasts commit. Otherwise broadcasts `GLOBAL_ABORT`.
- **Blocking Condition**: If coordinator crashes during Phase 2, participants in `PREPARED` must block indefinitely holding locks.

### 4.3 Conflict-Free Replicated Data Types (CRDTs)
A state-based CRDT is a Bounded Join-Semilattice $(S, \sqcup)$:
1. Commutative: $x \sqcup y = y \sqcup x$
2. Associative: $(x \sqcup y) \sqcup z = x \sqcup (y \sqcup z)$
3. Idempotent: $x \sqcup x = x$

- **PN-Counter Formulas**:
  $$\text{Value} = \sum_{i=1}^n P[i] - \sum_{i=1}^n N[i]$$
  $$(P_A \sqcup P_B)[k] = \max(P_A[k], P_B[k]), \quad (N_A \sqcup N_B)[k] = \max(N_A[k], N_B[k])$$

---

## 5. Modern Cryptography & Machine Learning Foundations

### 5.1 Elliptic Curve Group Operations (Weierstrass Form)
Curve: $y^2 \equiv x^3 + ax + b \pmod p$.
- **Slope ($\lambda$)**:
  $$\lambda = \begin{cases}
  \frac{y_2 - y_1}{x_2 - x_1} \pmod p & \text{if } P \ne Q \text{ (Point Addition)} \\
  \frac{3x_1^2 + a}{2y_1} \pmod p & \text{if } P = Q \text{ (Point Doubling)}
  \end{cases}$$
- **Sum Point $R = (x_3, y_3)$**:
  $$x_3 = \lambda^2 - x_1 - x_2 \pmod p, \quad y_3 = \lambda(x_1 - x_3) - y_1 \pmod p$$

### 5.2 ECDSA Nonce-Reuse Private Key Extraction (Sony PS3 Exploit)
Given two signatures $(r, s_1)$ and $(r, s_2)$ sharing nonce $k$:
$$k = \frac{H(m_1) - H(m_2)}{s_1 - s_2} \pmod n$$
$$d = \frac{s_1 \cdot k - H(m_1)}{r} \pmod n$$

### 5.3 Schnorr Non-Interactive Zero-Knowledge Proof (Fiat-Shamir)
- **Commitment**: $T = g^r \pmod p$
- **Challenge**: $c = H(g \parallel Y \parallel T) \pmod q$
- **Response**: $s = (r + c \cdot x) \pmod q$
- **Verification**:
  $$g^s \equiv T \cdot Y^c \pmod p$$

### 5.4 Bias-Variance Tradeoff Decomposition
$$\mathbb{E}[(y - \hat{f}(x))^2] = \text{Bias}[\hat{f}(x)]^2 + \text{Var}[\hat{f}(x)] + \sigma^2$$
- High Bias $\implies$ Underfitting $\implies$ Increase model capacity, add features.
- High Variance $\implies$ Overfitting $\implies$ Add regularization ($L_1/L_2$), dropout, collect more data.

### 5.5 AdamW Optimization Equations
$$\hat{m}_t = \frac{m_t}{1 - \beta_1^t}, \quad \hat{v}_t = \frac{v_t}{1 - \beta_2^t}$$
$$\theta_{t+1} = \theta_t - \eta \lambda \theta_t - \frac{\eta}{\sqrt{\hat{v}_t} + \epsilon} \hat{m}_t$$
Decouples weight decay $\lambda \theta_t$ from the adaptive learning rate scaling $1/\sqrt{\hat{v}_t}$.
