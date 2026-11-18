# Level 5 Revision & Formula Sheet: Cloud, DevOps, Microservices & SRE

---

## 1. Quick Reference: Chapters 06 to 10

| Chapter | Core Focus | Key Axioms & Formulas | Primary Pitfalls / Edge Cases |
|:---|:---|:---|:---|
| **CH06: Cloud Architecture & Serverless** | Multi-Tenancy, Autoscaling, Object Stores, FaaS | $A_{\text{serial}} = \prod A_i$; $A_{\text{parallel}} = 1 - \prod(1 - A_i)$; Jitter $U(0, \min(C, B \cdot 2^i))$ | Thundering herd on recovery; FaaS cold starts; unbounded cloud spend |
| **CH07: DevOps, CI/CD, Containers & IaC**| DORA Metrics, Docker/OCI, OverlayFS, GitOps, Canary | $DF, LTC, CFR, MTTR$; CoW upper/lower merge; $\text{Whiteout} = \text{.wh.}f$ | Flaky integration tests; stateful container loss; silent canary degradation |
| **CH08: Microservices & Distributed Data** | CAP/PACELC, Circuit Breakers, Sagas, Outbox CDC | PACELC: $PC/EC$ vs $PA/EL$; FSM $\delta(\text{CLOSED}, \text{err} \ge \tau) = \text{OPEN}$; Saga reverse $\mathcal{C}^{-1}$ | Distributed dual-writes; 2PC blocking locks; cascading cascade outages |
| **CH09: Testing at Scale (Unit to E2E)** | Test Pyramid, Meszaros Doubles, Mutation Testing, Pact | $MS = \frac{K}{M} \times 100\%$; Ice Cream Cone anti-pattern; Consumer-driven contract | Mocking what you do not own; flaky E2E tests; testing implementation details |
| **CH10: Observability, SRE & Incident Mgmt**| 4 Golden Signals, Prometheus, OpenTelemetry, Error Budgets| $B = \frac{E_{\text{obs}}}{1 - \text{SLO}}$; $T_{\text{exhaust}} = \frac{720\text{h}}{B}$; W3C `00-trace-span-flags` | Metric cardinality explosion; un-actionable alert fatigue; blind trace gaps |

---

## 2. Cloud Reliability & Availability Mathematics

### 2.1 Serial vs Parallel System Availability
- **Serial System (Pipeline)**: Uptime requires **all** independent subsystems to function simultaneously:
  $$A_{\text{serial}} = \prod_{i=1}^n A_i$$
- **Parallel System (Redundancy)**: Uptime requires **at least one** replica to function:
  $$A_{\text{parallel}} = 1 - \prod_{i=1}^n (1 - A_i)$$
- **Composite Tiered System**:
  $$A_{\text{system}} = \prod_{k=1}^m A_{\text{tier}_k} = \prod_{k=1}^m \left[ 1 - \prod_{j=1}^{r_k} (1 - A_{k, j}) \right]$$

### 2.2 Availability "Nines" and Downtime Budget Table
| Availability Level | Annual Allowed Downtime | Monthly Allowed Downtime | Daily Allowed Downtime |
|:---|:---:|:---:|:---:|
| **99% (Two Nines)** | 3.65 days (87.6 hours) | 7.20 hours | 14.4 minutes |
| **99.9% (Three Nines)** | 8.76 hours (525.6 min) | 43.2 minutes | 1.44 minutes |
| **99.99% (Four Nines)** | 52.6 minutes | 4.32 minutes | 8.64 seconds |
| **99.999% (Five Nines)**| 5.26 minutes | 25.9 seconds | 0.86 seconds |

### 2.3 Resilient Retry & Jitter Algorithms (AWS Architecture Pattern)
- **Exponential Backoff (No Jitter - Danger: Causes Synchronization / Thundering Herd)**:
  $$t_{\text{sleep}} = \min(C, B \cdot 2^{\text{attempt}})$$
