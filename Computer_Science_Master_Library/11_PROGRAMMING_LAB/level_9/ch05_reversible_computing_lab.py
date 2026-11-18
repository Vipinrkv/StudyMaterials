"""
Level 9 Programming Lab - Chapter 05: Reversible Computing & Landauer Bound
Implements Reversible Logic (Toffoli & Fredkin), Bennett Uncomputation, and Thermodynamic Limits.
"""
import sys
import math
from typing import Tuple, List

sys.stdout.reconfigure(encoding="utf-8")

# Physical constants
K_BOLTZMANN = 1.380649e-23  # J/K
LN_2 = math.log(2.0)

# -------------------------------------------------------------------------
# 1. Reversible Logic Gates
# -------------------------------------------------------------------------
def toffoli_gate(a: int, b: int, c: int) -> Tuple[int, int, int]:
    # Maps (a, b, c) -> (a, b, c ^ (a & b))
    return (a, b, c ^ (a & b))

def fredkin_gate(ctrl: int, a: int, b: int) -> Tuple[int, int, int]:
    # Controlled-SWAP: if ctrl == 1, swap a and b
    if ctrl == 1:
        return (ctrl, b, a)
    return (ctrl, a, b)

# -------------------------------------------------------------------------
# 2. Bennett Reversible Uncomputation
# -------------------------------------------------------------------------
class BennettEngine:
    """
    Demonstrates computing f(x) reversibly, copying the result,
    and uncomputing intermediate garbage to avoid Landauer dissipation.
    """
    @staticmethod
    def forward_compute(x1: int, x2: int, ancilla: int) -> Tuple[int, int, int, int]:
        # Compute AND into ancilla using Toffoli
        # (x1, x2, ancilla) -> (x1, x2, garbage_g)
        _, _, g = toffoli_gate(x1, x2, ancilla)
        # Result output is g
        return (x1, x2, ancilla, g)

    @staticmethod
    def copy_result(g: int, target_out: int) -> Tuple[int, int]:
        # CNOT from g into target_out (target_out initialized to 0)
        return (g, target_out ^ g)

    @staticmethod
    def uncompute(x1: int, x2: int, g: int) -> int:
        # Run Toffoli in reverse: (x1, x2, g) -> (x1, x2, restored_ancilla)
        _, _, restored = toffoli_gate(x1, x2, g)
        return restored

# -------------------------------------------------------------------------
# 3. Thermodynamic Landauer Calculation
# -------------------------------------------------------------------------
def calculate_landauer_limit(erased_bits: int, temp_kelvin: float = 300.0) -> float:
    # E >= N * k_B * T * ln(2)
    return erased_bits * K_BOLTZMANN * temp_kelvin * LN_2


def test_reversible_computing():
    print("===========================================================================")
    print("REVERSIBLE COMPUTING & THERMODYNAMIC LIMITS VERIFICATION TESTBED")
    print("LEVEL 9 LAB - CHAPTER 05")
    print("===========================================================================")

    # 1. Toffoli Involutive Reversibility Test
    print("[Test 1/4] Toffoli (CCNOT) Gate Truth Table & Self-Inverse Invariant...")
    for a in (0, 1):
        for b in (0, 1):
            for c in (0, 1):
                out1 = toffoli_gate(a, b, c)
                out2 = toffoli_gate(*out1)
                assert out2 == (a, b, c), f"Toffoli must be self-inverse: T(T({a},{b},{c})) = {out2}"
                # Target flip condition
                expected_c = c ^ (a & b)
                assert out1 == (a, b, expected_c)
    print("  -> Verified all 8 Toffoli truth table states: 100% bijective and self-inverse (T^2 = I).")

    # 2. Fredkin Conservative Hamming Weight Test
    print("[Test 2/4] Fredkin (CSWAP) Conservative Gate Invariant...")
    for c in (0, 1):
        for a in (0, 1):
            for b in (0, 1):
                f_out1 = fredkin_gate(c, a, b)
                f_out2 = fredkin_gate(*f_out1)
                assert f_out2 == (c, a, b), "Fredkin gate must be self-inverse"
                # Conservative property: sum of bits in == sum of bits out
                assert (c + a + b) == sum(f_out1), "Hamming weight must be strictly conserved"
    print("  -> Verified all 8 Fredkin states: Self-inverse and strict Hamming weight conservation.")

    # 3. Bennett Reversible Uncomputation Cycle
    print("[Test 3/4] Bennett Reversible Uncomputation Protocol...")
    x1, x2, ancilla = 1, 1, 0
    # Forward pass
    _, _, _, g = BennettEngine.forward_compute(x1, x2, ancilla)
    assert g == 1, "1 AND 1 must equal 1"

    # Copy output to clean target register
    target = 0
    g_kept, final_output = BennettEngine.copy_result(g, target)
    assert final_output == 1

    # Uncompute intermediate garbage g back to clean ancilla 0
    restored_ancilla = BennettEngine.uncompute(x1, x2, g_kept)
    assert restored_ancilla == 0, f"Ancilla must be restored to 0, got {restored_ancilla}"
    print("  -> Bennett uncomputation verified: Output captured (1), intermediate garbage reset to (0) reversibly.")

    # 4. Landauer Thermodynamic Dissipation Bound
    print("[Test 4/4] Landauer Principle Energy Dissipation Bound...")
    one_million_bits = 1_000_000
    joules = calculate_landauer_limit(one_million_bits, temp_kelvin=300.0)
    print(f"  -> Minimum thermodynamic dissipation for 1M erased bits at 300K: {joules:.4e} Joules")
    assert joules > 2.8e-15 and joules < 2.9e-15
    print("  -> Landauer bound confirmed (k_B * T * ln(2)).")

    print("===========================================================================")
    print("ALL 4 REVERSIBLE COMPUTING & THERMODYNAMICS TESTS PASSED (Exit Code 0).")
    print("===========================================================================")

if __name__ == "__main__":
    test_reversible_computing()
