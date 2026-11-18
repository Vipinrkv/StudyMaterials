# CHAPTER 03: HIGH-PERFORMANCE COMPUTING, GPU ARCHITECTURE, AND CUDA PROGRAMMING

---

## 1. ACADEMIC & REAL-WORLD CONTEXT

Over the past two decades, high-performance computing (HPC) has undergone a tectonic paradigm shift from latency-optimized homogeneous CPU clusters to throughput-optimized massively parallel heterogeneous GPU accelerators. In modern deep learning training clusters (NVIDIA H100/B200 clusters), scientific simulations (molecular dynamics, climate modeling), and cryptographic zero-knowledge proof generation, GPUs provide orders of magnitude higher compute density and memory bandwidth than general-purpose CPUs.

Where a modern CPU allocates extensive silicon real estate to branch predictors, deep out-of-order execution pipelines, and multi-megabyte L3 caches to minimize single-threaded instruction latency, a modern GPU dedicates the vast majority of its transistor budget to thousands of arithmetic logic units (ALUs) and hardware thread schedulers designed to hide latency through massive concurrent SIMT (Single Instruction, Multiple Threads) execution.

This chapter dissects the silicon microarchitecture of modern GPUs and the formal programming model of **CUDA** (Compute Unified Device Architecture). We examine Streaming Multiprocessors (SMs), warp scheduling, shared memory bank conflicts, memory coalescing, parallel reduction trees, Blelloch prefix scans, and tiled matrix multiplication (GEMM).

---

## 2. PEDAGOGICAL ROADMAP

```
                         GPU Silicon Microarchitecture
                                       │
        ┌──────────────────────────────┴──────────────────────────────┐
        ▼                                                             ▼
Host CPU vs Device GPU                                       Streaming Multiprocessors (SMs)
(PCIe/NVLink Bus, Pinned Host Memory)                        (Warp Schedulers, Register Files, Tensor Cores)
        │                                                             │
        ▼                                                             ▼
SIMD vs SIMT Execution Model                                 CUDA Execution Hierarchy
(Lock-Step Vector vs Independent Threads)                    (Grid -> Thread Block -> Warp -> Thread)
        │                                                             │
        └──────────────────────────────┬──────────────────────────────┘
                                       │
                                       ▼
                          GPU Memory Hierarchy & Physics
                                       │
        ┌──────────────────────────────┴──────────────────────────────┐
        ▼                                                             ▼
Global Memory & Coalescing                                    Shared Memory & Bank Conflicts
(128-byte DRAM Transactions, Cache Lines)                    (32 Banks, Modulo Indexing, Padded Strides)
        │                                                             │
        └──────────────────────────────┬──────────────────────────────┘
                                       │
                                       ▼
                         High-Throughput Parallel Primitives
                                       │
                 ┌─────────────────────┴─────────────────────┐
                 ▼                                           ▼
         Tree-Based Parallel Reduction               Tiled Matrix Multiplication (GEMM)
     (Warp Shuffle Intrinsics, O(log N))            (SRAM Shared Memory Tile Caching, O(N^3/B))
```

---

## 3. CORE PRINCIPLES & FORMAL DEFINITIONS

### 3.1 The CUDA Execution Hierarchy

CUDA structures computation hierarchically to map across physical silicon:
1. **Thread:** The basic scalar unit of execution, executing a kernel instance with its own private registers.
2. **Warp:** A hardware unit of exactly **32 threads** that execute instructions in lock-step on an SM.
3. **Thread Block:** A group of up to 1,024 threads scheduled onto a single SM, sharing fast on-chip **Shared Memory (SRAM)** and hardware barriers (`__syncthreads()`).
4. **Grid:** A collection of thread blocks executing the same kernel across all SMs in the GPU device.

A global thread index in a 1D grid is computed as:
$$\text{GlobalThreadID} = \text{blockIdx.x} \times \text{blockDim.x} + \text{threadIdx.x}$$

### 3.2 Warp Divergence

When threads within the same 32-thread warp evaluate diverging branches of a conditional statement (`if (cond)`):
$$\text{Execution Time} = T_{\text{then}} + T_{\text{else}}$$
The hardware serializes execution: threads for which the condition is false are masked off while the `then` branch executes, and vice versa. Warp divergence degrades compute efficiency by up to $32\times$.

