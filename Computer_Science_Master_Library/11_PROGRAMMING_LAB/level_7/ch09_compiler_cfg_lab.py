"""
ch09_compiler_cfg_lab.py
Level 7 Companion Lab: Control Flow Graphs, Dominance Frontiers & JIT Tiering.
Pure Python/Standard Library implementation with zero external dependencies.
"""

from __future__ import annotations
import sys
from typing import Dict, List, Set, Optional

# Windows UTF-8 console output
sys.stdout.reconfigure(encoding="utf-8")


class LabBlock:
    """Basic block node in a compiler Control Flow Graph."""
    def __init__(self, name: str):
        self.name = name
        self.preds: List[LabBlock] = []
        self.succs: List[LabBlock] = []

    def connect(self, succ: LabBlock) -> None:
        self.succs.append(succ)
        succ.preds.append(self)


def compute_dominators(entry: LabBlock, blocks: List[LabBlock]) -> Dict[str, Set[str]]:
    """Iterative dataflow dominator set computation."""
    all_names = {b.name for b in blocks}
    dom: Dict[str, Set[str]] = {}
    for b in blocks:
        dom[b.name] = set(all_names) if b != entry else {entry.name}

    changed = True
    while changed:
        changed = False
        for b in blocks:
            if b == entry:
                continue
            pred_sets = [dom[p.name] for p in b.preds]
            new_dom = {b.name}.union(set.intersection(*pred_sets) if pred_sets else set())
            if new_dom != dom[b.name]:
                dom[b.name] = new_dom
                changed = True
    return dom


def compute_immediate_dominators(dom: Dict[str, Set[str]]) -> Dict[str, Optional[str]]:
    """Derives unique immediate dominator (idom) for each node."""
    idom: Dict[str, Optional[str]] = {}
    for node, d_set in dom.items():
        strict = d_set - {node}
        idom_node = None
        for cand in strict:
            if all(cand not in (dom[other] - {other}) for other in strict if other != cand):
                idom_node = cand
                break
        idom[node] = idom_node
    return idom


def compute_dominance_frontiers(
    blocks: List[LabBlock],
    idom: Dict[str, Optional[str]]
) -> Dict[str, Set[str]]:
    """Computes Dominance Frontier for every block in the CFG."""
    df: Dict[str, Set[str]] = {b.name: set() for b in blocks}
    for b in blocks:
        for p in b.preds:
            runner = p.name
            while runner and runner != idom.get(b.name):
                df[runner].add(b.name)
                runner = idom.get(runner)
    return df


def test_cfg_dominance_frontiers():
    print("Running Test Suite 1: CFG Dominance Sets & Minimal Phi Placement...")
    # Construct diamond CFG: Entry -> (Then, Else) -> Merge
    entry = LabBlock("Entry")
    b_then = LabBlock("Then")
    b_else = LabBlock("Else")
    merge = LabBlock("Merge")

    entry.connect(b_then)
    entry.connect(b_else)
    b_then.connect(merge)
    b_else.connect(merge)

    blocks = [entry, b_then, b_else, merge]
    dom = compute_dominators(entry, blocks)

    # Entry dominates all blocks
    assert dom["Entry"] == {"Entry"}
    assert "Entry" in dom["Then"]
    assert "Entry" in dom["Else"]
    assert "Entry" in dom["Merge"]
    # Then and Else do NOT dominate Merge
    assert "Then" not in dom["Merge"]
    assert "Else" not in dom["Merge"]

    idom = compute_immediate_dominators(dom)
    assert idom["Merge"] == "Entry"

    df = compute_dominance_frontiers(blocks, idom)
    # Dominance frontier of Then and Else must strictly be {Merge}
    assert df["Then"] == {"Merge"}
    assert df["Else"] == {"Merge"}
    assert df["Merge"] == set()
    print("  Passed! Dominator tree and dominance frontiers correctly identify Merge as Phi placement point.")


def test_dead_code_elimination():
    print("Running Test Suite 2: SSA Dead Code Elimination (DCE)...")
    # Instructions: %a = 10; %b = 20; %unused = 999; %c = add %a, %b; return %c
    instructions = [
        ("assign", "%a", ["10"]),
        ("assign", "%b", ["20"]),
        ("assign", "%unused", ["999"]),
        ("add", "%c", ["%a", "%b"]),
        ("ret", "", ["%c"])
    ]
    # Mark used variables
    used = set()
    for _, _, args in instructions:
        for a in args:
            if a.startswith("%"):
                used.add(a)

    # Prune
    pruned = [inst for inst in instructions if inst[0] == "ret" or inst[1] in used]
    assert len(pruned) == 4
    pruned_vars = [inst[1] for inst in pruned]
    assert "%unused" not in pruned_vars
    assert "%a" in pruned_vars and "%b" in pruned_vars and "%c" in pruned_vars
    print("  Passed! Dead code elimination successfully removed unused SSA variables.")


def test_jit_tiering_and_bailout():
    print("Running Test Suite 3: JIT Tiering & Speculative Deoptimization...")
    invocations = 0
    is_compiled = False
    deopts = 0

    def run_method(arg):
        nonlocal invocations, is_compiled, deopts
        invocations += 1
        if invocations >= 10:
            is_compiled = True

        if is_compiled:
            if isinstance(arg, int):
                return arg * 2, "JIT_TIER_1"
            else:
                # Type bailout! Revert to interpreter
                is_compiled = False
                deopts += 1
                return len(arg) * 2, "DEOPT_BAILOUT"
        return (arg * 2 if isinstance(arg, int) else len(arg) * 2), "INTERPRETER"

    # 9 calls in interpreter
    for _ in range(9):
        _, mode = run_method(5)
        assert mode == "INTERPRETER"

    # 10th call tiers up to JIT
    _, mode = run_method(5)
    assert mode == "JIT_TIER_1"
    assert is_compiled is True

    # Call with string -> Triggers deoptimization bailout!
    _, mode = run_method("hello")
    assert mode == "DEOPT_BAILOUT"
    assert is_compiled is False
    assert deopts == 1
    print("  Passed! Dynamic tiering and speculative deoptimization bailout verified.")


if __name__ == "__main__":
    print("================================================================================")
    print("LEVEL 7 LAB 09: COMPILER SSA DOMINANCE & JIT TIERING ENGINE")
    print("================================================================================")
    test_cfg_dominance_frontiers()
    test_dead_code_elimination()
    test_jit_tiering_and_bailout()
    print("================================================================================")
    print("ALL 3 TEST SUITES PASSED CLEANLY (EXIT CODE 0)")
    print("================================================================================")
