"""
Practical Lab 1.3: Cache Locality and Memory Access Latency Demonstration
File: 11_PROGRAMMING_LAB/level_1/cache_locality.py
Author: Computer Science Master Library
Description: Proves the physical reality of CPU cache lines by measuring
             execution times between row-major (cache friendly) and
             column-major (cache hostile) 2D array traversals.
"""

import time
import sys


def run_cache_locality_benchmark(rows: int = 2000, cols: int = 2000) -> None:
    print("=" * 65)
    print("      CPU CACHE LOCALITY & MEMORY ACCESS BENCHMARK")
    print("=" * 65)
    print(f"Allocating 2D Matrix of size {rows} x {cols} ({rows * cols:,} integers)...")

    # Allocate a contiguous flat 2D grid
    # In row-major memory, matrix[r][c] sits next to matrix[r][c+1]
    matrix = [[1 for _ in range(cols)] for _ in range(rows)]
    print(
        f"Memory allocated successfully (~{round(sys.getsizeof(matrix) / 1024, 2)} KB array headers).\n"
    )

    # -------------------------------------------------------------
    # TEST 1: Row-Major Traversal (Cache-Friendly: Spatial Locality)
    # -------------------------------------------------------------
    print("Test 1: Running Row-Major Traversal (Row by Row)...")
    start_time = time.perf_counter()
    sum_row = 0
    for r in range(rows):
        for c in range(cols):
            sum_row += matrix[r][c]
    end_time = time.perf_counter()
    row_time = end_time - start_time
    print(f"-> Row-Major Execution Time : {row_time:.4f} seconds (Sum = {sum_row:,})")

    # -------------------------------------------------------------
    # TEST 2: Column-Major Traversal (Cache-Hostile: Strided Access)
    # -------------------------------------------------------------
    print("\nTest 2: Running Column-Major Traversal (Column by Column)...")
    start_time = time.perf_counter()
    sum_col = 0
    for c in range(cols):
        for r in range(rows):
            sum_col += matrix[r][c]
    end_time = time.perf_counter()
    col_time = end_time - start_time
    print(f"-> Column-Major Execution Time: {col_time:.4f} seconds (Sum = {sum_col:,})")

    # Analysis
    slowdown_ratio = col_time / row_time if row_time > 0 else 1.0
    print("-" * 65)
    print(f"ANALYSIS: Column-major traversal was {slowdown_ratio:.2f}x SLOWER!")
    print("REASON  : Column-by-column traversal forces CPU cache misses on")
    print("          almost every access, proving the physical memory hierarchy!")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    run_cache_locality_benchmark(rows=1500, cols=1500)