### 3.3 Memory Coalescing & Bank Conflicts

- **Global Memory Coalescing:** When all 32 threads in a warp access consecutive 4-byte or 8-byte words aligned to a 128-byte cache-line boundary, the hardware services the access in a **single DRAM transaction**. If memory accesses are strided or random, the memory controller must issue up to 32 separate transactions, slashing effective bandwidth by $96\%$.
- **Shared Memory Bank Conflicts:** Shared memory is organized into **32 independent banks** of 4-byte width:
  $$\text{BankID} = \left(\frac{\text{ByteAddress}}{4}\right) \pmod{32}$$
  If two or more threads in a warp access distinct addresses in the same bank, a **bank conflict** occurs, and the hardware serializes the memory requests.

---

## 4. MATHEMATICAL FOUNDATIONS & PROOFS

### 4.1 Tiled Matrix Multiplication (GEMM) Arithmetic Intensity

Consider multiplying two $N \times N$ matrices: $C = A \times B$.
- **Naive Algorithm:** Each element $C_{i,j} = \sum_{k=1}^N A_{i,k} B_{k,j}$ performs $2N$ FLOPs and reads $2N$ floats from high-latency global DRAM. Total DRAM reads: $2N^3$ floats. Arithmetic intensity:
  $$I_{\text{naive}} = \frac{2N^3 \text{ FLOPs}}{2N^3 \times 4 \text{ bytes}} = 0.25 \text{ FLOP/byte}$$
  The operation is severely **memory bandwidth-bound**.

- **Tiled Algorithm with Shared Memory:** Divide matrices into square tiles of size $B \times B$ that fit into high-speed on-chip shared memory ($B \approx 16 \text{ or } 32$).

**Theorem (Arithmetic Intensity of Tiled GEMM):** Tiling an $N \times N$ matrix multiplication with tile size $B$ reduces global DRAM access by a factor of $B$, increasing arithmetic intensity to $\frac{B}{4}$ FLOPs/byte.

*Proof:*
Each block loads a tile of $A$ ($B^2$ floats) and a tile of $B$ ($B^2$ floats) into shared memory once. The block then computes all inner products across the tile, performing $2B^3$ FLOPs using the cached on-chip data.
$$\text{Global Memory Reads per Tile Pass} = 2B^2 \times 4 \text{ bytes}$$
$$\text{Arithmetic Intensity } I_{\text{tiled}} = \frac{2B^3 \text{ FLOPs}}{8B^2 \text{ bytes}} = \frac{B}{4} \text{ FLOP/byte}$$
For tile size $B = 32$, $I_{\text{tiled}} = 8.0 \text{ FLOP/byte}$, a **$32\times$ reduction in DRAM traffic**. $\blacksquare$

---

## 5. ARCHITECTURAL PATTERNS & ENGINE DESIGNS

```
+─────────────────────────────────────────────────────────────────────────────+
|                    CUDA STREAMING MULTIPROCESSOR (SM)                       |
|                                                                             |
|   +───────────────────────────────────────────────────────────────────────+ |
|   |                  Instruction Cache & Warp Schedulers                  | |
|   |  - Warp Scheduler 0   - Warp Scheduler 1  - Warp Scheduler 2, 3       | |
|   +───────────────────────────────────┬───────────────────────────────────+ |
|                                       │ Dispatch Instructions               |
|                                       ▼                                     |
|   +───────────────────────────────────────────────────────────────────────+ |
|   |                 Massive Register File (64K x 32-bit)                  | |
|   +───────────────────────────────────┬───────────────────────────────────+ |
|                                       │ Fast Register Operands              |
|        ┌──────────────────────────────┼──────────────────────────────┐      |
|        ▼                              ▼                              ▼      |
|   +──────────+                   +──────────+                  +──────────+ |
|   | FP32 /   |                   | FP64 /   |                  | Tensor   | |
|   | INT32    |                   | Special  |                  | Cores    | |
|   | ALUs (64)|                   | Units    |                  | (MMA)    | |
|   +──────────+                   +──────────+                  +──────────+ |
|        │                              │                              │      |
|        └──────────────────────────────┼──────────────────────────────┘      |
|                                       ▼                                     |
|   +───────────────────────────────────────────────────────────────────────+ |
|   |          Configurable Shared Memory (SRAM) / L1 Cache (128 KB)        | |
|   |          - 32 Independent Banks (4-byte interleaved)                  | |
|   +───────────────────────────────────┬───────────────────────────────────+ |
|                                       │ Cache Misses                        |
|                                       ▼                                     |
|   +───────────────────────────────────────────────────────────────────────+ |
|   |            High-Bandwidth HBM3 / GDDR6 Global DRAM (80+ GB)           | |
|   +───────────────────────────────────────────────────────────────────────+ |
+─────────────────────────────────────────────────────────────────────────────+
```

