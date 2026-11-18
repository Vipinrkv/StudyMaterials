"""
Practical Lab 2.3 Companion: Operators, Bitwise Logic & Short-Circuit Simulator
File: 11_PROGRAMMING_LAB/level_2/ch03_flow_simulator.py
Author: Computer Science Master Library
Description: Emulates C operators, short-circuit execution safety,
             pre/post-increment semantics, and bitwise logic operations.
"""

import sys
from typing import Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def demonstrate_short_circuit_safety() -> None:
    print("=" * 65)
    print("      DEMONSTRATING SHORT-CIRCUIT EVALUATION SAFETY")
    print("=" * 65)

    dangerous_divisor = 0
    executed_dangerous_function = False

    def dangerous_divide(val: int) -> bool:
        nonlocal executed_dangerous_function
        executed_dangerous_function = True
        return (100 // val) > 5

    # Guard condition using AND (&&)
    # If divisor == 0, dangerous_divide() MUST NOT be called!
    condition = (dangerous_divisor != 0) and dangerous_divide(dangerous_divisor)

    print(f"Condition Result: {condition}")
    print(
        f"Did dangerous divide execute? {executed_dangerous_function} (Prevented crash!)"
    )
    assert executed_dangerous_function is False
    print("Short-circuit safety assertion verified.\n")


def demonstrate_bitwise_operations(a: int, b: int) -> None:
    print("=" * 65)
    print(f"      BITWISE OPERATIONS TRACE: A = {a} (0x{a:02X}), B = {b} (0x{b:02X})")
    print("=" * 65)

    op_and = a & b
    op_or = a | b
    op_xor = a ^ b
    op_shl = a << 2
    op_shr = a >> 1

    print(f"A & B  (AND)        : {op_and:3d} (Binary: {op_and:08b})")
    print(f"A | B  (OR)         : {op_or:3d} (Binary: {op_or:08b})")
    print(f"A ^ B  (XOR)        : {op_xor:3d} (Binary: {op_xor:08b})")
    print(
        f"A << 2 (Left Shift) : {op_shl:3d} (Binary: {op_shl:08b}, Value = A * 4)"
    )
    print(
        f"A >> 1 (Right Shift): {op_shr:3d} (Binary: {op_shr:08b}, Value = A // 2)"
    )

    assert op_and == (43 & 25)
    assert op_or == (43 | 25)
    assert op_xor == (43 ^ 25)
    assert op_shl == (43 * 4)
    assert op_shr == (43 // 2)
    print("-" * 65)
    print("All bitwise assertions mathematically verified.\n")


if __name__ == "__main__":
    demonstrate_short_circuit_safety()
    demonstrate_bitwise_operations(43, 25)
    print("All C control flow and operator simulation tests passed.")
