"""
PROJECT OLYMPUS: Planetary-Scale Autonomous Verified Micro-Engine
Core System Architecture & Integration Engine - Level 9 Capstone
"""
import sys
import math
from typing import Dict, List, Tuple, Set, Optional, Any
from enum import Enum

sys.stdout.reconfigure(encoding="utf-8")

BN254_PRIME = 21888242871839275222246405745257275088548364400416034343698204186575808495617

# =========================================================================
# 1. Substructural Type System (Affine Moves & Borrow Invariant)
# =========================================================================
class AffineViolationError(Exception):
    pass

class OlympusAffineEnv:
    def __init__(self):
        self.bindings: Dict[str, Dict[str, Any]] = {}
        self.active_borrows: Dict[str, str] = {}  # borrow_id -> 'SHARED' | 'EXCLUSIVE'

    def declare(self, name: str, is_linear: bool = False) -> None:
        if name in self.bindings:
            raise AffineViolationError(f"Identifier '{name}' already declared.")
        self.bindings[name] = {"is_moved": False, "is_linear": is_linear, "shared": 0, "exclusive": False}

    def move(self, src: str, dst: str) -> None:
        meta = self._get(src)
        if meta["shared"] > 0 or meta["exclusive"]:
            raise AffineViolationError(f"Cannot move '{src}' while active borrows exist.")
        meta["is_moved"] = True
        self.declare(dst, is_linear=meta["is_linear"])

    def borrow_shared(self, name: str, bid: str) -> None:
        meta = self._get(name)
        if meta["exclusive"]:
            raise AffineViolationError(f"Cannot borrow '{name}' as shared while exclusively borrowed.")
        meta["shared"] += 1
        self.active_borrows[bid] = "SHARED"

    def borrow_exclusive(self, name: str, bid: str) -> None:
        meta = self._get(name)
        if meta["shared"] > 0 or meta["exclusive"]:
            raise AffineViolationError(f"Cannot borrow '{name}' as exclusive while active borrows exist.")
        meta["exclusive"] = True
        self.active_borrows[bid] = "EXCLUSIVE"

    def release_borrow(self, name: str, bid: str) -> None:
        kind = self.active_borrows.pop(bid)
        meta = self.bindings[name]
        if kind == "SHARED":
            meta["shared"] -= 1
        elif kind == "EXCLUSIVE":
            meta["exclusive"] = False

    def consume(self, name: str) -> None:
        meta = self._get(name)
        if meta["shared"] > 0 or meta["exclusive"]:
            raise AffineViolationError(f"Cannot consume '{name}' while active borrows exist.")
        meta["is_moved"] = True

    def close_scope(self) -> None:
        for name, meta in self.bindings.items():
            if meta["is_linear"] and not meta["is_moved"]:
                raise AffineViolationError(f"Linear resource leak: '{name}' dropped without consumption.")

    def _get(self, name: str) -> Dict[str, Any]:
        if name not in self.bindings:
            raise AffineViolationError(f"Variable '{name}' not found.")
        meta = self.bindings[name]
        if meta["is_moved"]:
            raise AffineViolationError(f"Use of moved value: '{name}'.")
        return meta

# =========================================================================
# 2. Planetary Consensus & Hybrid Logical Clocks (HLC)
# =========================================================================
class OlympusHlcTimestamp:
    def __init__(self, l: int, c: int):
        self.l = l
        self.c = c

    def __lt__(self, other: 'OlympusHlcTimestamp') -> bool:
        if self.l != other.l:
            return self.l < other.l
        return self.c < other.c

    def __repr__(self) -> str:
        return f"({self.l}, {self.c})"

class OlympusHlc:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.l: int = 0
        self.c: int = 0

    def tick(self, pt: int) -> OlympusHlcTimestamp:
        l_old = self.l
        self.l = max(l_old, pt)
        if self.l == l_old:
            self.c += 1
        else:
            self.c = 0
        return OlympusHlcTimestamp(self.l, self.c)

    def update(self, remote: OlympusHlcTimestamp, pt: int) -> OlympusHlcTimestamp:
        l_old = self.l
        self.l = max(l_old, remote.l, pt)
        if self.l == l_old and self.l == remote.l:
            self.c = max(self.c, remote.c) + 1
        elif self.l == l_old:
            self.c += 1
        elif self.l == remote.l:
            self.c = remote.c + 1
        else:
            self.c = 0
        return OlympusHlcTimestamp(self.l, self.c)

