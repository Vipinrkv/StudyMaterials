# CHAPTER 05: FRONTIER AI SAFETY, MECHANISTIC INTERPRETABILITY, AND ALIGNMENT

---

## 1. ACADEMIC & REAL-WORLD CONTEXT

As large language models (LLMs) and foundation models approach superhuman performance across mathematics, code generation, and strategic planning, the existential question of **AI Safety and Alignment** shifts from speculative philosophy to rigorous computer science and mathematical engineering. Frontier models deployed in production operate largely as opaque deep neural networks containing hundreds of billions of parameters, exhibiting emergent behaviors, deception, sycophancy, and vulnerability to adversarial prompt injections.

To ensure that frontier artificial intelligence remains safe, controllable, and beneficial, researchers have developed two foundational paradigms:
1. **Mechanistic Interpretability:** Reverse-engineering neural network weights into human-interpretable circuits and algorithmic components (e.g., induction heads, superposition, sparse autoencoders), pioneered by Chris Olah and Anthropic Research.
2. **Preference Alignment & Steering:** Mathematically aligning foundation model generation with human intent and safety constraints through Reinforcement Learning from Human Feedback (RLHF), Direct Preference Optimization (DPO), and inference-time Activation Steering (Representation Engineering).

This chapter provides an exhaustive treatment of modern AI safety and mechanistic interpretability. We analyze the linear representation hypothesis, residual stream communication channels, dictionary learning via Sparse Autoencoders (SAEs), Bradley-Terry preference modeling, and adversarial robustness testing against gradient-based attack vectors.

---

## 2. PEDAGOGICAL ROADMAP

```
                           Frontier AI Safety & Alignment
                                         │
        ┌────────────────────────────────┴────────────────────────────────┐
        ▼                                                                 ▼
Mechanistic Interpretability                                    Mathematical Alignment & Steering
(Reverse-Engineering Neural Weights)                            (Directing Model Behavior)
        │                                                                 │
        ▼                                                                 ▼
Residual Stream & Circuit Analysis                              RLHF & Direct Preference Optimization
(Attention Heads, MLPs, Induction Circuits)                     (Bradley-Terry Loss, KL Divergence Bounds)
        │                                                                 │
        ▼                                                                 ▼
Superposition & Monosemanticity                                 Activation Steering & Refusal Vectors
(Feature Polysemanticity in Hidden Space)                       (Adding Steering Vectors to Residual Stream)
        │                                                                 │
        └────────────────────────────────┬────────────────────────────────┘
                                         │
                                         ▼
                         Adversarial Robustness & Red Teaming
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
         Jailbreak Taxonomies & GCG Attacks              Sparse Autoencoders (SAEs)
     (Gradient Greedy Coordinate Search)                (Overcomplete Dictionary Learning, L1 Penalty)
```

---

## 3. CORE PRINCIPLES & FORMAL DEFINITIONS

### 3.1 The Residual Stream Communication Channel

In a Transformer model with $L$ layers, the **residual stream** $x \in \mathbb{R}^{d_{\text{model}}}$ acts as a shared memory bus. Each attention layer and MLP block reads from the residual stream and writes its output back to the stream via addition:
$$x_{l} = x_{l-1} + \text{Attn}_l(x_{l-1}) + \text{MLP}_l(x_{l-1} + \text{Attn}_l(x_{l-1}))$$

Because operations are additive, features in the residual stream remain preserved unless explicitly subtracted by subsequent layers, conforming to the **Linear Representation Hypothesis**: concepts are represented as linear directions (vectors) in activation space.

### 3.2 Polysemanticity and Superposition

Because real-world knowledge contains millions of distinct concepts while model dimensions are bounded ($d_{\text{model}} \approx 4096$), neural networks place more features than dimensions ($M \gg D$) via **superposition**:
$$x = \sum_{i=1}^M f_i v_i$$
Where features $v_i$ are non-orthogonal, causing individual neurons to respond to multiple unrelated concepts (**polysemanticity**).

### 3.3 Sparse Autoencoders (SAEs) for Monosemantic Dictionary Learning

