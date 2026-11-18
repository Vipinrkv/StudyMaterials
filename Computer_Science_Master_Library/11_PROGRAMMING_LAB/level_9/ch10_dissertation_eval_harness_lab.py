"""
Level 9 Programming Lab - Chapter 10: Dissertation Empirical Evaluation Harness
Implements Statistical Hypothesis Testing (Welch's t-test) and ACM Artifact Evaluation Auditing.
"""
import sys
import math
from typing import List, Tuple

sys.stdout.reconfigure(encoding="utf-8")

# -------------------------------------------------------------------------
# 1. Statistical Hypothesis Testing Engine (Welch's t-test)
# -------------------------------------------------------------------------
class StatisticalHypothesisTester:
    @staticmethod
    def calculate_mean_and_var(data: List[float]) -> Tuple[float, float]:
        n = len(data)
        if n < 2:
            raise ValueError("Need at least 2 samples to compute variance.")
        mean = sum(data) / n
        var = sum((x - mean) ** 2 for x in data) / (n - 1)
        return mean, var

    @staticmethod
    def welch_t_test(sample1: List[float], sample2: List[float]) -> Tuple[float, float, float]:
        # Returns (t_stat, degrees_of_freedom, mean_difference)
        n1 = len(sample1)
        n2 = len(sample2)
        m1, v1 = StatisticalHypothesisTester.calculate_mean_and_var(sample1)
        m2, v2 = StatisticalHypothesisTester.calculate_mean_and_var(sample2)

        mean_diff = m1 - m2
        s_delta = math.sqrt((v1 / n1) + (v2 / n2))
        if s_delta == 0.0:
            return float("inf"), float("inf"), mean_diff

        t_stat = mean_diff / s_delta

        # Welch-Satterthwaite equation for degrees of freedom
        num = ((v1 / n1) + (v2 / n2)) ** 2
        denom = (((v1 / n1) ** 2) / (n1 - 1)) + (((v2 / n2) ** 2) / (n2 - 1))
        df = num / denom

        return t_stat, df, mean_diff

# -------------------------------------------------------------------------
# 2. ACM Artifact Evaluation Badge Auditor
# -------------------------------------------------------------------------
class ArtifactBadgeAuditor:
    @staticmethod
    def audit_claim(baseline_runs: List[float], proposed_runs: List[float], claimed_speedup: float, tolerance: float = 0.15) -> Tuple[bool, float, str]:
        m_base, _ = StatisticalHypothesisTester.calculate_mean_and_var(baseline_runs)
        m_prop, _ = StatisticalHypothesisTester.calculate_mean_and_var(proposed_runs)

        empirical_speedup = m_base / m_prop
        error_ratio = abs(empirical_speedup - claimed_speedup) / claimed_speedup

        if error_ratio <= tolerance:
            badge = "ACM_BADGE: RESULTS_REPLICATED (Passed within tolerance)"
            return True, empirical_speedup, badge
        else:
            badge = f"ACM_BADGE: REPLICATION_FAILED (Error ratio {error_ratio:.2%} > tolerance {tolerance:.2%})"
            return False, empirical_speedup, badge


def test_dissertation_eval_harness():
    print("===========================================================================")
    print("DISSERTATION EMPIRICAL EVALUATION & ARTIFACT AUDIT TESTBED")
    print("LEVEL 9 LAB - CHAPTER 10")
    print("===========================================================================")

    # 1. Benchmark Data Collection Simulation (Warm-up purged)
    print("[Test 1/3] Benchmark Data Gathering & Variance Calculation...")
    # Baseline latency (e.g. Traditional Raft, ms)
    baseline_latencies = [
        12.1, 12.8, 12.4, 11.9, 13.0, 12.5, 12.2, 12.9, 12.3, 12.6,
        12.7, 12.0, 12.5, 13.1, 12.2, 12.4, 12.8, 12.6, 12.3, 12.5,
        12.4, 12.7, 12.1, 12.9, 12.5, 12.6, 12.2, 12.8, 12.4, 12.5
    ]
    # Novel proposed system (HotStuff-v2, ms)
    proposed_latencies = [
        6.9, 7.2, 7.0, 6.8, 7.4, 7.1, 6.9, 7.3, 7.0, 7.1,
        7.2, 6.8, 7.1, 7.5, 6.9, 7.0, 7.2, 7.1, 6.9, 7.1,
        7.0, 7.2, 6.8, 7.3, 7.1, 7.2, 6.9, 7.3, 7.0, 7.1
    ]

    m1, v1 = StatisticalHypothesisTester.calculate_mean_and_var(baseline_latencies)
    m2, v2 = StatisticalHypothesisTester.calculate_mean_and_var(proposed_latencies)
    print(f"  -> Baseline Mean: {m1:.2f} ms (StdDev: {math.sqrt(v1):.2f} ms, N={len(baseline_latencies)})")
    print(f"  -> Proposed Mean: {m2:.2f} ms (StdDev: {math.sqrt(v2):.2f} ms, N={len(proposed_latencies)})")

    # 2. Welch's t-test Statistical Significance
    print("[Test 2/3] Welch's t-Test for Statistical Significance...")
    t_stat, df, diff = StatisticalHypothesisTester.welch_t_test(baseline_latencies, proposed_latencies)
    print(f"  -> Welch's t-statistic: {t_stat:.2f} (df: {df:.1f}, Mean Delta: {diff:.2f} ms)")
    assert t_stat > 10.0, f"t-statistic {t_stat} must exceed 10.0 for p << 1e-10 significance"
    print("  -> Null hypothesis H0 rejected with extreme significance (p < 1e-15).")

    # 3. ACM Artifact Evaluation Badge Certification
    print("[Test 3/3] ACM Artifact Evaluation Badge Certification...")
    # Claimed speedup: 1.75x
    passed, actual_speedup, badge_msg = ArtifactBadgeAuditor.audit_claim(
        baseline_latencies, proposed_latencies, claimed_speedup=1.75, tolerance=0.10
    )
    print(f"  -> Claimed Speedup: 1.75x, Replicated Speedup: {actual_speedup:.2f}x")
    print(f"  -> {badge_msg}")
    assert passed is True
    assert "RESULTS_REPLICATED" in badge_msg

    print("===========================================================================")
    print("ALL 3 DISSERTATION EVALUATION & AUDIT TESTS PASSED (Exit Code 0).")
    print("===========================================================================")

if __name__ == "__main__":
    test_dissertation_eval_harness()
