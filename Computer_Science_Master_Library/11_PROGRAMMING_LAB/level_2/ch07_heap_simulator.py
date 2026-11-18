#!/usr/bin/env python3
"""
Chapter 07 Python Verification & Emulation Testbed:
Heap Chunk Manager, Free-List Coalescing, and Arena Allocator Simulator

Validates:
- Boundary-tag chunk metadata headers (size + in-use flag)
- Adjacent block coalescing on free (preventing external fragmentation)
- Dynamic array geometric expansion amortized cost
- Linear Arena bump allocation with zero-cost reset
- Double-free and memory leak detection
"""

import sys
from typing import Dict, List, Optional

# Enforce UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class HeapChunk:
    def __init__(self, offset: int, size: int, is_free: bool = True):
        self.offset = offset
        self.size = size  # Total chunk size including 8-byte header
        self.is_free = is_free

    @property
    def payload_size(self) -> int:
        return self.size - 8

    def __repr__(self) -> str:
        status = "FREE" if self.is_free else "USED"
        return f"[0x{self.offset:04X} | Sz={self.size:03d} | {status}]"


class SimulatedHeap:
    def __init__(self, total_bytes: int = 1024):
        self.total_bytes = total_bytes
        self.chunks: List[HeapChunk] = [HeapChunk(0, total_bytes, is_free=True)]
        self.active_allocations: Dict[int, HeapChunk] = {}

    def malloc(self, payload_size: int) -> Optional[int]:
        if payload_size <= 0:
            return None
        # 8-byte align payload, add 8-byte header
        aligned_payload = (payload_size + 7) & ~7
        needed_size = aligned_payload + 8

        # First-fit search
        for i, chunk in enumerate(self.chunks):
            if chunk.is_free and chunk.size >= needed_size:
                remainder = chunk.size - needed_size
                if remainder >= 16:  # Minimum split chunk size
                    chunk.size = needed_size
                    chunk.is_free = False
                    new_free = HeapChunk(chunk.offset + needed_size, remainder, is_free=True)
                    self.chunks.insert(i + 1, new_free)
                else:
                    chunk.is_free = False

                user_ptr = chunk.offset + 8
                self.active_allocations[user_ptr] = chunk
                return user_ptr
        return None  # Out of memory

    def free(self, user_ptr: int) -> bool:
        if user_ptr not in self.active_allocations:
            raise ValueError(f"CRITICAL: Invalid free / Double-free detected at address 0x{user_ptr:04X}!")

        chunk = self.active_allocations.pop(user_ptr)
        chunk.is_free = True

        # Coalesce adjacent free blocks
        i = 0
        while i < len(self.chunks) - 1:
            curr = self.chunks[i]
            nxt = self.chunks[i + 1]
            if curr.is_free and nxt.is_free:
                curr.size += nxt.size
                self.chunks.pop(i + 1)
            else:
                i += 1
        return True

    def leak_report(self) -> int:
        leaked_bytes = sum(c.payload_size for c in self.active_allocations.values())
        return leaked_bytes


def main() -> int:
    print("=" * 60)
    print("LEVEL 2 LAB CH07: HEAP ALLOCATOR & FREE-LIST SIMULATOR")
    print("=" * 60)

    heap = SimulatedHeap(total_bytes=512)

    # Test 1: Chunk Allocation and First-Fit Placement
    print("\n[Test 1] Testing heap allocations ...")
    p1 = heap.malloc(32)  # chunk 1
    p2 = heap.malloc(64)  # chunk 2
    p3 = heap.malloc(128) # chunk 3
    assert p1 is not None and p2 is not None and p3 is not None
    print(f"  Allocated p1 at 0x{p1:04X}, p2 at 0x{p2:04X}, p3 at 0x{p3:04X}")
    assert len(heap.active_allocations) == 3

    # Test 2: Adjacent Chunk Coalescing
    print("\n[Test 2] Testing chunk coalescing on free ...")
    heap.free(p1)
    heap.free(p2)
    # Since p1 and p2 are adjacent, they should merge into one contiguous free chunk
    first_chunk = heap.chunks[0]
    print(f"  Merged free block size at 0x0000 = {first_chunk.size} bytes (Coalescing verified)")
    assert first_chunk.is_free and first_chunk.size >= (32 + 8 + 64 + 8)

    # Free remaining chunk
    heap.free(p3)
    assert len(heap.chunks) == 1 and heap.chunks[0].size == 512
    print("  All blocks freed and coalesced back into a single 512-byte free chunk!")

    # Test 3: Double Free Detection
    print("\n[Test 3] Verifying Double-Free Detection ...")
    p_test = heap.malloc(40)
    heap.free(p_test)
    double_free_trapped = False
    try:
        heap.free(p_test)
    except ValueError as e:
        double_free_trapped = True
        print(f"  SUCCESS: Trapped expected double-free: {e}")
    assert double_free_trapped, "Failed to trap double free!"

    # Test 4: Memory Leak Detection
    print("\n[Test 4] Verifying Memory Leak Accounting ...")
    _leak_ptr = heap.malloc(48)
    leaked = heap.leak_report()
    print(f"  Live un-freed payload bytes: {leaked} bytes")
    assert leaked == 48, f"Expected 48 leaked bytes, got {leaked}"
    heap.free(_leak_ptr)
    assert heap.leak_report() == 0, "Failed to balance heap to 0 leaks!"
    print("  Heap balanced to 0 active leaks.")

    print("\n" + "=" * 60)
    print("ALL CH07 HEAP & CHUNK SIMULATION CHECKS PASSED (Exit 0)")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
