"""
Practical Lab 1.2: 4-Bit Accumulator Machine CPU Simulator
File: 11_PROGRAMMING_LAB/level_1/cpu_simulator.py
Author: Computer Science Master Library
Description: Simulates the Von Neumann Fetch-Decode-Execute machine cycle,
             demonstrating registers (PC, IR, ACC) and ALU operations.
"""

from typing import List


class EducationalCPU:

    def __init__(self, memory_size: int = 16):
        # RAM: Array of 16 memory cells (holds instructions and data)
        self.memory: List[int] = [0] * memory_size

        # Internal Registers
        self.pc: int = 0  # Program Counter: points to next instruction
        self.ir: int = 0  # Instruction Register: holds current instruction
        self.acc: int = 0  # Accumulator: holds results of ALU operations
        self.halted: bool = False

        # Instruction Set Architecture (ISA) Opcode Mapping
        # High nibble (bits 7-4) = Opcode; Low nibble (bits 3-0) = Operand
        self.OPCODES = {
            1: "LOAD",  # Load value from memory address into ACC
            2: "STORE",  # Store value in ACC into memory address
            3: "ADD",  # Add value at memory address to ACC
            4: "SUB",  # Subtract value at memory address from ACC
            5: "PRINT",  # Print current ACC value
            0: "HALT",  # Stop execution
        }

    def load_program(self, program: List[int], start_address: int = 0) -> None:
        """Loads machine code instructions into simulated RAM."""
        for i, instruction in enumerate(program):
            self.memory[start_address + i] = instruction

    def step(self) -> None:
        """Executes one single Fetch-Decode-Execute machine cycle."""
        if self.halted:
            return

        # 1. FETCH STAGE
        self.ir = self.memory[self.pc]
        current_pc = self.pc
        self.pc += 1  # Increment PC

        # 2. DECODE STAGE
        opcode = (self.ir >> 4) & 0x0F  # Top 4 bits
        operand = self.ir & 0x0F  # Bottom 4 bits
        operation = self.OPCODES.get(opcode, "UNKNOWN")

        # 3. EXECUTE & STORE STAGE
        if operation == "LOAD":
            self.acc = self.memory[operand]
            print(
                f"[Cycle @ PC={current_pc}] LOAD: ACC <- Memory[{operand}] ({self.acc})"
            )
        elif operation == "STORE":
            self.memory[operand] = self.acc
            print(
                f"[Cycle @ PC={current_pc}] STORE: Memory[{operand}] <- ACC ({self.acc})"
            )
        elif operation == "ADD":
            operand_val = self.memory[operand]
            old_acc = self.acc
            self.acc += operand_val
            print(
                f"[Cycle @ PC={current_pc}] ALU ADD: {old_acc} + {operand_val} = {self.acc}"
            )
        elif operation == "SUB":
            operand_val = self.memory[operand]
            old_acc = self.acc
            self.acc -= operand_val
            print(
                f"[Cycle @ PC={current_pc}] ALU SUB: {old_acc} - {operand_val} = {self.acc}"
            )
        elif operation == "PRINT":
            print(f">>> OUTPUT DISPLAY: ACC = {self.acc}")
        elif operation == "HALT":
            self.halted = True
            print(f"[Cycle @ PC={current_pc}] HALT: Execution terminated.")
        else:
            raise ValueError(f"Illegal instruction opcode: {opcode}")

    def run(self) -> None:
        """Runs the machine cycle until HALT instruction is encountered."""
        print("=" * 60)
        print("          STARTING CPU MACHINE CYCLE EXECUTION")
        print("=" * 60)
        cycle_count = 0
        while not self.halted and self.pc < len(self.memory):
            cycle_count += 1
            self.step()
        print("=" * 60)
        print(f"Execution completed in {cycle_count} clock cycles.")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    # Create simulated CPU
    cpu = EducationalCPU(memory_size=16)

    # Program: Compute 25 + 17 and display the result.
    program = [
        (1 << 4) | 14,  # LOAD from cell 14
        (3 << 4) | 15,  # ADD value from cell 15
        (5 << 4) | 0,  # PRINT accumulator
        (0 << 4) | 0,  # HALT
    ]

    cpu.load_program(program, start_address=0)
    cpu.memory[14] = 25
    cpu.memory[15] = 17

    cpu.run()
    assert cpu.acc == 42, f"Expected 42, got {cpu.acc}"
    print("Verification assertion passed: ACC == 42.")
