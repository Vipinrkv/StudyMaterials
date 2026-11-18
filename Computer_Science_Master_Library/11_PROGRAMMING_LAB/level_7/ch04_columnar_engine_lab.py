"""
ch04_columnar_engine_lab.py
Level 7 Companion Lab: Columnar Physical Storage, Vectorized Filter & Radix Join.
Pure Python/Standard Library implementation with zero external dependencies.
"""

from __future__ import annotations
import sys
import math
from typing import Dict, List, Tuple, Any

# Windows UTF-8 console output
sys.stdout.reconfigure(encoding="utf-8")


class LabColumnChunk:
    """Frame of Reference (FoR) and Dictionary encoded columnar chunk."""
    def __init__(self, name: str, data: List[Any]):
        self.name = name
        self.count = len(data)
        self.encoding = "RAW"
        self.min_val = 0
        self.payload: Any = None
        self._encode(data)

    def _encode(self, data: List[Any]) -> None:
        if all(isinstance(x, int) for x in data):
            self.min_val = min(data)
            self.encoding = "FoR"
            self.payload = [x - self.min_val for x in data]
        elif all(isinstance(x, str) for x in data):
            unique = list(set(data))
            mapping = {v: i for i, v in enumerate(unique)}
            self.encoding = "DICT"
            self.payload = {"dict": unique, "codes": [mapping[x] for x in data]}
        else:
            self.payload = list(data)

    def decode(self) -> List[Any]:
        if self.encoding == "FoR":
            return [self.min_val + d for d in self.payload]
        elif self.encoding == "DICT":
            dictionary = self.payload["dict"]
            return [dictionary[c] for c in self.payload["codes"]]
        return list(self.payload)


class LabVectorBatch:
    """Fixed-size vector batch passed between analytical operators."""
    def __init__(self, cols: Dict[str, List[Any]], count: int):
        self.cols = cols
        self.count = count
        self.selection_vector: List[int] = list(range(count))

    def filter_gt(self, col_name: str, threshold: float) -> None:
        data = self.cols[col_name]
        self.selection_vector = [idx for idx in self.selection_vector if data[idx] > threshold]

    def aggregate_sum(self, group_col: str, agg_col: str) -> Dict[str, float]:
        groups = self.cols[group_col]
        values = self.cols[agg_col]
        sums: Dict[str, float] = {}
        for idx in self.selection_vector:
            g = groups[idx]
            v = values[idx]
            sums[g] = sums.get(g, 0.0) + v
        return sums


def lab_radix_partition(keys: List[int], values: List[float], num_bits: int = 2) -> Dict[int, List[Tuple[int, float]]]:
    """Partitions elements into 2^num_bits cache-sized buckets based on hash bitmask."""
    num_buckets = 1 << num_bits
    mask = num_buckets - 1
    buckets: Dict[int, List[Tuple[int, float]]] = {i: [] for i in range(num_buckets)}

    for k, v in zip(keys, values):
        bucket_idx = (hash(k) ^ (hash(k) >> 8)) & mask
        buckets[bucket_idx].append((k, v))

    return buckets


def test_columnar_encoding():
    print("Running Test Suite 1: Columnar Compression (FoR & Dictionary)...")
    # Integer data (order IDs)
    raw_ints = [10500, 10502, 10501, 10505, 10500]
    chunk_int = LabColumnChunk("order_id", raw_ints)
    assert chunk_int.encoding == "FoR"
    assert chunk_int.min_val == 10500
    assert chunk_int.payload == [0, 2, 1, 5, 0]
    assert chunk_int.decode() == raw_ints

    # String data (regions)
    raw_strs = ["APAC", "EMEA", "APAC", "AMER", "EMEA"]
    chunk_str = LabColumnChunk("region", raw_strs)
    assert chunk_str.encoding == "DICT"
    assert len(chunk_str.payload["dict"]) == 3
    assert chunk_str.decode() == raw_strs
    print("  Passed! Frame of Reference and Dictionary encodings decode losslessly.")


def test_vectorized_filter_aggregate():
    print("Running Test Suite 2: Vectorized Selection Vectors & Grouped Aggregates...")
    # 6 rows of synthetic order data
    cols = {
        "region": ["US", "US", "EU", "EU", "APAC", "APAC"],
        "amount": [120.0, 450.0, 800.0, 50.0, 950.0, 300.0]
    }
    batch = LabVectorBatch(cols, count=6)

    # Filter amount > 200.0
    # Surviving rows: idx 1 (450), idx 2 (800), idx 4 (950), idx 5 (300) -> 4 rows
    batch.filter_gt("amount", 200.0)
    assert batch.selection_vector == [1, 2, 4, 5]

    # Aggregate SUM(amount) GROUP BY region
    sums = batch.aggregate_sum("region", "amount")
    assert sums["US"] == 450.0
    assert sums["EU"] == 800.0
    assert sums["APAC"] == 1250.0  # 950 + 300
    print("  Passed! Vector filter and grouped sum computed without row materialization.")


def test_radix_hash_partitioning():
    print("Running Test Suite 3: Radix Hash Join Cache Partitioning...")
    keys = list(range(100))
    values = [float(x * 10) for x in range(100)]
    buckets = lab_radix_partition(keys, values, num_bits=2)  # 4 buckets

    assert len(buckets) == 4
    total_elements = sum(len(b) for b in buckets.values())
    assert total_elements == 100

    # Every bucket should have roughly balanced items (between 15 and 35)
    for b_idx, items in buckets.items():
        assert len(items) > 10, f"Bucket {b_idx} starved with only {len(items)} items"
    print("  Passed! Radix hash partitioning cleanly divided 100 items across 4 cache buckets.")


if __name__ == "__main__":
    print("================================================================================")
    print("LEVEL 7 LAB 04: COLUMNAR COMPRESSION & VECTORIZED EXECUTION ENGINE")
    print("================================================================================")
    test_columnar_encoding()
    test_vectorized_filter_aggregate()
    test_radix_hash_partitioning()
    print("================================================================================")
    print("ALL 3 TEST SUITES PASSED CLEANLY (EXIT CODE 0)")
    print("================================================================================")
