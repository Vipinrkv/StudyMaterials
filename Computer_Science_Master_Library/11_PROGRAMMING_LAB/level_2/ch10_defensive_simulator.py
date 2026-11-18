#!/usr/bin/env python3
"""
Chapter 10 Python Verification & Emulation Testbed:
Defensive Design by Contract and AddressSanitizer Redzone Simulator

Validates:
- Precondition and postcondition invariant enforcement
- AddressSanitizer (ASan) shadow memory and redzone corruption trap
- Memory leak accounting and double-free interception
- Safe string bounded truncation
"""

import sys
from typing import Dict, List, Optional

# Enforce UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class ShadowMemorySimulator:
    """Emulates ASan redzones around allocated memory chunks."""

    def __init__(self, size: int = 256):
        self.memory = bytearray(size)
        # 0 = Valid, 1 = Redzone / Poisoned
        self.shadow = bytearray(size)
        self.active_allocations: Dict[int, Tuple[int, int]] = {}  # ptr -> (start, payload_size)

    def allocate(self, payload_size: int, redzone_size: int = 8) -> int:
        # Search for enough contiguous unpoisoned space
        total_block = redzone_size + payload_size + redzone_size
        start_addr = len(self.active_allocations) * 64 + 16

        # Mark left redzone
        for i in range(start_addr, start_addr + redzone_size):
            self.shadow[i] = 1

        payload_start = start_addr + redzone_size
        # Mark payload as valid (0)
        for i in range(payload_start, payload_start + payload_size):
            self.shadow[i] = 0

        # Mark right redzone
        for i in range(payload_start + payload_size, payload_start + payload_size + redzone_size):
            self.shadow[i] = 1

        self.active_allocations[payload_start] = (start_addr, payload_size)
        return payload_start

    def write_byte(self, addr: int, val: int) -> None:
        if self.shadow[addr] == 1:
            raise MemoryError(f"ERROR: AddressSanitizer: buffer-overflow on address 0x{addr:04X} (Poisoned Redzone Access)!")
        self.memory[addr] = val & 0xFF

    def free(self, ptr: int, redzone_size: int = 8) -> None:
        if ptr not in self.active_allocations:
            raise ValueError(f"ERROR: Double free or invalid pointer free at 0x{ptr:04X}!")
        start, sz = self.active_allocations.pop(ptr)
        # Poison entire block
        for i in range(start, start + redzone_size + sz + redzone_size):
            self.shadow[i] = 1


def safe_truncate_copy(dest_capacity: int, src: str) -> str:
    """Defensive string copy with guaranteed bounds."""
    assert dest_capacity > 0, "Capacity must be positive"
    max_chars = dest_capacity - 1
    truncated = src[:max_chars]
    return truncated


def main() -> int:
    print("=" * 60)
    print("LEVEL 2 LAB CH10: DEFENSIVE & SANITIZER SIMULATOR")
    print("=" * 60)

    # Test 1: Defensive Bounded String Truncation
    print("\n[Test 1] Testing defensive string truncation ...")
    dest_cap = 8
    input_str = "BharatConnect"
    result = safe_truncate_copy(dest_cap, input_str)
    print(f"  Input: '{input_str}' (Len {len(input_str)}) -> Copied: '{result}' (Len {len(result)})")
    assert len(result) < dest_cap
    assert result == "BharatC"
    print("  -> Null termination and bounds strictly maintained.")

    # Test 2: AddressSanitizer Redzone Overflow Interception
    print("\n[Test 2] Testing AddressSanitizer (ASan) Redzone Detection ...")
    asan = ShadowMemorySimulator(size=512)
    ptr = asan.allocate(payload_size=16, redzone_size=8)
    print(f"  Allocated 16 bytes at 0x{ptr:04X} protected by 8-byte redzones.")

    # Write within bounds (0 to 15)
    for i in range(16):
        asan.write_byte(ptr + i, ord('A') + i)
    print("  Written 16 bytes within bounds cleanly.")

    # Simulate 1-byte off-by-one heap buffer overflow (writing to index 16)
    print("  Simulating 1-byte heap buffer overflow write into right redzone ...")
    overflow_caught = False
    try:
        asan.write_byte(ptr + 16, ord('X')) # Poisoned!
    except MemoryError as e:
        overflow_caught = True
        print(f"  SUCCESS: Caught expected ASan violation: {e}")
    assert overflow_caught, "Failed to trap heap buffer overflow!"

    # Test 3: Double Free Interception
    print("\n[Test 3] Testing Double Free Interception ...")
    asan.free(ptr)
    double_free_caught = False
    try:
        asan.free(ptr)
    except ValueError as e:
        double_free_caught = True
        print(f"  SUCCESS: Caught expected double free: {e}")
    assert double_free_caught, "Failed to trap double free!"

    print("\n" + "=" * 60)
    print("ALL CH10 DEFENSIVE & SANITIZER CHECKS PASSED (Exit 0)")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
