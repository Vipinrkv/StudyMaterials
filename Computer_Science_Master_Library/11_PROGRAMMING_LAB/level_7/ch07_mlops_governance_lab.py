"""
ch07_mlops_governance_lab.py
Level 7 Companion Lab: Feature Store Time-Travel Joins & PSI Drift Detection.
Pure Python/Standard Library implementation with zero external dependencies.
"""

from __future__ import annotations
import sys
import math
import bisect
from typing import Dict, List, Tuple, Optional

# Windows UTF-8 console output
sys.stdout.reconfigure(encoding="utf-8")


class LabFeatureStore:
    """Offline timeline and online cache feature store."""
    def __init__(self):
        # Maps entity_id -> list of (timestamp, value)
        self.timeline: Dict[str, List[Tuple[int, float]]] = {}
        self.online_kv: Dict[str, float] = {}

    def write(self, timestamp: int, entity_id: str, value: float) -> None:
        if entity_id not in self.timeline:
            self.timeline[entity_id] = []
        bisect.insort(self.timeline[entity_id], (timestamp, value))
        self.online_kv[entity_id] = value

    def time_travel_join(self, observation_time: int, entity_id: str) -> Optional[float]:
        """AS-OF join retrieving feature valid strictly at or before observation_time."""
        records = self.timeline.get(entity_id)
        if not records:
            return None
        ts_list = [t for t, _ in records]
        idx = bisect.bisect_right(ts_list, observation_time) - 1
        if idx >= 0:
            return records[idx][1]
        return None


def calculate_psi(baseline: List[float], target: List[float], num_bins: int = 5) -> float:
    """Computes Population Stability Index across continuous feature distributions."""
    min_v = min(min(baseline), min(target))
    max_v = max(max(baseline), max(target))
    width = (max_v - min_v) / num_bins

    b_counts = [0.0001] * num_bins
    t_counts = [0.0001] * num_bins

    for x in baseline:
        idx = min(int((x - min_v) / width), num_bins - 1)
        b_counts[idx] += 1.0

    for x in target:
        idx = min(int((x - min_v) / width), num_bins - 1)
        t_counts[idx] += 1.0

    b_props = [c / sum(b_counts) for c in b_counts]
    t_props = [c / sum(t_counts) for c in t_counts]

    psi = sum((t - b) * math.log(t / b) for b, t in zip(b_props, t_props))
    return psi


def test_point_in_time_join():
    print("Running Test Suite 1: Feature Store Point-in-Time (AS-OF) Correctness...")
    fs = LabFeatureStore()
    # Entity historical updates
    fs.write(100, "user:1", 50.0)
    fs.write(300, "user:1", 75.0)
    fs.write(600, "user:1", 90.0)

    # 1. Observation before any feature exists -> None
    assert fs.time_travel_join(50, "user:1") is None

    # 2. Observation between t=100 and t=300 -> Must return 50.0 (NOT future 75.0 or 90.0!)
    assert fs.time_travel_join(250, "user:1") == 50.0

    # 3. Observation exactly at t=300 -> Must return 75.0
    assert fs.time_travel_join(300, "user:1") == 75.0

    # 4. Observation at t=500 -> Must return 75.0
    assert fs.time_travel_join(500, "user:1") == 75.0

    # 5. Observation after latest t=600 -> Must return 90.0
    assert fs.time_travel_join(1000, "user:1") == 90.0
    print("  Passed! Point-in-time joins completely eliminate lookahead bias data leakage.")


def test_population_stability_index():
    print("Running Test Suite 2: Statistical Drift Detection via PSI...")
    # Baseline: 100 samples around 10-20
    baseline = [float(x) for x in range(10, 20)] * 10

    # Target 1: Identical distribution -> PSI must be ~0.0
    target_stable = [float(x) for x in range(10, 20)] * 10
    psi_stable = calculate_psi(baseline, target_stable)
    assert psi_stable < 0.05, f"Expected near-zero PSI, got {psi_stable}"

    # Target 2: Heavily shifted distribution (values in 50-60) -> PSI must be >> 0.25
    target_shifted = [float(x + 40) for x in range(10, 20)] * 10
    psi_drifted = calculate_psi(baseline, target_shifted)
    assert psi_drifted > 0.25, f"Expected severe drift PSI >= 0.25, got {psi_drifted}"
    print(f"  Passed! Stable PSI={psi_stable:.4f} (< 0.1), Drifted PSI={psi_drifted:.4f} (>= 0.25).")


def test_online_feature_caching():
    print("Running Test Suite 3: Low-Latency Online Feature Cache...")
    fs = LabFeatureStore()
    fs.write(100, "merchant:42", 1200.0)
    fs.write(200, "merchant:42", 1800.0)

    # Online store must immediately serve newest state
    assert fs.online_kv["merchant:42"] == 1800.0
    print("  Passed! Online KV cache serves current feature values with O(1) latency.")


if __name__ == "__main__":
    print("================================================================================")
    print("LEVEL 7 LAB 07: MLOPS FEATURE STORE & STATISTICAL DRIFT ENGINE")
    print("================================================================================")
    test_point_in_time_join()
    test_population_stability_index()
    test_online_feature_caching()
    print("================================================================================")
    print("ALL 3 TEST SUITES PASSED CLEANLY (EXIT CODE 0)")
    print("================================================================================")
