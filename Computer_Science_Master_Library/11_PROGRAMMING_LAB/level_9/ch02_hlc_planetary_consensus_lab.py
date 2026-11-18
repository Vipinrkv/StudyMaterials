"""
Level 9 Programming Lab - Chapter 02: Planetary Consensus, TrueTime & HLC
Implements TrueTime Commit-Wait, Hybrid Logical Clocks, and Percolator Snapshot Isolation.
"""
import sys
import time
from typing import Tuple, Dict, Optional, Any

sys.stdout.reconfigure(encoding="utf-8")

# -------------------------------------------------------------------------
# 1. TrueTime Simulator
# -------------------------------------------------------------------------
class TrueTimeOracle:
    def __init__(self, epsilon_ms: float = 5.0):
        self.epsilon_ms = epsilon_ms
        self.base_time = time.time() * 1000.0

    def now(self) -> Tuple[float, float]:
        # Returns [earliest, latest]
        current = time.time() * 1000.0
        return (current - self.epsilon_ms, current + self.epsilon_ms)

    def commit_wait(self, commit_ts: float) -> None:
        while True:
            earliest, _ = self.now()
            if earliest > commit_ts:
                break
            time.sleep(0.001)

# -------------------------------------------------------------------------
# 2. Hybrid Logical Clock (HLC)
# -------------------------------------------------------------------------
class HlcTimestamp:
    def __init__(self, l: int, c: int):
        self.l = l  # physical time component
        self.c = c  # logical counter

    def __lt__(self, other: 'HlcTimestamp') -> bool:
        if self.l != other.l:
            return self.l < other.l
        return self.c < other.c

    def __eq__(self, other: 'HlcTimestamp') -> bool:
        return self.l == other.l and self.c == other.c

    def __repr__(self) -> str:
        return f"({self.l}, {self.c})"

class HybridLogicalClock:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.l: int = 0
        self.c: int = 0

    def tick(self, pt: int) -> HlcTimestamp:
        # Local event
        l_old = self.l
        self.l = max(l_old, pt)
        if self.l == l_old:
            self.c += 1
        else:
            self.c = 0
        return HlcTimestamp(self.l, self.c)

    def update(self, remote_ts: HlcTimestamp, pt: int) -> HlcTimestamp:
        # Message received
        l_old = self.l
        self.l = max(l_old, remote_ts.l, pt)
        if self.l == l_old and self.l == remote_ts.l:
            self.c = max(self.c, remote_ts.c) + 1
        elif self.l == l_old:
            self.c += 1
        elif self.l == remote_ts.l:
            self.c = remote_ts.c + 1
        else:
            self.c = 0
        return HlcTimestamp(self.l, self.c)

# -------------------------------------------------------------------------
# 3. Percolator Transaction Engine
# -------------------------------------------------------------------------
class PercolatorConflictError(Exception):
    pass

class PercolatorStorage:
    def __init__(self):
        # key -> {ts: val}
        self.data: Dict[str, Dict[int, Any]] = {}
        # key -> {ts: primary_key_ref}
        self.lock: Dict[str, Dict[int, str]] = {}
        # key -> {commit_ts: start_ts}
        self.write: Dict[str, Dict[int, int]] = {}

    def read(self, key: str, read_ts: int) -> Optional[Any]:
        # Check for active locks at or before read_ts
        if key in self.lock:
            for l_ts in self.lock[key]:
                if l_ts <= read_ts:
                    raise PercolatorConflictError(f"Read conflict: Key '{key}' locked at ts {l_ts}")

        # Find latest write record with commit_ts <= read_ts
        if key not in self.write:
            return None
        valid_commits = [cts for cts in self.write[key] if cts <= read_ts]
        if not valid_commits:
            return None
        latest_commit = max(valid_commits)
        start_ts = self.write[key][latest_commit]
        return self.data[key].get(start_ts, None)

    def prewrite(self, key: str, value: Any, start_ts: int, primary_key: str) -> None:
        # Check if already locked
        if key in self.lock and len(self.lock[key]) > 0:
            raise PercolatorConflictError(f"Write conflict: Key '{key}' already locked.")
        # Check for write-after-start_ts conflicts
        if key in self.write:
            for cts in self.write[key]:
                if cts >= start_ts:
                    raise PercolatorConflictError(f"Write conflict: Key '{key}' committed at {cts} >= start_ts {start_ts}")

        if key not in self.data:
            self.data[key] = {}
        self.data[key][start_ts] = value

        if key not in self.lock:
            self.lock[key] = {}
        self.lock[key][start_ts] = primary_key

    def commit(self, key: str, start_ts: int, commit_ts: int) -> None:
        if key not in self.lock or start_ts not in self.lock[key]:
            raise PercolatorConflictError(f"Commit failed: Lock missing on '{key}' for start_ts {start_ts}")
        del self.lock[key][start_ts]
        if key not in self.write:
            self.write[key] = {}
        self.write[key][commit_ts] = start_ts


