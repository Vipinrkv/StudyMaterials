"""
ch06_vllm_paged_serving_lab.py
Level 7 Companion Lab: PagedAttention KV Cache & Continuous Batching Engine.
Pure Python/Standard Library implementation with zero external dependencies.
"""

from __future__ import annotations
import sys
import math
import random
from typing import Dict, List, Optional, Tuple

# Windows UTF-8 console output
sys.stdout.reconfigure(encoding="utf-8")


class LabPhysicalBlock:
    """Fixed-size memory block in GPU HBM."""
    def __init__(self, block_id: int, block_size: int = 4):
        self.block_id = block_id
        self.block_size = block_size
        self.tokens: List[int] = []
        self.ref_count = 0

    def is_full(self) -> bool:
        return len(self.tokens) >= self.block_size

    def append(self, token: int) -> None:
        self.tokens.append(token)


class LabBlockAllocator:
    """Global allocator for physical KV cache memory blocks."""
    def __init__(self, total_blocks: int, block_size: int = 4):
        self.block_size = block_size
        self.blocks = [LabPhysicalBlock(i, block_size) for i in range(total_blocks)]
        self.free_pool = list(range(total_blocks))

    def allocate(self) -> LabPhysicalBlock:
        if not self.free_pool:
            raise MemoryError("GPU HBM Out of KV Cache Blocks!")
        b_id = self.free_pool.pop()
        b = self.blocks[b_id]
        b.ref_count = 1
        b.tokens.clear()
        return b

    def free(self, block_id: int) -> None:
        b = self.blocks[block_id]
        b.ref_count -= 1
        if b.ref_count <= 0:
            b.ref_count = 0
            b.tokens.clear()
            self.free_pool.append(block_id)

    def num_free(self) -> int:
        return len(self.free_pool)


class LabSequence:
    """Client autoregressive generation request."""
    def __init__(self, seq_id: str, prompt_len: int, max_tokens: int):
        self.seq_id = seq_id
        self.prompt_len = prompt_len
        self.max_tokens = max_tokens
        self.gen_count = 0
        self.block_table: List[int] = []  # Logical to physical block mapping

    def total_tokens(self) -> int:
        return self.prompt_len + self.gen_count


def test_paged_memory_allocation():
    print("Running Test Suite 1: PagedAttention Block Allocation & Freeing...")
    allocator = LabBlockAllocator(total_blocks=10, block_size=4)
    assert allocator.num_free() == 10

    # Allocate 3 blocks
    b1 = allocator.allocate()
    b2 = allocator.allocate()
    b3 = allocator.allocate()
    assert allocator.num_free() == 7

    # Free b2
    allocator.free(b2.block_id)
    assert allocator.num_free() == 8

    # Free remaining
    allocator.free(b1.block_id)
    allocator.free(b3.block_id)
    assert allocator.num_free() == 10
    print("  Passed! Physical blocks correctly allocated, tracked, and recycled.")


def test_continuous_batching_scheduling():
    print("Running Test Suite 2: Continuous Iteration-Level Batch Scheduling...")
    allocator = LabBlockAllocator(total_blocks=20, block_size=4)

    # Request A: prompt 4, generate 2
    # Request B: prompt 2, generate 1
    seqA = LabSequence("A", prompt_len=4, max_tokens=2)
    seqB = LabSequence("B", prompt_len=2, max_tokens=1)

    # Initial allocation
    for _ in range(math.ceil(seqA.total_tokens() / 4)):
        seqA.block_table.append(allocator.allocate().block_id)
    for _ in range(math.ceil(seqB.total_tokens() / 4)):
        seqB.block_table.append(allocator.allocate().block_id)

    active = [seqA, seqB]
    iteration = 0
    finished = []

    while active:
        iteration += 1
        surviving = []
        for s in active:
            s.gen_count += 1
            if s.gen_count >= s.max_tokens:
                finished.append(s.seq_id)
                # Free memory immediately on completion!
                for b_id in s.block_table:
                    allocator.free(b_id)
            else:
                surviving.append(s)
        active = surviving

    # Seq B should have finished at iteration 1, Seq A at iteration 2
    assert finished == ["B", "A"]
    assert allocator.num_free() == 20  # All memory returned
    print("  Passed! Sequences evicted dynamically upon completion with zero padding bubbles.")


def test_speculative_decoding_acceptance():
    print("Running Test Suite 3: Speculative Decoding Rejection Sampling...")
    # Draft proposed 3 tokens with probabilities q
    # Target evaluated probabilities p
    draft_tokens = [101, 102, 103]
    draft_probs = [0.9, 0.8, 0.7]

    # Case 1: Target agrees with high confidence (p >= q) -> All accepted!
    target_probs_agree = [0.95, 0.85, 0.75]
    accepted_1 = []
    for t, q, p in zip(draft_tokens, draft_probs, target_probs_agree):
        alpha = min(1.0, p / q)
        if alpha >= 1.0:
            accepted_1.append(t)
    assert len(accepted_1) == 3

    # Case 2: Target rejects token 2 (p2 << q2)
    target_probs_reject = [0.95, 0.05, 0.75]
    accepted_2 = []
    for t, q, p in zip(draft_tokens, draft_probs, target_probs_reject):
        alpha = min(1.0, p / q)
        if alpha >= 0.5:  # Deterministic test threshold
            accepted_2.append(t)
        else:
            break  # Truncate on rejection!
    assert len(accepted_2) == 1
    assert accepted_2 == [101]
    print("  Passed! Speculative draft verification accepted high-prob tokens and truncated on rejection.")


if __name__ == "__main__":
    print("================================================================================")
    print("LEVEL 7 LAB 06: VLLM PAGEDATTENTION & CONTINUOUS SERVING ENGINE")
    print("================================================================================")
    test_paged_memory_allocation()
    test_continuous_batching_scheduling()
    test_speculative_decoding_acceptance()
    print("================================================================================")
    print("ALL 3 TEST SUITES PASSED CLEANLY (EXIT CODE 0)")
    print("================================================================================")
