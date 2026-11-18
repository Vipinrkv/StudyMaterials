"""
ch08_rag_vector_db_lab.py
Level 6 Companion Lab: Dense Vector Search, BM25 Scoring, and Reciprocal Rank Fusion (RRF).
Pure Python/Standard Library implementation with zero external dependencies.
"""

from __future__ import annotations
import sys
import math
from typing import List, Dict, Tuple

# Windows UTF-8 console output
sys.stdout.reconfigure(encoding="utf-8")


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Computes cosine similarity between two non-zero vectors."""
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return dot / (norm1 * norm2)


class BM25Retriever:
    """
    Okapi BM25 sparse keyword retriever.
    Formula: IDF(q_i) * ((f * (k1 + 1)) / (f + k1 * (1 - b + b * (|D| / avgdl))))
    """
    def __init__(self, corpus: List[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus = corpus
        self.doc_tokens = [doc.lower().split() for doc in corpus]
        self.N = len(corpus)
        self.avgdl = sum(len(d) for d in self.doc_tokens) / max(1, self.N)
        self.df: Dict[str, int] = {}
        self._compute_document_frequencies()

    def _compute_document_frequencies(self) -> None:
        for doc in self.doc_tokens:
            unique_terms = set(doc)
            for t in unique_terms:
                self.df[t] = self.df.get(t, 0) + 1

    def _idf(self, term: str) -> float:
        n_qi = self.df.get(term, 0)
        # Standard probabilistic BM25 IDF
        return math.log(1.0 + (self.N - n_qi + 0.5) / (n_qi + 0.5))

    def score(self, query: str) -> List[Tuple[int, float]]:
        q_terms = query.lower().split()
        scores: List[Tuple[int, float]] = []

        for doc_id, doc in enumerate(self.doc_tokens):
            doc_len = len(doc)
            doc_score = 0.0
            term_freqs: Dict[str, int] = {}
            for t in doc:
                term_freqs[t] = term_freqs.get(t, 0) + 1

            for q in q_terms:
                if q in term_freqs:
                    f = term_freqs[q]
                    idf = self._idf(q)
                    numerator = f * (self.k1 + 1.0)
                    denominator = f + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avgdl))
                    doc_score += idf * (numerator / denominator)

            scores.append((doc_id, doc_score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores


class VectorDatabase:
    """
    Dense vector database supporting brute-force exact cosine similarity search.
    """
    def __init__(self):
        self.documents: List[str] = []
        self.embeddings: List[List[float]] = []

    def add_document(self, text: str, embedding: List[float]) -> int:
        doc_id = len(self.documents)
        self.documents.append(text)
        self.embeddings.append(embedding)
        return doc_id

    def search(self, query_emb: List[float], top_k: int = 5) -> List[Tuple[int, float]]:
        scored = []
        for doc_id, emb in enumerate(self.embeddings):
            sim = cosine_similarity(query_emb, emb)
            scored.append((doc_id, sim))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]


def reciprocal_rank_fusion(
    ranked_lists: List[List[int]],
    k: int = 60
) -> List[Tuple[int, float]]:
    """
    Combines ranked results from sparse and dense retrieval streams using RRF:
    RRF_Score(d) = sum_{m in models} 1 / (k + rank_m(d))
    """
    scores: Dict[int, float] = {}

    for r_list in ranked_lists:
        for rank, doc_id in enumerate(r_list, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank))

    sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_results


def test_cosine_similarity():
    print("Running Test Suite 1: Cosine Similarity Metric Verification...")
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    assert abs(cosine_similarity(v1, v2) - 1.0) < 1e-6

    v3 = [0.0, 1.0, 0.0]
    assert abs(cosine_similarity(v1, v3) - 0.0) < 1e-6

    v4 = [-1.0, 0.0, 0.0]
    assert abs(cosine_similarity(v1, v4) - (-1.0)) < 1e-6
    print("  Passed! Exact cosine similarities verified for parallel, orthogonal, and opposing vectors.")


def test_bm25_retrieval():
    print("Running Test Suite 2: Okapi BM25 Keyword Scoring...")
    corpus = [
        "Distributed consensus using Raft and Paxos algorithms",
        "Deep neural networks and backpropagation gradient descent",
        "Kubernetes orchestration and container scheduling"
    ]
    bm25 = BM25Retriever(corpus)
    results = bm25.score("raft consensus")
    best_doc_id, best_score = results[0]
    assert best_doc_id == 0, f"Expected doc 0 to rank highest, got {best_doc_id}"
    assert best_score > 0.0
    print(f"  Passed! BM25 correctly ranked target document with score {best_score:.4f}.")


def test_rrf_hybrid_fusion():
    print("Running Test Suite 3: Reciprocal Rank Fusion (RRF)...")
    # Dense ranked list: doc 1, doc 0, doc 2
    dense_ranks = [1, 0, 2]
    # Sparse BM25 ranked list: doc 0, doc 1, doc 2
    sparse_ranks = [0, 1, 2]

    # Both doc 0 and doc 1 are at positions {1, 2} in either list, so their RRF scores must be equal:
    # 1/(60 + 1) + 1/(60 + 2) = 1/61 + 1/62
    fused = reciprocal_rank_fusion([dense_ranks, sparse_ranks], k=60)
    assert len(fused) == 3
    # Top two scores should be identical
    assert abs(fused[0][1] - fused[1][1]) < 1e-6
    # Lowest score should be doc 2 (rank 3 in both: 1/63 + 1/63)
    assert fused[2][0] == 2
    print(f"  Passed! RRF properly fuses sparse and dense rankings into consistent order.")


if __name__ == "__main__":
    print("================================================================================")
    print("LEVEL 6 LAB 08: RAG VECTOR DATABASE & HYBRID RRF SEARCH ENGINE")
    print("================================================================================")
    test_cosine_similarity()
    test_bm25_retrieval()
    test_rrf_hybrid_fusion()
    print("================================================================================")
    print("ALL 3 TEST SUITES PASSED CLEANLY (EXIT CODE 0)")
    print("================================================================================")
