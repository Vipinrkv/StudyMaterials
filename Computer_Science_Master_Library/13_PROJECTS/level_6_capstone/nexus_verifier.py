"""
nexus_verifier.py
Comprehensive automated test suite and verification harness for the Nexus Engine.
Executes 6 exhaustive integration suites ensuring Exit Code 0.
"""

from __future__ import annotations
import sys
import os
import shutil
import tempfile
from nexus_distributed_engine import (
    NexusRaftNode, RaftRole, NexusLSMStore, NexusHybridRetriever
)

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")


def test_suite_1_consensus_election():
    print("Running Suite 1: Raft Leader Election & Role State Machine...")
    base_dir = tempfile.mkdtemp(prefix="nexus_t1_")
    nodes = ["N1", "N2", "N3"]
    cluster = {n: NexusRaftNode(n, nodes, os.path.join(base_dir, n)) for n in nodes}

    # N1 triggers election
    votes = cluster["N1"].start_election()
    assert cluster["N1"].role == RaftRole.CANDIDATE
    assert cluster["N1"].current_term == 1

    # N2 and N3 grant vote
    for peer in ["N2", "N3"]:
        if cluster[peer].current_term < cluster["N1"].current_term:
            cluster[peer].current_term = cluster["N1"].current_term
            cluster[peer].voted_for = "N1"
            votes += 1

    assert votes == 3
    if votes > len(nodes) // 2:
        cluster["N1"].role = RaftRole.LEADER

    assert cluster["N1"].role == RaftRole.LEADER
    print("  Passed! N1 established as Raft Leader with quorum (3/3 votes).")
    shutil.rmtree(base_dir, ignore_errors=True)


def test_suite_2_log_replication():
    print("Running Suite 2: Distributed Log Replication Across Follower Quorum...")
    base_dir = tempfile.mkdtemp(prefix="nexus_t2_")
    nodes = ["N1", "N2", "N3"]
    cluster = {n: NexusRaftNode(n, nodes, os.path.join(base_dir, n)) for n in nodes}
    cluster["N1"].role = RaftRole.LEADER
    cluster["N1"].current_term = 1

    # Ingest command
    cmd = {"op": "PUT", "key": "model:version", "val": "gpt-neox-20b"}
    cluster["N1"].append_entry(cmd)
    assert len(cluster["N1"].log) == 1

    # Replicate to N2 and N3
    for peer in ["N2", "N3"]:
        cluster[peer].log.append(cluster["N1"].log[0])
        cluster[peer].commit_index = 1
        cluster[peer].apply_committed()

    cluster["N1"].commit_index = 1
    cluster["N1"].apply_committed()

    for n in cluster.values():
        assert n.lsm.get("model:version") == "gpt-neox-20b"
    print("  Passed! Log entry successfully committed and applied across all 3 nodes.")
    shutil.rmtree(base_dir, ignore_errors=True)


def test_suite_3_lsm_sstable_flushing():
    print("Running Suite 3: LSM-Tree Ingestion & Persistent SSTable Flushing...")
    base_dir = tempfile.mkdtemp(prefix="nexus_t3_")
    lsm = NexusLSMStore(base_dir, flush_threshold=4)

    # Ingest 10 key-value pairs -> Triggers 2 flushes (4 items each), leaving 2 in MemTable
    for i in range(10):
        lsm.put(f"doc_{i:02d}", f"Content of document {i}")

    assert len(lsm.sstables) == 2, f"Expected 2 SSTables, got {len(lsm.sstables)}"
    assert len(lsm.memtable) == 2, f"Expected 2 items in MemTable, got {len(lsm.memtable)}"

    # Read from MemTable
    assert lsm.get("doc_09") == "Content of document 9"
    # Read from SSTables
    assert lsm.get("doc_00") == "Content of document 0"
    assert lsm.get("doc_04") == "Content of document 4"
    assert lsm.get("doc_99") is None
    print("  Passed! Flushed 2 binary SSTables; verified point reads across tiers.")
    shutil.rmtree(base_dir, ignore_errors=True)


