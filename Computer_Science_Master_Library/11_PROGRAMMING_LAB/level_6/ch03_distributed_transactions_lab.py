# -*- coding: utf-8 -*-
"""
CH03: Distributed Transactions and Consistency Models Lab
=========================================================
Covers:
1. Two-Phase Commit (2PC) Protocol with Atomic Commit and Abort Rollback.
2. State-Based CRDTs: G-Counter, PN-Counter, and LWW-Element-Set.
3. Verification of Semilattice Invariants: Commutativity, Associativity, Idempotency.
"""
import sys
import copy
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any

sys.stdout.reconfigure(encoding="utf-8")


# ============================================================================
# Section 1: Two-Phase Commit (2PC) Distributed Transaction Engine
# ============================================================================

class ParticipantStatus(Enum):
    INIT = "INIT"
    PREPARED = "PREPARED"
    COMMITTED = "COMMITTED"
    ABORTED = "ABORTED"


class TwoPCParticipant:
    """Simulates a database shard participating in 2PC distributed transactions."""
    def __init__(self, node_id: str, balance: int):
        self.node_id = node_id
        self.balance = balance
        self.pending_debit: Optional[int] = None
        self.status = ParticipantStatus.INIT

    def prepare(self, tx_id: str, debit_amount: int) -> bool:
        """Phase 1: Verify constraints and acquire locks."""
        if self.balance >= debit_amount:
            self.pending_debit = debit_amount
            self.status = ParticipantStatus.PREPARED
            return True  # VOTE_COMMIT
        else:
            self.status = ParticipantStatus.ABORTED
            return False  # VOTE_ABORT

    def commit(self, tx_id: str) -> None:
        """Phase 2a: Commit changes to persistent state."""
        if self.status != ParticipantStatus.PREPARED:
            raise RuntimeError(f"Node {self.node_id} cannot commit from state {self.status}")
        self.balance -= self.pending_debit
        self.pending_debit = None
        self.status = ParticipantStatus.COMMITTED

    def abort(self, tx_id: str) -> None:
        """Phase 2b: Rollback changes and release locks."""
        self.pending_debit = None
        self.status = ParticipantStatus.ABORTED


class TwoPCCoordinator:
    """Orchestrates distributed atomic transactions across multiple shards."""
    def __init__(self, participants: List[TwoPCParticipant]):
        self.participants = participants

    def execute_transfer(self, tx_id: str, transfers: Dict[str, int]) -> bool:
        """
        Executes an atomic transfer.
        transfers: {node_id: debit_amount}
        Returns True if globally committed, False if globally aborted.
        """
        nodes_by_id = {p.node_id: p for p in self.participants}
        
        # Phase 1: Prepare
        votes: Dict[str, bool] = {}
        for nid, amount in transfers.items():
            participant = nodes_by_id[nid]
            vote = participant.prepare(tx_id, amount)
            votes[nid] = vote

        # Phase 2: Decision
        all_voted_commit = all(votes.values())
        
        if all_voted_commit:
            # Broadcast GLOBAL_COMMIT
            for nid in transfers.keys():
                nodes_by_id[nid].commit(tx_id)
            return True
        else:
            # Broadcast GLOBAL_ABORT to all involved
            for nid in transfers.keys():
                nodes_by_id[nid].abort(tx_id)
            return False


# ============================================================================
# Section 2: Conflict-Free Replicated Data Types (CRDTs)
# ============================================================================

class GCounter:
    """Grow-Only Counter (CvRDT). Monotonically increases across nodes."""
    def __init__(self, node_id: str, all_node_ids: List[str]):
        self.node_id = node_id
        self.vector: Dict[str, int] = {nid: 0 for nid in all_node_ids}

    def increment(self, delta: int = 1) -> None:
        if delta < 0:
            raise ValueError("GCounter increments must be non-negative")
        self.vector[self.node_id] += delta

    @property
    def value(self) -> int:
        return sum(self.vector.values())

    def merge(self, other: 'GCounter') -> 'GCounter':
        """Semilattice join operator: component-wise max."""
        merged = GCounter(self.node_id, list(self.vector.keys()))
        for k in self.vector.keys():
            merged.vector[k] = max(self.vector[k], other.vector[k])
        return merged


class PNCounter:
    """Positive-Negative Counter (CvRDT). Supports both increments and decrements."""
    def __init__(self, node_id: str, all_node_ids: List[str]):
        self.node_id = node_id
        self.p_counter = GCounter(node_id, all_node_ids)
        self.n_counter = GCounter(node_id, all_node_ids)

    def increment(self, delta: int = 1) -> None:
        self.p_counter.increment(delta)

    def decrement(self, delta: int = 1) -> None:
        self.n_counter.increment(delta)

    @property
    def value(self) -> int:
        return self.p_counter.value - self.n_counter.value

    def merge(self, other: 'PNCounter') -> 'PNCounter':
        merged = PNCounter(self.node_id, list(self.p_counter.vector.keys()))
        merged.p_counter = self.p_counter.merge(other.p_counter)
        merged.n_counter = self.n_counter.merge(other.n_counter)
        return merged


