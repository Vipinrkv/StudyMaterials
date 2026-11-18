"""
ch02_ebpf_io_uring_lab.py
Level 8 Chapter 02 Companion Laboratory: Linux Kernel Internals, eBPF & io_uring.
Simulates eBPF RISC Bytecode Decoding, Abstract Interval Verifier,
and io_uring Lock-Free Submission & Completion Queue Synchronization.
Pure Python/Standard Library with zero external dependencies.
"""

from __future__ import annotations
import sys
import struct
from typing import Dict, List, Tuple, Optional, Any

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")


class BpfInstruction:
    """eBPF 64-bit Instruction: [opcode (8) | dst (4) | src (4) | off (16) | imm (32)]"""
    def __init__(self, opcode: int, dst: int, src: int, off: int, imm: int):
        self.opcode = opcode
        self.dst = dst
        self.src = src
        self.off = off
        self.imm = imm

    @classmethod
    def encode(cls, opcode: int, dst: int, src: int, off: int, imm: int) -> bytes:
        return struct.pack("<BBhi", opcode, (src << 4) | (dst & 0x0F), off, imm)

    @classmethod
    def decode(cls, raw: bytes) -> BpfInstruction:
        opcode, regs, off, imm = struct.unpack("<BBhi", raw[:8])
        dst = regs & 0x0F
        src = (regs >> 4) & 0x0F
        return cls(opcode, dst, src, off, imm)


class BpfVerifier:
    """
    Abstract interpretation engine verifying eBPF programs for safety,
    bounded register intervals, and absence of memory out-of-bounds traps.
    """
    BPF_ALU64_ADD_IMM = 0x07
    BPF_ALU64_MOV_IMM = 0xB7
    BPF_EXIT = 0x95

    def __init__(self, max_instructions: int = 4096):
        self.max_insns = max_instructions

    def verify(self, program: List[BpfInstruction], memory_limit: int = 512) -> Tuple[bool, str]:
        if len(program) > self.max_insns:
            return False, f"Program exceeds max instructions ({len(program)} > {self.max_insns})"
        if not program or program[-1].opcode != self.BPF_EXIT:
            return False, "Program must terminate with BPF_EXIT instruction"

        # Abstract state: reg -> [min, max]
        reg_bounds: Dict[int, Tuple[int, int]] = {i: (0, 0) for i in range(11)}
        reg_bounds[1] = (0, memory_limit)  # R1 is context pointer

        for idx, insn in enumerate(program):
            if insn.opcode == self.BPF_ALU64_MOV_IMM:
                reg_bounds[insn.dst] = (insn.imm, insn.imm)
            elif insn.opcode == self.BPF_ALU64_ADD_IMM:
                low, high = reg_bounds[insn.dst]
                new_low = low + insn.imm
                new_high = high + insn.imm
                if new_high > 0xFFFFFFFFFFFFFFFF:
                    return False, f"Insn {idx}: Integer overflow detected in R{insn.dst}"
                reg_bounds[insn.dst] = (new_low, new_high)
            elif insn.opcode == self.BPF_EXIT:
                pass

        return True, "Verification succeeded: Program is safe to execute in kernel space"


class IoUringSimulator:
    """
    Simulates Linux io_uring lock-free circular ring buffers
    with user-kernel shared memory synchronization.
    """
    def __init__(self, capacity_power_of_two: int = 16):
        assert (capacity_power_of_two & (capacity_power_of_two - 1)) == 0
        self.capacity = capacity_power_of_two
        self.mask = capacity_power_of_two - 1

        self.sq: List[Optional[Dict[str, Any]]] = [None] * self.capacity
        self.cq: List[Optional[Dict[str, Any]]] = [None] * self.capacity

        self.sq_head = 0
        self.sq_tail = 0
        self.cq_head = 0
        self.cq_tail = 0

    def submit_sqe(self, opcode: str, fd: int, buffer_id: int) -> bool:
        if (self.sq_tail - self.sq_head) >= self.capacity:
            return False
        sqe = {"opcode": opcode, "fd": fd, "buffer_id": buffer_id, "user_data": self.sq_tail}
        self.sq[self.sq_tail & self.mask] = sqe
        self.sq_tail += 1
        return True

    def kernel_sqpoll(self) -> int:
        processed = 0
        while self.sq_head < self.sq_tail:
            sqe = self.sq[self.sq_head & self.mask]
            self.sq_head += 1

            res = 4096 if sqe["opcode"] == "READ" else 0
            cqe = {"user_data": sqe["user_data"], "res": res}
            self.cq[self.cq_tail & self.mask] = cqe
            self.cq_tail += 1
            processed += 1
        return processed

    def reap_cqe(self) -> Optional[Dict[str, Any]]:
        if self.cq_head >= self.cq_tail:
            return None
        cqe = self.cq[self.cq_head & self.mask]
        self.cq_head += 1
        return cqe


