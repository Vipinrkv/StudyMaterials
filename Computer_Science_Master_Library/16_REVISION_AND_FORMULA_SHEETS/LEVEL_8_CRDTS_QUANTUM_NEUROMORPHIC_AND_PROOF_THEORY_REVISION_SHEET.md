# LEVEL 8 REVISION & FORMULA SHEET: EMPIRICAL METHODS, CRDTS, QUANTUM COMPUTING, NEUROMORPHIC & THEOREM PROVING

---

## 1. ACADEMIC RESEARCH & EMPIRICAL BENCHMARKS

### Coordinated Omission Correction
$$\text{Missing Count} = \left\lfloor \frac{R}{\Delta} \right\rfloor - 1$$
$$\text{Injected Sample } k: \quad \text{Latency}_k = R - k \cdot \Delta \quad (k \in \{1, \dots, \text{Missing Count}\})$$

### Mann-Whitney U Non-Parametric Rank Statistic
$$U_1 = R_1 - \frac{n_1(n_1 + 1)}{2}, \quad U_2 = R_2 - \frac{n_2(n_2 + 1)}{2}, \quad U_1 + U_2 = n_1 n_2$$

### Percentile Bootstrap Confidence Interval
$$\text{CI}_{1-\alpha} = \left[ \hat{\theta}^*_{(\alpha/2)}, \quad \hat{\theta}^*_{(1 - \alpha/2)} \right]$$

---

## 2. CONFLICT-FREE REPLICATED DATA TYPES (CRDTS)

### Join-Semilattice Properties of Merge ($\sqcup$)
1. **Commutativity:** $x \sqcup y = y \sqcup x$
2. **Associativity:** $(x \sqcup y) \sqcup z = x \sqcup (y \sqcup z)$
3. **Idempotence:** $x \sqcup x = x$

### Core CRDT Equations
- **PN-Counter:** $\text{Val} = \sum P_i - \sum N_i$; $\text{Merge}(P) = \max(P_A, P_B)$, $\text{Merge}(N) = \max(N_A, N_B)$.
- **OR-Set (Observed-Remove):** $\text{Active} = \text{AddSet} \setminus \text{RemoveSet}$; Add creates unique tag $(e, \text{uuid})$.

---

## 3. QUANTUM COMPUTING & LOGIC GATES

### Qubit Normalization & Born Measurement
$$|\psi\rangle = \alpha |0\rangle + \beta |1\rangle, \quad |\alpha|^2 + |\beta|^2 = 1, \quad P(0) = |\alpha|^2, \quad P(1) = |\beta|^2$$

### Bloch Sphere Coordinate Mapping
$$|\psi\rangle = \cos\left(\frac{\theta}{2}\right) |0\rangle + e^{i\phi} \sin\left(\frac{\theta}{2}\right) |1\rangle$$

### Foundational Quantum Unitary Gates
$$H = \frac{1}{\sqrt{2}}\begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}, \quad X = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}, \quad Z = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}$$
$$\text{CNOT} = \begin{pmatrix} 1 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 0 & 1 \\ 0 & 0 & 1 & 0 \end{pmatrix}, \quad |\Phi^+\rangle = \text{CNOT}(H \otimes I)|00\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}$$

---

## 4. NEUROMORPHIC COMPUTING & SNNs

### Leaky Integrate-and-Fire (LIF) Differential Equation
$$\tau_m \frac{dV(t)}{dt} = -(V(t) - V_{\text{rest}}) + R_m I(t), \quad \text{Spike if } V(t) \ge V_{\text{th}} \implies V(t^+) = V_{\text{reset}}$$

### Spike-Timing-Dependent Plasticity (STDP) Rule
$$\Delta w = \begin{cases} 
A_+ \exp(-\Delta t / \tau_+) & \text{if } \Delta t = t_{\text{post}} - t_{\text{pre}} > 0 \quad (\text{LTP / Causal}) \\
-A_- \exp(\Delta t / \tau_-) & \text{if } \Delta t = t_{\text{post}} - t_{\text{pre}} < 0 \quad (\text{LTD / Acausal})
\end{cases}$$

### In-Memory Matrix Multiplication (Kirchhoff's & Ohm's Laws)
$$I_j = \sum_{i=1}^N V_i G_{i,j} \implies I = V^T G \quad (O(1) \text{ time physical vector-matrix multiply})$$

---

## 5. INTERACTIVE THEOREM PROVING & CURRY-HOWARD

### The Curry-Howard Mapping
$$A \implies B \quad \Longleftrightarrow \quad A \to B \quad (\text{Function Type / Lambda Abstraction})$$
$$A \land B \quad \Longleftrightarrow \quad A \times B \quad (\text{Product Type / Pair Constructor})$$
$$\forall x:A, B(x) \quad \Longleftrightarrow \quad \Pi (x : A), B(x) \quad (\text{Dependent Function Type})$$
$$\exists x:A, B(x) \quad \Longleftrightarrow \quad \Sigma (x : A), B(x) \quad (\text{Dependent Pair Type})$$

---

## 6. QUICK-FIRE EXAM REVISION MATRIX

| Term | Formal Definition / Core Equation | Key Real-World Tool / Reference |
| :--- | :--- | :--- |
| **Coordinated Omission** | In synchronous clients, server pauses omit incoming requests | Gil Tene, HdrHistogram |
| **SEC Convergence** | Replicas with same updates have identical states without consensus | CRDTs, Shapiro 2011, Yjs |
| **No-Cloning Theorem** | Unitary physics cannot duplicate an unknown state $|\psi\rangle$ | Wootters & Zurek 1982 |
| **LIF Neuron** | $\tau_m \dot{V} = -(V - V_{\text{rest}}) + R_m I$ | Intel Loihi 2, snnTorch |
| **STDP Learning** | Causal $\Delta t > 0 \implies \text{LTP}$; Acausal $\Delta t < 0 \implies \text{LTD}$ | Bi & Poo 1998 |
| **Curry-Howard** | Propositions as Types, Proofs as Programs | Lean 4, Coq, seL4 Microkernel |