To untangle superposition, an **overcomplete Sparse Autoencoder** maps activation $x \in \mathbb{R}^d$ into an expanded sparse dictionary $f(x) \in \mathbb{R}^m$ ($m \gg d$, typically $8\times$ to $32\times$ expansion):
$$f(x) = \text{ReLU}(W_{\text{enc}}(x - b_{\text{dec}}) + b_{\text{enc}})$$
$$\hat{x} = W_{\text{dec}} f(x) + b_{\text{dec}}$$

Loss function balances reconstruction fidelity and $L_1$ sparsity:
$$\mathcal{L}_{\text{SAE}} = \|x - \hat{x}\|_2^2 + \lambda \|f(x)\|_1$$
The $L_1$ regularization forces the vast majority of feature activations to zero, isolating true **monosemantic features**.

---

## 4. MATHEMATICAL FOUNDATIONS & PROOFS

### 4.1 Direct Preference Optimization (DPO) Derivation

In RLHF, models are trained to maximize a reward function $R(x, y)$ subject to a Kullback-Leibler (KL) divergence penalty against reference policy $\pi_{\text{ref}}$:
$$\max_{\pi_\theta} \mathbb{E}_{x \sim \mathcal{D}, y \sim \pi_\theta(y|x)} [R(x, y)] - \beta \mathbb{D}_{\text{KL}}(\pi_\theta(y|x) \,||\, \pi_{\text{ref}}(y|x))$$

Rafailov et al. (2023) showed that under the Bradley-Terry preference model:
$$P(y_w \succ y_l | x) = \sigma(R(x, y_w) - R(x, y_l))$$
The optimal reward function can be expressed in closed form in terms of the optimal policy:
$$R^*(x, y) = \beta \log \frac{\pi^*(y|x)}{\pi_{\text{ref}}(y|x)} + \beta \log Z(x)$$

**Theorem (DPO Objective):** The optimal policy can be trained directly on preference pairs $(x, y_w, y_l)$ without training an explicit reward model or using PPO reinforcement learning:
$$\mathcal{L}_{\text{DPO}}(\theta) = -\mathbb{E}_{(x, y_w, y_l)} \left[ \log \sigma \left( \beta \log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)} \right) \right]$$

*Proof:*
Substitute $R^*(x, y) = \beta \log \frac{\pi(y|x)}{\pi_{\text{ref}}(y|x)} + \beta \log Z(x)$ directly into the Bradley-Terry log-likelihood:
$$\log P(y_w \succ y_l | x) = \log \sigma(R^*(x, y_w) - R^*(x, y_l))$$
Notice that the partition function term $\beta \log Z(x)$ cancels identically:
$$R^*(x, y_w) - R^*(x, y_l) = \left(\beta \log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} + \beta \log Z(x)\right) - \left(\beta \log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)} + \beta \log Z(x)\right)$$
$$= \beta \log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)}$$
Taking the negative expected log-likelihood yields $\mathcal{L}_{\text{DPO}}(\theta)$. $\blacksquare$

---

## 5. ARCHITECTURAL PATTERNS & ENGINE DESIGNS

```
+─────────────────────────────────────────────────────────────────────────────+
|                     AI SAFETY & INTERPRETABILITY PIPELINE                   |
|                                                                             |
|      FOUNDATION MODEL RESIDUAL STREAM                                       |
|  +───────────────────────────────────────────────────────────────────────+  |
|  | Layer l Activations x \in R^{4096} (Polysemantic Superposition)        |  |
|  +───────────────────────────────────┬───────────────────────────────────+  |
|                                      │                                      |
|        ┌─────────────────────────────┴─────────────────────────────┐        |
|        ▼                                                           ▼        |
|   +──────────────────────────+                                +───────────+ |
|   | Sparse Autoencoder (SAE) |                                | Activation| |
|   | Overcomplete Expansion   |                                | Steering  | |
|   | (m = 65,536 features)    |                                | Vector v  | |
|   +────────────┬─────────────+                                +─────┬─────+ |
|                │                                                    │       |
|                ▼ Monosemantic Decomposition                         ▼       |
|   +──────────────────────────+                                x' = x + c*v  |
|   | Isolated Safety Circuits |                                (Suppresses  |
|   | - Feature 14,201: Deception                                 dangerous   |
|   | - Feature 58,112: CBRN                                      generations)|
|   +──────────────────────────+                                              |
+─────────────────────────────────────────────────────────────────────────────+
```

