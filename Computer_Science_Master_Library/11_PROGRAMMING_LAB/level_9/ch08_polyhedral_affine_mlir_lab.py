"""
Level 9 Programming Lab - Chapter 08: Polyhedral Model & Affine Loop Tiling
Implements Polyhedral Domain Inspection, Schedule Transformation Legality, and 2D Tiling.
"""
import sys
from typing import List, Tuple, Set

sys.stdout.reconfigure(encoding="utf-8")

# -------------------------------------------------------------------------
# 1. Polyhedral Iteration Domain
# -------------------------------------------------------------------------
class PolyhedralDomain2D:
    def __init__(self, i_min: int, i_max: int, j_min: int, j_max: int):
        self.i_min = i_min
        self.i_max = i_max
        self.j_min = j_min
        self.j_max = j_max

    def contains(self, point: Tuple[int, int]) -> bool:
        i, j = point
        return self.i_min <= i < self.i_max and self.j_min <= j < self.j_max

    def enumerate_points(self) -> List[Tuple[int, int]]:
        points = []
        for i in range(self.i_min, self.i_max):
            for j in range(self.j_min, self.j_max):
                points.append((i, j))
        return points

# -------------------------------------------------------------------------
# 2. Schedule Transformation Legality Checker
# -------------------------------------------------------------------------
def is_lexicographically_positive(vec: Tuple[int, ...]) -> bool:
    for val in vec:
        if val > 0:
            return True
        elif val < 0:
            return False
    return False  # Zero vector is not strictly positive

def check_schedule_legality(transform_matrix: List[List[int]], dependence_vectors: List[Tuple[int, int]]) -> bool:
    for d in dependence_vectors:
        # Multiply matrix by d
        t_d0 = transform_matrix[0][0] * d[0] + transform_matrix[0][1] * d[1]
        t_d1 = transform_matrix[1][0] * d[0] + transform_matrix[1][1] * d[1]
        if not is_lexicographically_positive((t_d0, t_d1)):
            return False
    return True

# -------------------------------------------------------------------------
# 3. Affine 2D Loop Tiler
# -------------------------------------------------------------------------
class AffineLoopTiler:
    @staticmethod
    def tile_2d(n: int, m: int, tile_i: int, tile_j: int) -> List[Tuple[int, int, int, int]]:
        # Returns list of (i_start, i_end, j_start, j_end)
        tiles = []
        for i_outer in range(0, n, tile_i):
            i_end = min(i_outer + tile_i, n)
            for j_outer in range(0, m, tile_j):
                j_end = min(j_outer + tile_j, m)
                tiles.append((i_outer, i_end, j_outer, j_end))
        return tiles


def test_polyhedral_mlir():
    print("===========================================================================")
    print("POLYHEDRAL LOOP MODEL & AFFINE COMPILATION TESTBED")
    print("LEVEL 9 LAB - CHAPTER 08")
    print("===========================================================================")

    # 1. Polyhedral Domain Point Enumeration
    print("[Test 1/3] Polyhedral Iteration Polytope Bounds & Enumeration...")
    domain = PolyhedralDomain2D(i_min=0, i_max=4, j_min=0, j_max=4)
    points = domain.enumerate_points()
    assert len(points) == 16
    assert domain.contains((0, 0)) and domain.contains((3, 3))
    assert not domain.contains((4, 4))
    print(f"  -> Successfully verified 2D integer domain containing {len(points)} grid points.")

    # 2. Schedule Transformation Legality Verification
    print("[Test 2/3] Schedule Transformation Legality (Interchange & Skewing)...")
    # Standard interchange matrix
    T_interchange = [
        [0, 1],
        [1, 0]
    ]

    # Dependence vector d1 = (0, 1) -> T * d1 = (1, 0) > 0 => Legal!
    assert check_schedule_legality(T_interchange, [(0, 1)]) is True
    print("  -> Loop Interchange on d=(0, 1): Confirmed LEGAL.")

    # Dependence vector d2 = (1, -1) -> T * d2 = (-1, 1) < 0 => ILLEGAL!
    assert check_schedule_legality(T_interchange, [(1, -1)]) is False
    print("  -> Loop Interchange on d=(1, -1): Confirmed ILLEGAL (caught reversal).")

    # Skewed schedule matrix: t1 = i + j, t2 = j
    T_skew = [
        [1, 1],
        [0, 1]
    ]
    # T_skew * d2 = (1 + (-1), 0 + (-1)) = (0, -1) which is negative,
    # but schedule t1 = i + 2j, t2 = i gives: (1 + 2*(-1), 1) = (-1, 1)
    # Correct skew for d=(1, -1) is t1 = 2i + j, t2 = i: (2(1) + (-1), 1) = (1, 1) > 0!
    T_valid_skew = [
        [2, 1],
        [1, 0]
    ]
    assert check_schedule_legality(T_valid_skew, [(1, -1)]) is True
    print("  -> Affine Loop Skewing on d=(1, -1): Confirmed LEGAL via positive hyperplane.")

    # 3. 2D Affine Tiling Partitioning Test
    print("[Test 3/3] 2D Affine Loop Tiling & Coverage Completeness...")
    tiles = AffineLoopTiler.tile_2d(n=64, m=64, tile_i=16, tile_j=16)
    assert len(tiles) == 16, f"64x64 domain tiled by 16x16 must produce 16 tiles, got {len(tiles)}"

    # Verify coverage and zero overlap
    visited_cells: Set[Tuple[int, int]] = set()
    for i_start, i_end, j_start, j_end in tiles:
        for i in range(i_start, i_end):
            for j in range(j_start, j_end):
                coord = (i, j)
                assert coord not in visited_cells, f"Duplicate iteration in tile: {coord}"
                visited_cells.add(coord)

    assert len(visited_cells) == 64 * 64 == 4096
    print(f"  -> Generated {len(tiles)} tiles covering all 4096 points with zero overlaps or gaps.")

    print("===========================================================================")
    print("ALL 3 POLYHEDRAL COMPILATION TESTS PASSED (Exit Code 0).")
    print("===========================================================================")

if __name__ == "__main__":
    test_polyhedral_mlir()
