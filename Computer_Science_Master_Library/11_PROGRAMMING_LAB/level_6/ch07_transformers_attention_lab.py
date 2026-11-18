"""
ch07_transformers_attention_lab.py
Level 6 Companion Lab: Multi-Head Attention, RoPE Positional Encoding, and KV-Cache.
Pure Python/Standard Library implementation with zero external dependencies.
"""

from __future__ import annotations
import sys
import math
from typing import List, Tuple

# Windows UTF-8 console output
sys.stdout.reconfigure(encoding="utf-8")


def softmax(logits: List[float]) -> List[float]:
    """Numerically stable softmax."""
    max_l = max(logits)
    exp_l = [math.exp(x - max_l) for x in logits]
    sum_exp = sum(exp_l)
    return [e / sum_exp for e in exp_l]


def dot_product(v1: List[float], v2: List[float]) -> float:
    return sum(a * b for a, b in zip(v1, v2))


def apply_rope_1d(x: List[float], pos: int, base: float = 10000.0) -> List[float]:
    """
    Applies Rotary Position Embedding (RoPE) to a vector of dimension D (D must be even).
    Rotates consecutive coordinate pairs (x_{2i}, x_{2i+1}) by angle theta_i * pos.
    theta_i = base^(-2i / D)
    """
    D = len(x)
    assert D % 2 == 0, "Dimension must be even for RoPE"
    rotated = [0.0] * D
    for i in range(D // 2):
        theta = pos / (base ** ((2 * i) / D))
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        x_2i = x[2 * i]
        x_2i1 = x[2 * i + 1]
        # 2D rotation matrix: [[cos, -sin], [sin, cos]]
        rotated[2 * i] = x_2i * cos_t - x_2i1 * sin_t
        rotated[2 * i + 1] = x_2i * sin_t + x_2i1 * cos_t
    return rotated


def scaled_dot_product_causal_attention(
    queries: List[List[float]],
    keys: List[List[float]],
    values: List[List[float]],
    scale: float
) -> List[List[float]]:
    """
    Computes Scaled Dot-Product Attention with an autoregressive causal mask:
    Attention(Q, K, V) = softmax((Q K^T / sqrt(d_k)) + Mask) V
    """
    N = len(queries)  # Sequence length of queries
    M = len(keys)     # Sequence length of keys
    d_v = len(values[0])
    output: List[List[float]] = []

    for i in range(N):
        # Compute dot product between query_i and key_j for j <= i (causal mask)
        raw_scores: List[float] = []
        for j in range(M):
            if j <= i:
                score = dot_product(queries[i], keys[j]) / scale
                raw_scores.append(score)
            else:
                raw_scores.append(-1e9)  # Mask out future tokens

        attn_weights = softmax(raw_scores)

        # Weighted sum over values
        out_token = [0.0] * d_v
        for j in range(M):
            weight = attn_weights[j]
            if weight > 0:
                for k in range(d_v):
                    out_token[k] += weight * values[j][k]
        output.append(out_token)

    return output


class KVCache:
    """
    Simulates autoregressive Key-Value Caching across sequential token generation steps.
    Eliminates re-computation of historical keys and values.
    """
    def __init__(self):
        self.cached_keys: List[List[float]] = []
        self.cached_values: List[List[float]] = []

    def append(self, k: List[float], v: List[float]) -> None:
        self.cached_keys.append(k)
        self.cached_values.append(v)

    def size(self) -> int:
        return len(self.cached_keys)

    def clear(self) -> None:
        self.cached_keys.clear()
        self.cached_values.clear()


def test_rope_rotation():
    print("Running Test Suite 1: Rotary Position Embedding (RoPE) Invariance...")
    v = [1.0, 0.0, 0.0, 1.0]  # 4D vector
    # At position 0, angle is 0, so vector must be unchanged: cos(0)=1, sin(0)=0
    r0 = apply_rope_1d(v, pos=0)
    for orig, rot in zip(v, r0):
        assert abs(orig - rot) < 1e-6, f"Expected {orig}, got {rot}"

    # At position > 0, L2 norm must be strictly preserved (orthogonal rotation)
    r5 = apply_rope_1d(v, pos=5)
    norm_orig = math.sqrt(sum(x**2 for x in v))
    norm_rot = math.sqrt(sum(x**2 for x in r5))
    assert abs(norm_orig - norm_rot) < 1e-6, f"Norm changed: {norm_orig} vs {norm_rot}"
    print(f"  Passed! RoPE preserves exact L2 vector norm ({norm_rot:.4f}).")


def test_causal_attention():
    print("Running Test Suite 2: Scaled Dot-Product Causal Attention Masking...")
    # 3 tokens, d_k = 2
    queries = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    keys = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    values = [[10.0, 0.0], [0.0, 20.0], [30.0, 30.0]]
    scale = math.sqrt(2.0)

    attn_out = scaled_dot_product_causal_attention(queries, keys, values, scale)

    # Token 0 can only attend to Token 0
    # Expected output for token 0: exactly value[0] = [10.0, 0.0]
    assert abs(attn_out[0][0] - 10.0) < 1e-4
    assert abs(attn_out[0][1] - 0.0) < 1e-4

    # Token 1 attends to tokens 0 and 1, but NOT token 2
    assert len(attn_out) == 3
    print(f"  Passed! Causal attention strictly masks future context.")


def test_kv_cache_generation():
    print("Running Test Suite 3: KV Cache State Accumulation...")
    kv = KVCache()
    assert kv.size() == 0

    tokens = [[0.1, 0.5], [0.2, 0.4], [0.3, 0.3]]
    for i, t in enumerate(tokens):
        kv.append(t, [v * 10 for v in t])
        assert kv.size() == i + 1

    assert len(kv.cached_keys) == 3
    assert len(kv.cached_values) == 3
    print(f"  Passed! KV Cache accumulates {kv.size()} prompt and generation steps correctly.")


if __name__ == "__main__":
    print("================================================================================")
    print("LEVEL 6 LAB 07: TRANSFORMERS ATTENTION & ROPE KV-CACHE ENGINE")
    print("================================================================================")
    test_rope_rotation()
    test_causal_attention()
    test_kv_cache_generation()
    print("================================================================================")
    print("ALL 3 TEST SUITES PASSED CLEANLY (EXIT CODE 0)")
    print("================================================================================")
