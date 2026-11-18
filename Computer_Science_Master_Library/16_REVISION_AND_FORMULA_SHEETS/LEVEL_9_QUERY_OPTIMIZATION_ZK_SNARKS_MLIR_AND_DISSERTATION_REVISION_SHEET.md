# LEVEL 9 REVISION & FORMULA SHEET: QUERY OPTIMIZATION, ZK-SNARKS, MLIR & DISSERTATION

**Target Level:** Level 9 (Veteran Expert & Innovator — Batch 2: Chapters 06–10)  
**Target Degrees:** M.Tech SE, PhD in CS / Software Engineering, Chief Scientist Certification  
**Core Purpose:** High-yield reference formulas, formal invariants, proof sketches, and operational runbooks.

---

## 1. Database Query Optimization & Cascades Memo (CH06)

### 1.1 Combinatorial Join Space Formulas
- **Left-Deep Trees:** $N_{\text{Left-Deep}}(n) = n!$
- **Bushy Trees (including cross products):**
  $$N_{\text{Bushy}}(n) = \frac{(2n-2)!}{(n-1)!} = (2n-3)!! \times n!$$
  For $n=5 \implies 1,680$. For $n=10 \implies 1.76 \times 10^9$. For $n=15 \implies 8.7 \times 10^{16}$.

### 1.2 DPsub Bellman Recurrence
$$C(S) = \min_{S_1 \subset S, S_2 = S \setminus S_1} \Big( C(S_1) + C(S_2) + \text{Cost}(\text{Join}(S_1, S_2)) \Big)$$

### 1.3 Hash Join Cost Model
$$\text{Cost}(\text{HashJoin}) = c_{\text{build}} \cdot |R_{\text{build}}| + c_{\text{probe}} \cdot |R_{\text{probe}}|$$
Where $|R_{\text{build}}| \le |R_{\text{probe}}|$. Output size: $|R_{\text{out}}| = |R_1| \cdot |R_2| \cdot \text{Selectivity}$.

---

## 2. Zero-Knowledge Proofs & Succinct Arguments (CH07)

### 2.1 Rank-1 Constraint System (R1CS)
$$(A \vec{s}) \circ (B \vec{s}) = (C \vec{s})$$
Where:
- $A, B, C \in \mathbb{F}_p^{m \times n}$.
- $\vec{s} = [1, x_1, \dots, x_l, w_1, \dots, w_k]^T \in \mathbb{F}_p^n$.
- $\circ$ is the element-wise Hadamard product.

### 2.2 Quadratic Arithmetic Program (QAP)
$$P(x) = \left( \sum_{i=1}^n s_i A_i(x) \right) \cdot \left( \sum_{i=1}^n s_i B_i(x) \right) - \left( \sum_{i=1}^n s_i C_i(x) \right)$$
Divisibility Invariant:
$$P(x) = H(x) \cdot T(x) \quad \text{where } T(x) = \prod_{j=1}^m (x - r_j)$$

### 2.3 Groth16 Bilinear Pairing Verification
$$e([A]_1, [B]_2) = e([\alpha]_1, [\beta]_2) \cdot e\left(\sum_{i=0}^l x_i \left[ \frac{\beta A_i(\tau) + \alpha B_i(\tau) + C_i(\tau)}{\gamma} \right]_1, [\gamma]_2 \right) \cdot e([C]_1, [\delta]_2)$$
- Proof size: Constant 3 group elements ($[A]_1 \in G_1, [B]_2 \in G_2, [C]_1 \in G_1$). Constant $\sim 2.5\text{ ms}$ verification.

---

## 3. Domain-Specific Accelerators & MLIR (CH08)

### 3.1 Polyhedral Loop Model
$$\mathcal{D} = \{ \vec{i} \in \mathbb{Z}^n \mid A \vec{i} + \vec{b} \ge \vec{0} \}$$
- Data dependence distance: $\vec{d} = \vec{j} - \vec{i}$ where $\vec{i} \prec \vec{j}$ and accesses collide.

### 3.2 Schedule Legality Criterion
A linear transformation schedule matrix $T$ is legal if and only if:
$$\forall \vec{d} \in \mathcal{D}_{\text{dependences}}: \quad T \vec{d} \succ_{\text{lex}} \vec{0}$$

### 3.3 MLIR Progressive Lowering Cascade
$$\text{torch / tosa} \xrightarrow{\text{tensor ops}} \text{linalg} \xrightarrow{\text{tiling/fusion}} \text{affine / scf} \xrightarrow{\text{vectorize}} \text{vector} \xrightarrow{\text{codegen}} \text{LLVM IR / TPU microcode}$$

---

## 4. Hardware Side Channels & Critical Defense (CH09)

### 4.1 Speculative Execution (Spectre) Timing Metric
$$\Delta t(k) = \text{AccessTime}\big(\&array2[k \times 64]\big)$$
$$\text{Secret Byte} = \arg\min_{k} \Delta t(k) \quad (\text{Cache Hit } \approx 15\text{ cycles vs. RAM Miss } \approx 200\text{ cycles})$$

### 4.2 DRAM Rowhammer Charge Dissipation
$$Q(t) = Q_0 - \sum \Delta Q_{\text{leakage}} \le Q_{\text{threshold}} \implies \text{Physical Bit Flip } (0 \to 1)$$
- **Defense:** Target Row Refresh (TRR) proactively replenishes adjacent victim row capacitors.

### 4.3 SCADA Hardware Air-Gap & Optical Diode
- **Physical Simplex Invariant:** Egress channel enabled via optical fiber; reverse ingress laser physically removed, making packet injection physically impossible.

---

## 5. Academic Dissertation & Empirical Methodology (CH10)

### 5.1 Welch's $t$-Test Formulation
$$t = \frac{\mu_1 - \mu_2}{\sqrt{\frac{s_1^2}{N_1} + \frac{s_2^2}{N_2}}}$$
$$\text{Degrees of Freedom } \nu \approx \frac{\left(\frac{s_1^2}{N_1} + \frac{s_2^2}{N_2}\right)^2}{\frac{(s_1^2 / N_1)^2}{N_1 - 1} + \frac{(s_2^2 / N_2)^2}{N_2 - 1}}$$
- Reject null hypothesis $\mathcal{H}_0$ if $p < 0.001$.

### 5.2 ACM Artifact Evaluation Badges
1. **Artifacts Available:** Permanently archived with persistent DOI (Zenodo / Figshare).
2. **Artifacts Evaluated - Functional:** Documented, consistent, and complete.
3. **Results Replicated:** Independent evaluation replicates main quantitative claims within tolerance $\epsilon$.
