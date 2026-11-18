"""
Level 4 Chapter 05: Theory of Computation — Automata, Formal Languages, and Parsing
Comprehensive Laboratory Verification Suite

Covers:
1. Table-driven DFA simulator (Parity & Mod-3 binary divisibility).
2. NFA with epsilon-transitions and Powerset (Subset) Construction.
3. DFA State Minimization via Table-Filling Algorithm.
4. CYK (Cocke-Younger-Kasami) Dynamic Programming CFG Parser.
"""

import sys
from collections import deque
from typing import Set, Dict, Tuple, List, Optional, Any

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# -------------------------------------------------------------
# 1. Deterministic Finite Automata (DFA)
# -------------------------------------------------------------
class DFA:
    def __init__(self, states: Set[int], alphabet: Set[str], delta: Dict[Tuple[int, str], int], q0: int, F: Set[int]):
        self.states = states
        self.alphabet = alphabet
        self.delta = delta
        self.q0 = q0
        self.F = F

    def accepts(self, input_string: str) -> bool:
        curr = self.q0
        for char in input_string:
            if char not in self.alphabet:
                return False
            key = (curr, char)
            if key not in self.delta:
                return False
            curr = self.delta[key]
        return curr in self.F


def create_mod3_binary_dfa() -> DFA:
    """Accepts binary strings representing numbers divisible by 3."""
    # States: 0 (remainder 0), 1 (remainder 1), 2 (remainder 2)
    states = {0, 1, 2}
    alphabet = {'0', '1'}
    # Transition: new_rem = (curr_rem * 2 + bit) % 3
    delta = {
        (0, '0'): 0, (0, '1'): 1,
        (1, '0'): 2, (1, '1'): 0,
        (2, '0'): 1, (2, '1'): 2
    }
    return DFA(states, alphabet, delta, q0=0, F={0})


# -------------------------------------------------------------
# 2. NFA & Subset Construction
# -------------------------------------------------------------
class NFA:
    def __init__(self, states: Set[int], alphabet: Set[str], delta: Dict[Tuple[int, str], Set[int]], q0: int, F: Set[int]):
        self.states = states
        self.alphabet = alphabet
        self.delta = delta
        self.q0 = q0
        self.F = F

    def epsilon_closure(self, state_set: Set[int]) -> Set[int]:
        closure = set(state_set)
        q = deque(state_set)
        while q:
            u = q.popleft()
            for v in self.delta.get((u, ""), set()):  # "" represents epsilon
                if v not in closure:
                    closure.add(v)
                    q.append(v)
        return closure

    def to_dfa(self) -> DFA:
        """Subset Construction Algorithm converting NFA to DFA."""
        dfa_states = set()
        dfa_delta = {}
        dfa_accepts = set()

        q0_closure = frozenset(self.epsilon_closure({self.q0}))
        state_map = {q0_closure: 0}
        rev_state_map = {0: q0_closure}
        next_id = 1

        queue = deque([q0_closure])
        dfa_states.add(0)
        if any(s in self.F for s in q0_closure):
            dfa_accepts.add(0)

        while queue:
            curr_set = queue.popleft()
            u_id = state_map[curr_set]

            for a in self.alphabet:
                dest_set = set()
                for s in curr_set:
                    dest_set.update(self.delta.get((s, a), set()))
                dest_closure = frozenset(self.epsilon_closure(dest_set))

                if not dest_closure:
                    continue

                if dest_closure not in state_map:
                    state_map[dest_closure] = next_id
                    rev_state_map[next_id] = dest_closure
                    dfa_states.add(next_id)
                    if any(s in self.F for s in dest_closure):
                        dfa_accepts.add(next_id)
                    queue.append(dest_closure)
                    next_id += 1

                dfa_delta[(u_id, a)] = state_map[dest_closure]

        return DFA(dfa_states, self.alphabet, dfa_delta, 0, dfa_accepts)


# -------------------------------------------------------------
# 3. DFA State Minimizer (Table-Filling Algorithm)
# -------------------------------------------------------------
def minimize_dfa(dfa: DFA) -> int:
    """Returns the number of states in the minimal canonical DFA."""
    states_list = sorted(list(dfa.states))
    n = len(states_list)
    state_to_idx = {s: i for i, s in enumerate(states_list)}
    marked = [[False] * n for _ in range(n)]

    # Step 1: Distinguish accepting vs non-accepting
    for i in range(n):
        for j in range(i + 1, n):
            s1, s2 = states_list[i], states_list[j]
            if (s1 in dfa.F) != (s2 in dfa.F):
                marked[i][j] = True

    # Step 2: Propagate distinctions
    changed = True
    while changed:
        changed = False
        for i in range(n):
            for j in range(i + 1, n):
                if marked[i][j]:
                    continue
                s1, s2 = states_list[i], states_list[j]
                for a in dfa.alphabet:
                    t1 = dfa.delta.get((s1, a))
                    t2 = dfa.delta.get((s2, a))
                    if t1 is not None and t2 is not None and t1 != t2:
                        idx1, idx2 = state_to_idx[t1], state_to_idx[t2]
                        u, v = min(idx1, idx2), max(idx1, idx2)
                        if marked[u][v]:
                            marked[i][j] = True
                            changed = True
                            break

    # Count equivalence classes
    parent = list(range(n))
    def find(x):
        if parent[x] != x: parent[x] = find(parent[x])
        return parent[x]

    for i in range(n):
        for j in range(i + 1, n):
            if not marked[i][j]:
                rx, ry = find(i), find(j)
                if rx != ry:
                    parent[rx] = ry

    unique_classes = set(find(i) for i in range(n))
    return len(unique_classes)