---

## 6. COMPARATIVE ANALYSIS: PARALLEL COMPUTING ACCELERATORS

| Dimension | Modern Server CPU (e.g. AMD EPYC) | GPU (NVIDIA H100) | Google TPU v5p | FPGA (Xilinx Alveo) |
| :--- | :--- | :--- | :--- | :--- |
| **Architecture** | Latency-optimized MIMD | Throughput-optimized SIMT | Systolic Matrix Array (ASIC) | Reconfigurable Logic Cells |
| **Peak FP32 / BF16** | ~4 TFLOPs FP32 | ~1,000 TFLOPs BF16 | ~459 TFLOPs BF16 | ~15 TFLOPs FP32 |
| **Memory Bandwidth** | ~400 GB/s (DDR5) | ~3,350 GB/s (HBM3) | ~4,800 GB/s (HBM3) | ~460 GB/s (HBM2) |
| **Programming Language** | C++, OpenMP, MPI | CUDA, Triton, OpenCL | XLA, JAX, PyTorch | VHDL, Verilog, OpenCL |
| **Optimal Workload** | Irregular control flow, graph search | Dense linear algebra, deep learning | Transformer matrix multiplication | Bit-level packet processing |

---

## 7. INDUSTRIAL CASE STUDIES & POST-MORTEMS

### Case Study: FlashAttention (Dao et al., 2022)
Standard Transformer attention computes $S = Q K^T$ and $P = \text{softmax}(S)$, materializing an $N \times N$ attention matrix in GPU DRAM. For context length $N = 16,384$, reading and writing $O(N^2)$ floats from HBM saturates memory bandwidth, resulting in slow generation. 
Dao et al. introduced **FlashAttention**, which tiles the attention computation into the SM's fast on-chip SRAM using online softmax renormalization, never writing the intermediate $N \times N$ matrix to DRAM. This kernel-level CUDA engineering achieved a $3\times$ speedup across global LLM workloads with exact mathematical equivalence.

---

## 8. COMPLETE, PRODUCTION-READY IMPLEMENTATION

Below is a complete, self-contained Python laboratory simulation (`cuda_gpu_simulator.py`) modeling GPU SIMT execution, warp divergence penalties, global memory coalescing efficiency, shared memory bank conflict serialization, and tree-based parallel reduction.