# =========================================================================
# 3. Autonomous Invariant Supervisor & Self-Healing
# =========================================================================
class OlympusSupervisorViolation(Exception):
    pass

class OlympusSupervisor:
    def __init__(self, max_actions: int = 10, forbidden: Set[str] = None):
        self.max_actions = max_actions
        self.step_count = 0
        self.forbidden = forbidden or {"DROP TABLE", "rm -rf", "format c:", "sudo"}

    def dispatch(self, action_name: str, payload: str) -> str:
        if self.step_count >= self.max_actions:
            raise OlympusSupervisorViolation("Action budget exhausted.")
        for bad in self.forbidden:
            if bad in payload:
                raise OlympusSupervisorViolation(f"Safety policy violation: '{bad}' detected.")
        self.step_count += 1
        return f"DISPATCH_OK: {action_name}"

# =========================================================================
# 4. Cascades Memo Query Optimizer
# =========================================================================
class OlympusGroupExpr:
    def __init__(self, op_name: str, children: Tuple[int, ...], cost: float):
        self.op_name = op_name
        self.children = children
        self.cost = cost

class OlympusGroup:
    def __init__(self, gid: int):
        self.gid = gid
        self.expressions: List[OlympusGroupExpr] = []
        self.best_expr: Optional[OlympusGroupExpr] = None
        self.best_cost: float = float("inf")

    def add(self, expr: OlympusGroupExpr) -> None:
        self.expressions.append(expr)
        if expr.cost < self.best_cost:
            self.best_cost = expr.cost
            self.best_expr = expr

class OlympusMemo:
    def __init__(self):
        self.groups: Dict[int, OlympusGroup] = {}
        self.next_gid = 1

    def create_group(self) -> OlympusGroup:
        gid = self.next_gid
        self.next_gid += 1
        g = OlympusGroup(gid)
        self.groups[gid] = g
        return g

# =========================================================================
# 5. Zero-Knowledge R1CS State Transition Verifier
# =========================================================================
class OlympusPrimeField:
    def __init__(self, val: int, p: int = BN254_PRIME):
        self.p = p
        self.val = val % p

    def __add__(self, other: 'OlympusPrimeField') -> 'OlympusPrimeField':
        return OlympusPrimeField((self.val + other.val) % self.p, self.p)

    def __mul__(self, other: 'OlympusPrimeField') -> 'OlympusPrimeField':
        return OlympusPrimeField((self.val * other.val) % self.p, self.p)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OlympusPrimeField):
            return False
        return self.val == other.val and self.p == other.p

class OlympusR1CS:
    def __init__(self, A: List[List[int]], B: List[List[int]], C: List[List[int]], p: int = BN254_PRIME):
        self.p = p
        self.m = len(A)
        self.n = len(A[0])
        self.A = [[OlympusPrimeField(v, p) for v in row] for row in A]
        self.B = [[OlympusPrimeField(v, p) for v in row] for row in B]
        self.C = [[OlympusPrimeField(v, p) for v in row] for row in C]

    def verify(self, witness: List[int]) -> bool:
        s = [OlympusPrimeField(v, self.p) for v in witness]
        for j in range(self.m):
            a_val = OlympusPrimeField(0, self.p)
            b_val = OlympusPrimeField(0, self.p)
            c_val = OlympusPrimeField(0, self.p)
            for i in range(self.n):
                a_val = a_val + (self.A[j][i] * s[i])
                b_val = b_val + (self.B[j][i] * s[i])
                c_val = c_val + (self.C[j][i] * s[i])
            if (a_val * b_val) != c_val:
                return False
        return True

# =========================================================================
# 6. Reversible Adiabatic Uncomputation
# =========================================================================
class OlympusReversible:
    @staticmethod
    def toffoli(a: int, b: int, c: int) -> Tuple[int, int, int]:
        return (a, b, c ^ (a & b))

    @staticmethod
    def uncompute_cycle(x1: int, x2: int) -> Tuple[int, int]:
        # Compute forward: x1 AND x2 into ancilla 0
        _, _, g = OlympusReversible.toffoli(x1, x2, 0)
        # Copy to clean target register
        out = 0 ^ g
        # Uncompute garbage g back to 0
        _, _, restored = OlympusReversible.toffoli(x1, x2, g)
        return (out, restored)
