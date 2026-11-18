"""
ch06_empirical_benchmark_lab.py
Level 8 Chapter 06 Companion Laboratory: Academic Research & Empirical Benchmarking.
Demonstrates Coordinated Omission Compensation, High Dynamic Range (HDR) Quantiles,
and Non-Parametric Bootstrap Confidence Intervals.
Pure Python/Standard Library with zero external dependencies.
"""

from __future__ import annotations
import sys
import math
import random
from typing import List, Tuple, Dict, Any

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")


class CoordinatedOmissionCorrector:
    """Detects and compensates for coordinated omission in latency logs."""
    @staticmethod
    def correct_latencies(observed_latencies_ms: List[float], expected_interval_ms: float) -> List[float]:
        corrected = []
        for lat in observed_latencies_ms:
            corrected.append(lat)
            if lat > expected_interval_ms:
                missing_count = int(lat // expected_interval_ms) - 1
                for k in range(1, missing_count + 1):
                    corrected.append(lat - (k * expected_interval_ms))
        return sorted(corrected)


class HdrPercentileTracker:
    """Computes exact statistical quantiles across high dynamic range latency logs."""
    def __init__(self, samples: List[float]):
        self.samples = sorted(samples)
        self.n = len(self.samples)

    def percentile(self, p: float) -> float:
        if self.n == 0:
            return 0.0
        k = (p / 100.0) * (self.n - 1)
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return self.samples[int(k)]
        d0 = self.samples[int(f)] * (c - k)
        d1 = self.samples[int(c)] * (k - f)
        return d0 + d1

    def summary(self) -> Dict[str, float]:
        return {
            "p50": self.percentile(50.0),
            "p95": self.percentile(95.0),
            "p99": self.percentile(99.0),
            "p999": self.percentile(99.9),
            "max": self.samples[-1] if self.samples else 0.0,
            "count": float(self.n)
        }


class BootstrapStatisticalEvaluator:
    """Computes non-parametric Bootstrap Confidence Intervals."""
    @staticmethod
    def bootstrap_ci(data: List[float], statistic_fn: Any, num_resamples: int = 1000, alpha: float = 0.05) -> Tuple[float, float]:
        n = len(data)
        bootstrap_stats = []
        random.seed(42)

        for _ in range(num_resamples):
            sample = [data[random.randint(0, n - 1)] for _ in range(n)]
            stat = statistic_fn(sample)
            bootstrap_stats.append(stat)

        bootstrap_stats.sort()
        lower_idx = int((alpha / 2.0) * num_resamples)
        upper_idx = int((1.0 - (alpha / 2.0)) * num_resamples)
        return bootstrap_stats[lower_idx], bootstrap_stats[upper_idx]


def main() -> None:
    print("=" * 70)
    print("LEVEL 8 CHAPTER 06: EMPIRICAL BENCHMARKING & RESEARCH HARNESS LAB")
    print("=" * 70)

    # 1. Synthesize Workload with Severe Stall
    print("\n[Test 1] Synthesizing Synchronous Workload with 50 ms Stall...")
    random.seed(101)
    # 990 fast requests (~1.0 ms)
    raw_latencies = [random.gauss(1.0, 0.1) for _ in range(990)]
    # 10 stalled requests (50.0 ms)
    raw_latencies.extend([50.0 for _ in range(10)])

    raw_tracker = HdrPercentileTracker(raw_latencies)
    raw_summary = raw_tracker.summary()
    print(f"  -> Raw Uncorrected Quantiles (Masked by Coordinated Omission):")
    print(f"     P50: {raw_summary['p50']:.2f} ms | P99: {raw_summary['p99']:.2f} ms | P99.9: {raw_summary['p999']:.2f} ms")

    # 2. Apply Coordinated Omission Compensation (Target arrival rate: 1 request every 1.0 ms)
    print("\n[Test 2] Applying Coordinated Omission Compensation...")
    corrected_latencies = CoordinatedOmissionCorrector.correct_latencies(raw_latencies, expected_interval_ms=1.0)
    corrected_tracker = HdrPercentileTracker(corrected_latencies)
    corrected_summary = corrected_tracker.summary()

    print(f"  -> Compensated Quantiles (True Latency Distribution Revealed):")
    print(f"     P50: {corrected_summary['p50']:.2f} ms | P99: {corrected_summary['p99']:.2f} ms | P99.9: {corrected_summary['p999']:.2f} ms")
    print(f"  -> Sample Count: Expanded from {len(raw_latencies)} to {len(corrected_latencies)} requests.")

    assert corrected_summary["p99"] > raw_summary["p99"], "Corrected P99 must reveal true tail degradation!"
    print("  -> Coordinated Omission Revelation: VERIFIED (True tail latency accurately captured).")

    # 3. Non-Parametric Bootstrap Confidence Interval
    print("\n[Test 3] Computing 95% Bootstrap Confidence Interval for Median Latency...")
    def calc_median(data: List[float]) -> float:
        s = sorted(data)
        return s[len(s) // 2]

    ci_lower, ci_upper = BootstrapStatisticalEvaluator.bootstrap_ci(
        corrected_latencies, statistic_fn=calc_median, num_resamples=1000, alpha=0.05
    )
    print(f"  -> 95% Bootstrap CI for Median: [{ci_lower:.4f} ms, {ci_upper:.4f} ms]")
    assert ci_lower <= corrected_summary["p50"] <= ci_upper
    print("  -> Bounded Non-Parametric Uncertainty: VERIFIED.")

    print("\n" + "=" * 70)
    print("ALL SCIENTIFIC BENCHMARKING TESTS PASSED (Exit Code 0).")
    print("=" * 70)
    sys.exit(0)


if __name__ == "__main__":
    main()