```python
"""
cuda_gpu_simulator.py
GPU Architecture, SIMT Thread Hierarchy & Memory Subsystem Simulator.
Emulates Warp Scheduling, Divergence Penalty, Global Memory Coalescing,
Shared Memory 32-Bank Interleaving, and Tree-Based Parallel Reduction.
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
        """
        Determines the number of 128-byte DRAM cache-line transactions
        required to satisfy a warp's memory requests (32 threads).
        """
        assert len(addresses) == 32
        cache_lines = set()
        for addr in addresses:
            line_idx = addr // cache_line_size
            cache_lines.add(line_idx)
        return len(cache_lines)

    @staticmethod
    def calculate_bank_conflicts(shared_memory_addresses: List[int], num_banks: int = 32) -> Tuple[int, int]:
        """
        Simulates 32-bank shared memory interleaved access (4 bytes per bank).
        Returns (max_conflicts_per_bank, total_serialized_passes).
        """
        assert len(shared_memory_addresses) == 32
        bank_counts = [0] * num_banks
        for addr in shared_memory_addresses:
            bank_id = (addr // 4) % num_banks
            bank_counts[bank_id] += 1

        max_conflict = max(bank_counts)
        # 1 means all threads hit distinct banks (0 conflicts); >1 means serialization
        serialized_passes = max_conflict
        return max_conflict, serialized_passes


class GpuWarpSimulator:
    """Simulates SIMT Warp Branch Divergence."""

    @staticmethod
    def execute_divergent_branch(predicates: List[bool], then_cycles: int, else_cycles: int) -> int:
        """
        Simulates execution of conditional branch if (pred) then ... else ...
        If warp threads evaluate both True and False, hardware serializes both branches.
        """
        assert len(predicates) == 32
        has_true = any(predicates)
        has_false = any(not p for p in predicates)

        if has_true and has_false:
            # Warp Divergence! Both paths execute sequentially with masked threads
            return then_cycles + else_cycles
        elif has_true:
            return then_cycles
        else:
            return else_cycles


class CudaParallelReduction:
    """
    Simulates tree-based logarithmic parallel reduction inside GPU thread blocks.
    Replaces sequential O(N) accumulation with O(log2 N) parallel steps.
    """
    @staticmethod
    def reduce_sum(data: List[float]) -> Tuple[float, List[int]]:
        """
        Simulates shared memory tree reduction.
        Returns (final_sum, active_threads_per_step).
        """
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
```

---

## 9. STEP-BY-STEP GUIDED LAB WALKTHROUGH

1. **Global Memory Coalescing Verification:** Formulate aligned consecutive accesses ($4 \times \text{tid}$) and observe 1 single 128-byte DRAM transaction. Contrast with strided accesses requiring 32 transactions.
2. **Shared Memory Bank Conflict Analysis:** Test consecutive address access (0 conflicts, 1 pass) vs stride-32 access where all 32 threads collide on Bank 0 (32-way conflict, 32 serialized passes).
3. **Warp Divergence Analysis:** Measure execution cycle cost when thread IDs evaluate uneven branch conditions (`tid % 2 == 0`).
4. **Logarithmic Tree Reduction:** Trace power-of-two parallel reduction steps from $N = 1024$ down to 1 in $\log_2(1024) = 10$ parallel steps.

---

## 10. COMPREHENSIVE BENCHMARKS & COMPLEXITY ANALYSIS

| Kernel / Memory Pattern | DRAM Transactions per Warp | Shared Memory Serialized Passes | Effective Bandwidth Utilization |
| :--- | :--- | :--- | :--- |
| **Aligned Coalesced Read** | **1 transaction** | N/A | **100% (3,350 GB/s on H100)** |
| **Strided Read (Stride 32)**| 32 transactions | N/A | **3.1% (Catastrophic stall)** |
| **Bank-Conflict-Free Shared** | N/A | **1 pass** | **100% on-chip SRAM speed** |
| **32-Way Shared Bank Conflict**| N/A | **32 serialized passes** | **3.1% (Severe serialization)** |

---

## 11. EXTREME EDGE CASES & FAILURE MODES

- **Warp Divergence in Loops:** Divergence within nested loops forces threads with completed loop bounds to stall until the thread with the maximum iteration count finishes.
- **Register Spilling to Local Memory:** If a CUDA kernel uses more registers than the SM's physical per-thread budget, excess registers spill to high-latency "local memory" (backed by DRAM), causing performance degradation.
- **Race Conditions in Shared Memory:** Failing to insert `__syncthreads()` between shared memory write and read passes causes non-deterministic data hazards across warps.

---

## 12. DEBUGGING, PROFILING & TRACE ANALYSIS

- **NVIDIA Nsight Compute (NCU):** Profiler for kernel-level instruction throughput, warp occupancy, register spills, and memory pipeline stalls.
- **NVIDIA Nsight Systems (NSYS):** System-wide timeline visualization tracing CPU-GPU kernel launches, PCIe data transfers, and CUDA stream concurrency.
- **Compute Sanitizer:** Dynamic memory error detector catching out-of-bounds accesses and shared memory data hazards at runtime.

---

## 13. REAL-WORLD PRODUCTION DRILLS & RUNBOOKS

