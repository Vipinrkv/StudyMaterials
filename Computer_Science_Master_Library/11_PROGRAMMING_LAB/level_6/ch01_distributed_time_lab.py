# -*- coding: utf-8 -*-
"""
CH01: Distributed Systems Models, Time, and Synchronization Lab
==============================================================
Covers:
1. Lamport Logical Clocks with happens-before causality ordering.
2. Vector Clocks with causal order and concurrency (a || b) detection.
3. Chandy-Lamport Distributed Snapshot Algorithm over FIFO channels.
"""
import sys
import copy
from typing import Dict, List, Optional, Set, Tuple, Any

sys.stdout.reconfigure(encoding="utf-8")


# ============================================================================
# Section 1: Lamport Logical Clock Engine
# ============================================================================

class LamportClock:
    """Implements Leslie Lamport's 1978 scalar logical clock algorithm."""
    def __init__(self, process_id: str):
        self.process_id = process_id
        self.clock = 0

    def tick(self) -> int:
        """Local event increments clock."""
        self.clock += 1
        return self.clock

    def send_event(self) -> int:
        """Send event increments local clock and attaches it to message."""
        self.clock += 1
        return self.clock

    def receive_event(self, received_clock: int) -> int:
        """Receive event updates clock to max(local, received) + 1."""
        self.clock = max(self.clock, received_clock) + 1
        return self.clock


# ============================================================================
# Section 2: Vector Clock Engine with Concurrency Detection
# ============================================================================

class VectorClock:
    """
    Implements Mattern & Fidge Vector Clock algorithm:
    Enables exact bidirectional causality: a -> b iff V(a) < V(b).
    Enables exact concurrency detection: a || b iff neither V(a) <= V(b) nor V(b) <= V(a).
    """
    def __init__(self, process_id: str, all_process_ids: List[str]):
        self.process_id = process_id
        self.all_processes = sorted(all_process_ids)
        self.vector: Dict[str, int] = {pid: 0 for pid in self.all_processes}

    def clone(self) -> 'VectorClock':
        cloned = VectorClock(self.process_id, self.all_processes)
        cloned.vector = copy.deepcopy(self.vector)
        return cloned

    def tick(self) -> Dict[str, int]:
        self.vector[self.process_id] += 1
        return copy.deepcopy(self.vector)

    def send_event(self) -> Dict[str, int]:
        self.vector[self.process_id] += 1
        return copy.deepcopy(self.vector)

    def receive_event(self, received_vector: Dict[str, int]) -> Dict[str, int]:
        for pid in self.all_processes:
            self.vector[pid] = max(self.vector.get(pid, 0), received_vector.get(pid, 0))
        self.vector[self.process_id] += 1
        return copy.deepcopy(self.vector)

    @staticmethod
    def compare(v1: Dict[str, int], v2: Dict[str, int]) -> str:
        """
        Compares two vector snapshots:
        Returns:
          'EQUAL'       if v1 == v2
          'BEFORE'      if v1 < v2 (v1 causally preceded v2)
          'AFTER'       if v1 > v2 (v1 causally followed v2)
          'CONCURRENT'  if v1 || v2 (concurrent independent events)
        """
        all_keys = set(v1.keys()).union(set(v2.keys()))
        v1_less_or_equal = all(v1.get(k, 0) <= v2.get(k, 0) for k in all_keys)
        v2_less_or_equal = all(v2.get(k, 0) <= v1.get(k, 0) for k in all_keys)

        if v1_less_or_equal and v2_less_or_equal:
            return "EQUAL"
        elif v1_less_or_equal and not v2_less_or_equal:
            return "BEFORE"
        elif v2_less_or_equal and not v1_less_or_equal:
            return "AFTER"
        else:
            return "CONCURRENT"


# ============================================================================
# Section 3: Chandy-Lamport Distributed Snapshot Simulator
# ============================================================================

