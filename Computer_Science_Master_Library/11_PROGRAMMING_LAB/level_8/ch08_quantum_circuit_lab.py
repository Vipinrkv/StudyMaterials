"""
ch08_quantum_circuit_lab.py
Level 8 Chapter 08 Companion Laboratory: Quantum Computing, Qubits & Circuits.
Simulates Multi-Qubit State Vectors, Unitary Gate Matrices (H, X, Z, CNOT),
Bell State Entanglement Generation, and Probabilistic Born-Rule Measurement.
Pure Python/Standard Library with zero external dependencies.
"""

from __future__ import annotations
import sys
import math
import random
from typing import List, Tuple, Dict, Any

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")


class QuantumRegister:
    """State vector simulator for an n-qubit quantum register."""
    def __init__(self, num_qubits: int):
        self.num_qubits = num_qubits
        self.dim = 1 << num_qubits
        self.state: List[complex] = [0.0j] * self.dim
        self.state[0] = 1.0 + 0.0j

    def apply_single_gate(self, gate: List[List[complex]], target_qubit: int) -> None:
        new_state = [0.0j] * self.dim
        for i in range(self.dim):
            bit = (i >> target_qubit) & 1
            peer = i ^ (1 << target_qubit)
            if bit == 0:
                new_state[i] += gate[0][0] * self.state[i] + gate[0][1] * self.state[peer]
            else:
                new_state[i] += gate[1][0] * self.state[peer] + gate[1][1] * self.state[i]
        self.state = new_state

    def apply_cnot(self, control_qubit: int, target_qubit: int) -> None:
        new_state = list(self.state)
        for i in range(self.dim):
            c_bit = (i >> control_qubit) & 1
            if c_bit == 1:
                target_flipped = i ^ (1 << target_qubit)
                if (i >> target_qubit) & 1 == 0:
                    new_state[i] = self.state[target_flipped]
                    new_state[target_flipped] = self.state[i]
        self.state = new_state

    def measure(self, shots: int = 1000) -> Dict[str, int]:
        probabilities = [abs(amp) ** 2 for amp in self.state]
        counts: Dict[str, int] = {}

        random.seed(42)
        for _ in range(shots):
            r = random.random()
            cum = 0.0
            chosen = 0
            for idx, p in enumerate(probabilities):
                cum += p
                if r <= cum:
                    chosen = idx
                    break
            bitstring = bin(chosen)[2:].zfill(self.num_qubits)
            counts[bitstring] = counts.get(bitstring, 0) + 1
        return counts


class QuantumGates:
    """Standard single-qubit unitary gate matrices."""
    INV_SQRT2 = 1.0 / math.sqrt(2.0)

    H = [
        [complex(INV_SQRT2, 0), complex(INV_SQRT2, 0)],
        [complex(INV_SQRT2, 0), complex(-INV_SQRT2, 0)]
    ]

    X = [
        [0.0j, 1.0 + 0.0j],
        [1.0 + 0.0j, 0.0j]
    ]

    Z = [
        [1.0 + 0.0j, 0.0j],
        [0.0j, -1.0 + 0.0j]
    ]


def main() -> None:
    print("=" * 70)
    print("LEVEL 8 CHAPTER 08: QUANTUM COMPUTING & CIRCUITS LAB")
    print("=" * 70)

    # 1. Single Qubit Superposition Test
    print("\n[Test 1] Testing Single-Qubit Superposition (Hadamard Gate)...")
    q1 = QuantumRegister(num_qubits=1)
    q1.apply_single_gate(QuantumGates.H, target_qubit=0)

    # Amplitudes should be [1/sqrt(2), 1/sqrt(2)]
    expected_prob = 0.5
    prob_0 = abs(q1.state[0]) ** 2
    prob_1 = abs(q1.state[1]) ** 2
    assert math.isclose(prob_0, expected_prob, rel_tol=1e-5)
    assert math.isclose(prob_1, expected_prob, rel_tol=1e-5)
    print(f"  -> State Vector: {q1.state[0]:.4f}|0> + {q1.state[1]:.4f}|1>.")
    print("  -> Superposition Born Probabilities: P(|0>) = 50.0%, P(|1>) = 50.0% (Verified).")

    # 2. Bell State Entanglement Test (|Phi+> = (|00> + |11>) / sqrt(2))
    print("\n[Test 2] Generating Maximally Entangled Bell State (|Phi+>)...")
    q2 = QuantumRegister(num_qubits=2)
    # Step 1: H on Qubit 0
    q2.apply_single_gate(QuantumGates.H, target_qubit=0)
    # Step 2: CNOT with Control=0, Target=1
    q2.apply_cnot(control_qubit=0, target_qubit=1)

    # Non-zero amplitudes must be only at index 0 (|00>) and index 3 (|11>)
    assert math.isclose(abs(q2.state[0]) ** 2, 0.5, rel_tol=1e-5)
    assert math.isclose(abs(q2.state[3]) ** 2, 0.5, rel_tol=1e-5)
    assert math.isclose(abs(q2.state[1]) ** 2, 0.0, rel_tol=1e-5)
    assert math.isclose(abs(q2.state[2]) ** 2, 0.0, rel_tol=1e-5)

    print(f"  -> State Vector: {q2.state[0]:.3f}|00> + {q2.state[3]:.3f}|11>.")
    print("  -> Zero Amplitudes for |01> and |10>: Confirmed (Non-local Entanglement).")

    # 3. Projective Measurement Simulation
    print("\n[Test 3] Performing 1000 Projective Measurements on Bell State...")
    counts = q2.measure(shots=1000)
    print(f"  -> Measurement Frequencies: {counts}")
    assert "01" not in counts and "10" not in counts, "Entangled Bell state must never yield |01> or |10>!"
    assert counts.get("00", 0) > 400 and counts.get("11", 0) > 400
    print("  -> Born-Rule Projective Collapse: VERIFIED (Exact correlation between qubits).")

    print("\n" + "=" * 70)
    print("ALL QUANTUM COMPUTING TESTS PASSED (Exit Code 0).")
    print("=" * 70)
    sys.exit(0)


if __name__ == "__main__":
    main()
