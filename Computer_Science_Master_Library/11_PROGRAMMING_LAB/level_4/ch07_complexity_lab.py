"""
Level 4 Chapter 07 Programming Lab: Complexity, Reductions & Approximation
========================================================================
Focus: Polynomial-time 2-approximation for Vertex Cover, exact baseline,
       DPLL SAT solver with unit propagation, and 3-SAT to CLIQUE reduction.
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")
from typing import List, Set, Tuple, Dict, Optional
import itertools


# ---------------------------------------------------------------------------
# 1. Vertex Cover: 2-Approximation Algorithm via Maximal Matching
# ---------------------------------------------------------------------------

def approx_vertex_cover(num_vertices: int, edges: List[Tuple[int, int]]) -> Set[int]:
    """
    Computes a 2-approximation for Vertex Cover using maximal matching.
    Theorem: The set of endpoints of any maximal matching is a vertex cover
             whose size is at most 2 * OPT.
    """
    cover: Set[int] = set()
    uncovered_edges = list(edges)

    for u, v in uncovered_edges:
        if u not in cover and v not in cover:
            # Add both endpoints to the cover
            cover.add(u)
            cover.add(v)

    return cover


def exact_vertex_cover(num_vertices: int, edges: List[Tuple[int, int]]) -> Set[int]:
    """
    Brute-force exact minimum vertex cover solver (Exponential O(2^n)).
    Used to mathematically verify the approximation ratio.
    """
    for k in range(num_vertices + 1):
        for candidate in itertools.combinations(range(num_vertices), k):
            cover_set = set(candidate)
            is_valid = True
            for u, v in edges:
                if u not in cover_set and v not in cover_set:
                    is_valid = False
                    break
            if is_valid:
                return cover_set
    return set(range(num_vertices))


# ---------------------------------------------------------------------------
# 2. DPLL (Davis-Putnam-Logemann-Loveland) SAT Solver
# ---------------------------------------------------------------------------

# Clause represented as a set of non-zero integers (positive = literal, negative = negated)
CNF = List[Set[int]]

def dpll_solve(cnf: CNF, assignment: Dict[int, bool]) -> Optional[Dict[int, bool]]:
    """
    DPLL algorithm for CNF satisfiability:
    1. Base cases: Empty clause -> Conflict; Empty formula -> Satisfiable.
    2. Unit Propagation: If a clause has a single unassigned literal, force its truth value.
    3. Branching: Choose unassigned variable and recursively branch on True and False.
    """
    # Simplify formula based on current assignment
    simplified_cnf: CNF = []
    for clause in cnf:
        clause_satisfied = False
        remaining_literals: Set[int] = set()
        for lit in clause:
            var = abs(lit)
            if var in assignment:
                val = assignment[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_satisfied = True
                    break
            else:
                remaining_literals.add(lit)
        if not clause_satisfied:
            if not remaining_literals:
                # Contradiction: empty clause
                return None
            simplified_cnf.append(remaining_literals)

    if not simplified_cnf:
        return assignment

    # Unit Propagation: look for clauses with length 1
    for clause in simplified_cnf:
        if len(clause) == 1:
            unit_lit = next(iter(clause))
            var = abs(unit_lit)
            new_assign = dict(assignment)
            new_assign[var] = (unit_lit > 0)
            return dpll_solve(simplified_cnf, new_assign)

    # Branching: select the first unassigned variable
    all_vars = set()
    for clause in simplified_cnf:
        for lit in clause:
            all_vars.add(abs(lit))
    unassigned = [v for v in all_vars if v not in assignment]
    if not unassigned:
        return assignment

    branch_var = unassigned[0]

    # Try True
    assign_true = dict(assignment)
    assign_true[branch_var] = True
    result = dpll_solve(simplified_cnf, assign_true)
    if result is not None:
        return result

    # Try False
    assign_false = dict(assignment)
    assign_false[branch_var] = False
    return dpll_solve(simplified_cnf, assign_false)


# ---------------------------------------------------------------------------
# 3. Polynomial-Time Reduction: 3-SAT to CLIQUE
# ---------------------------------------------------------------------------

def reduce_3sat_to_clique(clauses: List[Tuple[int, int, int]]) -> Tuple[List[str], List[Tuple[int, int]], int]:
    """
    Transforms a 3-SAT formula with m clauses into a Graph G and target clique size k = m.
    Each clause generates 3 vertices. Edges exist between non-contradictory literals in different clauses.
    """
    vertices = []
    vertex_map = []  # (clause_idx, literal_val)
    
    for c_idx, clause in enumerate(clauses):
        for lit in clause:
            v_name = f"C{c_idx}_lit_{lit}"
            vertices.append(v_name)
            vertex_map.append((c_idx, lit))

    edges = []
    n_v = len(vertices)
    for i in range(n_v):
        for j in range(i + 1, n_v):
            c_i, lit_i = vertex_map[i]
            c_j, lit_j = vertex_map[j]
            # Must be from different clauses and not contradictory
            if c_i != c_j and lit_i != -lit_j:
                edges.append((i, j))

    k = len(clauses)
    return vertices, edges, k


def test_complexity_suite():
    print("[TEST 1] Vertex Cover 2-Approximation Verification...")
    # Graph with 6 vertices: Petersen-like subgraph
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 4), (4, 0),
        (0, 5), (1, 5), (2, 5)
    ]
    num_vertices = 6

    exact_cover = exact_vertex_cover(num_vertices, edges)
    opt_size = len(exact_cover)
    approx_cover = approx_vertex_cover(num_vertices, edges)
    approx_size = len(approx_cover)

    # Verify validity of approx cover
    for u, v in edges:
        assert u in approx_cover or v in approx_cover, f"Edge ({u}, {v}) not covered!"

    ratio = approx_size / opt_size
    print(f"  -> Exact OPT size: {opt_size}, 2-Approx size: {approx_size}, Ratio: {ratio:.2f} <= 2.0")
    assert approx_size <= 2 * opt_size, "Approximation ratio violated!"

    print("[TEST 2] DPLL SAT Solver on Satisfiable and Unsatisfiable CNF...")
    # Satisfiable: (x1 or x2) and (not x1 or x2) and (x1 or not x2)
    # Solution: x1 = True, x2 = True
    sat_cnf = [{1, 2}, {-1, 2}, {1, -2}]
    sol = dpll_solve(sat_cnf, {})
    assert sol is not None, "DPLL failed on satisfiable CNF!"
    print(f"  -> Found satisfying assignment: {sol}")

    # Unsatisfiable: (x1) and (not x1)
    unsat_cnf = [{1}, {-1}]
    unsat_sol = dpll_solve(unsat_cnf, {})
    assert unsat_sol is None, "DPLL incorrectly claimed satisfiability for contradiction!"
    print("  -> Correctly identified unsatisfiable formula.")

    print("[TEST 3] 3-SAT to CLIQUE Reduction Construction...")
    # Formula: (x1 or x2 or x3) and (~x1 or ~x2 or x3)
    clauses = [(1, 2, 3), (-1, -2, 3)]
    verts, graph_edges, k = reduce_3sat_to_clique(clauses)
    assert len(verts) == 6, f"Expected 6 vertices, got {len(verts)}"
    assert k == 2, f"Target clique size must equal number of clauses (2), got {k}"
    print(f"  -> Reduction successfully created {len(verts)} vertices and {len(graph_edges)} edges for k={k}.")

    print("ALL Level 4 Chapter 07 Complexity lab tests passed successfully!")


if __name__ == "__main__":
    test_complexity_suite()