class Message:
    def __init__(self, sender: str, recipient: str, payload: Any, is_marker: bool = False):
        self.sender = sender
        self.recipient = recipient
        self.payload = payload
        self.is_marker = is_marker


class SnapshotProcess:
    def __init__(self, pid: str, initial_balance: int, all_pids: List[str]):
        self.pid = pid
        self.balance = initial_balance
        self.incoming_channels: Dict[str, List[Message]] = {
            sender: [] for sender in all_pids if sender != pid
        }
        self.outgoing_channels: List[str] = [p for p in all_pids if p != pid]
        
        # Snapshot state
        self.has_recorded_state = False
        self.saved_balance: Optional[int] = None
        self.channel_states: Dict[str, List[Any]] = {}
        self.channel_recording_active: Dict[str, bool] = {
            sender: False for sender in all_pids if sender != pid
        }

    def send_money(self, recipient_process: 'SnapshotProcess', amount: int) -> None:
        if self.balance < amount:
            raise ValueError("Insufficient balance")
        self.balance -= amount
        msg = Message(sender=self.pid, recipient=recipient_process.pid, payload=amount, is_marker=False)
        recipient_process.incoming_channels[self.pid].append(msg)

    def start_snapshot(self, network_processes: Dict[str, 'SnapshotProcess']) -> None:
        """Initiates the Chandy-Lamport snapshot from this process."""
        self.has_recorded_state = True
        self.saved_balance = self.balance
        # Start recording all incoming channels
        for sender in self.channel_recording_active:
            self.channel_recording_active[sender] = True
            self.channel_states[sender] = []
        
        # Broadcast MARKER along all outgoing channels
        for dest_pid in self.outgoing_channels:
            marker = Message(sender=self.pid, recipient=dest_pid, payload="MARKER", is_marker=True)
            network_processes[dest_pid].incoming_channels[self.pid].append(marker)

    def process_next_message(self, network_processes: Dict[str, 'SnapshotProcess']) -> Optional[str]:
        """Processes one pending message from any incoming channel."""
        for sender, channel in self.incoming_channels.items():
            if channel:
                msg = channel.pop(0)
                if msg.is_marker:
                    self._handle_marker(sender, network_processes)
                    return f"Processed MARKER from {sender}"
                else:
                    self._handle_data_message(sender, msg)
                    return f"Processed ${msg.payload} from {sender}"
        return None

    def _handle_marker(self, sender: str, network_processes: Dict[str, 'SnapshotProcess']) -> None:
        if not self.has_recorded_state:
            # First marker received: record local state
            self.has_recorded_state = True
            self.saved_balance = self.balance
            # Incoming channel from sender is marked as EMPTY
            self.channel_recording_active[sender] = False
            self.channel_states[sender] = []
            
            # Start recording all other incoming channels
            for other_sender in self.channel_recording_active:
                if other_sender != sender:
                    self.channel_recording_active[other_sender] = True
                    self.channel_states[other_sender] = []
            
            # Forward MARKER to all outgoing channels
            for dest_pid in self.outgoing_channels:
                marker = Message(sender=self.pid, recipient=dest_pid, payload="MARKER", is_marker=True)
                network_processes[dest_pid].incoming_channels[self.pid].append(marker)
        else:
            # Already recorded: stop recording this incoming channel
            self.channel_recording_active[sender] = False

    def _handle_data_message(self, sender: str, msg: Message) -> None:
        amount = msg.payload
        self.balance += amount
        if self.channel_recording_active.get(sender, False):
            self.channel_states[sender].append(amount)


# ============================================================================
# Section 4: Automated Verification Test Suite
# ============================================================================

