# LEVEL 7: MLOPS, HFT, COMPILERS, AND ZERO-TRUST REVISION SHEET

---

## 1. MASTER FORMULAE CHEAT SHEET

### 1.1 Transformer KV Cache Memory Footprint
$$\text{Total Memory} = 2 \times B \times S \times L \times H_{KV} \times d \times P \text{ bytes}$$
- $B$: Batch size, $S$: Context sequence length, $L$: Layers, $H_{KV}$: Key-Value heads, $d$: Head dimension, $P$: Bytes per parameter ($2$ for FP16, $1$ for FP8).
- Memory per token: $M_{\text{token}} = 2 \cdot L \cdot H_{KV} \cdot d \cdot P$.

### 1.2 Speculative Decoding Expected Speedup
$$\mathbb{E}[N] = \frac{1 - \beta^{K+1}}{1 - \beta}$$
- $K$: Draft lookahead length.
- $\beta$: Empirical token acceptance rate ($\alpha = \min(1, p(x) / q(x))$).

### 1.3 Population Stability Index (PSI)
$$\text{PSI} = \sum_{i=1}^{K} (A_i - B_i) \times \ln\left(\frac{A_i}{B_i}\right)$$
- $B_i$: Baseline training proportion in bin $i$.
- $A_i$: Production observed proportion in bin $i$.
- Decision Thresholds: $\text{PSI} < 0.1$ (Stable), $0.1 \le \text{PSI} < 0.25$ (Moderate Drift), $\text{PSI} \ge 0.25$ (Severe Drift / Retrain).

### 1.4 Kolmogorov-Smirnov (KS) Two-Sample Statistic
$$D = \sup_{x} |F_{\text{base}}(x) - F_{\text{prod}}(x)|$$
Reject null hypothesis of equal distributions at $\alpha = 0.05$ if $D > 1.36 \sqrt{\frac{N_1 + N_2}{N_1 N_2}}$.

### 1.5 LMAX Disruptor Power-of-Two Bitwise Wrapping
$$\text{Slot Index}(s) = s \ \& \ (N - 1), \quad \text{where } N = 2^k$$
Replaces 15-20 cycle integer modulo ($s \pmod N$) with a single 1-cycle bitwise operation.

### 1.6 Ephemeral SVID Private Key Compromise Vulnerability
$$P(\text{Exploit}) \le 1 - e^{-\lambda_{\text{leak}} \cdot T_{\text{lifetime}}} \approx \lambda_{\text{leak}} \cdot T_{\text{lifetime}}$$
Minimizing TTL ($T \le 3600\text{s}$) bounds exposure windows without Certificate Revocation Lists (CRLs).

---

## 2. RAPID RECALL COMPARISON TABLES

### 2.1 Model Serving Architecture Matrix

| Feature | Static Batching | Continuous Iteration Batching | PagedAttention (vLLM) |
| :--- | :--- | :--- | :--- |
| **Scheduling Step** | Waits for longest request | Emits/admits per token iteration | Token iteration + dynamic paging |
| **HBM Memory Waste** | $60\% - 80\%$ (Worst-case static padding)| Moderate (Static buffer reservations) | $< 4\%$ (Bounded to last block)|
| **Throughput Multiplier** | $1.0\times$ (Baseline) | $2.5\times - 4.0\times$ | $4.0\times - 8.0\times$ |
| **Prefix Caching** | Unsupported | Complex | Native Copy-on-Write (CoW) |

### 2.2 Low-Latency Networking Approaches

| Dimension | Standard Kernel (`AF_INET`) | Kernel Bypass (OpenOnload / DPDK) | FPGA Hardware Trading |
| :--- | :--- | :--- | :--- |
| **Latency (Tick-to-Trade)**| $3 - 10 \mu\text{s}$ | $600 - 1200\text{ ns}$ ($0.6 - 1.2 \mu\text{s}$) | $50 - 200\text{ ns}$ ($0.05 - 0.2 \mu\text{s}$) |
| **CPU Jitter** | High (Context switches, interrupts) | Minimal (Polled-mode PMD drivers) | Zero (Deterministic clock cycles) |
| **User/Kernel Boundary** | Copies packet via syscall `recv()` | Direct DMA to user-space host RAM | Custom silicon logic gates |

---

## 3. HIGH-PROBABILITY EXAM & INTERVIEW QUESTIONS

1. **How does PagedAttention eliminate internal and external memory fragmentation in GPU HBM?**
   - *Answer:* Traditional frameworks allocate contiguous memory based on the worst-case maximum sequence length $S_{\max}$, leaving unused space reserved (internal fragmentation) and variable request lengths leaving holes (external fragmentation). PagedAttention partitions the KV cache into fixed-size physical blocks (e.g., 16 tokens) allocated dynamically from an unfragmented global GPU pool and mapped via logical Block Tables, exactly mirroring operating system virtual memory paging.

2. **Why does Point-in-Time (AS-OF) feature joining prevent data leakage in machine learning models?**
   - *Answer:* In historical training datasets, joining observation events with the latest feature values leaks information that occurred after the prediction timestamp (lookahead bias). An AS-OF join queries the feature timeline strictly for the value that was valid at or immediately prior to the observation timestamp ($t_{\text{feature}} \le t_{\text{event}}$), guaranteeing that the model learns only from data that was physically available when the event took place.

3. **In the LMAX Disruptor, how does 64-byte padding eliminate false sharing?**
   - *Answer:* Modern CPUs move data in 64-byte cache lines. If the producer sequence and consumer sequence reside on the same 64-byte line, Core 1's write invalidates Core 2's cache line via the cache coherence protocol (MESI), even though they are independent variables. Padding variables with 64 bytes guarantees each sequence variable occupies its own distinct cache line, eliminating cache invalidation stalls.
