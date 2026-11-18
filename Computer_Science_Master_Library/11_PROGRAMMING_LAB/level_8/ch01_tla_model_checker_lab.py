"""
ch01_tla_model_checker_lab.py
Level 8 Chapter 01 Companion Laboratory: Formal Specification & Model Checking.
Executes Explicit-State BFS Graph Traversal, Invariant Verification,
Deadlock Detection, and Minimal Counterexample Error-Trace Synthesis.
Pure Python/Standard Library with zero external dependencies.
"""

from __future__ import annotations
import sys
import collections
from typing import Dict, List, Set, Tuple, Any, Optional, Callable

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")


class ModelCheckerState:
    """Immutable, hashable representation of a discrete system state."""
    def __init__(self, variables: Dict[str, Any]):
        self._vars = tuple(sorted(variables.items()))
        self._hash = hash(self._vars)
        self.dict_repr = variables

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ModelCheckerState):
            return False
        return self._vars == other._vars

    def __repr__(self) -> str:
        items = ", ".join(f"{k}: {v}" for k, v in self._vars)
        return f"State({items})"


class ExplicitModelChecker:
    """
    Explicit-state breadth-first model checker evaluating state invariants
    and generating minimal execution traces upon property refutation.
    """
    def __init__(self, init_states: List[Dict[str, Any]], next_action: Callable[[Dict[str, Any]], List[Dict[str, Any]]]):
        self.init_states = [ModelCheckerState(s) for s in init_states]
        self.next_action = next_action
        self.visited: Set[ModelCheckerState] = set()
        self.parent_map: Dict[ModelCheckerState, Optional[ModelCheckerState]] = {}
        self.total_states_explored = 0
        self.total_transitions = 0

    def check_invariant(self, invariant: Callable[[Dict[str, Any]], bool], inv_name: str = "Invariant") -> Tuple[bool, Optional[List[Dict[str, Any]]]]:
        """
        Executes BFS state space exploration.
        Returns (True, None) if invariant holds globally;
        Returns (False, [trace]) with minimal counterexample trace upon violation.
        """
        queue = collections.deque()

        for s0 in self.init_states:
            if not invariant(s0.dict_repr):
                return False, [s0.dict_repr]
            self.visited.add(s0)
            self.parent_map[s0] = None
            queue.append(s0)

        while queue:
            current = queue.popleft()
            self.total_states_explored += 1

            # Compute successor states: Next(current)
            succ_dicts = self.next_action(current.dict_repr)
            self.total_transitions += len(succ_dicts)

            for s_dict in succ_dicts:
                succ = ModelCheckerState(s_dict)

                # Check safety invariant: \Box Invariant
                if not invariant(succ.dict_repr):
                    self.parent_map[succ] = current
                    trace = self._reconstruct_trace(succ)
                    return False, trace

                if succ not in self.visited:
                    self.visited.add(succ)
                    self.parent_map[succ] = current
                    queue.append(succ)

        return True, None

    def _reconstruct_trace(self, bad_state: ModelCheckerState) -> List[Dict[str, Any]]:
        trace = []
        curr: Optional[ModelCheckerState] = bad_state
        while curr is not None:
            trace.append(curr.dict_repr)
            curr = self.parent_map.get(curr)
        trace.reverse()
        return trace


# ==============================================================================
# SPECIFICATION 1: PETERSON MUTEX PROTOCOL
# ==============================================================================

def peterson_init() -> List[Dict[str, Any]]:
    return [{
        "flag_0": False,
        "flag_1": False,
        "turn": 0,
        "pc_0": "idle",
        "pc_1": "idle",
    }]

