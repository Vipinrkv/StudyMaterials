# LEVEL 7: CONSENSUS, SRE, AND REAL-TIME DATA ENGINES REVISION SHEET

---

## 1. MASTER FORMULAE CHEAT SHEET

### 1.1 Consensus Quorum Intersection
For cluster size $N = 2F + 1$ tolerating at most $F$ crash failures:
$$\text{Quorum Size } Q = F + 1 = \left\lfloor \frac{N}{2} \right\rfloor + 1$$
$$|\mathcal{Q}_1 \cap \mathcal{Q}_2| \ge (F + 1) + (F + 1) - (2F + 1) = 1$$
Flexible Paxos Condition: $Q_1 + Q_2 > N$.

### 1.2 System Availability & Quantitative Reliability
$$\text{MTBF} = \text{MTTF} + \text{MTTR}, \qquad \mathcal{A} = \frac{\text{MTTF}}{\text{MTBF}} = \frac{\text{MTTF}}{\text{MTTF} + \text{MTTR}}$$
- Series Reliability ($n$ components without redundancy):
$$R_{\text{series}} = \prod_{i=1}^{n} R_i$$
- Parallel Redundancy ($k$ identical active-active replicas):
$$R_{\text{parallel}} = 1 - \prod_{j=1}^{k} (1 - R_j)$$

### 1.3 Little's Law in Concurrency & SRE
$$L = \lambda \cdot W \implies \lambda_{\max} = \frac{L_{\max}}{W}$$
Where $L$ is concurrency (active in-flight requests), $\lambda$ is arrival rate (throughput in req/sec), and $W$ is mean service latency (seconds).

### 1.4 Google SRE Multiwindow Burn Rate Formula
$$\text{Error Budget } \mathcal{EB} = 1.0 - \text{SLO}$$
$$\text{Burn Rate } B = \frac{\text{Observed Error Rate}}{\text{Allowed Error Rate}} = \frac{1 - \text{SLI}}{1 - \text{SLO}}$$
- **SEV-1 Page (14.4x):** Consumes $2\%$ of 30-day budget in 1 hour ($W_{\text{long}} = 1\text{h}$, $W_{\text{short}} = 5\text{m}$).
- **SEV-2 Ticket (6.0x):** Consumes $5\%$ of 30-day budget in 6 hours ($W_{\text{long}} = 6\text{h}$, $W_{\text{short}} = 30\text{m}$).

### 1.5 Columnar Frame of Reference (FoR) Compression
For integer block with $x_{\min} = \min(x_i)$ and $\Delta_{\max} = \max(x_i) - x_{\min}$:
$$b = \lceil \log_2(\Delta_{\max} + 1) \rceil \text{ bits/value}, \qquad \text{Compressed Size} = N \cdot b \text{ bits}$$

### 1.6 Bounded Out-of-Order Watermark Progression
$$W(t) = T_{\max} - \delta_{\text{delay}}$$
Window $[t_{\text{start}}, t_{\text{end}})$ triggers and purges when $W(t) \ge t_{\text{end}}$.

---

## 2. RAPID RECALL COMPARISON TABLES

### 2.1 Consensus Protocol Families

| Feature | Synod Paxos | Multi-Paxos | Raft | Zab |
| :--- | :--- | :--- | :--- | :--- |
| **Normal Write Latency** | 2 RTTs (Prepare + Accept) | 1 RTT (Stable Leader Accept) | 1 RTT (AppendEntries Quorum) | 1 RTT (Proposal + Commit) |
| **Leader Model** | None (Any proposer) | Weak/Stable Leader | Strong Leader (Term Dominance) | Primary with strict epoch broadcast |
| **Log Gaps / Holes** | Permitted (Per-slot Paxos) | Permitted (No-op gap filling) | Strictly forbidden (Contiguous) | Strictly forbidden (Contiguous FIFO) |
| **Election Safety** | Quorum promises in Phase 1 | Replay Phase 1 for uncommitted | Candidate log completeness check | Discovery phase synchronizes history |

### 2.2 Database Execution Paradigms

| Dimension | Volcano (Tuple-at-a-Time) | Vectorized (MonetDB/X100) | JIT Compilation (HyPer) |
| :--- | :--- | :--- | :--- |
| **Function Call Overhead** | $1 \text{ call / tuple}$ | $1 \text{ call / 1024 tuples}$ | Zero (Inlined machine loops) |
| **Data Residency** | Polluted L1/L2 caches | L1/L2 Cache Resident Vectors | CPU Registers |
| **Hardware SIMD Support** | Impractical | Native (AVX-2, AVX-512) | Native machine generation |
| **Compilation Latency** | Zero | Zero | $10\text{ms} - 50\text{ms}$ query startup |

---

## 3. HIGH-PROBABILITY EXAM & INTERVIEW QUESTIONS

1. **Why does a Stable Leader in Multi-Paxos eliminate Phase 1 for subsequent client proposals?**
   - *Answer:* Phase 1 establishes the proposer's right to submit proposals (ballot dominance) and discovers any previously accepted values across historical slots. Once a leader receives promises from a majority quorum for all future slots $\ge i$, no other proposer can interfere without a higher ballot. Therefore, the stable leader can safely broadcast Phase 2a (Accept) directly for subsequent slots, reducing write latency from 2 RTTs to 1 RTT.

2. **How does Fencing Token generation prevent the "Zombie Primary" split-brain defect?**
   - *Answer:* When a primary node stalls (e.g., GC pause) and the coordinator promotes a standby, the coordinator issues an incremented generation epoch token $T_{\text{new}} = T_{\text{old}} + 1$. Downstream storage targets enforce monotonic checks: any write carrying token $T < T_{\text{current}}$ is unconditionally rejected. When the resurrected zombie primary awakens, its writes carrying stale $T_{\text{old}}$ are safely dropped.

3. **In stream processing, what is the fundamental difference between At-Least-Once and Exactly-Once semantics?**
   - *Answer:* At-Least-Once guarantees no data loss by replaying unacknowledged messages upon failure, but risks duplicate processing if a sink crashes before recording consumer offsets. Exactly-Once Semantics (EOS) guarantees that internal state and external sink outputs reflect each event exactly once, achieved via coordinated distributed checkpointing (Chandy-Lamport / ABS) coupled with Two-Phase Commit or idempotent sinks.