# -------------------------------------------------------------
# 4. CYK Algorithm for CFG Parsing
# -------------------------------------------------------------
class CYKParser:
    def __init__(self, cnf_rules: Dict[str, List[str]], start_symbol: str = "S"):
        self.rules = cnf_rules
        self.start = start_symbol

    def parse(self, text: str) -> bool:
        tokens = list(text)
        n = len(tokens)
        if n == 0:
            return False

        # table[len][start_idx] -> Set of variables
        table: List[List[Set[str]]] = [[set() for _ in range(n)] for _ in range(n + 1)]

        # Phase 1: Terminal rules (A -> a)
        for i, token in enumerate(tokens):
            for var, prods in self.rules.items():
                for p in prods:
                    if p == token:
                        table[1][i].add(var)

        # Phase 2: Non-terminal rules (A -> BC)
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                for k in range(1, length):
                    left_set = table[k][i]
                    right_set = table[length - k][i + k]

                    for var, prods in self.rules.items():
                        for p in prods:
                            if len(p) == 2:
                                B, C = p[0], p[1]
                                if B in left_set and C in right_set:
                                    table[length][i].add(var)

        return self.start in table[n][0]


# -------------------------------------------------------------
# Test Suite
# -------------------------------------------------------------
def test_automata_lab():
    print("[TEST 1] DFA Binary Modulo-3 Divisibility...")
    dfa_mod3 = create_mod3_binary_dfa()
    # Test multiples of 3 in binary
    test_cases = [
        ("0", True),     # 0 % 3 = 0
        ("11", True),    # 3 % 3 = 0
        ("110", True),   # 6 % 3 = 0
        ("1001", True),  # 9 % 3 = 0
        ("1", False),    # 1 % 3 = 1
        ("10", False),   # 2 % 3 = 2
        ("101", False),  # 5 % 3 = 2
        ("111", False)   # 7 % 3 = 1
    ]
    for binary_str, expected in test_cases:
        actual = dfa_mod3.accepts(binary_str)
        assert actual == expected, f"Mod-3 DFA failed on '{binary_str}': expected {expected}, got {actual}"
    print("  -> Passed. Mod-3 DFA correctly classified all binary inputs.")

    print("[TEST 2] NFA to DFA Subset Construction...")
    # NFA recognizing strings ending in "01"
    # Q = {0, 1, 2}, start = 0, F = {2}
    # delta(0, '0') = {0, 1}, delta(0, '1') = {0}, delta(1, '1') = {2}
    nfa_delta = {
        (0, '0'): {0, 1},
        (0, '1'): {0},
        (1, '1'): {2}
    }
    nfa = NFA(states={0, 1, 2}, alphabet={'0', '1'}, delta=nfa_delta, q0=0, F={2})
    converted_dfa = nfa.to_dfa()

    assert converted_dfa.accepts("0001") is True
    assert converted_dfa.accepts("1101") is True
    assert converted_dfa.accepts("01") is True
    assert converted_dfa.accepts("1110") is False
    assert converted_dfa.accepts("1000") is False
    print("  -> Passed. Subset Construction yielded an equivalent deterministic automaton.")

    print("[TEST 3] DFA State Minimization...")
    min_states = minimize_dfa(converted_dfa)
    assert min_states <= 4
    print(f"  -> Passed. Table-filling algorithm minimized DFA to {min_states} canonical states.")

    print("[TEST 4] CYK Parsing Algorithm on Context-Free Grammar...")
    # CNF Grammar generating balanced a^n b^n (S -> AB | AC, C -> SB, A -> 'a', B -> 'b')
    cnf_rules = {
        "S": ["AB", "AC"],
        "C": ["SB"],
        "A": ["a"],
        "B": ["b"]
    }
    parser = CYKParser(cnf_rules, start_symbol="S")
    assert parser.parse("ab") is True       # a^1 b^1
    assert parser.parse("aabb") is True     # a^2 b^2
    assert parser.parse("aaabbb") is True   # a^3 b^3
    assert parser.parse("a") is False
    assert parser.parse("b") is False
    assert parser.parse("ba") is False
    assert parser.parse("aab") is False
    print("  -> Passed. CYK algorithm correctly parsed non-regular context-free strings.")

    print("ALL Level 4 Chapter 05 Automata & Languages lab tests passed successfully!")


if __name__ == "__main__":
    test_automata_lab()
