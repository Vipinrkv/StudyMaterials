"""
Level 4 Chapter 09 Programming Lab: Compiler Midend & Backend Optimization
==========================================================================
Focus: Three-Address Code (TAC), Control Flow Graph (CFG) basic blocks,
       monotone Live Variable Dataflow Analysis, Constant Propagation,
       Dead Code Elimination, and Kempe's Register Allocation.
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")
from typing import List, Dict, Set, Tuple, Optional, Any


class TACInstruction:
    def __init__(self, op: str, dest: Optional[str], src1: Optional[str], src2: Optional[str] = None):
        self.op = op          # e.g., "=", "+", "-", "*", "GOTO", "IF_GOTO"
        self.dest = dest      # Target variable name
        self.src1 = src1      # First operand
        self.src2 = src2      # Second operand

    def __repr__(self):
        if self.op == "=":
            return f"{self.dest} = {self.src1}"
        elif self.op in ("+", "-", "*", "/"):
            return f"{self.dest} = {self.src1} {self.op} {self.src2}"
        elif self.op == "GOTO":
            return f"goto {self.src1}"
        elif self.op == "IF_GOTO":
            return f"if {self.src1} goto {self.dest}"
        return f"{self.op} {self.dest}, {self.src1}, {self.src2}"


class BasicBlock:
    def __init__(self, block_id: int):
        self.id = block_id
        self.instructions: List[TACInstruction] = []
        self.predecessors: List['BasicBlock'] = []
        self.successors: List['BasicBlock'] = []
        self.gen: Set[str] = set()   # Variables used before definition
        self.kill: Set[str] = set()  # Variables defined
        self.live_in: Set[str] = set()
        self.live_out: Set[str] = set()

    def __repr__(self):
        return f"Block(B{self.id}, instrs={len(self.instructions)})"


class ControlFlowGraph:
    def __init__(self, instructions: List[TACInstruction]):
        self.instructions = instructions
        self.blocks: List[BasicBlock] = []
        self._build_cfg()

    def _build_cfg(self):
        # Identify leaders
        leaders = {0}
        labels: Dict[str, int] = {}

        for idx, inst in enumerate(self.instructions):
            if inst.op == "LABEL":
                labels[inst.src1] = idx
                leaders.add(idx)
            elif inst.op in ("GOTO", "IF_GOTO"):
                if idx + 1 < len(self.instructions):
                    leaders.add(idx + 1)

        # Create basic blocks
        sorted_leaders = sorted(list(leaders))
        block_map: Dict[int, BasicBlock] = {}

        for b_idx, start_pc in enumerate(sorted_leaders):
            end_pc = sorted_leaders[b_idx + 1] if b_idx + 1 < len(sorted_leaders) else len(self.instructions)
            bb = BasicBlock(b_idx)
            bb.instructions = self.instructions[start_pc:end_pc]
            self.blocks.append(bb)
            for pc in range(start_pc, end_pc):
                block_map[pc] = bb

        # Connect edges between blocks
        for b in self.blocks:
            if not b.instructions:
                continue
            last = b.instructions[-1]
            if last.op == "GOTO":
                target_pc = labels[last.src1]
                target_block = block_map[target_pc]
                b.successors.append(target_block)
                target_block.predecessors.append(b)
            elif last.op == "IF_GOTO":
                target_pc = labels[last.dest]
                target_block = block_map[target_pc]
                b.successors.append(target_block)
                target_block.predecessors.append(b)
                # Fallthrough
                curr_idx = self.blocks.index(b)
                if curr_idx + 1 < len(self.blocks):
                    fallthrough = self.blocks[curr_idx + 1]
                    b.successors.append(fallthrough)
                    fallthrough.predecessors.append(b)
            else:
                # Normal fallthrough
                curr_idx = self.blocks.index(b)
                if curr_idx + 1 < len(self.blocks):
                    fallthrough = self.blocks[curr_idx + 1]
                    b.successors.append(fallthrough)
                    fallthrough.predecessors.append(b)


# ---------------------------------------------------------------------------
# 1. Monotone Dataflow Analysis: Live Variables
# ---------------------------------------------------------------------------

def run_liveness_analysis(cfg: ControlFlowGraph):
    """
    Computes Live Variable Analysis:
    USE[B]: variables read before written in B
    DEF[B]: variables assigned in B
    OUT[B] = UNION_{S in Succ(B)} IN[S]
    IN[B]  = USE[B] UNION (OUT[B] \ DEF[B])
    """
    for b in cfg.blocks:
        use_set = set()
        def_set = set()
        for inst in b.instructions:
            for src in (inst.src1, inst.src2):
                if src and not src.isdigit() and src not in def_set:
                    use_set.add(src)
            if inst.dest and not inst.dest.isdigit():
                def_set.add(inst.dest)
        b.gen = use_set
        b.kill = def_set

    # Backward fixed-point iteration
    changed = True
    while changed:
        changed = False
        for b in reversed(cfg.blocks):
            new_out = set()
            for s in b.successors:
                new_out |= s.live_in
            b.live_out = new_out

            new_in = b.gen | (b.live_out - b.kill)
            if new_in != b.live_in:
                b.live_in = new_in
                changed = True


# ---------------------------------------------------------------------------
# 2. Optimization Passes: Constant Propagation & Dead Code Elimination
# ---------------------------------------------------------------------------

def optimize_constants_and_dce(instructions: List[TACInstruction]) -> List[TACInstruction]:
    """
    Executes constant propagation and dead code elimination over a linear sequence.
    """
    constants: Dict[str, int] = {}
    optimized: List[TACInstruction] = []

    # Constant Folding and Propagation Pass
    for inst in instructions:
        s1 = inst.src1
        s2 = inst.src2
        # Replace variable with known constant
        if s1 in constants:
            s1 = str(constants[s1])
        if s2 in constants:
            s2 = str(constants[s2])

        # Fold constant arithmetic
        if s1 and s2 and s1.isdigit() and s2.isdigit() and inst.op in ("+", "-", "*"):
            v1, v2 = int(s1), int(s2)
            if inst.op == "+": res = v1 + v2
            elif inst.op == "-": res = v1 - v2
            elif inst.op == "*": res = v1 * v2
            constants[inst.dest] = res
            optimized.append(TACInstruction("=", inst.dest, str(res)))
        elif inst.op == "=" and s1 and s1.isdigit():
            constants[inst.dest] = int(s1)
            optimized.append(TACInstruction("=", inst.dest, s1))
        else:
            optimized.append(TACInstruction(inst.op, inst.dest, s1, s2))

    # Dead Code Elimination Pass: remove assignments never read subsequently
    used_vars = set()
    for inst in optimized:
        for s in (inst.src1, inst.src2):
            if s and not s.isdigit():
                used_vars.add(s)

    final_pass = []
    for inst in optimized:
        # If dest is not used anywhere and instruction has no side-effects, eliminate
        if inst.dest and inst.dest not in used_vars and inst.dest != "return_val":
            continue
        final_pass.append(inst)

    return final_pass


# ---------------------------------------------------------------------------
# 3. Register Allocation via Kempe's Graph Coloring Heuristic
# ---------------------------------------------------------------------------

def allocate_registers(variables: List[str], interference: Dict[str, Set[str]], k: int) -> Dict[str, int]:
    """
    Kempe's graph coloring heuristic for register allocation with k physical registers.
    Returns: Mapping {var_name: register_color_id (1..k)}
    """
    adj = {v: set(neighbors) for v, neighbors in interference.items()}
    stack: List[str] = []
    removed = set()

    # Simplify phase
    while len(removed) < len(variables):
        found = False
        for v in variables:
            if v not in removed and len(adj[v] - removed) < k:
                stack.append(v)
                removed.add(v)
                found = True
                break
        if not found:
            # Spill candidate (highest degree)
            spill_cand = max([v for v in variables if v not in removed], key=lambda x: len(adj[x] - removed))
            stack.append(spill_cand)
            removed.add(spill_cand)

    # Select / Assign phase
    colors: Dict[str, int] = {}
    while stack:
        v = stack.pop()
        neighbor_colors = {colors[nbr] for nbr in adj[v] if nbr in colors}
        # Pick smallest available color
        assigned_color = None
        for c in range(1, k + 1):
            if c not in neighbor_colors:
                assigned_color = c
                break
        if assigned_color is None:
            raise RuntimeError(f"Register spilling required for variable '{v}' (Exceeded K={k})")
        colors[v] = assigned_color

    return colors


def test_optimizer_suite():
    print("[TEST 1] Control Flow Graph (CFG) Construction & Liveness Analysis...")
    # Program:
    # B0: a = 5; b = 10; goto B2
    # B1: a = a + 1
    # B2: if a < 20 goto B1
    # B3: return_val = a + b
    instrs = [
        TACInstruction("=", "a", "5"),
        TACInstruction("=", "b", "10"),
        TACInstruction("GOTO", None, "L_LOOP_CHECK"),
        TACInstruction("LABEL", None, "L_LOOP_BODY"),
        TACInstruction("+", "a", "a", "1"),
        TACInstruction("LABEL", None, "L_LOOP_CHECK"),
        TACInstruction("IF_GOTO", "L_LOOP_BODY", "a"),
        TACInstruction("LABEL", None, "L_EXIT"),
        TACInstruction("+", "return_val", "a", "b"),
    ]

    cfg = ControlFlowGraph(instrs)
    run_liveness_analysis(cfg)
    assert len(cfg.blocks) >= 3, f"Expected at least 3 basic blocks, got {len(cfg.blocks)}"
    print(f"  -> Built CFG with {len(cfg.blocks)} basic blocks.")
    print("  -> Live Variable Analysis converged successfully across all CFG blocks.")

    print("[TEST 2] Constant Folding & Dead Code Elimination...")
    raw_code = [
        TACInstruction("=", "x", "10"),
        TACInstruction("=", "y", "20"),
        TACInstruction("+", "dead_var", "x", "y"),  # Dead: never used
        TACInstruction("*", "z", "x", "y"),         # z = 10 * 20 = 200
        TACInstruction("=", "return_val", "z"),
    ]
    opt_code = optimize_constants_and_dce(raw_code)
    opt_dests = [inst.dest for inst in opt_code]
    assert "dead_var" not in opt_dests, "Dead Code Elimination failed to eliminate dead_var!"
    # Verify constant folding & propagation directly into return_val
    ret_inst = [inst for inst in opt_code if inst.dest == "return_val"][0]
    assert ret_inst.src1 == "200", f"Expected return_val = 200, got {ret_inst.src1}"
    print(f"  -> Successfully folded constants (return_val = {ret_inst.src1}) and eliminated dead assignments.")

    print("[TEST 3] Register Allocation via Chaitin-Kempe Graph Coloring...")
    # 4 variables: a, b, c, d
    # a conflicts with b, c
    # b conflicts with a, c, d
    # c conflicts with a, b, d
    # d conflicts with b, c
    variables = ["a", "b", "c", "d"]
    interference = {
        "a": {"b", "c"},
        "b": {"a", "c", "d"},
        "c": {"a", "b", "d"},
        "d": {"b", "c"}
    }
    # K = 3 physical registers (K-colorable: a=1, b=2, c=3, d=1)
    color_map = allocate_registers(variables, interference, k=3)
    # Verify no adjacent variables share colors
    for v, neighbors in interference.items():
        for nbr in neighbors:
            assert color_map[v] != color_map[nbr], f"Color conflict between {v} and {nbr}!"
    print(f"  -> Register allocation completed with 3 colors: {color_map} (Zero conflicts).")

    print("ALL Level 4 Chapter 09 Compiler Optimizer lab tests passed successfully!")


if __name__ == "__main__":
    test_optimizer_suite()
