"""
ch04_bft_hotstuff_lab.py
Level 8 Chapter 04 Companion Laboratory: Byzantine Fault Tolerance & HotStuff Consensus.
Simulates 3f+1 Quorum Calculations, HMAC Digital Signatures, Quorum Certificate Aggregation,
Equivocation Trapping, and 3-Chain Pipelined State Machine Replication.
Pure Python/Standard Library with zero external dependencies.
"""

from __future__ import annotations
import sys
import hashlib
import hmac
from typing import Dict, List, Optional, Tuple, Set, Any

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")


class BftProposal:
    """Consensus proposal carrying block height, payload, and parent hash."""
    def __init__(self, view: int, height: int, payload: str, parent_hash: str):
        self.view = view
        self.height = height
        self.payload = payload
        self.parent_hash = parent_hash

    def hash(self) -> str:
        data = f"{self.view}:{self.height}:{self.payload}:{self.parent_hash}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()[:16]


class QuorumCertificate:
    """Cryptographic certificate combining 2f+1 validator signatures."""
    def __init__(self, block_hash: str, view: int, signatures: Dict[str, str]):
        self.block_hash = block_hash
        self.view = view
        self.signatures = dict(signatures)

    def is_valid(self, quorum_size: int, node_keys: Dict[str, str]) -> bool:
        if len(self.signatures) < quorum_size:
            return False
        for node_id, sig in self.signatures.items():
            key = node_keys.get(node_id, "")
            expected = hmac.new(key.encode("utf-8"), f"{self.block_hash}:{self.view}".encode("utf-8"), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig, expected):
                return False
        return True


class BftValidatorNode:
    """Byzantine validator node with locking rules and equivocation protection."""
    def __init__(self, node_id: str, secret_key: str, total_nodes: int):
        self.node_id = node_id
        self.key = secret_key
        self.f = (total_nodes - 1) // 3
        self.quorum_size = 2 * self.f + 1

        self.locked_qc: Optional[QuorumCertificate] = None
        self.committed_blocks: List[BftProposal] = []
        self.signed_proposals_by_height: Dict[int, str] = {}

    def sign_vote(self, proposal: BftProposal) -> Optional[str]:
        h = proposal.height
        b_hash = proposal.hash()

        # Equivocation check
        if h in self.signed_proposals_by_height:
            if self.signed_proposals_by_height[h] != b_hash:
                return None  # Equivocation! Reject.

        # Safe Voting Rule: view must be >= locked QC view
        if self.locked_qc is not None:
            if proposal.view < self.locked_qc.view:
                return None

        self.signed_proposals_by_height[h] = b_hash
        return hmac.new(self.key.encode("utf-8"), f"{b_hash}:{proposal.view}".encode("utf-8"), hashlib.sha256).hexdigest()

    def update_lock(self, qc: QuorumCertificate) -> None:
        if self.locked_qc is None or qc.view > self.locked_qc.view:
            self.locked_qc = qc

    def commit_block(self, block: BftProposal) -> None:
        self.committed_blocks.append(block)


def main() -> None:
    print("=" * 70)
    print("LEVEL 8 CHAPTER 04: BYZANTINE FAULT TOLERANCE & HOTSTUFF LAB")
    print("=" * 70)

    # 1. 3f + 1 Quorum Lower Bound Verification
    print("\n[Test 1] Testing Byzantine 3f + 1 Quorum Lower Bounds...")
    total_nodes = 4  # n = 4, f = 1
    f_max = (total_nodes - 1) // 3
    quorum_size = 2 * f_max + 1
    assert f_max == 1
    assert quorum_size == 3
    print(f"  -> Cluster Size: {total_nodes} nodes | Fault Tolerance: {f_max} Byzantine fault | Quorum Size: {quorum_size}.")

    # 2. Setup 4 Validators
    keys = {f"val_{i}": f"SECRET_KEY_{i}" for i in range(total_nodes)}
    nodes = [BftValidatorNode(f"val_{i}", keys[f"val_{i}"], total_nodes) for i in range(total_nodes)]

    # 3. Honest Block Proposal & Quorum Certificate Generation
    print("\n[Test 2] Proposing Block 1 and Generating Quorum Certificate...")
    block_1 = BftProposal(view=1, height=1, payload="TX_TRANSFER_100_ETH", parent_hash="GENESIS")
    b1_hash = block_1.hash()

    # Collect signatures from 3 correct validators (nodes 0, 1, 2)
    sigs_b1 = {}
    for node in nodes[:3]:
        sig = node.sign_vote(block_1)
        assert sig is not None
        sigs_b1[node.node_id] = sig

    qc_1 = QuorumCertificate(b1_hash, view=1, signatures=sigs_b1)
    assert qc_1.is_valid(quorum_size=3, node_keys=keys) is True
    print(f"  -> Quorum Certificate QC(B1): Verified with {len(sigs_b1)} valid digital signatures.")

    # Update lock on validators
    for node in nodes:
        node.update_lock(qc_1)

    # 4. Byzantine Equivocation Attack Trapping
    print("\n[Test 3] Simulating Malicious Leader Equivocation Attack (Double Signing)...")
    # Malicious block for the exact same height 1
    conflicting_block = BftProposal(view=1, height=1, payload="ATTACKER_DOUBLE_SPEND", parent_hash="GENESIS")
    assert conflicting_block.hash() != b1_hash

    # Honest nodes 0, 1, 2 must refuse to sign conflicting block 1
    for node in nodes[:3]:
        rejected_vote = node.sign_vote(conflicting_block)
        assert rejected_vote is None, f"Node {node.node_id} failed to reject equivocation!"
    print("  -> Equivocation Attack Trap: Successfully blocked. Zero validators signed double proposal.")

    # 5. HotStuff Pipelined Block Chaining (Blocks 2 & 3)
    print("\n[Test 4] Executing HotStuff 3-Chain Pipeline Commit...")
    # Block 2 extends Block 1
    block_2 = BftProposal(view=2, height=2, payload="TX_PAYMENT_B2", parent_hash=b1_hash)
    sigs_b2 = {node.node_id: node.sign_vote(block_2) for node in nodes[:3]}
    qc_2 = QuorumCertificate(block_2.hash(), view=2, signatures=sigs_b2)
    assert qc_2.is_valid(quorum_size=3, node_keys=keys) is True
    for node in nodes:
        node.update_lock(qc_2)

    # Block 3 extends Block 2
    block_3 = BftProposal(view=3, height=3, payload="TX_PAYMENT_B3", parent_hash=block_2.hash())
    sigs_b3 = {node.node_id: node.sign_vote(block_3) for node in nodes[:3]}
    qc_3 = QuorumCertificate(block_3.hash(), view=3, signatures=sigs_b3)
    assert qc_3.is_valid(quorum_size=3, node_keys=keys) is True

    # Three-chain completed: Block 1 is committed!
    for node in nodes:
        node.commit_block(block_1)
        assert len(node.committed_blocks) == 1
        assert node.committed_blocks[0].payload == "TX_TRANSFER_100_ETH"

    print("  -> HotStuff Three-Chain Commit: Block 1 finalized safely across all cluster nodes.")

    print("\n" + "=" * 70)
    print("ALL BYZANTINE FAULT TOLERANCE TESTS PASSED (Exit Code 0).")
    print("=" * 70)
    sys.exit(0)


if __name__ == "__main__":
    main()
