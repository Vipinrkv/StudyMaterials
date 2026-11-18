#!/usr/bin/env python3
"""
Chapter 06 Python Verification & Emulation Testbed:
Structure Padding, Member Alignment, and Union Type-Punning Simulator

Validates:
- Member offset formula: Off_i = ceil((Off_{i-1} + Size_{i-1}) / Align_i) * Align_i
- Total struct size calculation with tail padding
- Member reordering optimization (descending alignment)
- Union type-punning bit extraction (IEEE 754 float inspection)
"""

import math
import struct
import sys
from typing import List, Tuple

# Enforce UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class StructMember:
    def __init__(self, name: str, size: int, alignment: int):
        self.name = name
        self.size = size
        self.alignment = alignment


def calculate_struct_layout(members: List[StructMember]) -> Tuple[int, List[Tuple[str, int, int]]]:
    """Calculates member offsets, internal padding, and total size with tail padding."""
    current_offset = 0
    layout = []
    max_align = 1

    for m in members:
        max_align = max(max_align, m.alignment)
        # Align current offset to member's natural alignment
        aligned_offset = math.ceil(current_offset / m.alignment) * m.alignment
        padding = aligned_offset - current_offset
        layout.append((m.name, aligned_offset, padding))
        current_offset = aligned_offset + m.size

    # Tail padding to make total size a multiple of max_align
    total_size = math.ceil(current_offset / max_align) * max_align
    return total_size, layout


def main() -> int:
    print("=" * 60)
    print("LEVEL 2 LAB CH06: STRUCT PADDING & ALIGNMENT SIMULATOR")
    print("=" * 60)

    # Test 1: Unoptimized Struct Layout
    # struct Unoptimized { char c1; double d; char c2; int i; };
    unopt_members = [
        StructMember("c1", 1, 1),
        StructMember("d", 8, 8),
        StructMember("c2", 1, 1),
        StructMember("i", 4, 4),
    ]

    total_unopt, layout_unopt = calculate_struct_layout(unopt_members)
    print("\n[Test 1] Unoptimized Struct Analysis:")
    for name, offset, pad in layout_unopt:
        print(f"  Member '{name}': Offset = {offset:02d} (Preceding Padding = {pad} bytes)")
    print(f"  Total Unoptimized Footprint = {total_unopt} bytes")
    assert total_unopt == 24, f"Expected 24 bytes, got {total_unopt}"
    assert layout_unopt[1][1] == 8, "Member 'd' must be aligned to offset 8!"
    assert layout_unopt[3][1] == 20, "Member 'i' must be aligned to offset 20!"

    # Test 2: Optimized Struct Layout (Reordered by descending alignment)
    # struct Optimized { double d; int i; char c1; char c2; };
    opt_members = sorted(unopt_members, key=lambda m: m.alignment, reverse=True)
    total_opt, layout_opt = calculate_struct_layout(opt_members)
    print("\n[Test 2] Optimized Struct Analysis (Sorted by Alignment):")
    for name, offset, pad in layout_opt:
        print(f"  Member '{name}': Offset = {offset:02d} (Preceding Padding = {pad} bytes)")
    print(f"  Total Optimized Footprint = {total_opt} bytes")
    assert total_opt == 16, f"Expected 16 bytes, got {total_opt}"
    waste_saved = ((total_unopt - total_opt) / total_unopt) * 100
    print(f"  SUCCESS: Member reordering saved {waste_saved:.1f}% RAM footprint.")

    # Test 3: Union Type-Punning Emulation
    print("\n[Test 3] Union Type-Punning (Float to Raw Bit Pattern) ...")
    test_float = 3.1415927
    packed_bytes = struct.pack("<f", test_float)  # Little-endian 32-bit float
    raw_uint32 = struct.unpack("<I", packed_bytes)[0]
    print(f"  Float: {test_float}")
    print(f"  Hex Word: 0x{raw_uint32:08X}")
    print(f"  Bytes: {[f'0x{b:02X}' for b in packed_bytes]}")
    # Verify IEEE 754 bit-pattern for pi (~0x40490FDB)
    assert (raw_uint32 >> 24) == 0x40, "Invalid IEEE 754 exponent bits!"

    print("\n" + "=" * 60)
    print("ALL CH06 MEMORY ALIGNMENT CHECKS PASSED (Exit 0)")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
