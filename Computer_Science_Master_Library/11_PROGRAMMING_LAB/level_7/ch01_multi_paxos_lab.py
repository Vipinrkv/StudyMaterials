"""
ch01_multi_paxos_lab.py
Level 7 Companion Lab: Multi-Paxos Consensus Engine & Stable Leader Fast-Path.
Pure Python/Standard Library implementation with zero external dependencies.
"""

from __future__ import annotations
import sys
import copy
from typing import Dict, List, Optional, Tuple, Any

# Windows UTF-8 console output
sys.stdout.reconfigure(encoding="utf-8")


class LabPaxosSlot:
    """Slot state for Multi-Paxos log."""
    def __init__(self, slot_id: int):
        self.slot_id = slot_id
        self.promised_ballot: int = 0
        self.accepted_ballot: int = 0
        self.accepted_value: Optional[Dict[str, Any]] = None
        self.is_committed: bool = False


class LabAcceptor:
    """Acceptor role handling Prepare (Phase 1) and Accept (Phase 2)."""
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.slots: Dict[int, LabPaxosSlot] = {}
        self.max_promised_ballot: int = 0
        self.is_alive = True

    def _get_slot(self, slot_id: int) -> LabPaxosSlot:
        if slot_id not in self.slots:
            self.slots[slot_id] = LabPaxosSlot(slot_id)
        return self.slots[slot_id]

    def handle_prepare(self, ballot: int, slot_id: int) -> Tuple[bool, int, Optional[Dict[str, Any]]]:
        if not self.is_alive:
            return False, 0, None
        slot = self._get_slot(slot_id)
        if ballot >= slot.promised_ballot and ballot >= self.max_promised_ballot:
            slot.promised_ballot = ballot
            self.max_promised_ballot = ballot
            return True, slot.accepted_ballot, slot.accepted_value
        return False, slot.promised_ballot, None

    def handle_accept(self, ballot: int, slot_id: int, value: Dict[str, Any]) -> bool:
        if not self.is_alive:
            return False
        slot = self._get_slot(slot_id)
        if ballot >= slot.promised_ballot:
            slot.promised_ballot = ballot
            slot.accepted_ballot = ballot
            slot.accepted_value = copy.deepcopy(value)
            return True
        return False

    def mark_committed(self, slot_id: int) -> None:
        if self.is_alive:
            self._get_slot(slot_id).is_committed = True