class LWWElementSet:
    """Last-Write-Wins Element Set (CvRDT). Resolves add/remove conflicts via timestamps."""
    def __init__(self):
        self.add_set: Dict[str, float] = {}     # element -> timestamp
        self.remove_set: Dict[str, float] = {}  # element -> timestamp

    def add(self, element: str, timestamp: float) -> None:
        prev_ts = self.add_set.get(element, -1.0)
        if timestamp > prev_ts:
            self.add_set[element] = timestamp

    def remove(self, element: str, timestamp: float) -> None:
        prev_ts = self.remove_set.get(element, -1.0)
        if timestamp > prev_ts:
            self.remove_set[element] = timestamp

    def read(self) -> Set[str]:
        """An element is in the set iff add_timestamp > remove_timestamp."""
        result = set()
        for elem, add_ts in self.add_set.items():
            rem_ts = self.remove_set.get(elem, -1.0)
            if add_ts > rem_ts:
                result.add(elem)
        return result

    def merge(self, other: 'LWWElementSet') -> 'LWWElementSet':
        merged = LWWElementSet()
        all_add_keys = set(self.add_set.keys()).union(set(other.add_set.keys()))
        for k in all_add_keys:
            merged.add_set[k] = max(self.add_set.get(k, -1.0), other.add_set.get(k, -1.0))
            
        all_rem_keys = set(self.remove_set.keys()).union(set(other.remove_set.keys()))
        for k in all_rem_keys:
            merged.remove_set[k] = max(self.remove_set.get(k, -1.0), other.remove_set.get(k, -1.0))
        return merged


# ============================================================================
# Section 3: Automated Verification Test Suite
# ============================================================================

def run_tests():
    print("=== Level 6 Chapter 3: Distributed Transactions & CRDTs Lab ===")

    # Test 1: 2PC Happy Path (Global Commit)
    p1 = TwoPCParticipant("SHARD_NYC", balance=500)
    p2 = TwoPCParticipant("SHARD_LON", balance=300)
    coordinator = TwoPCCoordinator([p1, p2])

    ok1 = coordinator.execute_transfer("tx_001", {"SHARD_NYC": 100, "SHARD_LON": 50})
    assert ok1 is True
    assert p1.balance == 400
    assert p2.balance == 250
    assert p1.status == ParticipantStatus.COMMITTED
    assert p2.status == ParticipantStatus.COMMITTED
    print("  [PASS] 2PC Happy-Path: Global Commit Across Distributed Shards Verified")

    # Test 2: 2PC Failure Path (Global Abort Rollback)
    # SHARD_LON only has $250, but transfer requests $400 -> Should abort both!
    ok2 = coordinator.execute_transfer("tx_002", {"SHARD_NYC": 50, "SHARD_LON": 400})
    assert ok2 is False
    assert p1.balance == 400  # P1 was NOT debited!
    assert p2.balance == 250  # P2 was NOT debited!
    assert p1.status == ParticipantStatus.ABORTED
    assert p2.status == ParticipantStatus.ABORTED
    print("  [PASS] 2PC Abort Rollback: Insufficient Balance Triggers Full Reversion")

    # Test 3: PN-Counter CRDT Convergence
    node_ids = ["A", "B", "C"]
    c_a = PNCounter("A", node_ids)
    c_b = PNCounter("B", node_ids)

    # A increments 10, decrements 2 -> Net 8
    c_a.increment(10)
    c_a.decrement(2)
    assert c_a.value == 8

    # B increments 5, decrements 1 -> Net 4
    c_b.increment(5)
    c_b.decrement(1)
    assert c_b.value == 4

    # Merge A and B
    merged_a = c_a.merge(c_b)
    merged_b = c_b.merge(c_a)
    
    # Commutativity check: A merge B == B merge A
    assert merged_a.value == merged_b.value == (8 + 4) == 12
    # Idempotence check: merge with self changes nothing
    assert merged_a.merge(merged_a).value == 12
    print(f"  [PASS] PN-Counter CRDT Converged: 8 + 4 = {merged_a.value} (Commutative & Idempotent)")

    # Test 4: LWW-Element-Set Add/Remove & Concurrent Resolution
    set1 = LWWElementSet()
    set2 = LWWElementSet()

    set1.add("item_laptop", timestamp=100.0)
    set1.add("item_mouse", timestamp=105.0)
    
    # Node 2 removes laptop at t=110, adds keyboard at t=102
    set2.remove("item_laptop", timestamp=110.0)  # Later timestamp than add(100.0)
    set2.add("item_keyboard", timestamp=102.0)

    # Merge
    merged_set = set1.merge(set2)
    current_elements = merged_set.read()
    
    assert "item_laptop" not in current_elements  # Removed at t=110 > t=100
    assert "item_mouse" in current_elements
    assert "item_keyboard" in current_elements
    print(f"  [PASS] LWW-Element-Set CRDT Conflict Resolution Validated: {current_elements}")

    print("ALL TESTS PASSED: Level 6 Chapter 3 Distributed Transactions & CRDTs verified successfully.")


if __name__ == "__main__":
    run_tests()
