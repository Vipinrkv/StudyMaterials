"""
ch03_gpu_simt_cuda_lab.py
Level 8 Chapter 03 Companion Laboratory: GPU Architecture & CUDA Programming.
Simulates GPU Warp Branch Divergence, DRAM Memory Coalescing Efficiency,
Shared Memory 32-Bank Interleaving Conflicts, and Logarithmic Tree Reduction.
Pure Python/Standard Library with zero external dependencies.
"""

from __future__ import annotations
import sys
import math
from typing import List, Tuple, Dict, Any

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")


class GpuMemorySubsystem:
    """Simulates GPU DRAM Memory Coalescing and Shared Memory Bank Interleaving."""

    @staticmethod
    def calculate_coalesced_transactions(addresses: List[int], cache_line_size: int = 128) -> int:
        assert len(addresses) == 32
        cache_lines = set()
        for addr in addresses:
            line_idx = addr // cache_line_size
            cache_lines.add(line_idx)
        return len(cache_lines)

    @staticmethod
    def calculate_bank_conflicts(shared_memory_addresses: List[int], num_banks: int = 32) -> Tuple[int, int]:
        assert len(shared_memory_addresses) == 32
        bank_counts = [0] * num_banks
        for addr in shared_memory_addresses:
            bank_id = (addr // 4) % num_banks
            bank_counts[bank_id] += 1

        max_conflict = max(bank_counts)
        serialized_passes = max_conflict
        return max_conflict, serialized_passes


class GpuWarpSimulator:
    """Simulates SIMT Warp Branch Divergence."""

    @staticmethod
    def execute_divergent_branch(predicates: List[bool], then_cycles: int, else_cycles: int) -> int:
        assert len(predicates) == 32
        has_true = any(predicates)
        has_false = any(not p for p in predicates)

        if has_true and has_false:
            return then_cycles + else_cycles
        elif has_true:
            return then_cycles
        else:
            return else_cycles


class CudaParallelReduction:
    """Simulates tree-based logarithmic parallel reduction inside GPU thread blocks."""

    @staticmethod
    def reduce_sum(data: List[float]) -> Tuple[float, List[int]]:
        n = len(data)
        assert (n & (n - 1)) == 0, "Reduction size must be power of two"
        current = list(data)
        active_counts = []

        stride = n // 2
        while stride > 0:
            active_counts.append(stride)
            for tid in range(stride):
                current[tid] += current[tid + stride]
            stride //= 2

        return current[0], active_counts


def main() -> None:
    print("=" * 70)
    print("LEVEL 8 CHAPTER 03: GPU ARCHITECTURE & CUDA PROGRAMMING LAB")
    print("=" * 70)

    # 1. Test Global Memory Coalescing
    print("\n[Test 1] Testing Global Memory DRAM Coalescing...")
    # Coalesced: consecutive 4-byte integers starting at 0
    coalesced_addrs = [tid * 4 for tid in range(32)]
    tx_coalesced = GpuMemorySubsystem.calculate_coalesced_transactions(coalesced_addrs, cache_line_size=128)
    assert tx_coalesced == 1, f"Expected 1 DRAM transaction for coalesced warp, got {tx_coalesced}"
    print(f"  -> Coalesced Access: 32 threads -> {tx_coalesced} DRAM Transaction (100% Efficiency).")

    # Uncoalesced / Strided: stride 128 (each thread lands in a distinct 128-byte line)
    strided_addrs = [tid * 128 for tid in range(32)]
    tx_strided = GpuMemorySubsystem.calculate_coalesced_transactions(strided_addrs, cache_line_size=128)
    assert tx_strided == 32, f"Expected 32 DRAM transactions for stride-128, got {tx_strided}"
    print(f"  -> Strided Access: 32 threads -> {tx_strided} DRAM Transactions (Severe Stall).")

    # 2. Test Shared Memory Bank Conflicts
    print("\n[Test 2] Testing Shared Memory 32-Bank Interleaving...")
    # Zero Conflict: consecutive 4-byte words map to banks 0..31
    smem_good = [tid * 4 for tid in range(32)]
    max_c_good, passes_good = GpuMemorySubsystem.calculate_bank_conflicts(smem_good)
    assert passes_good == 1, f"Expected 1 serialized pass, got {passes_good}"
    print(f"  -> Linear Stride-1: {passes_good} Pass (Zero Bank Conflicts).")

    # 32-Way Conflict: stride-32 (all threads hit Bank 0)
    smem_bad = [tid * 128 for tid in range(32)]  # 128 / 4 = 32 -> 32 % 32 = 0
    max_c_bad, passes_bad = GpuMemorySubsystem.calculate_bank_conflicts(smem_bad)
    assert passes_bad == 32, f"Expected 32-way conflict, got {passes_bad}"
    print(f"  -> Stride-32 Hazard: {passes_bad} Serialized Passes (32-Way Conflict).")

    # 3. Test Warp Branch Divergence
    print("\n[Test 3] Testing SIMT Warp Branch Divergence Penalty...")
    uniform_preds = [True] * 32
    cycles_uniform = GpuWarpSimulator.execute_divergent_branch(uniform_preds, then_cycles=10, else_cycles=15)
    assert cycles_uniform == 10

    divergent_preds = [tid % 2 == 0 for tid in range(32)]
    cycles_divergent = GpuWarpSimulator.execute_divergent_branch(divergent_preds, then_cycles=10, else_cycles=15)
    assert cycles_divergent == 25, f"Expected 25 cycles (10+15), got {cycles_divergent}"
    print(f"  -> Uniform Warp: {cycles_uniform} cycles; Divergent Warp: {cycles_divergent} cycles (Serialized).")

    # 4. Test Logarithmic Parallel Tree Reduction
    print("\n[Test 4] Testing Tree-Based Logarithmic Parallel Reduction...")
    input_data = [float(i + 1) for i in range(1024)]
    expected_sum = sum(input_data)  # 1024 * 1025 / 2 = 524800.0
    actual_sum, steps = CudaParallelReduction.reduce_sum(input_data)
    assert math.isclose(actual_sum, expected_sum, rel_tol=1e-5), f"Expected {expected_sum}, got {actual_sum}"
    assert len(steps) == 10, f"Expected 10 reduction steps for 1024 items, got {len(steps)}"
    print(f"  -> 1024-Element Reduction: {actual_sum} (Computed in {len(steps)} parallel steps: {steps[:3]}...{steps[-1]}).")

    print("\n" + "=" * 70)
    print("ALL GPU & CUDA ARCHITECTURE TESTS PASSED (Exit Code 0).")
    print("=" * 70)
    sys.exit(0)


if __name__ == "__main__":
    main()
