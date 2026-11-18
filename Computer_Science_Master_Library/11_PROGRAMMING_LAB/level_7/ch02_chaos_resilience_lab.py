"""
ch02_chaos_resilience_lab.py
Level 7 Companion Lab: High-Availability Split-Brain Fencing & Chaos Monkey.
Pure Python/Standard Library implementation with zero external dependencies.
"""

from __future__ import annotations
import sys
from typing import Dict, List, Optional

# Windows UTF-8 console output
sys.stdout.reconfigure(encoding="utf-8")


class LabFencingToken:
    """Generation epoch fencing token."""
    def __init__(self, epoch: int, leader_id: str):
        self.epoch = epoch
        self.leader_id = leader_id


class LabSharedStorage:
    """Target storage enforcing epoch fencing checks."""
    def __init__(self):
        self.current_epoch = 0
        self.store: Dict[str, str] = {}

    def write(self, token: LabFencingToken, key: str, value: str) -> bool:
        if token.epoch < self.current_epoch:
            return False  # Fenced out!
        if token.epoch > self.current_epoch:
            self.current_epoch = token.epoch
        self.store[key] = value
        return True


class LabHANode:
    """High-availability node with state and simulated fault flags."""
    def __init__(self, node_id: str, storage: LabSharedStorage):
        self.node_id = node_id
        self.storage = storage
        self.is_leader = False
        self.is_alive = True
        self.epoch = 0

    def promote(self, epoch: int) -> None:
        self.is_leader = True
        self.epoch = epoch

    def demote(self) -> None:
        self.is_leader = False

    def write(self, key: str, value: str) -> bool:
        if not self.is_alive or not self.is_leader:
            return False
        token = LabFencingToken(self.epoch, self.node_id)
        return self.storage.write(token, key, value)


class LabHACoordinator:
    """Manages quorums and drives automated failover."""
    def __init__(self, nodes: List[LabHANode]):
        self.nodes = nodes
        self.epoch = 0
        self.active_leader: Optional[LabHANode] = None
        self.reconcile()

    def reconcile(self) -> Optional[LabHANode]:
        alive = [n for n in self.nodes if n.is_alive]
        quorum = (len(self.nodes) // 2) + 1

        if len(alive) < quorum:
            if self.active_leader:
                self.active_leader.demote()
                self.active_leader = None
            return None

        if not self.active_leader or not self.active_leader.is_alive:
            if self.active_leader:
                self.active_leader.demote()
            self.epoch += 1
            new_leader = alive[0]
            new_leader.promote(self.epoch)
            self.active_leader = new_leader

        return self.active_leader


def test_initial_leader_promotion():
    print("Running Test Suite 1: HA Quorum Leader Promotion...")
    storage = LabSharedStorage()
    nodes = [LabHANode(f"N{i}", storage) for i in range(3)]
    coord = LabHACoordinator(nodes)

    assert coord.active_leader is not None
    assert coord.active_leader.node_id == "N0"
    assert coord.active_leader.epoch == 1

    ok = coord.active_leader.write("service:status", "HEALTHY")
    assert ok is True
    assert storage.store["service:status"] == "HEALTHY"
    print("  Passed! Primary leader promoted with epoch 1; successfully wrote to storage.")


def test_automated_failover_and_epoch_increment():
    print("Running Test Suite 2: Automated Failover on Primary Crash...")
    storage = LabSharedStorage()
    nodes = [LabHANode(f"N{i}", storage) for i in range(3)]
    coord = LabHACoordinator(nodes)

    old_leader = coord.active_leader
    # Initial write by old leader at epoch 1
    old_leader.write("service:status", "OLD_LEADER_ACTIVE")
    assert storage.current_epoch == 1

    # Crash old leader (N0)
    old_leader.is_alive = False

    # Trigger coordinator reconciliation
    new_leader = coord.reconcile()
    assert new_leader is not None
    assert new_leader.node_id == "N1"
    assert new_leader.epoch == 2
    assert storage.current_epoch == 1  # Storage remains at 1 until new leader writes

    ok = new_leader.write("service:status", "FAILOVER_COMPLETE")
    assert ok is True
    assert storage.current_epoch == 2
    assert storage.store["service:status"] == "FAILOVER_COMPLETE"
    print("  Passed! Standby promoted to leader with incremented epoch 2.")


def test_split_brain_fencing_protection():
    print("Running Test Suite 3: Split-Brain Fencing Token Enforcement...")
    storage = LabSharedStorage()
    nodes = [LabHANode(f"N{i}", storage) for i in range(3)]
    coord = LabHACoordinator(nodes)

    old_leader = coord.active_leader  # N0 with epoch 1
    old_leader.write("service:status", "EPOCH1_OK")
    assert storage.current_epoch == 1

    old_leader.is_alive = False
    new_leader = coord.reconcile()  # Promotes N1 with epoch 2
    assert new_leader.epoch == 2
    # New leader writes to storage, advancing storage current_epoch to 2
    new_leader.write("service:status", "EPOCH2_OK")
    assert storage.current_epoch == 2

    # Now resurrect N0 as a "Zombie Primary" that still thinks it is leader at epoch 1
    old_leader.is_alive = True
    old_leader.is_leader = True

    # Zombie N0 tries to overwrite storage with stale epoch 1
    zombie_write_ok = old_leader.write("service:status", "ZOMBIE_CORRUPTION")
    assert zombie_write_ok is False, "Storage failed to fence out stale leader write!"
    assert storage.store["service:status"] != "ZOMBIE_CORRUPTION"
    print("  Passed! Storage backend strictly rejected stale leader write via fencing token.")


if __name__ == "__main__":
    print("================================================================================")
    print("LEVEL 7 LAB 02: HIGH-AVAILABILITY & SPLIT-BRAIN FENCING TESTBED")
    print("================================================================================")
    test_initial_leader_promotion()
    test_automated_failover_and_epoch_increment()
    test_split_brain_fencing_protection()
    print("================================================================================")
    print("ALL 3 TEST SUITES PASSED CLEANLY (EXIT CODE 0)")
    print("================================================================================")
