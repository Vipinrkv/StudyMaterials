"""
ch05_ai_safety_alignment_lab.py
Level 8 Chapter 05 Companion Laboratory: AI Safety, Mechanistic Interpretability & Alignment.
Simulates Sparse Autoencoder (SAE) Overcomplete Dictionary Learning,
Contrastive Activation Steering, and Direct Preference Optimization (DPO) Bradley-Terry Loss.
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

        random.seed(42)
        self.W_enc = [[random.gauss(0, 0.1) for _ in range(d_hidden)] for _ in range(d_in)]
        self.W_dec = [[random.gauss(0, 0.1) for _ in range(d_in)] for _ in range(d_hidden)]
        self.b_enc = [0.0] * d_hidden
        self.b_dec = [0.0] * d_in

    def encode(self, x: List[float]) -> List[float]:
        centered = [x[i] - self.b_dec[i] for i in range(self.d_in)]
        features = [0.0] * self.d_hidden
        for j in range(self.d_hidden):
            val = sum(centered[i] * self.W_enc[i][j] for i in range(self.d_in)) + self.b_enc[j]
            features[j] = max(0.0, val)
        return features

    def decode(self, f: List[float]) -> List[float]:
        x_hat = list(self.b_dec)
        for i in range(self.d_in):
            x_hat[i] += sum(f[j] * self.W_dec[j][i] for j in range(self.d_hidden))
        return x_hat

    def compute_loss(self, x: List[float], x_hat: List[float], f: List[float]) -> Tuple[float, float, float]:
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
        dim = len(harmful_acts[0])
        n_harmful = len(harmful_acts)
        n_harmless = len(harmless_acts)

        mean_harmful = [sum(harmful_acts[k][i] for k in range(n_harmful)) / n_harmful for i in range(dim)]
        mean_harmless = [sum(harmless_acts[k][i] for k in range(n_harmless)) / n_harmless for i in range(dim)]

        return [mean_harmful[i] - mean_harmless[i] for i in range(dim)]

    @staticmethod
    def apply_steering(x: List[float], v_steer: List[float], multiplier: float = 1.0) -> List[float]:
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
        log_ratio_w = logp_pi_w - logp_ref_w
        log_ratio_l = logp_pi_l - logp_ref_l
        implicit_reward_diff = beta * (log_ratio_w - log_ratio_l)
        prob = cls.sigmoid(implicit_reward_diff)
        return -math.log(max(1e-12, prob))


def main() -> None:
    print("=" * 70)
    print("LEVEL 8 CHAPTER 05: AI SAFETY, INTERPRETABILITY & ALIGNMENT LAB")
    print("=" * 70)

    # 1. Test Sparse Autoencoder Dictionary Extraction
    print("\n[Test 1] Testing Sparse Autoencoder (SAE) Monosemantic Encoding...")
    sae = SparseAutoencoder(d_in=16, d_hidden=64, l1_lambda=0.05)
    test_activation = [random.uniform(-1.0, 1.0) for _ in range(16)]

    features = sae.encode(test_activation)
    reconstructed = sae.decode(features)
    loss, l2_err, l1_pen = sae.compute_loss(test_activation, reconstructed, features)

    active_count = sum(1 for v in features if v > 0.0)
    sparsity_pct = (1.0 - (active_count / len(features))) * 100.0

    assert len(features) == 64
    assert len(reconstructed) == 16
    print(f"  -> Input Dim: 16 -> Dictionary Dim: 64 ({active_count} active features, {sparsity_pct:.1f}% sparse).")
    print(f"  -> Total Loss: {loss:.4f} (L2 Reconstruction: {l2_err:.4f}, L1 Sparsity: {l1_pen:.4f}).")

    # 2. Test Contrastive Activation Steering
    print("\n[Test 2] Testing Contrastive Activation Steering Vector...")
    harmful_acts = [[random.uniform(0.5, 1.5) for _ in range(8)] for _ in range(10)]
    harmless_acts = [[random.uniform(-1.5, -0.5) for _ in range(8)] for _ in range(10)]

    v_steer = ActivationSteeringEngine.compute_steering_vector(harmful_acts, harmless_acts)
    assert len(v_steer) == 8
    assert all(val > 0.0 for val in v_steer), "Steering vector should point towards harmful direction"

    neutral_prompt_act = [0.0] * 8
    # Steer in negative direction (suppress harmful behavior)
    aligned_act = ActivationSteeringEngine.apply_steering(neutral_prompt_act, v_steer, multiplier=-1.0)
    assert all(val < 0.0 for val in aligned_act)
    print(f"  -> Refusal Steering Vector Computed: Average shift {sum(v_steer)/len(v_steer):.2f}.")
    print("  -> Inference-Time Steering Applied: Successfully shifted towards harmless manifold.")

    # 3. Test Direct Preference Optimization (DPO) Loss
    print("\n[Test 3] Testing Direct Preference Optimization (DPO) Bradley-Terry Loss...")
    # Case A: Well-aligned policy (Preferred prompt has much higher likelihood than dispreferred)
    loss_aligned = DpoLossEvaluator.compute_dpo_loss(
        logp_pi_w=-2.0, logp_ref_w=-5.0,  # Ratio = +3.0
        logp_pi_l=-8.0, logp_ref_l=-5.0,  # Ratio = -3.0
        beta=0.1
    )
    # Implicit reward difference = 0.1 * (3 - (-3)) = 0.6 -> Loss is low
    print(f"  -> Well-Aligned Policy DPO Loss: {loss_aligned:.4f}")

    # Case B: Degraded policy (Model prefers harmful response)
    loss_misaligned = DpoLossEvaluator.compute_dpo_loss(
        logp_pi_w=-8.0, logp_ref_w=-5.0,  # Ratio = -3.0
        logp_pi_l=-2.0, logp_ref_l=-5.0,  # Ratio = +3.0
        beta=0.1
    )
    print(f"  -> Misaligned Policy DPO Loss: {loss_misaligned:.4f}")

    assert loss_aligned < loss_misaligned, "Aligned policy must have lower DPO loss than misaligned policy!"
    print("  -> DPO Relative Margin Invariant: Verified.")

    print("\n" + "=" * 70)
    print("ALL AI SAFETY & ALIGNMENT TESTS PASSED (Exit Code 0).")
    print("=" * 70)
    sys.exit(0)


if __name__ == "__main__":
    main()
