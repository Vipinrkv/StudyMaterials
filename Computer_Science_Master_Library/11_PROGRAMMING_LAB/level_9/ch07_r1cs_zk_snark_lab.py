"""
Level 9 Programming Lab - Chapter 07: R1CS Zero-Knowledge Constraint Verifier
Implements Finite Prime Field Arithmetic, R1CS Circuit Constraints, and Witness Auditing.
"""
import sys
from typing import List, Tuple

sys.stdout.reconfigure(encoding="utf-8")

# BN254 Scalar Field Prime (alt_bn128 group order r)
BN254_PRIME = 21888242871839275222246405745257275088548364400416034343698204186575808495617

class PrimeField:
    def __init__(self, val: int, p: int = BN254_PRIME):
        self.p = p
        self.val = val % p

    def __add__(self, other: 'PrimeField') -> 'PrimeField':
        return PrimeField((self.val + other.val) % self.p, self.p)

    def __sub__(self, other: 'PrimeField') -> 'PrimeField':
        return PrimeField((self.val - other.val) % self.p, self.p)

    def __mul__(self, other: 'PrimeField') -> 'PrimeField':
        return PrimeField((self.val * other.val) % self.p, self.p)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PrimeField):
            return False
        return self.val == other.val and self.p == other.p

    def __repr__(self) -> str:
        return f"{self.val}"

class R1CSVerifier:
    def __init__(self, A: List[List[int]], B: List[List[int]], C: List[List[int]], p: int = BN254_PRIME):
        self.m = len(A)       # Number of constraints
        self.n = len(A[0])    # Number of variables in witness
        self.p = p
        self.A = [[PrimeField(val, p) for val in row] for row in A]
        self.B = [[PrimeField(val, p) for val in row] for row in B]
        self.C = [[PrimeField(val, p) for val in row] for row in C]

    def verify_witness(self, witness: List[int]) -> Tuple[bool, List[int]]:
        if len(witness) != self.n:
            raise ValueError(f"Witness length {len(witness)} does not match R1CS dimension {self.n}")

        s = [PrimeField(val, self.p) for val in witness]
        failed_constraints = []

        for j in range(self.m):
            # Compute A_j . s
            val_a = PrimeField(0, self.p)
            for i in range(self.n):
                val_a = val_a + (self.A[j][i] * s[i])

            # Compute B_j . s
            val_b = PrimeField(0, self.p)
            for i in range(self.n):
                val_b = val_b + (self.B[j][i] * s[i])

            # Compute C_j . s
            val_c = PrimeField(0, self.p)
            for i in range(self.n):
                val_c = val_c + (self.C[j][i] * s[i])

            # Check (A_j . s) * (B_j . s) == (C_j . s)
            left_side = val_a * val_b
            if left_side != val_c:
                failed_constraints.append(j)

        return (len(failed_constraints) == 0, failed_constraints)


def test_r1cs_snark():
    print("===========================================================================")
    print("R1CS ZERO-KNOWLEDGE ARITHMETIC CIRCUIT VERIFICATION TESTBED")
    print("LEVEL 9 LAB - CHAPTER 07")
    print("===========================================================================")

    # Circuit: x^3 + x + 5 = y
    # Witness vector: s = [1, y, x, v1, v2]
    # v1 = x * x
    # v2 = v1 * x
    # y = v2 + x + 5  =>  (v2 + x + 5) * 1 = y

    # Indices: 0: 1, 1: y, 2: x, 3: v1, 4: v2
    A = [
        [0, 0, 1, 0, 0],  # Gate 1: x
        [0, 0, 0, 1, 0],  # Gate 2: v1
        [5, 0, 1, 0, 1],  # Gate 3: 5*1 + 1*x + 1*v2
    ]
    B = [
        [0, 0, 1, 0, 0],  # Gate 1: x
        [0, 0, 1, 0, 0],  # Gate 2: x
        [1, 0, 0, 0, 0],  # Gate 3: 1
    ]
    C = [
        [0, 0, 0, 1, 0],  # Gate 1: v1
        [0, 0, 0, 0, 1],  # Gate 2: v2
        [0, 1, 0, 0, 0],  # Gate 3: y
    ]

    verifier = R1CSVerifier(A, B, C)

    # 1. Honest Witness Test
    print("[Test 1/3] Honest Witness Verification (x = 3, y = 35)...")
    x = 3
    v1 = x * x        # 9
    v2 = v1 * x       # 27
    y = v2 + x + 5    # 35
    honest_witness = [1, y, x, v1, v2]

    is_valid, failed = verifier.verify_witness(honest_witness)
    assert is_valid is True, f"Honest witness must pass R1CS constraints, failed: {failed}"
    print(f"  -> Honest witness {honest_witness} successfully verified: All 3 gates satisfied.")

    # 2. Tampered Secret Witness Test (Cheat: x = 4, but claim output is still 35)
    print("[Test 2/3] Tampered Witness Trapping (Cheating Prover)...")
    cheat_x = 4
    v1_fake = cheat_x * cheat_x   # 16
    v2_fake = v1_fake * cheat_x  # 64
    # But prover tries to claim y = 35
    tampered_witness = [1, 35, cheat_x, v1_fake, v2_fake]
    is_valid_fake, failed_fake = verifier.verify_witness(tampered_witness)
    assert is_valid_fake is False
    assert 2 in failed_fake, "Gate 3 must fail because 64 + 4 + 5 = 73 != 35"
    print(f"  -> Successfully trapped cheating witness: Constraint {failed_fake} violated.")

    # 3. Finite Field Overflow & Negative Value Test
    print("[Test 3/3] Finite Field Arithmetic & Modulo Wrap-Around...")
    p = BN254_PRIME
    f1 = PrimeField(-5, p)
    f2 = PrimeField(5, p)
    assert (f1 + f2).val == 0
    f_mul = PrimeField(p - 1, p) * PrimeField(p - 1, p)
    assert f_mul.val == 1, "(-1) * (-1) == 1 in prime field"
    print("  -> BN254 prime field arithmetic verified: Additive inverses and multiplicative identity confirmed.")

    print("===========================================================================")
    print("ALL 3 R1CS & FINITE FIELD VERIFICATION TESTS PASSED (Exit Code 0).")
    print("===========================================================================")

if __name__ == "__main__":
    test_r1cs_snark()