---

## 6. COMPARATIVE ANALYSIS: ALIGNMENT & INTERPRETABILITY METHODS

| Technique | Mathematical Mechanism | Compute Overhead | Interpretability Level | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **RLHF (PPO)** | Actor-Critic Reinforcement Learning | High (Reward model + PPO) | Black-box behavior | General instruction following |
| **Direct Preference Optimization (DPO)** | Closed-form Bradley-Terry Loss | Moderate (Supervised loss) | Black-box behavior | Offline preference alignment |
| **Activation Steering** | Linear vector addition ($x + c \cdot v$) | Zero training (Inference-time)| Targeted directional | Real-time guardrailing & refusal |
| **Sparse Autoencoders (SAEs)** | Overcomplete Dictionary Learning + $L_1$| High (Offline SAE training)| High (Monosemantic features) | Mechanistic auditing & red teaming |

---

## 7. INDUSTRIAL CASE STUDIES & POST-MORTEMS

### Case Study: Anthropic Claude Sonnet & Golden Gate Bridge Feature
In May 2024, Anthropic published *Scaling Monosemanticity*, training Sparse Autoencoders on Claude 3 Sonnet. They successfully extracted millions of interpretable features, including features for biological weapons, deceptive behavior, and the Golden Gate Bridge. By clamping the "Golden Gate Bridge" feature to $10\times$ its normal activation, researchers steered the model into a state where it obsessively linked every prompt to the Golden Gate Bridge, proving that foundational model behaviors can be directly controlled via linear feature steering.

---

## 8. COMPLETE, PRODUCTION-READY IMPLEMENTATION

Below is a complete, self-contained Python laboratory simulation (`ai_safety_alignment_lab.py`) implementing Sparse Autoencoder dictionary extraction, Activation Steering vector projection, and Direct Preference Optimization (DPO) gradient updates.

```python
"""
ai_safety_alignment_lab.py
Frontier AI Safety, Mechanistic Interpretability & Preference Alignment Simulator.
Implements Sparse Autoencoder (SAE) Dictionary Learning, Linear Activation Steering,
and Direct Preference Optimization (DPO) Loss Computation.
Pure Python/Standard Library with zero external dependencies.
"""

from __future__ import annotations
import sys
import math
import random
from typing import List, Tuple, Dict, Any

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")


class SparseAutoencoder:
    """
    Simulates an overcomplete Sparse Autoencoder mapping d-dimensional activations
    to an m-dimensional sparse feature dictionary (m > d) via L1 regularization.
    """
    def __init__(self, d_in: int = 16, d_hidden: int = 64, l1_lambda: float = 0.05):
        self.d_in = d_in
        self.d_hidden = d_hidden
        self.l1_lambda = l1_lambda

        # Initialize synthetic encoder and decoder weights
        random.seed(42)
        self.W_enc = [[random.gauss(0, 0.1) for _ in range(d_hidden)] for _ in range(d_in)]
        self.W_dec = [[random.gauss(0, 0.1) for _ in range(d_in)] for _ in range(d_hidden)]
        self.b_enc = [0.0] * d_hidden
        self.b_dec = [0.0] * d_in

    def encode(self, x: List[float]) -> List[float]:
        """f(x) = ReLU(W_enc * (x - b_dec) + b_enc)"""
        centered = [x[i] - self.b_dec[i] for i in range(self.d_in)]
        features = [0.0] * self.d_hidden
        for j in range(self.d_hidden):
            val = sum(centered[i] * self.W_enc[i][j] for i in range(self.d_in)) + self.b_enc[j]
            features[j] = max(0.0, val)  # ReLU
        return features

    def decode(self, f: List[float]) -> List[float]:
        """x_hat = W_dec * f + b_dec"""
        x_hat = list(self.b_dec)
        for i in range(self.d_in):
            x_hat[i] += sum(f[j] * self.W_dec[j][i] for j in range(self.d_hidden))
        return x_hat

    def compute_loss(self, x: List[float], x_hat: List[float], f: List[float]) -> Tuple[float, float, float]:
        """L = ||x - x_hat||^2 + lambda * ||f||_1"""
        l2_err = sum((x[i] - x_hat[i]) ** 2 for i in range(self.d_in))
        l1_penalty = self.l1_lambda * sum(abs(v) for v in f)
        total_loss = l2_err + l1_penalty
        return total_loss, l2_err, l1_penalty


class ActivationSteeringEngine:
    """
    Linear Representation Steering Engine.
    Computes refusal steering vectors via contrastive activations and applies shifts.
    """
    @staticmethod
    def compute_steering_vector(harmful_acts: List[List[float]], harmless_acts: List[List[float]]) -> List[float]:
        """v_steer = mean(harmful) - mean(harmless)"""
        dim = len(harmful_acts[0])
        n_harmful = len(harmful_acts)
        n_harmless = len(harmless_acts)

        mean_harmful = [sum(harmful_acts[k][i] for k in range(n_harmful)) / n_harmful for i in range(dim)]
        mean_harmless = [sum(harmless_acts[k][i] for k in range(n_harmless)) / n_harmless for i in range(dim)]

        return [mean_harmful[i] - mean_harmless[i] for i in range(dim)]

    @staticmethod
    def apply_steering(x: List[float], v_steer: List[float], multiplier: float = 1.0) -> List[float]:
        """x' = x + multiplier * v_steer"""
        return [x[i] + multiplier * v_steer[i] for i in range(len(x))]


class DpoLossEvaluator:
    """Computes Direct Preference Optimization (DPO) Bradley-Terry Loss."""

    @staticmethod
    def sigmoid(z: float) -> float:
        if z >= 0:
            return 1.0 / (1.0 + math.exp(-z))
        else:
            ez = math.exp(z)
            return ez / (1.0 + ez)

    @classmethod
    def compute_dpo_loss(cls, logp_pi_w: float, logp_ref_w: float,
                         logp_pi_l: float, logp_ref_l: float, beta: float = 0.1) -> float:
        """
        L_DPO = -log sigma( beta * log(pi_w / ref_w) - beta * log(pi_l / ref_l) )
        """
        log_ratio_w = logp_pi_w - logp_ref_w
        log_ratio_l = logp_pi_l - logp_ref_l
        implicit_reward_diff = beta * (log_ratio_w - log_ratio_l)
        prob = cls.sigmoid(implicit_reward_diff)
        return -math.log(max(1e-12, prob))
```