- **Runbook — Diagnosing Low GPU Tensor Core Utilization:**
  1. Inspect warp execution state in NCU: check for warp stall reasons (`stall_memory_throttle` vs `stall_sync`).
  2. Verify thread block dimensions: ensure block sizes are multiples of 32 (e.g., 128, 256) to prevent underfilled warps.
  3. Ensure matrix dimensions align to multiples of 8 or 16 for Tensor Core MMA (Matrix Multiply-Accumulate) instructions.

---

## 14. COMPREHENSIVE CURRICULUM & DEGREE MAPPINGS

- **B.Tech / BCS:** Parallel computing concepts, multi-core vs many-core, SIMD vectorization.
- **MCS / MCA:** CUDA thread hierarchy, grid/block layouts, global vs shared memory, basic parallel algorithms.
- **M.Tech / MESE:** GPU microarchitecture, warp scheduling, memory coalescing theory, tiled GEMM, Tensor Core programming, Triton compiler.

---

## 15. INTERVIEW MASTERY: 10 ARCHITECTURAL & GPU PROBLEMS

1. **Question:** What is a warp in CUDA, and why does it consist of 32 threads?
   - *Answer:* A warp is the fundamental hardware scheduling unit of a GPU SM. It consists of 32 threads that execute the same instruction simultaneously in SIMT fashion, balancing hardware instruction dispatch overhead with instruction-level and thread-level parallelism.
2. **Question:** What is global memory coalescing?
   - *Answer:* Global memory coalescing occurs when threads within a warp access contiguous memory locations that fall within a single 128-byte cache line. The GPU memory controller consolidates these 32 individual memory accesses into a single physical DRAM transaction.
3. **Question:** What causes a shared memory bank conflict?
   - *Answer:* Shared memory is divided into 32 equal-sized banks. A bank conflict occurs when two or more threads in the same warp request different memory addresses that map to the same memory bank. The hardware must serialize the conflicting accesses.
4. **Question:** What is the difference between SIMD and SIMT?
   - *Answer:* In SIMD (Single Instruction, Multiple Data), vector registers execute lock-step operations across wide vector lanes exposed explicitly in software. In SIMT (Single Instruction, Multiple Threads), individual threads write scalar instructions with private register state, and the hardware warp scheduler dynamically manages vector execution and branch masking.
5. **Question:** How does tiled matrix multiplication achieve higher performance than naive matrix multiplication?
   - *Answer:* Tiling caches blocks of matrices $A$ and $B$ into fast, on-chip shared memory, allowing the data to be reused across $B$ multiply-accumulate operations, reducing high-latency global DRAM access by a factor of $B$.
6. **Question:** What does `__syncthreads()` do in CUDA?
   - *Answer:* It acts as a block-wide hardware execution and memory barrier. All threads in the thread block must reach this point before any thread is allowed to proceed, guaranteeing that shared memory writes prior to the barrier are visible to all threads.
7. **Question:** What is warp shuffle (`__shfl_sync`), and why is it faster than shared memory?
   - *Answer:* Warp shuffle intrinsics allow threads within the same warp to directly exchange register values without reading or writing through shared memory, eliminating SRAM latency, shared memory allocation, and bank conflict risks.
8. **Question:** Why should thread block sizes always be a multiple of 32?
   - *Answer:* Because the hardware schedules work in 32-thread warps. A block size that is not a multiple of 32 leaves unused threads in the final warp masked off, wasting SM execution resources.
9. **Question:** What is the Roofline Model in GPU computing?
   - *Answer:* A visual performance model plotting attainable performance (TFLOPs) against arithmetic intensity (FLOP/byte). It defines two distinct operational regimes: memory bandwidth-bound (steep diagonal slope) and compute-bound (horizontal peak ceiling).
10. **Question:** What is asynchronous memory copy in modern CUDA (`cudaMemcpyAsync`)?
    - *Answer:* It initiates non-blocking direct memory access (DMA) transfers between host pinned memory and device global memory via dedicated copy engines, allowing data transfer to overlap concurrently with GPU kernel execution.

---

## 16. EXAMINATIONS & KNOWLEDGE RETENTION DRILLS