class LabMultiPaxosLeader:
    """Leader orchestrating Multi-Paxos phases and state machine updates."""
    def __init__(self, leader_id: str, acceptors: List[LabAcceptor]):
        self.leader_id = leader_id
        self.acceptors = acceptors
        self.ballot = 100
        self.next_slot = 1
        self.last_applied_slot = 0
        self.is_stable_leader = False
        self.state_machine: Dict[str, Any] = {}

    def acquire_leadership(self, max_slot: int = 5) -> bool:
        self.ballot += 1
        quorum = (len(self.acceptors) // 2) + 1

        for slot_id in range(1, max_slot + 1):
            promises = 0
            highest_b = -1
            chosen_v = None

            for acc in self.acceptors:
                ok, b, v = acc.handle_prepare(self.ballot, slot_id)
                if ok:
                    promises += 1
                    if v is not None and b > highest_b:
                        highest_b = b
                        chosen_v = v

            if promises < quorum:
                self.is_stable_leader = False
                return False

            if chosen_v is not None:
                self._replicate_phase2(slot_id, chosen_v)

        self.is_stable_leader = True
        return True

    def propose(self, command: Dict[str, Any]) -> Tuple[bool, int]:
        if not self.is_stable_leader:
            ok = self.acquire_leadership()
            if not ok:
                return False, -1

        slot = self.next_slot
        self.next_slot += 1
        success = self._replicate_phase2(slot, command)
        if success:
            self._apply()
            return True, slot
        return False, slot

    def _replicate_phase2(self, slot_id: int, command: Dict[str, Any]) -> bool:
        quorum = (len(self.acceptors) // 2) + 1
        acks = 0
        for acc in self.acceptors:
            if acc.handle_accept(self.ballot, slot_id, command):
                acks += 1

        if acks >= quorum:
            for acc in self.acceptors:
                acc.mark_committed(slot_id)
            return True
        return False

    def _apply(self) -> None:
        while True:
            target = self.last_applied_slot + 1
            # Check if any live acceptor has target committed
            found = False
            for acc in self.acceptors:
                if acc.is_alive and target in acc.slots:
                    slot = acc.slots[target]
                    if slot.is_committed and slot.accepted_value:
                        cmd = slot.accepted_value
                        if cmd.get("op") == "SET":
                            self.state_machine[cmd["key"]] = cmd["val"]
                        self.last_applied_slot = target
                        found = True
                        break
            if not found:
                break


def test_leadership_acquisition():
    print("Running Test Suite 1: Multi-Paxos Leadership Acquisition (Phase 1)...")
    acceptors = [LabAcceptor(f"A{i}") for i in range(5)]
    leader = LabMultiPaxosLeader("L1", acceptors)

    ok = leader.acquire_leadership(max_slot=5)
    assert ok is True
    assert leader.is_stable_leader is True
    print("  Passed! Leader successfully established stable leadership across 5 acceptors.")


def test_fast_path_replication():
    print("Running Test Suite 2: Stable Leader Fast-Path Phase 2 Writes...")
    acceptors = [LabAcceptor(f"A{i}") for i in range(5)]
    leader = LabMultiPaxosLeader("L1", acceptors)
    leader.acquire_leadership()

    # Issue 3 consecutive writes directly in 1 RTT
    ok1, s1 = leader.propose({"op": "SET", "key": "k1", "val": "v1"})
    ok2, s2 = leader.propose({"op": "SET", "key": "k2", "val": "v2"})
    ok3, s3 = leader.propose({"op": "SET", "key": "k3", "val": "v3"})

    assert ok1 and ok2 and ok3
    assert s1 == 1 and s2 == 2 and s3 == 3
    assert leader.state_machine["k1"] == "v1"
    assert leader.state_machine["k2"] == "v2"
    assert leader.state_machine["k3"] == "v3"
    print("  Passed! Fast-path writes committed and applied sequentially to state machine.")


def test_minority_acceptor_crashes():
    print("Running Test Suite 3: Minority Acceptor Crashes & Quorum Safety...")
    acceptors = [LabAcceptor(f"A{i}") for i in range(5)]
    leader = LabMultiPaxosLeader("L1", acceptors)
    leader.acquire_leadership()

    # Crash 2 acceptors (A3, A4) -> 3 acceptors remain (Quorum = 3/5)
    acceptors[3].is_alive = False
    acceptors[4].is_alive = False

    ok, slot = leader.propose({"op": "SET", "key": "k_survive", "val": "alive"})
    assert ok is True
    assert leader.state_machine["k_survive"] == "alive"

    # Crash 1 more acceptor (A2) -> Only 2 remain (Below Quorum!)
    acceptors[2].is_alive = False
    ok_fail, _ = leader.propose({"op": "SET", "key": "k_fail", "val": "dead"})
    assert ok_fail is False
    assert "k_fail" not in leader.state_machine
    print("  Passed! Quorum correctly permits writes with 2 crashes and rejects with 3 crashes.")


if __name__ == "__main__":
    print("================================================================================")
    print("LEVEL 7 LAB 01: MULTI-PAXOS CONSENSUS & REPLICATION ENGINE")
    print("================================================================================")
    test_leadership_acquisition()
    test_fast_path_replication()
    test_minority_acceptor_crashes()
    print("================================================================================")
    print("ALL 3 TEST SUITES PASSED CLEANLY (EXIT CODE 0)")
    print("================================================================================")
