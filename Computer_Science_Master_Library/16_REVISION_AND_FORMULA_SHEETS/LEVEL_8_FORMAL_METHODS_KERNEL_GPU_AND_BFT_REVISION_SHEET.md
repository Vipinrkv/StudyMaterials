# LEVEL 8 REVISION & FORMULA SHEET: FORMAL METHODS, KERNEL INTERNALS, GPU ARCHITECTURE, BFT CONSENSUS & AI SAFETY

---

## 1. FORMAL SPECIFICATION & TLA+ LOGIC

### Core Temporal Logic Operators
$$\Box F \iff \forall i \ge 0, \quad \sigma^{+i} \models F \quad (\text{Always } F)$$
$$\Diamond F \iff \exists i \ge 0, \quad \sigma^{+i} \models F \quad (\text{Eventually } F)$$
$$F \rightsquigarrow G \triangleq \Box(F \implies \Diamond G) \quad (F \text{ leads to } G)$$

### Fairness Definitions
- **Weak Fairness ($\text{WF}_v(A)$):**
  $$\text{WF}_v(A) \triangleq \Box \Diamond \neg \text{ENABLED}\langle A \rangle_v \lor \Box \Diamond \langle A \rangle_v$$
- **Strong Fairness ($\text{SF}_v(A)$):**
  $$\text{SF}_v(A) \triangleq \Diamond \Box \neg \text{ENABLED}\langle A \rangle_v \lor \Box \Diamond \langle A \rangle_v$$

### Inductive Invariant Criteria
1. $\text{Init} \implies \text{Inv}$
2. $\text{Inv} \land [\text{Next}]_v \implies \text{Inv}'$

---

## 2. LINUX KERNEL, EBPF & IO_URING

### io_uring Lock-Free Masking
$$\text{Index} = \text{Sequence} \ \& \ (\text{QueueCapacity} - 1) \quad (\text{Capacity is power of two})$$

### eBPF Verifier Interval Tracking
$$R_1 \in [a, b], \quad R_2 \in [c, d] \implies R_1 + R_2 \in [a+c, b+d]$$
$$\text{Memory Safety Guarantee: } \text{Base} + umax(R_{\text{offset}}) + \text{size} \le \text{BufferLimit}$$

### Ring 3 vs Ring 0 Penalty
$$T_{\text{syscall}} = T_{\text{privilege}} + T_{\text{KPTI}} + T_{\text{TLB\_flush}} + T_{\text{cache\_eviction}}$$

---

## 3. HIGH-PERFORMANCE COMPUTING & GPU CUDA

### Global Thread Index Mapping
$$\text{GlobalThreadID} = \text{blockIdx.x} \times \text{blockDim.x} + \text{threadIdx.x}$$

### Shared Memory Bank Interleaving (32 Banks)
$$\text{BankID} = \left(\frac{\text{ByteAddress}}{4}\right) \pmod{32}$$
- **Zero Conflict:** Consecutive 4-byte accesses map to banks $0, 1, \dots, 31$ ($1\times$ pass).
- **Stride-32 Hazard:** All 32 threads in warp map to Bank 0 ($32\times$ serialized passes).

### Arithmetic Intensity of Tiled GEMM
$$I_{\text{naive}} = \frac{2N^3 \text{ FLOPs}}{8N^3 \text{ bytes}} = 0.25 \text{ FLOP/byte}$$
$$I_{\text{tiled}} = \frac{2B^3 \text{ FLOPs}}{8B^2 \text{ bytes}} = \frac{B}{4} \text{ FLOP/byte} \quad (32\times \text{ DRAM reduction for } B=32)$$

---

## 4. BYZANTINE FAULT TOLERANCE & HOTSTUFF

### Quorum Bounds
$$n \ge 3f + 1, \quad Q_{\text{BFT}} \ge 2f + 1$$
$$|Q_1 \cap Q_2| \ge (n - f) + (n - f) - n = n - 2f \ge f + 1 \quad (\text{Guarantees } \ge 1 \text{ honest intersection})$$

### Complexity Comparison
| Metric | PBFT (1999) | Tendermint | HotStuff (2019) |
| :--- | :--- | :--- | :--- |
| **Normal Path** | $O(n^2)$ | $O(n^2)$ | **$O(n)$** |
| **View Change** | $O(n^3)$ | $O(n^2)$ | **$O(n)$** |
| **Commit Rule** | 2-phase | 2-phase lock | **3-chain pipelined** |

---

## 5. FRONTIER AI SAFETY & ALIGNMENT

### Direct Preference Optimization (DPO) Loss
$$\mathcal{L}_{\text{DPO}}(\theta) = -\log \sigma \left( \beta \log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)} \right)$$

### Sparse Autoencoder (SAE) Monosemantic Loss
$$\mathcal{L}_{\text{SAE}} = \|x - \hat{x}\|_2^2 + \lambda \|f(x)\|_1$$
$$f(x) = \text{ReLU}(W_{\text{enc}}(x - b_{\text{dec}}) + b_{\text{enc}}), \quad \hat{x} = W_{\text{dec}} f(x) + b_{\text{dec}}$$

### Linear Activation Steering
$$v_{\text{steer}} = \mu_{\text{harmful}} - \mu_{\text{harmless}}$$
$$x_{\text{aligned}} = x + c \cdot v_{\text{steer}} \quad (c < 0 \text{ for refusal suppression})$$

---

## 6. QUICK-FIRE EXAM REVISION MATRIX

| Term | Formal Definition / Core Equation | Key Real-World Tool / Reference |
| :--- | :--- | :--- |
| **TLA+ Invariant** | $\text{Init} \land [\text{Next}]_v \implies \text{Inv}$ | TLC Model Checker, AWS S3 |
| **eBPF CO-RE** | Relocatable struct offsets via BTF debug metadata | Cilium, Meta Katran, libbpf |
| **io_uring SQPOLL**| Dedicated kernel thread polls user submission queue | Linux 5.1+, Jens Axboe |
| **SIMT Warp** | 32 hardware threads executing lock-step instructions | NVIDIA H100, CUDA NCU |
| **Bank Conflict** | Multiple threads requesting distinct offsets in same bank | CUDA Shared Memory SRAM |
| **BFT 3-Chain** | Block committed after 3 consecutive ancestor QCs | HotStuff, Aptos, Diem |
| **Monosemanticity**| 1 neuron/feature mapping to exactly 1 human concept | Anthropic SAE, TransformerLens |
