# LEVEL 6: DEEP LEARNING, TRANSFORMERS, AND STORAGE ENGINES REVISION SHEET

---

## 1. MASTER FORMULAE CHEAT SHEET

### 1.1 Convolutional Layer Dimensions
Given input dimensions $(H_{\text{in}}, W_{\text{in}})$, kernel size $(K_H, K_W)$, padding $P$, and stride $S$:
$$H_{\text{out}} = \left\lfloor \frac{H_{\text{in}} - K_H + 2P}{S} \right\rfloor + 1, \qquad W_{\text{out}} = \left\lfloor \frac{W_{\text{in}} - K_W + 2P}{S} \right\rfloor + 1$$

### 1.2 Scaled Dot-Product Attention
$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{Q K^T}{\sqrt{d_k}} + M\right) V$$
- Variance normalization: if elements of $q_i$ and $k_j$ have mean $0$ and variance $1$, their dot product has variance $d_k$. Dividing by $\sqrt{d_k}$ restores variance to $1.0$, preventing softmax gradients from vanishing into flat saturated regions.
- Causal Mask $M_{ij} = 0$ for $j \le i$, and $M_{ij} = -\infty$ for $j > i$.

### 1.3 Rotary Position Embedding (RoPE)
For coordinate pair $(x_{2i}, x_{2i+1})$ at sequence position $m$ with base $\beta = 10000$:
$$\theta_i = \beta^{-2i / d}, \qquad R_{\Theta, m}^d x = \begin{bmatrix} \cos(m\theta_i) & -\sin(m\theta_i) \\ \sin(m\theta_i) & \cos(m\theta_i) \end{bmatrix} \begin{bmatrix} x_{2i} \\ x_{2i+1} \end{bmatrix}$$
Key Invariant: $\langle R_m q, R_n k \rangle = g(q, k, m - n)$ (Relative distance encoding without absolute coordinate leakage).

### 1.4 Okapi BM25 Sparse Retrieval
$$\text{Score}(D, Q) = \sum_{i=1}^{n} \text{IDF}(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}$$
$$\text{IDF}(q_i) = \ln\left(1 + \frac{N - n(q_i) + 0.5}{n(q_i) + 0.5}\right)$$
Default hyperparameters: $k_1 \in [1.2, 2.0]$, $b = 0.75$.

### 1.5 Reciprocal Rank Fusion (RRF)
$$\text{RRF\_Score}(d) = \sum_{m \in \mathcal{M}} \frac{1}{k + r_m(d)}, \qquad k = 60$$

### 1.6 Storage Amplification Trilemma & Bloom Filter Sizing
$$\text{Write Amplification } (WA) = \frac{\text{Bytes Written to Storage}}{\text{Bytes Written by Application}}, \qquad \text{Space Amplification } (SA) = \frac{\text{Storage Footprint}}{\text{Active Logical Data}}$$
$$\text{Bloom Filter Bits per Key: } \frac{m}{n} = -\frac{\ln p}{(\ln 2)^2} \approx -1.44 \log_2(p)$$
For $p = 1\%$, $\frac{m}{n} \approx 9.6 \approx 10$ bits/key, with $k = \frac{m}{n} \ln 2 \approx 7$ hash functions.

### 1.7 Kubernetes Horizontal Pod Autoscaler (HPA)
$$R = \left\lceil C \times \frac{M_{\text{current}}}{M_{\text{target}}} \right\rceil$$
Tolerance band: if $\left| \frac{M_{\text{current}}}{M_{\text{target}}} - 1.0 \right| \le 0.10$, $R = C$ (prevents flapping).

---

## 2. RAPID RECALL COMPARISON TABLES

### 2.1 Attention Variants Comparison

| Architecture | Query Heads ($H_Q$) | Key/Value Heads ($H_{KV}$) | KV Memory Footprint | Serving Throughput |
| :--- | :--- | :--- | :--- | :--- |
| **Multi-Head Attention (MHA)** | $H$ | $H$ | Baseline ($1.0 \times$) | Baseline |
| **Multi-Query Attention (MQA)** | $H$ | $1$ | $\frac{1}{H} \times$ (Up to $97\%$ reduction) | Ultra-High |
| **Grouped-Query Attention (GQA)** | $H$ | $G \ll H$ (e.g. 8) | $\frac{G}{H} \times$ (Balance quality/speed) | High (LLaMA-3 default) |

### 2.2 Storage Engine Architecture Matrix

| Dimension | B-Tree (InnoDB, PostgreSQL) | LSM-Tree (RocksDB, Cassandra) |
| :--- | :--- | :--- |
| **Primary Ingestion Path** | In-place random page writes | Append-only sequential WAL + MemTable |
| **Write Amplification ($WA$)** | High ($10 - 40$) | Low to Medium ($2 - 12$) |
| **Read Amplification ($RA$)** | Low ($1 - 3$ page I/Os) | Bounded by Bloom Filters ($\le 1.1$ I/O) |
| **Space Amplification ($SA$)** | Low to Medium ($1.3 - 2.0$) | Leveled Compaction: Low ($1.11$) |
| **Compaction Strategies** | Page defragmentation / Vacuum | Size-Tiered (STCS) or Leveled (LCS) |

---

## 3. HIGH-PROBABILITY EXAM & INTERVIEW QUESTIONS

1. **Why does dividing by $\sqrt{d_k}$ in scaled dot-product attention prevent vanishing gradients?**
   - *Answer:* For independent components of $q$ and $k$ with zero mean and unit variance, their inner product $\sum_{i=1}^{d_k} q_i k_i$ has variance $\text{Var} = d_k$. As dimension $d_k$ grows large, values diverge into extremes, driving softmax output to 0 or 1 where the softmax derivative $\sigma(x)(1 - \sigma(x))$ approaches zero, extinguishing gradient propagation. Dividing by $\sqrt{d_k}$ normalizes variance back to $1.0$.

2. **In an LSM-Tree, how does Leveled Compaction eliminate overlapping keys across files in levels $L_1$ through $L_k$?**
   - *Answer:* When a level $L_i$ exceeds its byte quota, one SSTable is selected and merged with all SSTables in level $L_{i+1}$ whose key ranges overlap with it. The resulting merged SSTables are partitioned into fixed-size chunks (e.g., 64MB) with strictly disjoint non-overlapping key ranges, guaranteeing that any key appears in at most one SSTable per level.

3. **How does Kubernetes Kube-Scheduler ensure high availability during Pod placement?**
   - *Answer:* Through the `InterPodAntiAffinity` and `TopologySpreadConstraints` scoring and filtering plugins, which evaluate node labels (e.g., `topology.kubernetes.io/zone`) to distribute replicas across distinct failure domains (racks or availability zones), preventing single-zone cluster outages from taking down the service.