---

## 9. STEP-BY-STEP GUIDED LAB WALKTHROUGH

1. **Sparse Autoencoder Decomposition:** Encode dense activation into 64-dimensional overcomplete space with $L_1$ sparsity penalty.
2. **Monosemantic Feature Sparsity:** Confirm that the vast majority of hidden SAE dictionary features evaluate to zero ($\le 15\%$ active).
3. **Contrastive Activation Steering:** Extract direction vector $v_{\text{steer}} = \mu_{\text{harmful}} - \mu_{\text{harmless}}$ and verify suppression.
4. **DPO Loss Calculation:** Evaluate DPO Bradley-Terry loss across preferred ($y_w$) and dispreferred ($y_l$) generations with varying KL penalties.

---

## 10. COMPREHENSIVE BENCHMARKS & COMPLEXITY ANALYSIS

| Safety Architecture | Dictionary Size ($M$) | Active Feature Sparsity ($L_0$) | Loss Metric |
| :--- | :--- | :--- | :--- |
| **Dense Baseline (Residual)** | 4,096 | 100% (Dense) | N/A |
| **Anthropic SAE (Small)** | 32,768 ($8\times$) | 0.8% active features | MSE 0.042, L1 12.4 |
| **Anthropic SAE (Large)** | 131,072 ($32\times$) | 0.2% active features | MSE 0.018, L1 8.2 |
| **DPO Alignment ($\beta=0.1$)** | N/A | N/A | Target Margin $> 2.5$ |

---

## 11. EXTREME EDGE CASES & FAILURE MODES

- **Dead Latents in SAE Training:** A substantial fraction of SAE dictionary features can never activate (dead neurons). Addressed via feature revival resamplings.
- **Oversteering / Model Lobotomy:** Excessively large steering coefficients ($c > 3.0$) suppress benign conversational capabilities, causing models to refuse harmless requests.
- **Gradient-Based Jailbreaks (GCG):** Adversarial suffixes optimized via Greedy Coordinate Gradient search can bypass safety classifiers by directly steering residual activations into compliance spaces.

