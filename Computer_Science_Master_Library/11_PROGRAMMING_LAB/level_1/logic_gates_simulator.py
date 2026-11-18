"""
Practical Lab 1.5: Logic Gates and 4-Bit Ripple Carry Adder Simulation
File: 11_PROGRAMMING_LAB/level_1/logic_gates_simulator.py
Author: Computer Science Master Library
Description: Implements basic and universal logic gates from first principles
             and builds a verified 4-Bit Ripple Carry Adder circuit.
"""

import sys
from typing import Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# -------------------------------------------------------------
# Fundamental Logic Gate Functions
# -------------------------------------------------------------
def gate_not(a: int) -> int:
    return 1 if a == 0 else 0


def gate_and(a: int, b: int) -> int:
    return 1 if (a == 1 and b == 1) else 0


def gate_or(a: int, b: int) -> int:
    return 1 if (a == 1 or b == 1) else 0


def gate_nand(a: int, b: int) -> int:
    return gate_not(gate_and(a, b))


def gate_nor(a: int, b: int) -> int:
    return gate_not(gate_or(a, b))


def gate_xor(a: int, b: int) -> int:
    return gate_or(gate_and(a, gate_not(b)), gate_and(gate_not(a), b))


def gate_xnor(a: int, b: int) -> int:
    return gate_not(gate_xor(a, b))


# -------------------------------------------------------------
# Combinational Circuits: Adders
# -------------------------------------------------------------
def half_adder(a: int, b: int) -> Tuple[int, int]:
    """Computes Sum and Carry for two 1-bit inputs."""
    s = gate_xor(a, b)
    c = gate_and(a, b)
    return s, c


def full_adder(a: int, b: int, c_in: int) -> Tuple[int, int]:
    """Computes Sum and Carry-out for two bits plus carry-in."""
    s1, c1 = half_adder(a, b)
    sum_out, c2 = half_adder(s1, c_in)
    c_out = gate_or(c1, c2)
    return sum_out, c_out


def ripple_carry_adder_4bit(a: int, b: int) -> Tuple[int, int]:
    """
    Simulates a 4-bit hardware adder.
    Inputs: a (0-15), b (0-15)
    Returns: (4-bit sum, carry_out)
    """
    carry = 0
    sum_bits = []

    for i in range(4):
        bit_a = (a >> i) & 1
        bit_b = (b >> i) & 1
        s, carry = full_adder(bit_a, bit_b, carry)
        sum_bits.append(s)

    total_sum = 0
    for i, bit in enumerate(sum_bits):
        total_sum |= bit << i

    return total_sum, carry


def verify_boolean_algebra() -> None:
    print("=" * 60)
    print("      VERIFYING DE MORGAN'S THEOREMS VIA TRUTH TABLE")
    print("=" * 60)
    print("A B | NOT(A and B) | (NOT A or NOT B) | Equivalent?")
    for a in [0, 1]:
        for b in [0, 1]:
            lhs = gate_not(gate_and(a, b))
            rhs = gate_or(gate_not(a), gate_not(b))
            print(f"{a} {b} |       {lhs}        |         {rhs}          | {lhs == rhs}")
    print()


if __name__ == "__main__":
    verify_boolean_algebra()

    print("=" * 60)
    print("      TESTING 4-BIT RIPPLE CARRY ADDER")
    print("=" * 60)
    test_cases = [(5, 3), (7, 6), (12, 3), (15, 1)]
    for val_a, val_b in test_cases:
        res_sum, res_carry = ripple_carry_adder_4bit(val_a, val_b)
        actual_total = res_sum + (res_carry << 4)
        print(f"Adding: {val_a:2d} + {val_b:2d}")
        print(
            f"  Binary Inputs : {val_a:04b} + {val_b:04b}"
        )
        print(
            f"  Hardware Out  : Sum={res_sum:04b} ({res_sum}), Carry-out={res_carry}"
        )
        print(
            f"  Total Decimal : {actual_total} (Verified: {val_a + val_b == actual_total})\n"
        )
        assert val_a + val_b == actual_total, "Adder calculation mismatch!"

    print("All logic gate and adder tests passed successfully.")