- **Full Jitter (Recommended Standard)**:
  $$t_{\text{sleep}} = \text{Uniform}\left(0, \ \min(C, B \cdot 2^{\text{attempt}})\right)$$
- **Decorrelated Jitter**:
  $$t_{\text{sleep}} = \min\left(C, \ \text{Uniform}(B, \ t_{\text{prev}} \cdot 3)\right)$$

---

## 3. DevOps, CI/CD & Containerization Invariants

### 3.1 DORA Core Metrics (State of DevOps)
1. **Deployment Frequency (DF)**: Rate of successful production deployments (Elite: On-demand / multiple times per day).
2. **Lead Time for Changes (LTC)**: Elapsed time from commit to running in production (Elite: $< 1$ hour).
3. **Change Failure Rate (CFR)**: Percentage of deployments causing production degraded service (Elite: $0\% - 15\%$).
4. **Mean Time to Recovery (MTTR)**: Time taken to restore service after an incident (Elite: $< 1$ hour).

### 3.2 Linux Container Isolation Primitives
```
                    Linux Kernel Container Isolation
  +-------------------------------------------------------------------+
  | Namespaces (What a process can SEE)                               |
  |  - PID (Process trees)             - NET (Network interfaces, IPs)|
  |  - MNT (Mount points/filesystems)  - IPC (Inter-process memory)   |
  |  - UTS (Hostname & NIS domain)     - USER (UID/GID virtualization)|
  +-------------------------------------------------------------------+
  | Cgroups v2 (How much a process can USE)                           |
  |  - cpu.max (CFS bandwidth quota)   - memory.max / memory.high     |
  |  - io.weight (Block I/O throttle)  - pids.max (Fork-bomb defense) |
  +-------------------------------------------------------------------+
  | Security Hardening                                                |
  |  - Seccomp (Syscall filtering via BPF)                            |
  |  - Linux Capabilities (Dropping CAP_SYS_ADMIN, CAP_NET_ADMIN)     |
  +-------------------------------------------------------------------+
```

### 3.3 OverlayFS Storage Semantics
- **Lower Layers**: Read-only immutable container base image layers.
- **Upper Layer**: Read-write layer ephemeral to container lifecycle.
- **Copy-on-Write (CoW)**: First write to a lower file triggers copy-up into upper layer before modification.
- **Whiteout Files**: Deletion of lower layer file `app.bin` creates a character device file `.wh.app.bin` in upper layer.

---

## 4. Microservices, Distributed Data & Resiliency Axioms

### 4.1 CAP and PACELC Theorems
- **CAP Theorem (Brewer)**: In the presence of a Network Partition ($P$), a distributed system must choose between:
  - **Consistency ($C$)**: Every read returns the most recent write or an error.
  - **Availability ($A$)**: Every non-failing node returns a non-error response without guarantee of latest write.
- **PACELC Theorem (Abadi)**:
  $$\text{If } \mathbf{P} \implies \text{Choose } (\mathbf{A} \lor \mathbf{C}); \quad \text{ELSE } \implies \text{Choose } (\mathbf{L} \text{ [Latency]} \lor \mathbf{C} \text{ [Consistency]})$$
  - *PC/EC*: Spanner, ZooKeeper, Raft.
  - *PA/EL*: Cassandra, DynamoDB (eventual consistency mode).

### 4.2 Circuit Breaker Finite State Machine (Michael Nygard Pattern)
```
            +--------------------------------------------+
            |                                            |
            v  (consecutive_failures >= threshold)       |
      +------------+ ---------------------------> +----------+
      |   CLOSED   |                              |   OPEN   |
      |  (Pass-thru| <--------------------------- |(Fast-fail|
      +------------+  (probes succeed >= needed)  +----------+
            ^                                            |
            |                                            | (recovery_timeout elapsed)
            |              +---------------+             |
            +------------- |   HALF_OPEN   | <-----------+
              (Success)    | (Canary Probe)|
                           +---------------+
                                   |
                                   | (probe fails)
                                   v
                             (Back to OPEN)
```