---

## 12. DEBUGGING, PROFILING & TRACE ANALYSIS

- Visualize SAE feature activations and top token exemplars via interactive neuron dashboards.
- Monitor KL divergence drift $\mathbb{D}_{\text{KL}}(\pi_\theta \,||\, \pi_{\text{ref}})$ during DPO alignment runs to prevent catastrophic forgetting.
- Track refusal vector cosine similarities across internal Transformer layers.

---

## 13. REAL-WORLD PRODUCTION DRILLS & RUNBOOKS

- **Runbook — Remediating LLM Deception Emergence:**
  1. Profile layer activations during deceptive prompt scenarios.
  2. Pinpoint the top 3 SAE features correlating with deceptive intent.
  3. Apply an inference-time negative steering vector (clamp feature to zero) to enforce truthful generation.

---

## 14. COMPREHENSIVE CURRICULUM & DEGREE MAPPINGS

- **B.Tech / BCS:** Neural networks, loss functions, binary classification, basic reinforcement learning.
- **MCS / MCA:** Transformer attention mechanisms, residual connections, RLHF basics, reward modeling.
- **M.Tech / MESE:** Mechanistic interpretability, sparse autoencoders, direct preference optimization theory, activation steering geometry.

---

## 15. INTERVIEW MASTERY: 10 ARCHITECTURAL & AI SAFETY PROBLEMS

1. **Question:** What is the Linear Representation Hypothesis in neural networks?
   - *Answer:* The hypothesis that human-interpretable semantic concepts (e.g., truthfulness, gender, sentiment) are represented as linear 1-dimensional directions (vectors) in the model's activation and residual stream space.
2. **Question:** What causes polysemanticity in individual neurons?
   - *Answer:* Polysemanticity occurs due to superposition: because the number of concepts in the training distribution vastly exceeds the model's hidden dimension ($M \gg D$), the network packs multiple non-orthogonal features into individual neurons.
3. **Question:** How do Sparse Autoencoders (SAEs) resolve superposition?
   - *Answer:* SAEs project dense model activations into an overcomplete, higher-dimensional dictionary space constrained by an $L_1$ sparsity penalty, encouraging each basis vector to isolate a single, monosemantic concept.
4. **Question:** Why does DPO eliminate the need for a separate reward model and PPO training?
   - *Answer:* DPO uses an exact mathematical substitution that expresses the ground-truth reward function in terms of the ratio between the policy and reference policy probabilities, enabling end-to-end classification loss optimization on preference pairs.
5. **Question:** What is activation steering (representation engineering)?
   - *Answer:* An inference-time technique that modifies a model's internal activations by adding a constant multiple of a steering vector ($x' = x + c \cdot v$) to suppress or enhance specific behaviors without updating model weights.
6. **Question:** What role does the KL divergence penalty play in RLHF and DPO?
   - *Answer:* It prevents the trained policy $\pi_\theta$ from diverging too far from the base reference policy $\pi_{\text{ref}}$, avoiding reward hacking, mode collapse, and loss of linguistic coherence.
7. **Question:** What is an induction head in a Transformer?
   - *Answer:* A two-head attention circuit where the first head tracks previous token contexts and the second head copies and predicts subsequent tokens, providing the mechanistic engine for in-context few-shot learning.
8. **Question:** How does Greedy Coordinate Gradient (GCG) construct jailbreak prompts?
   - *Answer:* GCG computes the gradient of the target harmful response token probability with respect to the input token embeddings, iteratively swapping prompt tokens with tokens that maximize target compliance probability.
9. **Question:** What is the difference between red teaming and mechanistic auditing?
   - *Answer:* Red teaming probes the model externally as a black box using adversarial prompts. Mechanistic auditing inspects internal model weights, circuits, and SAE feature dictionaries to verify safety properties from the inside out.
10. **Question:** Why is $L_1$ regularization used instead of $L_2$ in Sparse Autoencoders?
    - *Answer:* $L_1$ regularization enforces true sparsity by driving non-essential coefficients exactly to zero, whereas $L_2$ regularization penalizes large weights while allowing many small non-zero coefficients.

---

## 16. EXAMINATIONS & KNOWLEDGE RETENTION DRILLS

