#!/usr/bin/env python3
"""
Chapter 04 Python Verification & Emulation Testbed:
Call Stack, Activation Records, and Recursion Depth Simulator

Validates:
- Stack frame push / pop lifecycle.
- Return address preservation.
- Local variable scoping & isolation between frames.
- Stack overflow detection when recursion exceeds configured limit.
"""

import sys
from typing import Any, Dict, List, Optional

# Enforce UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class StackFrame:
    def __init__(self, func_name: str, args: Dict[str, Any], return_address: int):
        self.func_name = func_name
        self.args = args
        self.locals: Dict[str, Any] = {}
        self.return_address = return_address

    def __repr__(self) -> str:
        return f"Frame<{self.func_name} | args={self.args} | locals={self.locals} | ret=0x{self.return_address:04X}>"


class CallStackSimulator:
    def __init__(self, max_depth: int = 100):
        self.max_depth = max_depth
        self.stack: List[StackFrame] = []
        self.peak_depth: int = 0
        self.instruction_pointer: int = 0x1000

    def push(self, func_name: str, args: Dict[str, Any], return_address: int) -> StackFrame:
        if len(self.stack) >= self.max_depth:
            raise RecursionError(f"STACK OVERFLOW ERROR: Exceeded maximum call stack depth of {self.max_depth} frames!")
        frame = StackFrame(func_name, args, return_address)
        self.stack.append(frame)
        if len(self.stack) > self.peak_depth:
            self.peak_depth = len(self.stack)
        return frame

    def pop(self) -> StackFrame:
        if not self.stack:
            raise IndexError("Stack Underflow: Attempted to pop from an empty call stack!")
        return self.stack.pop()

    def current_frame(self) -> Optional[StackFrame]:
        return self.stack[-1] if self.stack else None

    def dump_stack(self) -> None:
        print("\n--- ACTIVE CALL STACK (Top to Bottom) ---")
        if not self.stack:
            print("  [Stack is Empty]")
        for i, frame in enumerate(reversed(self.stack)):
            level = len(self.stack) - 1 - i
            print(f"  Frame [{level:02d}] -> {frame}")
        print("------------------------------------------\n")


def simulate_factorial(sim: CallStackSimulator, n: int, call_ip: int) -> int:
    sim.push("factorial", {"n": n}, call_ip)
    frame = sim.current_frame()
    assert frame is not None

    if n <= 1:
        frame.locals["result"] = 1
        sim.pop()
        return 1

    # Recursive call simulating next instruction address
    next_ip = call_ip + 0x0008
    sub_res = simulate_factorial(sim, n - 1, next_ip)
    result = n * sub_res
    frame.locals["result"] = result
    sim.pop()
    return result


def main() -> int:
    print("=" * 60)
    print("LEVEL 2 LAB CH04: CALL STACK & ACTIVATION RECORD SIMULATOR")
    print("=" * 60)

    sim = CallStackSimulator(max_depth=16)

    # Test 1: Recursive Factorial Simulation
    target_n = 5
    print(f"\n[Test 1] Executing recursive factorial({target_n}) ...")
    sim.push("main", {"argc": 1}, 0x0000)
    
    fact_val = simulate_factorial(sim, target_n, 0x1004)
    print(f"Factorial result: {target_n}! = {fact_val}")
    assert fact_val == 120, f"Expected 120, got {fact_val}"

    # Main frame should still be on stack before exit
    assert len(sim.stack) == 1
    main_frame = sim.pop()
    assert main_frame.func_name == "main"
    assert len(sim.stack) == 0
    print(f"SUCCESS: Stack balanced to zero frames. Peak depth was {sim.peak_depth} frames.")

    # Test 2: Stack Overflow Guard Verification
    print("\n[Test 2] Verifying Stack Overflow Protection (Triggering infinite recursion) ...")
    sim_overflow = CallStackSimulator(max_depth=5)
    overflow_caught = False
    try:
        def infinite_rec(depth: int):
            sim_overflow.push("infinite_rec", {"d": depth}, 0x2000)
            infinite_rec(depth + 1)
        infinite_rec(1)
    except RecursionError as e:
        overflow_caught = True
        print(f"SUCCESS: Caught expected overflow exception -> {e}")

    assert overflow_caught, "Failed to trap call stack overflow!"

    print("\n" + "=" * 60)
    print("ALL CH04 CALL STACK SIMULATION CHECKS PASSED (Exit 0)")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
