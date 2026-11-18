"""
Level 9 Programming Lab - Chapter 03: Autonomous AI Systems & SBFL
Implements Ochiai Spectrum-Based Fault Localization, Invariant Tool Bounds, and Self-Healing.
"""
import sys
import math
from typing import List, Dict, Set, Tuple

sys.stdout.reconfigure(encoding="utf-8")

# -------------------------------------------------------------------------
# 1. Spectrum-Based Fault Localization (Ochiai)
# -------------------------------------------------------------------------
class OchiaiLocalizer:
    def __init__(self, total_statements: int):
        self.num_statements = total_statements
        # Each entry: (executed_statements_set, is_passed)
        self.test_runs: List[Tuple[Set[int], bool]] = []

    def record_run(self, executed_stmts: Set[int], passed: bool) -> None:
        self.test_runs.append((executed_stmts, passed))

    def compute_suspiciousness(self) -> Dict[int, float]:
        scores: Dict[int, float] = {}
        total_failed = sum(1 for _, passed in self.test_runs if not passed)

        for stmt in range(1, self.num_statements + 1):
            n_cf = 0  # Failed & Executed
            n_uf = 0  # Failed & Not Executed
            n_cs = 0  # Passed & Executed

            for executed, passed in self.test_runs:
                if not passed:
                    if stmt in executed:
                        n_cf += 1
                    else:
                        n_uf += 1
                else:
                    if stmt in executed:
                        n_cs += 1

            denom = math.sqrt((n_cf + n_uf) * (n_cf + n_cs))
            if denom == 0.0:
                scores[stmt] = 0.0
            else:
                scores[stmt] = n_cf / denom

        return scores

# -------------------------------------------------------------------------
# 2. Invariant-Bounded Tool Supervisor
# -------------------------------------------------------------------------
class SafetyInvariantViolation(Exception):
    pass

class BudgetExceededError(Exception):
    pass

class InvariantBoundedSupervisor:
    def __init__(self, max_steps: int = 5, forbidden_commands: Set[str] = None):
        self.max_steps = max_steps
        self.step_count = 0
        self.forbidden = forbidden_commands or {"rm -rf /", "DROP TABLE", "format c:", "sudo"}
        self.history: List[str] = []

    def dispatch(self, tool_name: str, payload: str) -> str:
        if self.step_count >= self.max_steps:
            raise BudgetExceededError(f"Agent exceeded step budget of {self.max_steps} actions.")

        # Invariant check
        for bad in self.forbidden:
            if bad in payload:
                raise SafetyInvariantViolation(f"Unsafe action blocked: payload contains forbidden token '{bad}'")

        self.step_count += 1
        self.history.append(f"{tool_name}:{payload}")
        return f"OK: Executed {tool_name} successfully."

# -------------------------------------------------------------------------
# 3. Autonomous Self-Healing Simulation
# -------------------------------------------------------------------------
def test_autonomous_systems():
    print("===========================================================================")
    print("AUTONOMOUS AI SYSTEMS & SBFL VERIFICATION TESTBED")
    print("LEVEL 9 LAB - CHAPTER 03")
    print("===========================================================================")

    # 1. Ochiai Fault Localization Test
    print("[Test 1/3] Spectrum-Based Fault Localization (Ochiai Metric)...")
    localizer = OchiaiLocalizer(total_statements=4)

    # T1: Passed, executed {1, 2}
    localizer.record_run({1, 2}, passed=True)
    # T2: Passed, executed {2, 4}
    localizer.record_run({2, 4}, passed=True)
    # T3: Failed, executed {1, 3}
    localizer.record_run({1, 3}, passed=False)
    # T4: Failed, executed {3}
    localizer.record_run({3}, passed=False)

    scores = localizer.compute_suspiciousness()
    print(f"  -> Ochiai Scores: {scores}")
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_culprit, top_score = ranked[0]
    assert top_culprit == 3, f"Statement 3 must be the top defect candidate, got {top_culprit}"
    assert math.isclose(top_score, 1.0, rel_tol=1e-5), f"Statement 3 must have Ochiai score 1.0, got {top_score}"
    print(f"  -> Statement {top_culprit} correctly isolated as root defect with score {top_score:.3f}.")

    # 2. Invariant-Bounded Tool Supervisor Test
    print("[Test 2/3] Invariant-Bounded Tool Execution & Budget Enforcement...")
    supervisor = InvariantBoundedSupervisor(max_steps=3)

    # Valid tool invocations
    res1 = supervisor.dispatch("read_file", "src/engine.py")
    res2 = supervisor.dispatch("run_test", "pytest test_suite.py")
    assert supervisor.step_count == 2

    # Block destructive action
    try:
        supervisor.dispatch("shell_exec", "rm -rf / --no-preserve-root")
        assert False, "Should have raised SafetyInvariantViolation"
    except SafetyInvariantViolation as e:
        print(f"  -> Successfully intercepted dangerous payload: {e}")

    # Exhaust budget
    supervisor.dispatch("apply_patch", "patch_v1.diff")
    try:
        supervisor.dispatch("apply_patch", "patch_v2.diff")
        assert False, "Should have raised BudgetExceededError"
    except BudgetExceededError as e:
        print(f"  -> Successfully enforced budget limit: {e}")

    # 3. Automated Self-Healing Verification
    print("[Test 3/3] Closed-Loop Multi-Agent Self-Healing Pipeline...")
    def eval_patch(patch_factor: float) -> bool:
        # Ground truth: VIP discount must be 20%
        prices = [(100.0, True, 20.0), (200.0, False, 0.0), (50.0, True, 10.0)]
        for price, is_vip, expected in prices:
            calc = price * (patch_factor if is_vip else 0.0)
            if not math.isclose(calc, expected, rel_tol=1e-3):
                return False
        return True

    # Initial flawed state (factor = 0.10)
    assert eval_patch(0.10) is False, "Flawed program must fail test suite"

    # Simulated Coder Agent synthesizes candidate patches
    candidates = [0.05, 0.15, 0.20, 0.25]
    successful_patch = None
    for cand in candidates:
        if eval_patch(cand):
            successful_patch = cand
            break

    assert successful_patch == 0.20
    print(f"  -> Self-Healing Loop verified: Patched VIP discount factor to {successful_patch} (All tests pass).")

    print("===========================================================================")
    print("ALL 3 AUTONOMOUS SYSTEMS & FAULT LOCALIZATION TESTS PASSED (Exit Code 0).")
    print("===========================================================================")

if __name__ == "__main__":
    test_autonomous_systems()
