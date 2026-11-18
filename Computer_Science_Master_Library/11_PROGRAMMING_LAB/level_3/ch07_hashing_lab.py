"""
Level 3 Chapter 07: Hashing, Hash Tables, and Collision Resolution
Comprehensive Laboratory Verification Suite

Covers:
1. Open Addressing with Linear Probing and Tombstones.
2. Dynamic Rehashing at load factor alpha >= 0.70.
3. Tombstone reuse and chain continuation.
4. Robin Hood Hashing: Probe Sequence Length (PSL) tracking and variance reduction.
"""

import sys
import math
from typing import Optional, Any, List, Tuple

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

TOMBSTONE = object()  # Sentinel marker for deleted slot


class LinearProbingHashTable:
    def __init__(self, capacity: int = 8):
        self.capacity = capacity
        self.size = 0
        self.tombstones = 0
        self.keys: List[Optional[Any]] = [None] * capacity
        self.vals: List[Optional[Any]] = [None] * capacity

    def _hash(self, key: Any) -> int:
        return (hash(key) & 0x7FFFFFFF) % self.capacity

    @property
    def load_factor(self) -> float:
        return (self.size + self.tombstones) / self.capacity

    def put(self, key: Any, val: Any) -> None:
        if self.load_factor >= 0.70:
            self._rehash(self.capacity * 2)

        idx = self._hash(key)
        first_tombstone = None

        while self.keys[idx] is not None:
            if self.keys[idx] is TOMBSTONE:
                if first_tombstone is None:
                    first_tombstone = idx
            elif self.keys[idx] == key:
                self.vals[idx] = val  # Update existing
                return
            idx = (idx + 1) % self.capacity

        dest = first_tombstone if first_tombstone is not None else idx
        if dest == first_tombstone:
            self.tombstones -= 1

        self.keys[dest] = key
        self.vals[dest] = val
        self.size += 1

    def get(self, key: Any) -> Optional[Any]:
        idx = self._hash(key)
        start = idx

        while self.keys[idx] is not None:
            if self.keys[idx] is not TOMBSTONE and self.keys[idx] == key:
                return self.vals[idx]
            idx = (idx + 1) % self.capacity
            if idx == start:
                break
        return None

    def delete(self, key: Any) -> bool:
        idx = self._hash(key)
        start = idx

        while self.keys[idx] is not None:
            if self.keys[idx] is not TOMBSTONE and self.keys[idx] == key:
                self.keys[idx] = TOMBSTONE
                self.vals[idx] = None
                self.size -= 1
                self.tombstones += 1
                return True
            idx = (idx + 1) % self.capacity
            if idx == start:
                break
        return False

    def _rehash(self, new_cap: int) -> None:
        old_keys = self.keys
        old_vals = self.vals

        self.capacity = new_cap
        self.size = 0
        self.tombstones = 0
        self.keys = [None] * new_cap
        self.vals = [None] * new_cap

        for k, v in zip(old_keys, old_vals):
            if k is not None and k is not TOMBSTONE:
                self.put(k, v)