def run_tests():
    print("=== Level 6 Chapter 1: Distributed Systems Models & Time Lab ===")

    # Test 1: Lamport Logical Clocks
    p1_lamport = LamportClock("P1")
    p2_lamport = LamportClock("P2")

    t1 = p1_lamport.tick()
    t2 = p1_lamport.send_event()
    assert t1 == 1 and t2 == 2
    
    # P2 receives message from P1 with clock=2
    t3 = p2_lamport.receive_event(received_clock=t2)
    assert t3 == 3  # max(0, 2) + 1 = 3
    assert t2 < t3  # Causality condition: a -> b implies L(a) < L(b)
    print("  [PASS] Lamport Logical Clock Order Condition Verified")

    # Test 2: Vector Clocks & Concurrency Detection
    pids = ["A", "B", "C"]
    vc_a = VectorClock("A", pids)
    vc_b = VectorClock("B", pids)
    vc_c = VectorClock("C", pids)

    # Event 1: A does local event
    snap_a1 = vc_a.tick()
    assert snap_a1 == {"A": 1, "B": 0, "C": 0}

    # Event 2: B does local event
    snap_b1 = vc_b.tick()
    assert snap_b1 == {"A": 0, "B": 1, "C": 0}

    # Concurrency test: A and B acted independently without communication
    assert VectorClock.compare(snap_a1, snap_b1) == "CONCURRENT"
    print("  [PASS] Vector Clock detected concurrent events (A || B)")

    # Event 3: A sends message to B
    msg_vector = vc_a.send_event()  # A:2, B:0, C:0
    snap_b2 = vc_b.receive_event(msg_vector)  # B updates: max(A:2, B:1) -> then B increments local
    assert snap_b2["A"] == 2 and snap_b2["B"] == 2

    # Causality test: msg_vector causally precedes snap_b2
    assert VectorClock.compare(msg_vector, snap_b2) == "BEFORE"
    assert VectorClock.compare(snap_b2, msg_vector) == "AFTER"
    print(f"  [PASS] Vector Clock Causality Proven: A_send {msg_vector} -> B_recv {snap_b2}")

    # Test 3: Chandy-Lamport Distributed Snapshot
    # 3 nodes: P1=$100, P2=$200, P3=$300. Total money invariant = $600.
    nodes = {
        "P1": SnapshotProcess("P1", 100, ["P1", "P2", "P3"]),
        "P2": SnapshotProcess("P2", 200, ["P1", "P2", "P3"]),
        "P3": SnapshotProcess("P3", 300, ["P1", "P2", "P3"])
    }

    # P1 transfers $30 to P2 (message is in-flight on channel P1->P2)
    nodes["P1"].send_money(nodes["P2"], 30)
    assert nodes["P1"].balance == 70
    assert nodes["P2"].balance == 200

    # P1 initiates snapshot while $30 is in-flight!
    nodes["P1"].start_snapshot(nodes)
    assert nodes["P1"].saved_balance == 70

    # Step simulation until all messages and markers are processed
    for _ in range(15):
        for pid in ["P1", "P2", "P3"]:
            nodes[pid].process_next_message(nodes)

    # Verify all nodes recorded state
    assert all(nodes[p].has_recorded_state for p in nodes)
    
    # Check total money in snapshot: Saved Balances + In-Flight Channel States
    sum_saved_balances = sum(nodes[p].saved_balance for p in nodes)
    
    # In-flight money captured in channels
    in_flight_captured = 0
    for p in nodes:
        for ch_sender, msgs in nodes[p].channel_states.items():
            in_flight_captured += sum(msgs)

    total_captured_money = sum_saved_balances + in_flight_captured
    assert total_captured_money == 600, f"Snapshot violated money conservation! Expected 600, got {total_captured_money}"
    print(f"  [PASS] Chandy-Lamport Snapshot Preserved Money Conservation: "
          f"Node Balances ({sum_saved_balances}) + In-Flight ({in_flight_captured}) = ${total_captured_money}")

    print("ALL TESTS PASSED: Level 6 Chapter 1 Distributed Time & Snapshots Engine verified successfully.")


if __name__ == "__main__":
    run_tests()
