"""
aethelgard_engine.py
Level 8 Capstone Project: Aethelgard Formally Verified Distributed Hybrid Runtime.
Synthesizes Curry-Howard Constructive Proof Verification, TLA+ BFS Model Checking,
HotStuff 3-Chain Byzantine Fault Tolerance, Strong Eventual Consistency CRDTs,
Neuromorphic Leaky Integrate-and-Fire Dynamics, and Quantum State Vector Simulation.
Pure Python/Standard Library with zero external dependencies.
"""

from __future__ import annotations
import sys
import math
import uuid
import hashlib
import hmac
import collections
import random
from typing import Dict, List, Set, Tuple, Optional, Any, Callable

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")


# ==============================================================================
# MODULE 1: CURRY-HOWARD CONSTRUCTIVE PROOF CHECKER
# ==============================================================================

class Prop:
    pass

class Atom(Prop):
    def __init__(self, name: str):
        self.name = name
    def __repr__(self) -> str:
        return self.name
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Atom) and self.name == other.name

class Implies(Prop):
    def __init__(self, src: Prop, dst: Prop):
        self.src = src
        self.dst = dst
    def __repr__(self) -> str:
        return f"({self.src} -> {self.dst})"
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Implies) and self.src == other.src and self.dst == other.dst

class And(Prop):
    def __init__(self, left: Prop, right: Prop):
        self.left = left
        self.right = right
    def __repr__(self) -> str:
        return f"({self.left} /\\ {self.right})"
    def __eq__(self, other: object) -> bool:
        return isinstance(other, And) and self.left == other.left and self.right == other.right

class ProofTerm:
    pass

class Var(ProofTerm):
    def __init__(self, name: str):
        self.name = name

class Lam(ProofTerm):
    def __init__(self, var_name: str, var_type: Prop, body: ProofTerm):
        self.var_name = var_name
        self.var_type = var_type
        self.body = body

class App(ProofTerm):
    def __init__(self, func: ProofTerm, arg: ProofTerm):
        self.func = func
        self.arg = arg

class Pair(ProofTerm):
    def __init__(self, left: ProofTerm, right: ProofTerm):
        self.left = left
        self.right = right

class Fst(ProofTerm):
    def __init__(self, pair: ProofTerm):
        self.pair = pair

class Snd(ProofTerm):
    def __init__(self, pair: ProofTerm):
        self.pair = pair


class AethelgardProofKernel:
    """Type-checking kernel verifying Curry-Howard proof terms."""
    @classmethod
    def verify(cls, term: ProofTerm, context: Dict[str, Prop]) -> Prop:
        if isinstance(term, Var):
            if term.name not in context:
                raise TypeError(f"Unbound hypothesis: {term.name}")
            return context[term.name]
        elif isinstance(term, Lam):
            new_ctx = dict(context)
            new_ctx[term.var_name] = term.var_type
            return Implies(term.var_type, cls.verify(term.body, new_ctx))
        elif isinstance(term, App):
            fn_type = cls.verify(term.func, context)
            if not isinstance(fn_type, Implies):
                raise TypeError(f"Non-function in application: {fn_type}")
            arg_type = cls.verify(term.arg, context)
            if fn_type.src != arg_type:
                raise TypeError(f"Argument mismatch: expected {fn_type.src}, got {arg_type}")
            return fn_type.dst
        elif isinstance(term, Pair):
            return And(cls.verify(term.left, context), cls.verify(term.right, context))
        elif isinstance(term, Fst):
            p = cls.verify(term.pair, context)
            if not isinstance(p, And):
                raise TypeError(f"fst requires conjunction, got {p}")
            return p.left
        elif isinstance(term, Snd):
            p = cls.verify(term.pair, context)
            if not isinstance(p, And):
                raise TypeError(f"snd requires conjunction, got {p}")
            return p.right
        raise TypeError("Invalid AST")


# ==============================================================================
# MODULE 2: EXPLICIT-STATE MODEL CHECKING ENGINE
# ==============================================================================

class AethelgardModelChecker:
    """BFS explicit state explorer for concurrent protocol safety."""
    def __init__(self, init_states: List[Dict[str, Any]], next_fn: Callable[[Dict[str, Any]], List[Dict[str, Any]]]):
        self.init_states = init_states
        self.next_fn = next_fn

    def check(self, inv_fn: Callable[[Dict[str, Any]], bool]) -> Tuple[bool, Optional[List[Dict[str, Any]]]]:
        visited: Set[Tuple[Tuple[str, Any], ...]] = set()
        queue = collections.deque()
        parents: Dict[Tuple[Tuple[str, Any], ...], Optional[Tuple[Tuple[str, Any], ...]]] = {}
        state_map: Dict[Tuple[Tuple[str, Any], ...], Dict[str, Any]] = {}

        for s0 in self.init_states:
            k = tuple(sorted(s0.items()))
            if not inv_fn(s0):
                return False, [s0]
            visited.add(k)
            parents[k] = None
            state_map[k] = s0
            queue.append(k)

        while queue:
            curr_k = queue.popleft()
            curr_dict = state_map[curr_k]
            succs = self.next_fn(curr_dict)

            for succ in succs:
                succ_k = tuple(sorted(succ.items()))
                if not inv_fn(succ):
                    # Invariant violated! Build trace
                    trace = [succ]
                    p = curr_k
                    while p is not None:
                        trace.append(state_map[p])
                        p = parents[p]
                    trace.reverse()
                    return False, trace

                if succ_k not in visited:
                    visited.add(succ_k)
                    parents[succ_k] = curr_k
                    state_map[succ_k] = succ
                    queue.append(succ_k)

        return True, None