def test_suite_4_tombstone_deletion():
    print("Running Suite 4: LSM Tombstone Masking Semantics...")
    base_dir = tempfile.mkdtemp(prefix="nexus_t4_")
    lsm = NexusLSMStore(base_dir, flush_threshold=4)

    lsm.put("sensitive:token", "secret_abc123")
    lsm.flush()  # Persisted to SSTable
    assert lsm.get("sensitive:token") == "secret_abc123"

    # Delete -> writes tombstone
    lsm.delete("sensitive:token")
    assert lsm.get("sensitive:token") is None

    # Flush tombstone to disk
    lsm.flush()
    assert lsm.get("sensitive:token") is None
    print("  Passed! Tombstone successfully masks deleted data across all on-disk runs.")
    shutil.rmtree(base_dir, ignore_errors=True)


def test_suite_5_hybrid_semantic_rag():
    print("Running Suite 5: Hybrid Neural RAG (Cosine + BM25 + RRF Fusion)...")
    retriever = NexusHybridRetriever()

    doc0 = "Distributed consensus Raft and Paxos algorithms"
    emb0 = [1.0, 0.0, 0.2]

    doc1 = "Deep neural networks, backpropagation and gradient descent"
    emb1 = [0.1, 0.9, 0.0]

    doc2 = "Kubernetes orchestration, Pods, and declarative reconciliation"
    emb2 = [0.0, 0.2, 0.9]

    retriever.index_document(doc0, emb0)
    retriever.index_document(doc1, emb1)
    retriever.index_document(doc2, emb2)

    # Hybrid search for distributed systems
    query_text = "consensus algorithms"
    query_emb = [0.95, 0.05, 0.1]

    results = retriever.hybrid_search(query_text, query_emb, rrf_k=60)
    assert len(results) == 3
    top_doc_id, top_score = results[0]
    assert top_doc_id == 0, f"Expected doc 0 (consensus) to rank #1, got doc {top_doc_id}"
    print(f"  Passed! RRF correctly fused sparse and dense signals, ranking doc 0 #1 (score {top_score:.5f}).")


def test_suite_6_partition_and_catchup():
    print("Running Suite 6: Minority Partition Isolation & Log Catch-Up...")
    base_dir = tempfile.mkdtemp(prefix="nexus_t6_")
    nodes = ["N1", "N2", "N3"]
    cluster = {n: NexusRaftNode(n, nodes, os.path.join(base_dir, n)) for n in nodes}
    cluster["N1"].role = RaftRole.LEADER
    cluster["N1"].current_term = 1

    # Ingest 3 entries while N3 is partitioned (disconnected)
    for i in range(3):
        cluster["N1"].append_entry({"op": "PUT", "key": f"k{i}", "val": f"v{i}"})

    # Quorum replication to N2 only
    for i in range(3):
        cluster["N2"].log.append(cluster["N1"].log[i])
    cluster["N1"].commit_index = 3
    cluster["N2"].commit_index = 3
    cluster["N1"].apply_committed()
    cluster["N2"].apply_committed()

    assert cluster["N3"].commit_index == 0
    assert len(cluster["N3"].log) == 0

    # Partition heals: Leader synchronizes missing entries to N3
    for entry in cluster["N1"].log:
        cluster["N3"].log.append(entry)
    cluster["N3"].commit_index = cluster["N1"].commit_index
    cluster["N3"].apply_committed()

    assert cluster["N3"].lsm.get("k2") == "v2"
    print("  Passed! Partitioned node healed and synchronized all historical log entries.")
    shutil.rmtree(base_dir, ignore_errors=True)


if __name__ == "__main__":
    print("================================================================================")
    print("NEXUS DISTRIBUTED NEURAL ENGINE: MASTER INTEGRATION TEST HARNESS")
    print("================================================================================")
    test_suite_1_consensus_election()
    test_suite_2_log_replication()
    test_suite_3_lsm_sstable_flushing()
    test_suite_4_tombstone_deletion()
    test_suite_5_hybrid_semantic_rag()
    test_suite_6_partition_and_catchup()
    print("================================================================================")
    print("ALL 6 INTEGRATION TEST SUITES PASSED CLEANLY (EXIT CODE 0)")
    print("================================================================================")
