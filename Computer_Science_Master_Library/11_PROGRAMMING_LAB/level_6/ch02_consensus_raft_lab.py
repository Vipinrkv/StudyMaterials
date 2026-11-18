# -*- coding: utf-8 -*-
"""
CH02: Consensus, Replication, and Fault Tolerance Lab
====================================================
Covers:
1. Complete Raft Consensus State Machine (Follower, Candidate, Leader).
2. Quorum-based Leader Election with RequestVote RPC and safety invariants.
3. Log Replication via AppendEntries RPC, conflict truncation, and FSM commit application.
"""
import sys
import copy
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any

sys.stdout.reconfigure(encoding="utf-8")


# ============================================================================
# Section 1: Raft Core Data Types
# ============================================================================

class NodeRole(Enum):
    FOLLOWER = "FOLLOWER"
    CANDIDATE = "CANDIDATE"
    LEADER = "LEADER"


class LogEntry:
    def __init__(self, term: int, index: int, command: Tuple[str, str, Any]):
        self.term = term
        self.index = index
        self.command = command  # e.g. ("SET", "balance_alice", 100)

    def __repr__(self):
        return f"Entry(idx={self.index}, term={self.term}, cmd={self.command})"


class RequestVoteArgs:
    def __init__(self, term: int, candidate_id: str, last_log_index: int, last_log_term: int):
        self.term = term
        self.candidate_id = candidate_id
        self.last_log_index = last_log_index
        self.last_log_term = last_log_term


class RequestVoteReply:
    def __init__(self, term: int, vote_granted: bool):
        self.term = term
        self.vote_granted = vote_granted


class AppendEntriesArgs:
    def __init__(self, term: int, leader_id: str, prev_log_index: int, prev_log_term: int, entries: List[LogEntry], leader_commit: int):
        self.term = term
        self.leader_id = leader_id
        self.prev_log_index = prev_log_index
        self.prev_log_term = prev_log_term
        self.entries = entries
        self.leader_commit = leader_commit


class AppendEntriesReply:
    def __init__(self, term: int, success: bool, match_index: int):
        self.term = term
        self.success = success
        self.match_index = match_index


# ============================================================================
# Section 2: Raft Consensus Node
# ============================================================================