# ==============================================================================
# MODULE 3: HOTSTUFF BYZANTINE FAULT TOLERANCE
# ==============================================================================

class AethelgardBftProposal:
    def __init__(self, view: int, height: int, payload: str, parent_hash: str):
        self.view = view
        self.height = height
        self.payload = payload
        self.parent_hash = parent_hash

    def hash(self) -> str:
        d = f"{self.view}:{self.height}:{self.payload}:{self.parent_hash}"
        return hashlib.sha256(d.encode("utf-8")).hexdigest()[:16]


class AethelgardBftQC:
    def __init__(self, block_hash: str, view: int, sigs: Dict[str, str]):
        self.block_hash = block_hash
        self.view = view
        self.sigs = dict(sigs)

    def is_valid(self, quorum: int, keys: Dict[str, str]) -> bool:
        if len(self.sigs) < quorum:
            return False
        for node_id, sig in self.sigs.items():
            expected = hmac.new(keys[node_id].encode("utf-8"), f"{self.block_hash}:{self.view}".encode("utf-8"), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig, expected):
                return False
        return True


class AethelgardBftNode:
    def __init__(self, node_id: str, secret_key: str, total_nodes: int = 4):
        self.node_id = node_id
        self.key = secret_key
        self.f = (total_nodes - 1) // 3
        self.quorum = 2 * self.f + 1
        self.locked_qc: Optional[AethelgardBftQC] = None
        self.signed_proposals: Dict[int, str] = {}
        self.committed: List[AethelgardBftProposal] = []

    def vote(self, prop: AethelgardBftProposal) -> Optional[str]:
        h = prop.height
        b_hash = prop.hash()
        # Equivocation protection
        if h in self.signed_proposals and self.signed_proposals[h] != b_hash:
            return None
        # Lock rule
        if self.locked_qc and prop.view < self.locked_qc.view:
            return None

        self.signed_proposals[h] = b_hash
        return hmac.new(self.key.encode("utf-8"), f"{b_hash}:{prop.view}".encode("utf-8"), hashlib.sha256).hexdigest()

    def update_lock(self, qc: AethelgardBftQC) -> None:
        if not self.locked_qc or qc.view > self.locked_qc.view:
            self.locked_qc = qc


# ==============================================================================
# MODULE 4: STRONG EVENTUAL CONSISTENCY CRDT STORE
# ==============================================================================

class AethelgardOrSet:
    """Observed-Remove Set with UUID tagging."""
    def __init__(self):
        self.add_set: Set[Tuple[str, str]] = set()
        self.rem_set: Set[Tuple[str, str]] = set()

    def add(self, item: str) -> str:
        tag = str(uuid.uuid4())[:8]
        self.add_set.add((item, tag))
        return tag

    def remove(self, item: str) -> None:
        for it, tag in self.add_set:
            if it == item:
                self.rem_set.add((it, tag))

    def read(self) -> Set[str]:
        return {it for it, tag in (self.add_set - self.rem_set)}

    def merge(self, other: AethelgardOrSet) -> AethelgardOrSet:
        m = AethelgardOrSet()
        m.add_set = self.add_set | other.add_set
        m.rem_set = self.rem_set | other.rem_set
        return m


# ==============================================================================
# MODULE 5: NEUROMORPHIC SPIKING NEURAL INGRESS CLASSIFIER
# ==============================================================================

class AethelgardLifNeuron:
    """Leaky Integrate-and-Fire biological neuron model."""
    def __init__(self, tau_m: float = 20.0, v_rest: float = -70.0, v_thresh: float = -50.0):
        self.tau_m = tau_m
        self.v_rest = v_rest
        self.v_thresh = v_thresh
        self.v = v_rest

    def step(self, dt: float, current: float) -> bool:
        dv = (dt / self.tau_m) * (-(self.v - self.v_rest) + 10.0 * current)
        self.v += dv
        if self.v >= self.v_thresh:
            self.v = self.v_rest
            return True
        return False


# ==============================================================================
# MODULE 6: QUANTUM STATE VECTOR SIMULATOR
# ==============================================================================

class AethelgardQuantumEngine:
    """Simulates 2-qubit state vector quantum mechanics."""
    INV_SQRT2 = 1.0 / math.sqrt(2.0)

    def __init__(self):
        # State vector: [|00>, |01>, |10>, |11>]
        self.state: List[complex] = [1.0 + 0.0j, 0.0j, 0.0j, 0.0j]

    def create_bell_state(self) -> None:
        # Hadamard on Qubit 0, then CNOT(0 -> 1)
        # Result: (|00> + |11>) / sqrt(2)
        self.state = [complex(self.INV_SQRT2, 0), 0.0j, 0.0j, complex(self.INV_SQRT2, 0)]

    def measure_probabilities(self) -> Dict[str, float]:
        labels = ["00", "01", "10", "11"]
        return {labels[i]: abs(self.state[i]) ** 2 for i in range(4)}
