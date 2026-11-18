"""
ch09_lsm_storage_engine_lab.py
Level 6 Companion Lab: Log-Structured Merge-Tree (LSM-Tree) Storage Engine.
Pure Python/Standard Library implementation with zero external dependencies.
"""

from __future__ import annotations
import sys
import os
import math
import struct
import bisect
import tempfile
import hashlib
from typing import List, Tuple, Optional, Dict

# Windows UTF-8 console output
sys.stdout.reconfigure(encoding="utf-8")


class LabBloomFilter:
    """
    Bloom filter implementation for fast SSTable membership checking.
    """
    def __init__(self, capacity: int, fp_rate: float = 0.01):
        self.capacity = max(capacity, 10)
        self.num_bits = int(- (self.capacity * math.log(fp_rate)) / (math.log(2) ** 2))
        self.num_bits = max(self.num_bits, 64)
        self.num_hashes = max(1, int((self.num_bits / self.capacity) * math.log(2)))
        self.bit_array = bytearray((self.num_bits + 7) // 8)

    def _hashes(self, key: str) -> List[int]:
        digest = hashlib.sha256(key.encode("utf-8")).digest()
        h1, h2 = struct.unpack(">QQ", digest[:16])
        return [(h1 + i * h2) % self.num_bits for i in range(self.num_hashes)]

    def add(self, key: str) -> None:
        for b in self._hashes(key):
            self.bit_array[b // 8] |= (1 << (b % 8))

    def contains(self, key: str) -> bool:
        for b in self._hashes(key):
            if not (self.bit_array[b // 8] & (1 << (b % 8))):
                return False
        return True


class LabSSTable:
    """
    Sorted String Table with block sparse index and Bloom filter.
    """
    TOMBSTONE = "__DELETED__"

    def __init__(self, file_path: str, data: List[Tuple[str, str]], index_step: int = 4):
        self.file_path = file_path
        self.sparse_index: List[Tuple[str, int]] = []
        self.bloom = LabBloomFilter(len(data))
        self._write(data, index_step)

    def _write(self, data: List[Tuple[str, str]], index_step: int) -> None:
        with open(self.file_path, "wb") as f:
            for i, (k, v) in enumerate(data):
                offset = f.tell()
                self.bloom.add(k)
                if i % index_step == 0:
                    self.sparse_index.append((k, offset))

                k_bytes = k.encode("utf-8")
                v_bytes = v.encode("utf-8")
                f.write(struct.pack(">II", len(k_bytes), len(v_bytes)) + k_bytes + v_bytes)

    def get(self, key: str) -> Optional[str]:
        if not self.bloom.contains(key):
            return None

        keys = [k for k, _ in self.sparse_index]
        idx = bisect.bisect_right(keys, key) - 1
        if idx < 0:
            return None

        start_off = self.sparse_index[idx][1]
        next_off = self.sparse_index[idx + 1][1] if idx + 1 < len(self.sparse_index) else None

        with open(self.file_path, "rb") as f:
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


class LabLSMTree:
    """
    Log-Structured Merge-Tree Engine with MemTable flushing and tombstone masking.
    """
    def __init__(self, root_dir: str, flush_threshold: int = 10):
        self.root_dir = root_dir
        os.makedirs(root_dir, exist_ok=True)
        self.wal_path = os.path.join(root_dir, "wal.log")
        self.flush_threshold = flush_threshold
        self.memtable: Dict[str, str] = {}
        self.sstables: List[LabSSTable] = []
        self._counter = 0

    def put(self, key: str, value: str) -> None:
        with open(self.wal_path, "a", encoding="utf-8") as f:
            f.write(f"{key}\t{value}\n")

        self.memtable[key] = value
        if len(self.memtable) >= self.flush_threshold:
            self.flush()

    def delete(self, key: str) -> None:
        self.put(key, LabSSTable.TOMBSTONE)

    def flush(self) -> None:
        if not self.memtable:
            return
        sorted_items = sorted(self.memtable.items())
        path = os.path.join(self.root_dir, f"sstable_{self._counter:03d}.sst")
        self._counter += 1
        sst = LabSSTable(path, sorted_items)
        self.sstables.insert(0, sst)  # Most recent first
        self.memtable.clear()
        open(self.wal_path, "w", encoding="utf-8").close()

    def get(self, key: str) -> Optional[str]:
        if key in self.memtable:
            v = self.memtable[key]
            return None if v == LabSSTable.TOMBSTONE else v

        for sst in self.sstables:
            v = sst.get(key)
            if v is not None:
                return None if v == LabSSTable.TOMBSTONE else v
        return None


def test_bloom_filter():
    print("Running Test Suite 1: Bloom Filter Zero False-Negative Guarantee...")
    bf = LabBloomFilter(capacity=100, fp_rate=0.01)
    keys = [f"key_{i}" for i in range(50)]
    for k in keys:
        bf.add(k)

    # Every inserted key MUST return True (no false negatives)
    for k in keys:
        assert bf.contains(k) is True, f"False negative on key {k}"

    # Non-existent key checks
    neg_count = sum(1 for i in range(100, 200) if bf.contains(f"key_{i}"))
    assert neg_count <= 5, f"False positive rate exceeded: {neg_count}/100"
    print(f"  Passed! Zero false negatives and {neg_count}% empirical false-positive rate.")


def test_lsm_put_get_flush():
    print("Running Test Suite 2: LSM-Tree Ingestion, Flush, and Point Lookups...")
    temp_dir = tempfile.mkdtemp(prefix="lsm_test_")
    lsm = LabLSMTree(temp_dir, flush_threshold=5)

    # Ingest 12 items -> triggers 2 flushes (5 items each), 2 items remain in MemTable
    for i in range(12):
        lsm.put(f"key_{i:02d}", f"val_{i}")

    assert len(lsm.sstables) == 2, f"Expected 2 SSTables, got {len(lsm.sstables)}"
    assert len(lsm.memtable) == 2, f"Expected 2 items in MemTable, got {len(lsm.memtable)}"

    # Read from MemTable
    assert lsm.get("key_11") == "val_11"
    # Read from flushed SSTables
    assert lsm.get("key_00") == "val_0"
    assert lsm.get("key_04") == "val_4"
    assert lsm.get("key_09") == "val_9"
    # Read non-existent key
    assert lsm.get("key_99") is None
    print("  Passed! MemTable and SSTable lookups match expected values.")


def test_lsm_tombstone_deletion():
    print("Running Test Suite 3: LSM-Tree Tombstone Deletion Semantics...")
    temp_dir = tempfile.mkdtemp(prefix="lsm_del_test_")
    lsm = LabLSMTree(temp_dir, flush_threshold=5)

    lsm.put("user:101", "Alice")
    lsm.flush()  # Flushed to SSTable

    assert lsm.get("user:101") == "Alice"

    # Delete key
    lsm.delete("user:101")
    # Active memtable contains tombstone
    assert lsm.get("user:101") is None

    # Flush tombstone to a newer SSTable
    lsm.flush()
    # Newer SSTable masks older SSTable value
    assert lsm.get("user:101") is None
    print("  Passed! Tombstones properly mask older SSTable records.")


if __name__ == "__main__":
    print("================================================================================")
    print("LEVEL 6 LAB 09: LSM-TREE ENGINE & BLOOM FILTER TESTBED")
    print("================================================================================")
    test_bloom_filter()
    test_lsm_put_get_flush()
    test_lsm_tombstone_deletion()
    print("================================================================================")
    print("ALL 3 TEST SUITES PASSED CLEANLY (EXIT CODE 0)")
    print("================================================================================")