class RaftNode:
    """Implements Diego Ongaro's Raft consensus algorithm."""
    def __init__(self, node_id: str, peer_ids: List[str]):
        self.node_id = node_id
        self.peer_ids = peer_ids  # List of other node IDs in the cluster
        self.role = NodeRole.FOLLOWER
        
        # Persistent state on all servers
        self.current_term = 0
        self.voted_for: Optional[str] = None
        # Log is 1-indexed. Index 0 is a sentinel dummy entry
        self.log: List[LogEntry] = [LogEntry(term=0, index=0, command=("INIT", "", None))]
        
        # Volatile state on all servers
        self.commit_index = 0
        self.last_applied = 0
        
        # Volatile state on leaders
        self.next_index: Dict[str, int] = {}
        self.match_index: Dict[str, int] = {}
        
        # State Machine (Key-Value Store)
        self.state_machine: Dict[str, Any] = {}

    @property
    def last_log_index(self) -> int:
        return self.log[-1].index

    @property
    def last_log_term(self) -> int:
        return self.log[-1].term

    @property
    def cluster_size(self) -> int:
        return len(self.peer_ids) + 1

    @property
    def majority(self) -> int:
        return (self.cluster_size // 2) + 1

    # -------------------------------------------------------------------------
    # Election Management
    # -------------------------------------------------------------------------
    def start_election(self) -> RequestVoteArgs:
        """Transitions to CANDIDATE, increments term, votes for self."""
        self.role = NodeRole.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        
        return RequestVoteArgs(
            term=self.current_term,
            candidate_id=self.node_id,
            last_log_index=self.last_log_index,
            last_log_term=self.last_log_term
        )

    def handle_request_vote(self, args: RequestVoteArgs) -> RequestVoteReply:
        """Evaluates incoming RequestVote according to Raft Section 5.2 & 5.4.1."""
        # 1. Reply false if term < current_term
        if args.term < self.current_term:
            return RequestVoteReply(term=self.current_term, vote_granted=False)
            
        # If term > current_term, update term and convert to follower
        if args.term > self.current_term:
            self.current_term = args.term
            self.role = NodeRole.FOLLOWER
            self.voted_for = None

        # 2. Check if voted_for is null or candidate_id
        can_vote = (self.voted_for is None or self.voted_for == args.candidate_id)
        
        # 3. Check if candidate's log is at least as up-to-date as receiver's log
        log_ok = (args.last_log_term > self.last_log_term) or (
            args.last_log_term == self.last_log_term and args.last_log_index >= self.last_log_index
        )

        if can_vote and log_ok:
            self.voted_for = args.candidate_id
            return RequestVoteReply(term=self.current_term, vote_granted=True)
            
        return RequestVoteReply(term=self.current_term, vote_granted=False)

    def become_leader(self) -> None:
        """Transitions candidate to leader upon receiving majority votes."""
        self.role = NodeRole.LEADER
        for peer in self.peer_ids:
            self.next_index[peer] = self.last_log_index + 1
            self.match_index[peer] = 0

    # -------------------------------------------------------------------------
    # Log Replication Management
    # -------------------------------------------------------------------------
    def client_propose(self, command: Tuple[str, str, Any]) -> int:
        """Leader appends entry to its local log and returns entry index."""
        if self.role != NodeRole.LEADER:
            raise RuntimeError(f"Node {self.node_id} is not leader")
        
        new_index = self.last_log_index + 1
        entry = LogEntry(term=self.current_term, index=new_index, command=command)
        self.log.append(entry)
        return new_index

    def create_append_entries_args(self, peer_id: str) -> AppendEntriesArgs:
        """Constructs AppendEntries payload for a given follower."""
        prev_idx = self.next_index[peer_id] - 1
        prev_term = self.log[prev_idx].term
        entries_to_send = self.log[prev_idx + 1:]
        
        return AppendEntriesArgs(
            term=self.current_term,
            leader_id=self.node_id,
            prev_log_index=prev_idx,
            prev_log_term=prev_term,
            entries=copy.deepcopy(entries_to_send),
            leader_commit=self.commit_index
        )

    def handle_append_entries(self, args: AppendEntriesArgs) -> AppendEntriesReply:
        """Follower processes AppendEntries RPC (Raft Section 5.3)."""
        # 1. Reply false if term < current_term
        if args.term < self.current_term:
            return AppendEntriesReply(term=self.current_term, success=False, match_index=0)

        # Recognize valid leader
        if args.term > self.current_term or self.role == NodeRole.CANDIDATE:
            self.current_term = args.term
            self.role = NodeRole.FOLLOWER
            self.voted_for = None

        # 2. Reply false if log doesn't contain an entry at prev_log_index matching prev_log_term
        if args.prev_log_index >= len(self.log):
            return AppendEntriesReply(term=self.current_term, success=False, match_index=self.last_log_index)
        if self.log[args.prev_log_index].term != args.prev_log_term:
            return AppendEntriesReply(term=self.current_term, success=False, match_index=self.last_log_index)

        # 3. If an existing entry conflicts with a new one, delete existing entry and all that follow it
        insert_idx = args.prev_log_index + 1
        for entry in args.entries:
            if insert_idx < len(self.log):
                if self.log[insert_idx].term != entry.term or self.log[insert_idx].command != entry.command:
                    # Truncate conflict
                    self.log = self.log[:insert_idx]
                    self.log.append(entry)
            else:
                self.log.append(entry)
            insert_idx += 1

        # 4. If leader_commit > commit_index, set commit_index = min(leader_commit, last_log_index)
        if args.leader_commit > self.commit_index:
            self.commit_index = min(args.leader_commit, self.last_log_index)
            self._apply_entries_to_state_machine()

        return AppendEntriesReply(term=self.current_term, success=True, match_index=self.last_log_index)

    def process_append_entries_reply(self, peer_id: str, reply: AppendEntriesReply) -> None:
        """Leader processes response from follower."""
        if self.role != NodeRole.LEADER:
            return
            
        if reply.term > self.current_term:
            self.current_term = reply.term
            self.role = NodeRole.FOLLOWER
            self.voted_for = None
            return

        if reply.success:
            self.next_index[peer_id] = reply.match_index + 1
            self.match_index[peer_id] = reply.match_index
            self._check_and_advance_commit_index()
        else:
            # Back up next_index on follower
            if self.next_index[peer_id] > 1:
                self.next_index[peer_id] -= 1

    def _check_and_advance_commit_index(self) -> None:
        """Advances leader commitIndex if a log entry from current term is replicated on majority."""
        for N in range(self.last_log_index, self.commit_index, -1):
            if self.log[N].term == self.current_term:
                # Count match_index >= N across cluster (including leader itself)
                matches = 1  # Leader itself
                for peer in self.peer_ids:
                    if self.match_index.get(peer, 0) >= N:
                        matches += 1
                if matches >= self.majority:
                    self.commit_index = N
                    self._apply_entries_to_state_machine()
                    break

    def _apply_entries_to_state_machine(self) -> None:
        """Applies committed entries from last_applied + 1 to commit_index."""
        while self.last_applied < self.commit_index:
            self.last_applied += 1
            entry = self.log[self.last_applied]
            op, key, val = entry.command
            if op == "SET":
                self.state_machine[key] = val


# ============================================================================
# Section 3: Automated Verification Test Suite
# ============================================================================

def run_tests():
    print("=== Level 6 Chapter 2: Consensus & Raft Lab ===")

    # Test 1: Quorum & Leader Election in 3-Node Cluster
    nodes = {
        "N1": RaftNode("N1", ["N2", "N3"]),
        "N2": RaftNode("N2", ["N1", "N3"]),
        "N3": RaftNode("N3", ["N1", "N2"])
    }
    
    assert nodes["N1"].majority == 2
    
    # N1 times out and triggers election
    vote_args = nodes["N1"].start_election()
    assert nodes["N1"].current_term == 1
    assert nodes["N1"].role == NodeRole.CANDIDATE
    
    # Send RequestVote to N2 and N3
    r2 = nodes["N2"].handle_request_vote(vote_args)
    r3 = nodes["N3"].handle_request_vote(vote_args)
    assert r2.vote_granted is True
    assert r3.vote_granted is True

    # N1 receives 3 votes (including self) >= majority (2) -> Becomes Leader
    nodes["N1"].become_leader()
    assert nodes["N1"].role == NodeRole.LEADER
    print("  [PASS] Raft Leader Election Succeeded (N1 elected Leader with Quorum 3/3)")

    # Test 2: Client Command Proposal & Log Replication
    idx1 = nodes["N1"].client_propose(("SET", "balance_alice", 100))
    idx2 = nodes["N1"].client_propose(("SET", "balance_bob", 250))
    assert idx1 == 1 and idx2 == 2
    assert nodes["N1"].commit_index == 0  # Not yet committed

    # Leader replicates to N2 and N3 via AppendEntries
    for peer in ["N2", "N3"]:
        args = nodes["N1"].create_append_entries_args(peer)
        reply = nodes[peer].handle_append_entries(args)
        assert reply.success is True
        nodes["N1"].process_append_entries_reply(peer, reply)

    # Both entries are now committed on majority!
    assert nodes["N1"].commit_index == 2
    assert nodes["N1"].state_machine["balance_alice"] == 100
    assert nodes["N1"].state_machine["balance_bob"] == 250

    # Heartbeat to let followers know of new commit_index
    for peer in ["N2", "N3"]:
        hb_args = nodes["N1"].create_append_entries_args(peer)
        nodes[peer].handle_append_entries(hb_args)
        assert nodes[peer].commit_index == 2
        assert nodes[peer].state_machine["balance_alice"] == 100
        assert nodes[peer].state_machine["balance_bob"] == 250
    print("  [PASS] Raft Log Replication & State Machine Application Committed across Cluster")

    # Test 3: Log Conflict Truncation (Safety Invariant)
    # Simulate N3 being disconnected and receiving a rogue conflicting entry at index 2
    rogue_entry = LogEntry(term=1, index=2, command=("SET", "balance_bob", 999999))
    nodes["N3"].log[2] = rogue_entry
    assert nodes["N3"].log[2].command == ("SET", "balance_bob", 999999)

    # Leader syncs to N3: rewind next_index so leader sends index 2
    nodes["N1"].next_index["N3"] = 2
    sync_args = nodes["N1"].create_append_entries_args("N3")
    sync_reply = nodes["N3"].handle_append_entries(sync_args)
    assert sync_reply.success is True
    assert nodes["N3"].log[2].command == ("SET", "balance_bob", 250)
    print("  [PASS] Raft Log Conflict Truncation Verified: Rogue entry overwritten with canonical log")

    print("ALL TESTS PASSED: Level 6 Chapter 2 Raft Consensus Engine verified successfully.")


if __name__ == "__main__":
    run_tests()
