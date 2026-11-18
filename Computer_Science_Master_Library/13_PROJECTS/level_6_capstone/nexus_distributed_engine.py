"""
nexus_distributed_engine.py
Level 6 Capstone Project: Distributed Neural Knowledge & Consensus Cluster.
Synthesizes Raft Consensus, LSM Storage Engine with Bloom Filters, and Hybrid Semantic RAG.
Pure Python/Standard Library implementation with zero external dependencies.
"""

from __future__ import annotations
import sys
import os
import math
import copy
import struct
import bisect
import hashlib
import hmac
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")


class RaftRole(Enum):
    FOLLOWER = "FOLLOWER"
    CANDIDATE = "CANDIDATE"
    LEADER = "LEADER"


class NexusBloomFilter:
    """Mathematical Bloom filter with double-hashing."""
    def __init__(self, capacity: int, fp_rate: float = 0.01):
        self.capacity = max(capacity, 10)
        self.num_bits = max(64, int(- (self.capacity * math.log(fp_rate)) / (math.log(2) ** 2)))
        self.num_hashes = max(1, int((self.num_bits / self.capacity) * math.log(2)))
        self.bit_array = bytearray((self.num_bits + 7) // 8)

    def _hashes(self, key: str) -> List[int]:
        digest = hashlib.sha256(key.encode("utf-8")).digest()
        h1, h2 = struct.unpack(">QQ", digest[:16])
        return [(h1 + i * h2) % self.num_bits for i in range(self.num_hashes)]

    def add(self, key: str) -> None:
        for bit in self._hashes(key):
            self.bit_array[bit // 8] |= (1 << (bit % 8))

    def contains(self, key: str) -> bool:
        for bit in self._hashes(key):
            if not (self.bit_array[bit // 8] & (1 << (bit % 8))):
                return False
        return True


class NexusSSTable:
    """Immutable Sorted String Table."""
    TOMBSTONE = "__NEXUS_TOMBSTONE__"

    def __init__(self, path: str, items: List[Tuple[str, str]]):
        self.path = path
        self.sparse_index: List[Tuple[str, int]] = []
        self.bloom = NexusBloomFilter(len(items))
        self._write(items)

    def _write(self, items: List[Tuple[str, str]]) -> None:
        with open(self.path, "wb") as f:
            for i, (k, v) in enumerate(items):
                offset = f.tell()
                self.bloom.add(k)
                if i % 4 == 0:
                    self.sparse_index.append((k, offset))
                k_b = k.encode("utf-8")
                v_b = v.encode("utf-8")
                f.write(struct.pack(">II", len(k_b), len(v_b)) + k_b + v_b)

    def get(self, key: str) -> Optional[str]:
        if not self.bloom.contains(key):
            return None
        keys = [k for k, _ in self.sparse_index]
        idx = bisect.bisect_right(keys, key) - 1
        if idx < 0:
            return None

        start_off = self.sparse_index[idx][1]
        next_off = self.sparse_index[idx + 1][1] if idx + 1 < len(self.sparse_index) else None

        with open(self.path, "rb") as f:
            f.seek(start_off)
            while True:
                if next_off and f.tell() >= next_off:
                    break
                hdr = f.read(8)
                if not hdr or len(hdr) < 8:
                    break
                k_len, v_len = struct.unpack(">II", hdr)
                cur_k = f.read(k_len).decode("utf-8")
                cur_v = f.read(v_len).decode("utf-8")
                if cur_k == key:
                    return cur_v
                if cur_k > key:
                    break
        return None


class NexusLSMStore:
    """LSM storage engine with WAL, MemTable and SSTables."""
    def __init__(self, root_dir: str, flush_threshold: int = 5):
        self.root_dir = root_dir
        os.makedirs(root_dir, exist_ok=True)
        self.wal_path = os.path.join(root_dir, "nexus_wal.log")
        self.flush_threshold = flush_threshold
        self.memtable: Dict[str, str] = {}
        self.sstables: List[NexusSSTable] = []
        self._counter = 0

    def put(self, key: str, value: str) -> None:
        with open(self.wal_path, "a", encoding="utf-8") as f:
            f.write(f"{key}\t{value}\n")
        self.memtable[key] = value
        if len(self.memtable) >= self.flush_threshold:
            self.flush()

    def delete(self, key: str) -> None:
        self.put(key, NexusSSTable.TOMBSTONE)

    def flush(self) -> None:
        if not self.memtable:
            return
        sorted_items = sorted(self.memtable.items())
        path = os.path.join(self.root_dir, f"nexus_sst_{self._counter:03d}.db")
        self._counter += 1
        sst = NexusSSTable(path, sorted_items)
        self.sstables.insert(0, sst)
        self.memtable.clear()
        open(self.wal_path, "w", encoding="utf-8").close()

    def get(self, key: str) -> Optional[str]:
        if key in self.memtable:
            v = self.memtable[key]
            return None if v == NexusSSTable.TOMBSTONE else v
        for sst in self.sstables:
            v = sst.get(key)
            if v is not None:
                return None if v == NexusSSTable.TOMBSTONE else v
        return None


class NexusHybridRetriever:
    """Hybrid RAG Search: Dense Cosine Similarity + Sparse BM25 + Reciprocal Rank Fusion."""
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.docs: List[str] = []
        self.embeddings: List[List[float]] = []
        self.doc_tokens: List[List[str]] = []
        self.df: Dict[str, int] = {}

    def index_document(self, text: str, embedding: List[float]) -> int:
        doc_id = len(self.docs)
        self.docs.append(text)
        self.embeddings.append(embedding)
        tokens = text.lower().split()
        self.doc_tokens.append(tokens)
        for t in set(tokens):
            self.df[t] = self.df.get(t, 0) + 1
        return doc_id

    def _cosine(self, v1: List[float], v2: List[float]) -> float:
        dot = sum(a * b for a, b in zip(v1, v2))
        n1 = math.sqrt(sum(a * a for a in v1))
        n2 = math.sqrt(sum(b * b for b in v2))
        return dot / (n1 * n2) if (n1 > 0 and n2 > 0) else 0.0

    def dense_search(self, query_emb: List[float]) -> List[int]:
        scored = [(i, self._cosine(query_emb, e)) for i, e in enumerate(self.embeddings)]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [doc_id for doc_id, _ in scored]

    def sparse_search(self, query_text: str) -> List[int]:
        N = len(self.docs)
        if N == 0:
            return []
        avgdl = sum(len(d) for d in self.doc_tokens) / N
        q_terms = query_text.lower().split()
        scores: List[Tuple[int, float]] = []

        for doc_id, tokens in enumerate(self.doc_tokens):
            score = 0.0
            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            for q in q_terms:
                if q in tf:
                    f = tf[q]
                    n_qi = self.df.get(q, 0)
                    idf = math.log(1.0 + (N - n_qi + 0.5) / (n_qi + 0.5))
                    num = f * (self.k1 + 1.0)
                    den = f + self.k1 * (1.0 - self.b + self.b * (len(tokens) / avgdl))
                    score += idf * (num / den)
            scores.append((doc_id, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return [doc_id for doc_id, _ in scores]

    def hybrid_search(self, query_text: str, query_emb: List[float], rrf_k: int = 60) -> List[Tuple[int, float]]:
        dense_ranks = self.dense_search(query_emb)
        sparse_ranks = self.sparse_search(query_text)

        rrf_scores: Dict[int, float] = {}
        for r_list in [dense_ranks, sparse_ranks]:
            for rank, doc_id in enumerate(r_list, start=1):
                rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (rrf_k + rank))

        results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        return results


class NexusRaftNode:
    """Raft consensus node managing replication and LSM state machine."""
    def __init__(self, node_id: str, cluster_nodes: List[str], storage_dir: str):
        self.node_id = node_id
        self.peers = [p for p in cluster_nodes if p != node_id]
        self.role = RaftRole.FOLLOWER
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.log: List[Dict[str, Any]] = []  # Log entries: {"term": int, "cmd": dict}
        self.commit_index = 0
        self.last_applied = 0
        self.lsm = NexusLSMStore(storage_dir)
        self.retriever = NexusHybridRetriever()

    def start_election(self) -> int:
        self.role = RaftRole.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        votes = 1  # Vote for self
        return votes

    def append_entry(self, cmd: Dict[str, Any]) -> None:
        if self.role != RaftRole.LEADER:
            raise RuntimeError("Only leader accepts mutations")
        entry = {"term": self.current_term, "cmd": cmd}
        self.log.append(entry)

    def apply_committed(self) -> None:
        while self.last_applied < self.commit_index:
            self.last_applied += 1
            entry = self.log[self.last_applied - 1]
            cmd = entry["cmd"]
            op = cmd.get("op")
            if op == "PUT":
                self.lsm.put(cmd["key"], cmd["val"])
                if "embedding" in cmd:
                    self.retriever.index_document(cmd["val"], cmd["embedding"])
            elif op == "DELETE":
                self.lsm.delete(cmd["key"])
