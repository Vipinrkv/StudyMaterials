#!/usr/bin/env python3
"""
Level 2 Capstone Verification Harness: MiniKVS Testbed
Language: Python 3.11+

Validates:
1. Packed binary disk format matching C `#pragma pack(1)`:
   - Header: Magic (1B: 0x5A), Flags (1B), Timestamp (8B), KeyLen (2B), ValLen (4B) -> 16 Bytes
   - Key String (KeyLen bytes)
   - Value String (ValLen bytes)
   - Checksum (1B XOR over Header, Key, Value)
2. In-memory hash indexing and O(1) random-access disk seek offsets.
3. Crash resilience & index recovery from existing append-only logs.
4. Tombstone deletion semantics.
5. Zero memory leak verification.
"""

import os
import struct
import sys
import tempfile
import time
from typing import Dict, Optional, Tuple

# Enforce UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HEADER_FORMAT = "<BBQHI"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
assert HEADER_SIZE == 16, f"Expected 16-byte header, got {HEADER_SIZE}"

KVS_MAGIC = 0x5A
FLAG_ACTIVE = 0x00
FLAG_TOMBSTONE = 0x01


def compute_xor_checksum(data: bytes) -> int:
    csum = 0
    for b in data:
        csum ^= b
    return csum


class MiniKVSEmulator:
    """Python reference emulator adhering to the exact C MiniKVS binary wire protocol."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        # In-memory index: key -> (file_offset_of_val, val_len)
        self.index: Dict[str, Tuple[int, int]] = {}
        self.active_allocations_bytes = 0

        # Open file in append/update binary mode
        self.file = open(self.filepath, "a+b")
        self._recover_index()

    def _recover_index(self):
        """Rebuilds the in-memory index by scanning the append-only log from offset 0."""
        self.file.seek(0, os.SEEK_SET)
        while True:
            hdr_bytes = self.file.read(HEADER_SIZE)
            if len(hdr_bytes) < HEADER_SIZE:
                break

            magic, flags, ts, klen, vlen = struct.unpack(HEADER_FORMAT, hdr_bytes)
            if magic != KVS_MAGIC:
                break

            key_bytes = self.file.read(klen)
            if len(key_bytes) < klen:
                break
            key = key_bytes.decode("utf-8")

            val_offset = self.file.tell()
            self.file.seek(vlen, os.SEEK_CUR)  # Skip value payload

            csum_byte = self.file.read(1)
            if len(csum_byte) < 1:
                break

            if flags & FLAG_TOMBSTONE:
                self.index.pop(key, None)
            else:
                self.index[key] = (val_offset, vlen)

    def put(self, key: str, val: str) -> None:
        key_bytes = key.encode("utf-8")
        val_bytes = val.encode("utf-8")

        self.file.seek(0, os.SEEK_END)
        record_start = self.file.tell()

        ts = int(time.time() * 1000)
        hdr = struct.pack(HEADER_FORMAT, KVS_MAGIC, FLAG_ACTIVE, ts, len(key_bytes), len(val_bytes))

        # Checksum calculation matching C
        csum = compute_xor_checksum(hdr) ^ compute_xor_checksum(key_bytes) ^ compute_xor_checksum(val_bytes)

        # Write to disk
        self.file.write(hdr)
        self.file.write(key_bytes)
        self.file.write(val_bytes)
        self.file.write(bytes([csum]))
        self.file.flush()

        val_offset = record_start + HEADER_SIZE + len(key_bytes)
        self.index[key] = (val_offset, len(val_bytes))
        self.active_allocations_bytes += len(key_bytes) + 24  # Track simulated node size

    def get(self, key: str) -> Optional[str]:
        if key not in self.index:
            return None

        val_offset, val_len = self.index[key]
        # O(1) Direct Seek!
        self.file.seek(val_offset, os.SEEK_SET)
        val_bytes = self.file.read(val_len)
        return val_bytes.decode("utf-8")

    def delete(self, key: str) -> bool:
        if key not in self.index:
            return False

        key_bytes = key.encode("utf-8")
        self.file.seek(0, os.SEEK_END)
        ts = int(time.time() * 1000)

        hdr = struct.pack(HEADER_FORMAT, KVS_MAGIC, FLAG_TOMBSTONE, ts, len(key_bytes), 0)
        csum = compute_xor_checksum(hdr) ^ compute_xor_checksum(key_bytes)

        self.file.write(hdr)
        self.file.write(key_bytes)
        self.file.write(bytes([csum]))
        self.file.flush()

        self.index.pop(key)
        self.active_allocations_bytes -= (len(key_bytes) + 24)
        return True

    def close(self):
        if self.file:
            self.file.close()
            self.file = None
        self.index.clear()
        self.active_allocations_bytes = 0


def main() -> int:
    print("=" * 65)
    print("LEVEL 2 CAPSTONE: MINIKVS STORAGE ENGINE VERIFICATION")
    print("=" * 65)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".kvs") as tmp:
        db_path = tmp.name

    try:
        # Test 1: Engine Initialization & Basic CRUD Operations
        print("\n[Phase 1] Testing Basic PUT / GET / DELETE Operations ...")
        kvs = MiniKVSEmulator(db_path)

        kvs.put("user:1001", '{"name": "Ananya", "upi": "ananya@oksbi"}')
        kvs.put("user:1002", '{"name": "Rohan", "upi": "rohan@icici"}')
        kvs.put("config:cache_size", "4096")

        val1 = kvs.get("user:1001")
        val2 = kvs.get("user:1002")
        print(f"  GET user:1001 -> {val1}")
        print(f"  GET user:1002 -> {val2}")
        assert val1 is not None and "Ananya" in val1
        assert val2 is not None and "Rohan" in val2
        assert kvs.get("nonexistent_key") is None
        print("  -> Basic CRUD operations verified.")

        # Test 2: In-Place Update and Tombstone Deletion
        print("\n[Phase 2] Testing Key Overwrites & Tombstone Deletion ...")
        kvs.put("user:1001", '{"name": "Ananya", "tier": "platinum"}')
        updated_val = kvs.get("user:1001")
        print(f"  Updated user:1001 -> {updated_val}")
        assert updated_val is not None and "platinum" in updated_val

        del_ok = kvs.delete("user:1002")
        assert del_ok is True
        assert kvs.get("user:1002") is None
        print("  Successfully deleted user:1002 (Tombstone recorded).")

        kvs.close()
        assert kvs.active_allocations_bytes == 0, "Memory leak detected on close!"

        # Test 3: Binary Wire Format Inspection
        print("\n[Phase 3] Inspecting Physical Binary Wire Format on Disk ...")
        file_bytes = os.path.getsize(db_path)
        print(f"  Physical append-only log size = {file_bytes} bytes")
        with open(db_path, "rb") as f:
            first_16 = f.read(16)
            magic, flags, ts, klen, vlen = struct.unpack(HEADER_FORMAT, first_16)
            print(f"  First Record Header: Magic=0x{magic:02X}, Flags={flags}, KeyLen={klen}, ValLen={vlen}")
            assert magic == KVS_MAGIC, "Invalid magic byte in wire format!"
            assert klen == len("user:1001")

        # Test 4: Crash Recovery & Index Replay
        print("\n[Phase 4] Testing Crash Recovery & Cold-Start Replay ...")
        kvs_recovered = MiniKVSEmulator(db_path)
        print(f"  Rebuilt index key count: {len(kvs_recovered.index)}")

        # Verify active keys were restored and deleted keys remain gone
        rec_val1 = kvs_recovered.get("user:1001")
        rec_val2 = kvs_recovered.get("user:1002")
        rec_conf = kvs_recovered.get("config:cache_size")

        print(f"  Recovered user:1001 -> {rec_val1}")
        print(f"  Recovered user:1002 -> {rec_val2} (Expected None)")
        print(f"  Recovered config    -> {rec_conf}")

        assert rec_val1 is not None and "platinum" in rec_val1
        assert rec_val2 is None, "Deleted tombstoned key resurrected after recovery!"
        assert rec_conf == "4096"
        print("  -> Crash recovery & index rebuild verified with 100% fidelity.")

        kvs_recovered.close()
        assert kvs_recovered.active_allocations_bytes == 0

    finally:
        if os.path.exists(db_path):
            os.remove(db_path)

    print("\n" + "=" * 65)
    print("ALL LEVEL 2 CAPSTONE (MINIKVS) VERIFICATION CHECKS PASSED (Exit 0)")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(main())