def test_planetary_consensus():
    print("===========================================================================")
    print("PLANETARY CONSENSUS, TRUETIME & HLC VERIFICATION TESTBED")
    print("LEVEL 9 LAB - CHAPTER 02")
    print("===========================================================================")

    # 1. TrueTime Commit-Wait Test
    print("[Test 1/3] TrueTime Uncertainty Bounds & Commit-Wait...")
    tt = TrueTimeOracle(epsilon_ms=3.0)
    e1, l1 = tt.now()
    assert l1 - e1 == 6.0, f"Uncertainty interval must equal 2*epsilon (6.0), got {l1 - e1}"
    commit_ts = l1
    t_start = time.time()
    tt.commit_wait(commit_ts)
    t_waited = (time.time() - t_start) * 1000.0
    print(f"  -> Commit-Wait enforced: waited {t_waited:.2f} ms until earliest > {commit_ts:.2f}")
    assert t_waited >= 2.5, "Commit wait duration must be at least ~2*epsilon"

    # 2. Hybrid Logical Clock Causality Test
    print("[Test 2/3] Hybrid Logical Clock (HLC) Causal Order...")
    node_a = HybridLogicalClock("Node-A")
    node_b = HybridLogicalClock("Node-B")

    ts1 = node_a.tick(pt=100)
    assert ts1.l == 100 and ts1.c == 0

    # Local tick without physical advance increments logical counter
    ts2 = node_a.tick(pt=100)
    assert ts2.l == 100 and ts2.c == 1
    assert ts1 < ts2

    # Send message from A to B where B physical clock lags behind (pt=90)
    ts3 = node_b.update(ts2, pt=90)
    assert ts3.l == 100 and ts3.c == 2, f"HLC should adopt max physical time 100 and increment counter, got {ts3}"
    assert ts2 < ts3
    print(f"  -> Causality strictly preserved: {ts1} < {ts2} < {ts3} across lagging clock node.")

    # 3. Percolator Snapshot Isolation Multi-Row Transaction Test
    print("[Test 3/3] Percolator 2-Phase Distributed Transaction...")
    storage = PercolatorStorage()

    # Initial balance setup
    storage.data["acc_alice"] = {10: 1000}
    storage.write["acc_alice"] = {15: 10}
    storage.data["acc_bob"] = {10: 500}
    storage.write["acc_bob"] = {15: 10}

    # Verify initial read at ts=20
    assert storage.read("acc_alice", read_ts=20) == 1000
    assert storage.read("acc_bob", read_ts=20) == 500

    # Execute transfer $200 from Alice to Bob at start_ts=25
    storage.prewrite("acc_alice", 800, start_ts=25, primary_key="acc_alice")
    storage.prewrite("acc_bob", 700, start_ts=25, primary_key="acc_alice")

    # Concurrent reader at read_ts=26 should encounter lock conflict
    try:
        storage.read("acc_alice", read_ts=26)
        assert False, "Should raise lock conflict"
    except PercolatorConflictError as e:
        print(f"  -> Successfully caught uncommitted lock conflict: {e}")

    # Prior snapshot reader at read_ts=24 sees old data without conflict
    # (assuming lock is at ts=25 > 24)
    assert storage.read("acc_alice", read_ts=24) == 1000

    # Commit phase at commit_ts=30
    storage.commit("acc_alice", start_ts=25, commit_ts=30)
    storage.commit("acc_bob", start_ts=25, commit_ts=30)

    # Post-commit read at read_ts=35 sees updated atomic balances
    assert storage.read("acc_alice", read_ts=35) == 800
    assert storage.read("acc_bob", read_ts=35) == 700
    print("  -> Atomic multi-row 2PC transfer committed and verified under Snapshot Isolation.")

    print("===========================================================================")
    print("ALL 3 PLANETARY CONSENSUS & CLOCK TESTS PASSED (Exit Code 0).")
    print("===========================================================================")

if __name__ == "__main__":
    test_planetary_consensus()