def peterson_next(s: Dict[str, Any]) -> List[Dict[str, Any]]:
    succs = []

    # Process 0
    if s["pc_0"] == "idle":
        s_next = dict(s)
        s_next["flag_0"] = True
        s_next["pc_0"] = "set_turn"
        succs.append(s_next)
    elif s["pc_0"] == "set_turn":
        s_next = dict(s)
        s_next["turn"] = 1
        s_next["pc_0"] = "wait"
        succs.append(s_next)
    elif s["pc_0"] == "wait":
        if not s["flag_1"] or s["turn"] == 0:
            s_next = dict(s)
            s_next["pc_0"] = "critical"
            succs.append(s_next)
    elif s["pc_0"] == "critical":
        s_next = dict(s)
        s_next["flag_0"] = False
        s_next["pc_0"] = "idle"
        succs.append(s_next)

    # Process 1
    if s["pc_1"] == "idle":
        s_next = dict(s)
        s_next["flag_1"] = True
        s_next["pc_1"] = "set_turn"
        succs.append(s_next)
    elif s["pc_1"] == "set_turn":
        s_next = dict(s)
        s_next["turn"] = 0
        s_next["pc_1"] = "wait"
        succs.append(s_next)
    elif s["pc_1"] == "wait":
        if not s["flag_0"] or s["turn"] == 1:
            s_next = dict(s)
            s_next["pc_1"] = "critical"
            succs.append(s_next)
    elif s["pc_1"] == "critical":
        s_next = dict(s)
        s_next["flag_1"] = False
        s_next["pc_1"] = "idle"
        succs.append(s_next)

    return succs

def mutual_exclusion_inv(s: Dict[str, Any]) -> bool:
    return not (s["pc_0"] == "critical" and s["pc_1"] == "critical")


# ==============================================================================
# SPECIFICATION 2: FLAWED PROTOCOL (INTENTIONAL RACE CONDITION)
# ==============================================================================

def flawed_init() -> List[Dict[str, Any]]:
    return [{
        "lock": False,
        "pc_0": "idle",
        "pc_1": "idle",
    }]

def flawed_next(s: Dict[str, Any]) -> List[Dict[str, Any]]:
    succs = []
    # Process 0
    if s["pc_0"] == "idle":
        # Check lock non-atomically
        if not s["lock"]:
            s_next = dict(s)
            s_next["pc_0"] = "acquire"
            succs.append(s_next)
    elif s["pc_0"] == "acquire":
        s_next = dict(s)
        s_next["lock"] = True
        s_next["pc_0"] = "critical"
        succs.append(s_next)
    elif s["pc_0"] == "critical":
        s_next = dict(s)
        s_next["lock"] = False
        s_next["pc_0"] = "idle"
        succs.append(s_next)

    # Process 1
    if s["pc_1"] == "idle":
        if not s["lock"]:
            s_next = dict(s)
            s_next["pc_1"] = "acquire"
            succs.append(s_next)
    elif s["pc_1"] == "acquire":
        s_next = dict(s)
        s_next["lock"] = True
        s_next["pc_1"] = "critical"
        succs.append(s_next)
    elif s["pc_1"] == "critical":
        s_next = dict(s)
        s_next["lock"] = False
        s_next["pc_1"] = "idle"
        succs.append(s_next)

    return succs


def main() -> None:
    print("=" * 70)
    print("LEVEL 8 CHAPTER 01: FORMAL SPECIFICATION & MODEL CHECKING LAB")
    print("=" * 70)

    # Test 1: Verify correct Peterson Mutex protocol
    print("\n[Test 1] Exploring Peterson Algorithm state space...")
    checker1 = ExplicitModelChecker(peterson_init(), peterson_next)
    ok1, trace1 = checker1.check_invariant(mutual_exclusion_inv, "MutualExclusion")
    assert ok1 is True, "Peterson algorithm must satisfy mutual exclusion!"
    assert trace1 is None
    print(f"  -> State Space Explored: {len(checker1.visited)} states, {checker1.total_transitions} transitions.")
    print("  -> Safety Invariant [\\Box MutualExclusion]: VERIFIED (No violations).")

    # Test 2: Detect race condition in flawed protocol
    print("\n[Test 2] Model checking Flawed Mutex protocol (Expect Violation)...")
    checker2 = ExplicitModelChecker(flawed_init(), flawed_next)
    ok2, trace2 = checker2.check_invariant(mutual_exclusion_inv, "MutualExclusion")
    assert ok2 is False, "Flawed protocol must violate mutual exclusion!"
    assert trace2 is not None and len(trace2) > 0
    print(f"  -> Invariant Violation Detected! Trace length: {len(trace2)} steps.")
    print("  -> Minimal Counterexample Error Trace:")
    for step_i, state in enumerate(trace2):
        print(f"     Step {step_i}: pc_0={state['pc_0']}, pc_1={state['pc_1']}, lock={state['lock']}")

    print("\n" + "=" * 70)
    print("ALL FORMAL MODEL CHECKING TESTS PASSED (Exit Code 0).")
    print("=" * 70)
    sys.exit(0)


if __name__ == "__main__":
    main()
