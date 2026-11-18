# LEVEL 6 CAPSTONE PROJECT: NEXUS DISTRIBUTED NEURAL KNOWLEDGE & CONSENSUS ENGINE

---

## 1. EXECUTIVE SUMMARY & ARCHITECTURAL SPECIFICATION

Modern enterprise distributed platforms demand the simultaneous convergence of three complex disciplines:
1. **Distributed Consensus & Fault Tolerance:** Strongly consistent replicated transaction logs capable of surviving arbitrary node crashes and network partitions.
2. **High-Performance Persistent Storage:** Fast write ingestion and space-bounded storage powered by Log-Structured Merge-Trees (LSM-Trees) with Bloom filters.
3. **Neural Semantic Retrieval & Hybrid Search:** Real-time dense vector indexing (Cosine Similarity) coupled with sparse BM25 keyword scoring via Reciprocal Rank Fusion (RRF).

The **Nexus Engine** is an industrial-grade, single-binary distributed knowledge cluster. It synthesizes:
- A multi-node Raft consensus replication group (`RaftState`, `RequestVote`, `AppendEntries`).
- An on-disk LSM storage subsystem with append-only WAL, RAM MemTable, binary SSTables, and Bloom filters.
- A semantic knowledge store indexing multi-dimensional neural embeddings alongside document text.
- Cryptographic HMAC-SHA256 authenticated RPC routing.

```
+───────────────────────────────────────────────────────────────────────────────+
|                           NEXUS DISTRIBUTED CLUSTER                           |
|                                                                               |
|   +─────────────────────────+   +─────────────────────────+   +─────────────+ |
|   |       NexusNode 1       |   |       NexusNode 2       |   | NexusNode 3 | |
|   |       (LEADER)          |<─>|       (FOLLOWER)        |<─>| (FOLLOWER)  | |
|   +─────────────────────────+   +─────────────────────────+   +─────────────+ |
|        │                                                                      |
|        ▼ Replicated Raft Log (Term, Index, Command)                           |
|   +─────────────────────────────────────────────────────────────────────────+ |
|   |                        LSM Storage Engine Subsystem                     |
|   |  - Write-Ahead Log (WAL)                                                |
|   |  - MemTable (Sorted RAM Key-Value Buffer)                               |
|   |  - Persistent SSTables + Bloom Filters (10 bits/key, k=7)               |
|   +─────────────────────────────────────────────────────────────────────────+ |
|        │                                                                      |
|        ▼ Semantic Knowledge Base                                              |
|   +─────────────────────────────────────────────────────────────────────────+ |
|   |                        Hybrid Neural RAG Pipeline                       |
|   |  - Dense Cosine Similarity Embeddings                                   |
|   |  - Sparse BM25 Keyword Scoring                                          |
|   |  - Reciprocal Rank Fusion (RRF, k=60) Hybrid Retrieval                  |
|   +─────────────────────────────────────────────────────────────────────────+ |
+───────────────────────────────────────────────────────────────────────────────+
```

---

## 2. COMPONENT ARCHITECTURE & CONTRACTS

1. **`NexusRaftNode`:**
   - Manages state transitions (`FOLLOWER`, `CANDIDATE`, `LEADER`).
   - Handles election terms, votes, heartbeat timeouts, and log replication.
   - Enforces the Leader Completeness and State Machine Safety invariants.
2. **`NexusLSMStore`:**
   - Buffers incoming key-value mutations in RAM.
   - Flushes to persistent binary SSTables upon crossing configurable capacity thresholds.
   - Fast point lookups using mathematical Bloom filters to suppress disk scans.
3. **`NexusHybridRetriever`:**
   - Indexes documents with associated floating-point dense embedding vectors.
   - Executes dense Cosine distance rankings and sparse BM25 query evaluations.
   - Blends result sets into a single unified ranking using Reciprocal Rank Fusion.
4. **`NexusClusterCoordinator`:**
   - Coordinates cluster topology, node join/leave operations, and authenticated cryptographic RPC message routing.

---

## 3. VERIFICATION & VALIDATION PROTOCOL

The test verifier (`nexus_verifier.py`) conducts 6 comprehensive integration test suites:
1. **Cluster Consensus Election:** Leader election across 3 nodes with strict term increments.
2. **Replicated Storage Mutation:** Write ingestion replicated from leader to quorum of followers.
3. **LSM-Tree Flush & Persistence:** Multiple write bursts triggering SSTable creation with Bloom filter point lookups.
4. **Tombstone Deletion Integrity:** Value deletion correctly masking historical SSTables.
5. **Dense & Sparse Hybrid Semantic RAG:** Cosine similarity and BM25 ranking validated with RRF fusion.
6. **Network Partition & Healing:** Isolating a minority follower and proving seamless recovery and log catch-up upon rejoining.