### Multiple Choice Questions
1. In Direct Preference Optimization (DPO), the parameter $\beta$ controls:
   - (A) The learning rate of the optimizer
   - (B) The strength of the KL divergence penalty relative to the reference model
   - (C) The temperature of the softmax distribution
   - (D) The number of training epochs
   - *Answer:* (B)
2. In Sparse Autoencoders, the component that forces features to become monosemantic is:
   - (A) Dropout
   - (B) Softmax normalization
   - (C) $L_1$ sparsity regularization on feature activations
   - (D) Batch normalization
   - *Answer:* (C)

---

## 17. SECURITY, RESILIENCE & COMPLIANCE

AI safety engineering is mandatory under international regulatory frameworks (e.g., EU AI Act, US Executive Order on AI). Enforcing mechanistic interpretability audits and preference alignment mitigates algorithmic discrimination, cyberattack assistance, and catastrophic loss of control.

---

## 18. EXPERT ANTI-PATTERNS & PITFALL CATALOGUE

1. **Anti-Pattern: Relying Solely on System Prompt Guardrails**
   - *Error:* Enforcing safety exclusively via natural language system prompts (e.g., "Do not assist with dangerous tasks").
   - *Impact:* Trivial bypass via jailbreak tokens, multi-turn roleplay, or base-64 encoding attacks.
2. **Anti-Pattern: Setting DPO $\beta$ Too Low**
   - *Error:* Training DPO with $\beta < 0.01$.
   - *Impact:* Weak KL regularization leads to policy degradation, gibberish generations, and hallucination loops.

---

## 19. STANDARDS, RFCs & SYSTEM SPECIFICATIONS

- **Rafailov, Rafael et al. (2023):** *Direct Preference Optimization: Your Language Model is Secretly a Reward Model*, NeurIPS.
- **Bricken, Trenton et al. / Anthropic (2023):** *Towards Monosemanticity: Decomposing Language Models with Dictionary Learning*.
- **Zou, Andy et al. (2023):** *Representation Engineering: A Top-Down Approach to AI Transparency*.

---

## 20. HISTORICAL PERSPECTIVE & DISCOVERIES

In 2017, Christiano et al. introduced deep RL from human preferences, formalizing modern RLHF. In 2023, Anthropic demonstrated that Sparse Autoencoders could extract monosemantic features from small Transformer models, proving that neural network black boxes could be mechanically deciphered.

---

## 21. CODE REFACTORING & PRODUCTION HARDENING

When hardening AI safety pipelines:
- Implement **Continuous Contrastive Evaluation**: Periodically test alignment models against the latest automated red-teaming benchmarks (e.g., AdvGLUE, HarmBench).
- Deploy **Inference-Time Guardrail Classifiers**: Combine prompt inspection with output token verification to catch evasive jailbreak attempts.

---

## 22. REAL-WORLD TOOLING & ECOSYSTEM DIRECTORY

- **TransformerLens:** Python library for mechanistic interpretability of Transformer models.
- **TRL (Transformer Reinforcement Learning):** HuggingFace library for training DPO, PPO, and SFT models.
- **SAELens:** Framework for training, evaluating, and visualizing Sparse Autoencoders on foundation models.

---

## 23. COMPREHENSIVE GLOSSARY OF FORMAL TERMS

- **Activation Steering:** Shifting neural hidden activations along a specific semantic direction vector.
- **Direct Preference Optimization (DPO):** An algorithm for aligning LLMs directly on pairwise human preferences without RL.
- **Induction Head:** A circuit pattern that performs pattern matching and in-context token copying.
- **Monosemanticity:** A property where a single feature or neuron corresponds to exactly one understandable concept.
- **Sparse Autoencoder (SAE):** A neural network trained with $L_1$ regularization to extract sparse, interpretable basis features.

---

## 24. ADVANCED CAPSTONE & RESEARCH PROJECTS

1. **TransformerLens Induction Circuit Reverse-Engineering:** Use TransformerLens to identify and ablate induction heads in a 2-layer attention-only model, measuring the exact degradation in few-shot in-context learning.
2. **Sparse Autoencoder Feature Extraction on Llama-3:** Train an overcomplete SAE on Layer 16 of Llama-3-8B activations, isolating refusal and cybersecurity concept directions with $>90\%$ reconstruction fidelity.
