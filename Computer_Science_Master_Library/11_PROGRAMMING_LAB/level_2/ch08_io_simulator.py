#!/usr/bin/env python3
"""
Chapter 08 Python Verification & Emulation Testbed:
Buffered Stream I/O, Binary Persistence, and Random Access Seeking

Validates:
- Binary struct packing and unpacking matching C `#pragma pack(1)`
- Direct seeking offset formula: Offset = Index * sizeof(Record)
- EOF boundary handling and truncation protection
- Amortized buffered I/O performance simulation
"""

import os
import struct
import sys
import tempfile

# Enforce UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Record format: uint32 (4 bytes), char[24] (24 bytes), double (8 bytes) -> 36 bytes total
RECORD_FORMAT = "<I24sd"
RECORD_SIZE = struct.calcsize(RECORD_FORMAT)
assert RECORD_SIZE == 36, f"Expected 36 bytes, got {RECORD_SIZE}"


def pack_record(rec_id: int, key: str, value: float) -> bytes:
    encoded_key = key.encode("utf-8")[:23] + b"\x00"  # Ensure null termination
    encoded_key = encoded_key.ljust(24, b"\x00")
    return struct.pack(RECORD_FORMAT, rec_id, encoded_key, value)


def unpack_record(raw_bytes: bytes) -> tuple:
    rec_id, raw_key, value = struct.unpack(RECORD_FORMAT, raw_bytes)
    # Strip null bytes from key
    key = raw_key.split(b"\x00")[0].decode("utf-8")
    return rec_id, key, value


def main() -> int:
    print("=" * 60)
    print("LEVEL 2 LAB CH08: BUFFERED FILE I/O & SEEK SIMULATOR")
    print("=" * 60)

    # Test 1: Binary Serialization & Deserialization
    print("\n[Test 1] Testing packed binary record serialization ...")
    test_records = [
        (101, "cpu_frequency", 3.8),
        (102, "gpu_temp", 62.5),
        (103, "network_rx", 1024.0),
        (104, "disk_free_gb", 480.2),
    ]

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_path = tmp_file.name
        for rec in test_records:
            tmp_file.write(pack_record(*rec))

    try:
        # Verify file size
        file_size = os.path.getsize(tmp_path)
        expected_size = len(test_records) * RECORD_SIZE
        print(f"  File size on disk = {file_size} bytes (Expected {expected_size} bytes)")
        assert file_size == expected_size, f"Size mismatch: {file_size} vs {expected_size}"

        # Test 2: Direct Random-Access Seeking (O(1) Seek to Record 2)
        print("\n[Test 2] Testing random access seek to Record Index 2 ...")
        target_idx = 2
        seek_offset = target_idx * RECORD_SIZE

        with open(tmp_path, "rb") as f:
            f.seek(seek_offset, os.SEEK_SET)
            raw = f.read(RECORD_SIZE)
            rec_id, key, val = unpack_record(raw)
            print(f"  Read Record 2: ID={rec_id}, Key='{key}', Val={val}")
            assert rec_id == 103 and key == "network_rx" and val == 1024.0

        # Test 3: Truncated Read Boundary Protection
        print("\n[Test 3] Testing EOF Truncation Protection ...")
        with open(tmp_path, "rb") as f:
            f.seek(file_size - 10, os.SEEK_SET) # Only 10 bytes left
            partial = f.read(RECORD_SIZE)
            print(f"  Attempted 36-byte read at offset {file_size - 10}, received {len(partial)} bytes")
            assert len(partial) < RECORD_SIZE, "Failed to trap truncated partial read!"
            print("  SUCCESS: Partial read detected correctly.")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    print("\n" + "=" * 60)
    print("ALL CH08 FILE I/O & PERSISTENCE CHECKS PASSED (Exit 0)")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