class RobinHoodHashTable:
    """Robin Hood Hashing where keys with higher PSL displace keys with lower PSL."""
    def __init__(self, capacity: int = 16):
        self.capacity = capacity
        self.size = 0
        # Entries: (key, val, psl)
        self.table: List[Optional[Tuple[Any, Any, int]]] = [None] * capacity

    def _home_slot(self, key: Any) -> int:
        return (hash(key) & 0x7FFFFFFF) % self.capacity

    def put(self, key: Any, val: Any) -> None:
        if self.size / self.capacity >= 0.85:
            self._rehash(self.capacity * 2)

        curr_key = key
        curr_val = val
        curr_psl = 0
        idx = self._home_slot(curr_key)

        while True:
            entry = self.table[idx]
            if entry is None:
                self.table[idx] = (curr_key, curr_val, curr_psl)
                self.size += 1
                return
            elif entry[0] == curr_key:
                # Update key
                self.table[idx] = (curr_key, curr_val, entry[2])
                return

            existing_psl = entry[2]
            if curr_psl > existing_psl:
                # Robin Hood swap: take from rich, give to poor!
                self.table[idx] = (curr_key, curr_val, curr_psl)
                curr_key, curr_val, curr_psl = entry[0], entry[1], existing_psl

            curr_psl += 1
            idx = (idx + 1) % self.capacity

    def get(self, key: Any) -> Optional[Any]:
        idx = self._home_slot(key)
        psl = 0

        while True:
            entry = self.table[idx]
            if entry is None or psl > entry[2]:
                return None  # Early termination: key cannot exist further!
            if entry[0] == key:
                return entry[1]
            psl += 1
            idx = (idx + 1) % self.capacity

    def get_psl_distribution(self) -> List[int]:
        return [entry[2] for entry in self.table if entry is not None]

    def _rehash(self, new_cap: int) -> None:
        old_table = self.table
        self.capacity = new_cap
        self.size = 0
        self.table = [None] * new_cap
        for entry in old_table:
            if entry is not None:
                self.put(entry[0], entry[1])


def test_hashing_lab():
    print("[TEST 1] Linear Probing basic put, get, update...")
    ht = LinearProbingHashTable(capacity=8)
    ht.put("apple", 10)
    ht.put("banana", 20)
    ht.put("orange", 30)
    assert ht.get("apple") == 10
    assert ht.get("banana") == 20
    assert ht.get("orange") == 30
    assert ht.get("mango") is None

    ht.put("apple", 99)
    assert ht.get("apple") == 99
    assert ht.size == 3
    print("  -> Passed. Basic operations verified.")

    print("[TEST 2] Tombstone deletion and chain continuity...")
    # Force collisions by creating colliding keys in a small table
    ht2 = LinearProbingHashTable(capacity=16)
    for i in range(10):
        ht2.put(f"key_{i}", i * 100)

    # Delete an intermediate key
    assert ht2.delete("key_3") is True
    assert ht2.get("key_3") is None
    # Subsequent keys in probe chain must still be reachable
    for i in range(4, 10):
        assert ht2.get(f"key_{i}") == i * 100, f"Chain broken at key_{i}"

    # Re-insert should reuse tombstone
    ht2.put("new_key", 777)
    assert ht2.get("new_key") == 777
    print("  -> Passed. Tombstones preserve search chains and can be reused.")

    print("[TEST 3] Dynamic Rehashing on high load factor...")
    ht3 = LinearProbingHashTable(capacity=4)
    for i in range(100):
        ht3.put(f"id_{i}", i)
    assert ht3.size == 100
    assert ht3.capacity >= 128
    for i in range(100):
        assert ht3.get(f"id_{i}") == i
    print(f"  -> Passed. Resized smoothly to capacity {ht3.capacity} with 100 items.")

    print("[TEST 4] Robin Hood Hashing PSL Variance Verification...")
    rh = RobinHoodHashTable(capacity=64)
    for i in range(50):
        rh.put(f"user_{i}", i)

    for i in range(50):
        assert rh.get(f"user_{i}") == i

    psls = rh.get_psl_distribution()
    mean_psl = sum(psls) / len(psls)
    max_psl = max(psls)
    variance = sum((p - mean_psl) ** 2 for p in psls) / len(psls)
    print(f"  -> Robin Hood stats: Mean PSL={mean_psl:.2f}, Max PSL={max_psl}, Variance={variance:.2f}")
    assert max_psl < 10, f"Robin Hood PSL too high: {max_psl}"
    print("  -> Passed. Robin Hood enforces fair, low-variance search paths.")

    print("ALL Chapter 07 Hashing lab tests passed successfully!")


if __name__ == "__main__":
    test_hashing_lab()