### 4.3 Saga Pattern: Distributed Consistency
- **Forward Action Sequence**: $T_1 \to T_2 \to \dots \to T_k$.
- **Compensating Action Sequence**: If step $T_k$ fails, execute $\mathcal{C}_{k-1}^{-1} \to \mathcal{C}_{k-2}^{-1} \to \dots \to \mathcal{C}_1^{-1}$ in strict reverse order.
- **Idempotency Invariant**: All compensating actions $\mathcal{C}_i^{-1}$ must be strictly idempotent: $\mathcal{C}^{-1}(\mathcal{C}^{-1}(x)) = \mathcal{C}^{-1}(x)$.

---

## 5. Testing at Scale & Observability SRE Standards

### 5.1 Gerard Meszaros Test Doubles Taxonomy
| Double Type | Definition | Verification Role |
|:---|:---|:---|
| **Dummy** | Passed to satisfy signatures; never actually executed or called | Interface satisfaction only |
| **Stub** | Returns hardcoded canned responses for predetermined inputs | State verification (Downstream input) |
| **Spy** | Stub that records invocation counts, method names, and parameters | Behavior verification post-execution |
| **Mock** | Pre-programmed with expectations; asserts call count & order itself | Behavior verification during execution |
| **Fake** | Fully functional shortcut implementation (e.g. in-memory SQLite/Dict)| State verification without network/DB |

### 5.2 Mutation Testing Score
$$MS = \frac{\text{Mutants Killed}}{\text{Total Mutants Created}} \times 100\%$$
- **High Code Coverage + Low Mutation Score** = Fragile assertion hygiene (tests execute code but assert nothing).
- **Target Standard**: Maintain $MS \ge 85\%$ on critical business logic modules.

### 5.3 Distributed Tracing (W3C Trace Context Specification)
- **Header Key**: `traceparent`
- **Format**: `version(2 hex)-trace_id(32 hex)-parent_id(16 hex)-trace_flags(2 hex)`
- **Example**: `00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`
  - `00`: Current W3C specification version.
  - `4bf92f3577b34da6a3ce929d0e0e4736`: Globally unique 128-bit trace ID.
  - `00f067aa0ba902b7`: 64-bit caller span ID.
  - `01`: Context flags (`01` = Sampled/Recorded, `00` = Not Sampled).

### 5.4 Google SRE Multiwindow Error Budget Alerting
- **Error Budget**: $EB = 1.0 - \text{SLO}$ (e.g., $99.9\% \implies EB = 0.001$).
- **Burn Rate ($B$)**: Multiplier of allowable error consumption rate:
  $$B = \frac{\text{Observed Error Rate}}{EB}$$
- **Time to 100% Depletion (30-day window = 720 hours)**:
  $$T_{\text{exhaust}} = \frac{720\text{ hours}}{B}$$
- **SRE Alert Rules**:
  - **SEV-1 Critical Page**: $1\text{-hour window with } B \ge 14.4$ (Depletes $2\%$ of monthly budget in $1$ hour; total exhaustion in $50$ hours).
  - **SEV-2 Ticket Warning**: $6\text{-hour window with } B \ge 6.0$ (Depletes $5\%$ of monthly budget in $6$ hours; total exhaustion in $120$ hours).

### 5.5 The Four Golden Signals (Google SRE Standard)
1. **Latency**: Time taken to service a request (differentiating between successful and error latencies).
2. **Traffic**: Demand placed upon system (HTTP reqs/sec, transactions/sec, bandwidth).
3. **Errors**: Rate of requests that fail explicitly (HTTP 500s) or implicitly (wrong content returned).
4. **Saturation**: How full the service is (CPU usage, memory pressure, thread pool utilization, I/O wait).