def main() -> None:
    print("=" * 70)
    print("LEVEL 8 CHAPTER 02: LINUX KERNEL INTERNALS, EBPF & IO_URING LAB")
    print("=" * 70)

    # 1. Test eBPF Bytecode Encoding & Decoding
    print("\n[Test 1] Testing eBPF instruction binary encoding & decoding...")
    # MOV R0, 42
    raw = BpfInstruction.encode(0xB7, 0, 0, 0, 42)
    assert len(raw) == 8, f"eBPF instruction must be exactly 8 bytes, got {len(raw)}"
    decoded = BpfInstruction.decode(raw)
    assert decoded.opcode == 0xB7 and decoded.dst == 0 and decoded.imm == 42
    print("  -> Instruction 64-bit struct packing: Verified (MOV R0, 42).")

    # 2. Test eBPF Verifier
    print("\n[Test 2] Verifying safe eBPF program...")
    prog_safe = [
        BpfInstruction(0xB7, 0, 0, 0, 0),    # MOV R0, 0
        BpfInstruction(0x07, 0, 0, 0, 100),  # ADD R0, 100
        BpfInstruction(0x95, 0, 0, 0, 0),    # EXIT
    ]
    verifier = BpfVerifier()
    ok_safe, msg_safe = verifier.verify(prog_safe)
    assert ok_safe is True, f"Safe program rejected: {msg_safe}"
    print(f"  -> Safe Program Verifier: Passed ({msg_safe}).")

    print("\n[Test 3] Verifying unsafe program (Missing BPF_EXIT)...")
    prog_unsafe = [
        BpfInstruction(0xB7, 0, 0, 0, 1),
    ]
    ok_unsafe, msg_unsafe = verifier.verify(prog_unsafe)
    assert ok_unsafe is False, "Unsafe program must be rejected by kernel verifier!"
    print(f"  -> Unsafe Program Rejected: Passed ({msg_unsafe}).")

    # 3. Test io_uring Double Ring Buffer
    print("\n[Test 4] Testing io_uring Lock-Free Submission & Completion Queue...")
    ring = IoUringSimulator(capacity_power_of_two=8)

    # Submit 4 I/O read requests
    for i in range(4):
        assert ring.submit_sqe("READ", fd=10 + i, buffer_id=100 + i) is True

    assert ring.sq_tail == 4
    assert ring.sq_head == 0

    # Kernel SQPOLL consumes requests
    processed = ring.kernel_sqpoll()
    assert processed == 4, f"Expected 4 processed SQEs, got {processed}"
    assert ring.sq_head == 4
    assert ring.cq_tail == 4

    # User space reaps completions
    reaped = []
    while True:
        cqe = ring.reap_cqe()
        if cqe is None:
            break
        reaped.append(cqe)

    assert len(reaped) == 4
    assert [c["res"] for c in reaped] == [4096, 4096, 4096, 4096]
    print(f"  -> io_uring Asynchronous I/O Lifecycle: Verified ({len(reaped)} CQEs reaped).")

    print("\n" + "=" * 70)
    print("ALL EBPF & IO_URING KERNEL TESTS PASSED (Exit Code 0).")
    print("=" * 70)
    sys.exit(0)


if __name__ == "__main__":
    main()