### Multiple Choice Questions
1. In modern NVIDIA GPUs, shared memory consists of how many independent banks?
   - (A) 8
   - (B) 16
   - (C) 32
   - (D) 64
   - *Answer:* (C)
2. If all 32 threads in a warp access consecutive 4-byte integers starting at an aligned 128-byte boundary, the number of DRAM transactions required is:
   - (A) 1
   - (B) 4
   - (C) 16
   - (D) 32
   - *Answer:* (A)

---

## 17. SECURITY, RESILIENCE & COMPLIANCE

Multi-tenant GPU clusters in cloud platforms (e.g., Kubernetes running MIG—Multi-Instance GPU) require hardware-level memory isolation. Failing to clear GPU VRAM between tenant workloads can leak proprietary model weights and training data across tenant boundaries.

---

## 18. EXPERT ANTI-PATTERNS & PITFALL CATALOGUE

1. **Anti-Pattern: Excessive Register Usage Leading to Low Occupancy**
   - *Error:* Declaring too many local variables inside a CUDA kernel, consuming $>64$ registers per thread.
   - *Impact:* The SM cannot schedule enough concurrent warps to hide memory latency, collapsing occupancy.
2. **Anti-Pattern: Stride-32 Shared Memory Access**
   - *Error:* Indexing shared memory with `s_data[tid * 32]`.
   - *Impact:* Every thread in the warp maps to Bank 0, causing a catastrophic 32-way bank conflict.

---

## 19. STANDARDS, RFCs & SYSTEM SPECIFICATIONS

- **NVIDIA Corporation (2024):** *CUDA C++ Programming Guide*, Version 12.x.
- **Dao, Tri et al. (2022):** *FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness*, NeurIPS.
- **Williams, Samuel et al. (2009):** *Roofline: An Insightful Visual Performance Model for Multicore Architectures*, CACM.

---

## 20. HISTORICAL PERSPECTIVE & DISCOVERIES

In 2006, NVIDIA launched CUDA alongside the G80 architecture (GeForce 8800 GTX), decoupling GPU computing from graphics shading languages (OpenGL/DirectX) and introducing general-purpose compute to mainstream silicon. In 2012, Alex Krizhevsky trained AlexNet on two NVIDIA GTX 580 GPUs, igniting the modern deep learning revolution.

---

## 21. CODE REFACTORING & PRODUCTION HARDENING

When hardening CUDA kernels:
- Replace shared memory reductions with **warp shuffle intrinsics** (`__shfl_down_sync`) to eliminate SRAM bank conflicts.
- Use **C++ templates** to unroll loops with compile-time constants, enabling compiler dead-code elimination and register reuse.

---

## 22. REAL-WORLD TOOLING & ECOSYSTEM DIRECTORY

- **PyTorch & Triton:** Modern high-level tensor programming compiling down to optimized GPU kernels.
- **CUTLASS:** NVIDIA C++ template library for high-performance matrix multiplication at tensor core scale.
- **cuBLAS & cuDNN:** Highly tuned primitives for linear algebra and deep neural networks.

---

## 23. COMPREHENSIVE GLOSSARY OF FORMAL TERMS

- **Arithmetic Intensity:** The ratio of floating-point operations performed to bytes transferred from DRAM (FLOPs/byte).
- **Occupancy:** The ratio of active warps on an SM to the maximum theoretical warps supported by the hardware.
- **Streaming Multiprocessor (SM):** The core compute module of an NVIDIA GPU containing ALUs, register files, and warp schedulers.
- **Warp:** A group of 32 threads executed concurrently by an SM in SIMT fashion.

---

## 24. ADVANCED CAPSTONE & RESEARCH PROJECTS

1. **High-Performance 2D Tiled GEMM Kernel in Triton:** Implement a tiled matrix multiplication kernel in OpenAI Triton with double buffering, achieving $>85\%$ of cuBLAS peak TFLOPs on NVIDIA GPUs.
2. **GPU Parallel Blelloch Prefix Scan Engine:** Author an efficient all-prefix-sums (Scan) CUDA kernel with work-efficient $O(N)$ arithmetic and zero bank conflicts, benchmarking against Thrust.
