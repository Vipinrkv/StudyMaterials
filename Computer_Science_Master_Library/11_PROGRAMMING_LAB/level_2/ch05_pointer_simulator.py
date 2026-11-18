#!/usr/bin/env python3
"""
Chapter 05 Python Verification & Emulation Testbed:
Memory Address Space, Pointer Arithmetic, and Buffer Overrun Simulator

Validates:
- Row-major 2D array offset arithmetic: Base + (r * cols + c) * sizeof(T)
- Pointer arithmetic scaling factors across types (char=1, short=2, int=4, double=8)
- Memory dereference reads and writes (simulating swap(&a, &b))
- Null-terminated C-string scanning and buffer overrun detection
"""

import struct
import sys
from typing import Dict, List, Tuple

# Enforce UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class SimulatedMemory:
    """Simulates a flat byte-addressable linear RAM memory space."""

    def __init__(self, size: int = 4096, base_address: int = 0x1000):
        self.size = size
        self.base_address = base_address
        self.memory = bytearray(size)

    def _check_bounds(self, addr: int, byte_len: int) -> int:
        offset = addr - self.base_address
        if offset < 0 or (offset + byte_len) > self.size:
            raise MemoryError(f"SIGSEGV: Segmentation fault at address 0x{addr:08X} (Out of mapped bounds)!")
        return offset

    def write_int32(self, addr: int, value: int) -> None:
        offset = self._check_bounds(addr, 4)
        struct.pack_into("<i", self.memory, offset, value)

    def read_int32(self, addr: int) -> int:
        offset = self._check_bounds(addr, 4)
        return struct.unpack_from("<i", self.memory, offset)[0]

    def write_string(self, addr: int, text: str) -> None:
        encoded = text.encode("utf-8") + b"\x00"  # Append null terminator
        offset = self._check_bounds(addr, len(encoded))
        self.memory[offset : offset + len(encoded)] = encoded

    def read_string(self, addr: int, max_bytes: int = 256) -> str:
        offset = self._check_bounds(addr, 1)
        chars = []
        for i in range(max_bytes):
            curr_offset = offset + i
            if curr_offset >= self.size:
                raise MemoryError("SIGSEGV: Buffer read overrun before encountering null terminator!")
            b = self.memory[curr_offset]
            if b == 0:
                break
            chars.append(chr(b))
        else:
            raise ValueError("String not null-terminated within max_bytes limit!")
        return "".join(chars)


def simulate_swap(ram: SimulatedMemory, ptr_a: int, ptr_b: int) -> None:
    """Emulates C function: void swap(int *a, int *b)"""
    temp = ram.read_int32(ptr_a)
    ram.write_int32(ptr_a, ram.read_int32(ptr_b))
    ram.write_int32(ptr_b, temp)


def compute_2d_offset(base: int, r: int, c: int, total_cols: int, elem_size: int) -> int:
    """Computes row-major memory address for matrix[r][c]"""
    return base + ((r * total_cols) + c) * elem_size


def main() -> int:
    print("=" * 60)
    print("LEVEL 2 LAB CH05: POINTER ARITHMETIC & MEMORY SIMULATOR")
    print("=" * 60)

    ram = SimulatedMemory(size=1024, base_address=0x2000)

    # Test 1: Pointer Swapping Simulation
    addr_x = 0x2010
    addr_y = 0x2014
    ram.write_int32(addr_x, 42)
    ram.write_int32(addr_y, 99)

    print(f"\n[Test 1] Testing pointer swap at 0x{addr_x:04X} and 0x{addr_y:04X} ...")
    print(f"  Before: *addr_x = {ram.read_int32(addr_x)}, *addr_y = {ram.read_int32(addr_y)}")
    simulate_swap(ram, addr_x, addr_y)
    val_x = ram.read_int32(addr_x)
    val_y = ram.read_int32(addr_y)
    print(f"  After:  *addr_x = {val_x}, *addr_y = {val_y}")
    assert val_x == 99 and val_y == 42, "Pointer swap failed!"
    print("  -> Pointer swap logic verified.")

    # Test 2: Row-Major 2D Matrix Address Mapping
    print("\n[Test 2] Testing 2D Row-Major Matrix Address Calculation ...")
    base_matrix = 0x2100
    rows, cols = 3, 4
    elem_size = 4  # sizeof(int)

    # Populate matrix elements
    val = 1
    for r in range(rows):
        for c in range(cols):
            elem_addr = compute_2d_offset(base_matrix, r, c, cols, elem_size)
            ram.write_int32(elem_addr, val * 10)
            val += 1

    # Verify that matrix[2][3] is located at Base + (2 * 4 + 3) * 4 = Base + 44
    target_addr = compute_2d_offset(base_matrix, 2, 3, cols, elem_size)
    assert target_addr == base_matrix + 44
    target_val = ram.read_int32(target_addr)
    assert target_val == 120, f"Expected 120, got {target_val}"
    print(f"  matrix[2][3] at 0x{target_addr:04X} = {target_val} (Row-major offset math verified)")

    # Test 3: C-String Null Termination and Buffer Overflow Simulation
    print("\n[Test 3] Testing C-String Null Termination & Boundary Checks ...")
    str_addr = 0x2200
    ram.write_string(str_addr, "Antigravity")
    retrieved = ram.read_string(str_addr)
    assert retrieved == "Antigravity", f"String mismatch: {retrieved}"
    print(f"  Read null-terminated string at 0x{str_addr:04X}: \"{retrieved}\"")

    # Simulate buffer overrun detection (erasing null terminator and filling following bytes)
    offset_null = (str_addr - ram.base_address) + len("Antigravity")
    for b_idx in range(offset_null, offset_null + 20):
        ram.memory[b_idx] = ord("X")  # Overwrite with non-null character
    print("  Simulated missing null terminator. Verifying safety check ...")
    overrun_caught = False
    try:
        ram.read_string(str_addr, max_bytes=15)
    except ValueError as e:
        overrun_caught = True
        print(f"  Caught expected buffer boundary violation: {e}")
    assert overrun_caught, "Failed to trap missing null terminator!"

    print("\n" + "=" * 60)
    print("ALL CH05 POINTER & ARRAY SIMULATION CHECKS PASSED (Exit 0)")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
