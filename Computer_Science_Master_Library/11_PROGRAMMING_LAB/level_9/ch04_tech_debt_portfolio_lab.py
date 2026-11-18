"""
Level 9 Programming Lab - Chapter 04: Technical Debt Portfolio & Conway Auditor
Implements Financial NPV Modeling of Technical Debt and Conway Graph Homomorphism.
"""
import sys
import math
from typing import Dict, List, Tuple, Set

sys.stdout.reconfigure(encoding="utf-8")

# -------------------------------------------------------------------------
# 1. Technical Debt Financial Valuation
# -------------------------------------------------------------------------
class TechnicalDebtPortfolio:
    def __init__(self, initial_interest_per_month: float, contagion_rate: float = 0.02, monthly_discount_rate: float = 0.008):
        self.i0 = initial_interest_per_month
        self.alpha = contagion_rate
        self.r = monthly_discount_rate

    def calculate_deferral_cost(self, months: int) -> float:
        total = 0.0
        for t in range(1, months + 1):
            interest_t = self.i0 * ((1.0 + self.alpha) ** (t - 1))
            total += interest_t
        return total

    def evaluate_refactoring_npv(self, refactor_cost: float, friction_reduction_ratio: float, horizon_months: int) -> Tuple[float, bool]:
        npv = -refactor_cost
        for t in range(1, horizon_months + 1):
            interest_t = self.i0 * ((1.0 + self.alpha) ** (t - 1))
            savings_t = interest_t * friction_reduction_ratio
            discounted_savings = savings_t / ((1.0 + self.r) ** t)
            npv += discounted_savings
        return npv, npv > 0.0

# -------------------------------------------------------------------------
# 2. Conway's Law Graph Homomorphism Auditor
# -------------------------------------------------------------------------
class ConwayAuditor:
    def __init__(self):
        # service -> team
        self.service_mapping: Dict[str, str] = {}
        # set of (team_a, team_b) with communication channels
        self.team_channels: Set[Tuple[str, str]] = set()

    def register_service(self, service_name: str, owning_team: str) -> None:
        self.service_mapping[service_name] = owning_team

    def add_team_channel(self, team_a: str, team_b: str) -> None:
        self.team_channels.add((team_a, team_b))
        self.team_channels.add((team_b, team_a))

    def audit_dependencies(self, dependencies: List[Tuple[str, str]]) -> List[Tuple[str, str, str, str]]:
        # Returns list of violations: (src_svc, dst_svc, src_team, dst_team)
        violations = []
        for src_svc, dst_svc in dependencies:
            team_src = self.service_mapping.get(src_svc)
            team_dst = self.service_mapping.get(dst_svc)
            if not team_src or not team_dst:
                continue
            if team_src == team_dst:
                continue  # Intra-team communication is always permitted
            if (team_src, team_dst) not in self.team_channels:
                violations.append((src_svc, dst_svc, team_src, team_dst))
        return violations

# -------------------------------------------------------------------------
# 3. DORA Metrics Classifier
# -------------------------------------------------------------------------
def classify_dora(deploys_per_day: float, lead_time_hours: float, cfr_percent: float, mttr_hours: float) -> str:
    # Elite: multiple deploys/day, lead time < 24h, CFR < 15%, MTTR < 1h
    if deploys_per_day >= 1.0 and lead_time_hours <= 24.0 and cfr_percent <= 15.0 and mttr_hours <= 1.0:
        return "ELITE"
    elif deploys_per_day >= 0.14 and lead_time_hours <= 168.0 and cfr_percent <= 20.0 and mttr_hours <= 24.0:
        return "HIGH"
    elif deploys_per_day >= 0.03:
        return "MEDIUM"
    else:
        return "LOW"


def test_tech_strategy_portfolio():
    print("===========================================================================")
    print("TECHNOLOGY STRATEGY & CONWAY AUDITOR VERIFICATION TESTBED")
    print("LEVEL 9 LAB - CHAPTER 04")
    print("===========================================================================")

    # 1. Technical Debt Financial Valuation
    print("[Test 1/3] Technical Debt Financial Valuation & Refactoring NPV...")
    portfolio = TechnicalDebtPortfolio(initial_interest_per_month=15000.0, contagion_rate=0.02, monthly_discount_rate=0.008)
    deferral_24m = portfolio.calculate_deferral_cost(months=24)
    print(f"  -> 24-Month Cumulative Deferral Friction: ${deferral_24m:,.2f}")
    assert deferral_24m > 400000.0, "Compound friction over 24m must exceed $400,000"

    npv, is_justified = portfolio.evaluate_refactoring_npv(refactor_cost=200000.0, friction_reduction_ratio=0.70, horizon_months=24)
    print(f"  -> Refactoring NPV (Cost $200k, 70% reduction): ${npv:,.2f} (Justified: {is_justified})")
    assert is_justified is True
    assert npv > 50000.0, "NPV should be significantly positive (> $50k)"

    # 2. Conway's Law Graph Homomorphism Auditor
    print("[Test 2/3] Conway's Law Graph Homomorphism Audit...")
    auditor = ConwayAuditor()
    auditor.register_service("payments_svc", "payments_team")
    auditor.register_service("ledger_svc", "ledger_team")
    auditor.register_service("notifications_svc", "growth_team")

    # Authorize payments <-> ledger communication channel
    auditor.add_team_channel("payments_team", "ledger_team")

    # Audit architectural dependencies
    dependencies = [
        ("payments_svc", "ledger_svc"),        # Valid (channel exists)
        ("payments_svc", "notifications_svc")  # Conway Violation (no channel between payments & growth)
    ]
    violations = auditor.audit_dependencies(dependencies)
    assert len(violations) == 1
    src_s, dst_s, t_src, t_dst = violations[0]
    assert src_s == "payments_svc" and dst_s == "notifications_svc"
    print(f"  -> Successfully caught Conway violation: {src_s} ({t_src}) -> {dst_s} ({t_dst}) without team channel.")

    # 3. DORA Metrics Classifier
    print("[Test 3/3] DORA Engineering Excellence Classification...")
    tier_elite = classify_dora(deploys_per_day=5.0, lead_time_hours=2.0, cfr_percent=5.0, mttr_hours=0.5)
    tier_high = classify_dora(deploys_per_day=0.5, lead_time_hours=48.0, cfr_percent=12.0, mttr_hours=4.0)
    tier_low = classify_dora(deploys_per_day=0.01, lead_time_hours=500.0, cfr_percent=45.0, mttr_hours=120.0)

    assert tier_elite == "ELITE"
    assert tier_high == "HIGH"
    assert tier_low == "LOW"
    print(f"  -> DORA classification confirmed: Elite ({tier_elite}), High ({tier_high}), Low ({tier_low}).")

    print("===========================================================================")
    print("ALL 3 STRATEGY & GOVERNANCE TESTS PASSED (Exit Code 0).")
    print("===========================================================================")

if __name__ == "__main__":
    test_tech_strategy_portfolio()
