"""
Level 4 Chapter 06 Programming Lab: Turing Machine Simulator & Decider
=====================================================================
Focus: Formal 7-tuple Turing Machine simulation, bi-directional tape,
       decider for non-context-free language L = {a^n b^n c^n | n >= 1},
       and binary incrementer.
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")
from typing import Dict, Tuple, Set, List, Optional


class TuringMachine:
    def __init__(
        self,
        states: Set[str],
        input_alphabet: Set[str],
        tape_alphabet: Set[str],
        transitions: Dict[Tuple[str, str], Tuple[str, str, str]],
        start_state: str,
        accept_state: str,
        reject_state: str,
        blank_symbol: str = "⊔",
    ):
        self.states = states
        self.input_alphabet = input_alphabet
        self.tape_alphabet = tape_alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_state = accept_state
        self.reject_state = reject_state
        self.blank_symbol = blank_symbol

    def run(self, input_string: str, max_steps: int = 10000) -> Tuple[bool, int, str]:
        """
        Executes the Turing machine on input_string.
        Returns: (accepted: bool, step_count: int, final_tape: str)
        """
        for char in input_string:
            if char not in self.input_alphabet:
                raise ValueError(f"Input character '{char}' not in input alphabet")

        # Bi-directional tape represented by a dictionary
        tape: Dict[int, str] = {i: char for i, char in enumerate(input_string)}
        head: int = 0
        state: str = self.start_state
        steps: int = 0

        while steps < max_steps:
            if state == self.accept_state:
                return True, steps, self._get_tape_string(tape)
            if state == self.reject_state:
                return False, steps, self._get_tape_string(tape)

            current_sym = tape.get(head, self.blank_symbol)
            transition_key = (state, current_sym)

            if transition_key not in self.transitions:
                # Undefined transition is an implicit rejection
                return False, steps, self._get_tape_string(tape)

            next_state, write_sym, direction = self.transitions[transition_key]
            tape[head] = write_sym
            state = next_state

            if direction == "R":
                head += 1
            elif direction == "L":
                head -= 1
            else:
                raise ValueError(f"Invalid direction: {direction}")

            steps += 1

        # Step limit exceeded (potential infinite loop)
        return False, steps, self._get_tape_string(tape)

    def _get_tape_string(self, tape: Dict[int, str]) -> str:
        if not tape:
            return ""
        min_idx = min(tape.keys())
        max_idx = max(tape.keys())
        # Trim leading and trailing blanks
        chars = [tape.get(i, self.blank_symbol) for i in range(min_idx, max_idx + 1)]
        s = "".join(chars)
        return s.strip(self.blank_symbol)


def create_an_bn_cn_decider() -> TuringMachine:
    """
    Decider for non-context-free language: L = { a^n b^n c^n | n >= 1 }
    Alphabet: {a, b, c}, Markers: {X, Y, Z}, Blank: ⊔
    """
    states = {"q0", "q_find_b", "q_find_c", "q_return", "q_verify_blank", "q_accept", "q_reject"}
    input_alphabet = {"a", "b", "c"}
    tape_alphabet = {"a", "b", "c", "X", "Y", "Z", "⊔"}

    transitions = {
        # q0: Mark 'a' with 'X', proceed to find 'b'
        ("q0", "a"): ("q_find_b", "X", "R"),
        ("q0", "Y"): ("q_verify_blank", "Y", "R"),  # All a's have been processed
        
        # q_find_b: Skip remaining 'a's and marked 'Y's to find first 'b'
        ("q_find_b", "a"): ("q_find_b", "a", "R"),
        ("q_find_b", "Y"): ("q_find_b", "Y", "R"),
        ("q_find_b", "b"): ("q_find_c", "Y", "R"),  # Mark 'b' with 'Y', find 'c'

        # q_find_c: Skip remaining 'b's and marked 'Z's to find first 'c'
        ("q_find_c", "b"): ("q_find_c", "b", "R"),
        ("q_find_c", "Z"): ("q_find_c", "Z", "R"),
        ("q_find_c", "c"): ("q_return", "Z", "L"),  # Mark 'c' with 'Z', return to start

        # q_return: Rewind tape head leftward back to previous 'X'
        ("q_return", "Z"): ("q_return", "Z", "L"),
        ("q_return", "b"): ("q_return", "b", "L"),
        ("q_return", "Y"): ("q_return", "Y", "L"),
        ("q_return", "a"): ("q_return", "a", "L"),
        ("q_return", "X"): ("q0", "X", "R"),  # Found X, start next iteration

        # q_verify_blank: Ensure no stray a, b, or c remains
        ("q_verify_blank", "Y"): ("q_verify_blank", "Y", "R"),
        ("q_verify_blank", "Z"): ("q_verify_blank", "Z", "R"),
        ("q_verify_blank", "⊔"): ("q_accept", "⊔", "R"),
    }

    return TuringMachine(
        states=states,
        input_alphabet=input_alphabet,
        tape_alphabet=tape_alphabet,
        transitions=transitions,
        start_state="q0",
        accept_state="q_accept",
        reject_state="q_reject",
    )


def create_binary_incrementer() -> TuringMachine:
    """
    Turing Machine that computes f(w) = w + 1 in binary notation.
    """
    states = {"q_scan_end", "q_add", "q_accept"}
    input_alphabet = {"0", "1"}
    tape_alphabet = {"0", "1", "⊔"}

    transitions = {
        # Scan to the end of the binary string
        ("q_scan_end", "0"): ("q_scan_end", "0", "R"),
        ("q_scan_end", "1"): ("q_scan_end", "1", "R"),
        ("q_scan_end", "⊔"): ("q_add", "⊔", "L"),

        # Add 1 with ripple carry
        ("q_add", "0"): ("q_accept", "1", "R"),
        ("q_add", "1"): ("q_add", "0", "L"),
        ("q_add", "⊔"): ("q_accept", "1", "R"),
    }

    return TuringMachine(
        states=states,
        input_alphabet=input_alphabet,
        tape_alphabet=tape_alphabet,
        transitions=transitions,
        start_state="q_scan_end",
        accept_state="q_accept",
        reject_state="q_reject",
    )


def test_turing_machine_suite():
    print("[TEST 1] Testing Decider for non-context-free language L = {a^n b^n c^n | n >= 1}...")
    tm = create_an_bn_cn_decider()

    # Valid strings
    valid_test_cases = ["abc", "aabbcc", "aaabbbccc"]
    for s in valid_test_cases:
        accepted, steps, tape = tm.run(s)
        assert accepted, f"Expected acceptance for {s}, but got rejection"
        print(f"  -> Accepted '{s}' in {steps} steps.")

    # Invalid strings
    invalid_test_cases = ["ab", "aabc", "abbc", "abcc", "ba", "cbaf", "", "aabbccc"]
    for s in invalid_test_cases:
        if any(c not in tm.input_alphabet for c in s):
            continue
        accepted, steps, tape = tm.run(s)
        assert not accepted, f"Expected rejection for '{s}', but got acceptance"
    print("  -> Rejections verified on all non-matching strings.")

    print("[TEST 2] Testing Binary Incrementer Turing Machine...")
    inc_tm = create_binary_incrementer()
    
    test_increments = [
        ("0", "1"),
        ("1", "10"),
        ("10", "11"),
        ("11", "100"),
        ("1011", "1100"),
        ("1111", "10000")
    ]
    for inp, expected in test_increments:
        accepted, steps, output = inc_tm.run(inp)
        assert accepted, f"Incrementer failed on {inp}"
        assert output == expected, f"For input {inp}, expected {expected}, got {output}"
        print(f"  -> {inp} + 1 = {output} (Verified in {steps} steps)")

    print("ALL Level 4 Chapter 06 Turing Machine lab tests passed successfully!")


if __name__ == "__main__":
    test_turing_machine_suite()
