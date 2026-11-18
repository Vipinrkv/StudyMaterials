#!/usr/bin/env python3
"""
Level 3 Lab CH03: Stacks, Queues, and Deques Testbed
Language: Python 3.11+

Validates:
1. Power-of-two Circular Ring Buffer with bitwise index masking (mask = cap - 1).
2. Balanced parentheses verification.
3. Dijkstra's Shunting-Yard Infix to Postfix converter and evaluation.
4. Monotonic Deque Sliding Window Maximum in strict O(n) linear time.
"""

from collections import deque
import sys
from typing import List, Optional

# Enforce UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class FastRingBuffer:
    def __init__(self, power_of_two_cap: int = 8):
        assert (power_of_two_cap & (power_of_two_cap - 1)) == 0, "Capacity must be power of two"
        self.capacity = power_of_two_cap
        self.mask = power_of_two_cap - 1
        self.buffer = [None] * power_of_two_cap
        self.head = 0  # Read ptr
        self.tail = 0  # Write ptr

    def enqueue(self, val: int) -> bool:
        if ((self.tail + 1) & self.mask) == (self.head & self.mask):
            return False  # Full
        self.buffer[self.tail & self.mask] = val
        self.tail += 1
        return True

    def dequeue(self) -> Optional[int]:
        if (self.head & self.mask) == (self.tail & self.mask):
            return None  # Empty
        val = self.buffer[self.head & self.mask]
        self.head += 1
        return val


def is_balanced_brackets(s: str) -> bool:
    stack = []
    pairs = {')': '(', '}': '{', ']': '['}
    for char in s:
        if char in "({[":
            stack.append(char)
        elif char in ")}]":
            if not stack or stack[-1] != pairs[char]:
                return False
            stack.pop()
    return len(stack) == 0


def infix_to_postfix(expr: str) -> str:
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
    output = []
    stack = []

    for token in expr.split():
        if token.isdigit():
            output.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if stack and stack[-1] == '(':
                stack.pop()
        else:
            # Operator
            while (stack and stack[-1] != '(' and
                   precedence.get(stack[-1], 0) >= precedence.get(token, 0)):
                output.append(stack.pop())
            stack.append(token)

    while stack:
        output.append(stack.pop())

    return " ".join(output)


def sliding_window_max(nums: List[int], k: int) -> List[int]:
    """Monotonic deque implementation achieving O(n) time."""
    if not nums or k <= 0:
        return []

    dq = deque()  # Stores indices of elements in monotonically decreasing order
    result = []

    for i, n in enumerate(nums):
        # 1. Pop elements from front that are outside current window
        while dq and dq[0] < i - k + 1:
            dq.popleft()

        # 2. Pop elements from back that are smaller than current element
        while dq and nums[dq[-1]] <= n:
            dq.pop()

        dq.append(i)

        # 3. Add to result once first window is formed
        if i >= k - 1:
            result.append(nums[dq[0]])

    return result


def main() -> int:
    print("=" * 65)
    print("LEVEL 3 LAB CH03: STACKS, QUEUES & MONOTONIC STRUCTURES")
    print("=" * 65)

    # Test 1: Power-of-Two Ring Buffer
    print("\n[Test 1] Testing Power-of-Two Fast Ring Buffer ...")
    rb = FastRingBuffer(power_of_two_cap=4)
    assert rb.enqueue(10) is True
    assert rb.enqueue(20) is True
    assert rb.enqueue(30) is True
    assert rb.enqueue(40) is False  # Capacity 4 holds 3 items with sacrificial slot
    print("  Enqueue 10, 20, 30 succeeded; 4th enqueue rejected (Buffer Full).")

    assert rb.dequeue() == 10
    assert rb.dequeue() == 20
    assert rb.enqueue(40) is True  # Wrapped enqueue
    assert rb.dequeue() == 30
    assert rb.dequeue() == 40
    assert rb.dequeue() is None   # Buffer Empty
    print("  Wrapped FIFO dequeue verified.")

    # Test 2: Balanced Parentheses
    print("\n[Test 2] Testing Balanced Parentheses ...")
    assert is_balanced_brackets("{[()()]}") is True
    assert is_balanced_brackets("{[(])}") is False
    assert is_balanced_brackets("(((") is False
    print("  Parentheses matching logic verified.")

    # Test 3: Dijkstra's Shunting-Yard Infix to Postfix
    print("\n[Test 3] Testing Shunting-Yard Infix to Postfix Conversion ...")
    infix = "3 + 4 * 2 / ( 1 - 5 )"
    postfix = infix_to_postfix(infix)
    print(f"  Infix:   {infix}")
    print(f"  Postfix: {postfix}")
    assert postfix == "3 4 2 * 1 5 - / +", f"Unexpected postfix output: {postfix}"

    # Test 4: Monotonic Deque Sliding Window Maximum (O(n))
    print("\n[Test 4] Testing Sliding Window Maximum (Monotonic Queue) ...")
    test_array = [1, 3, -1, -3, 5, 3, 6, 7]
    k_window = 3
    window_maxes = sliding_window_max(test_array, k_window)
    print(f"  Input Array: {test_array}, k = {k_window}")
    print(f"  Sliding Max: {window_maxes}")
    assert window_maxes == [3, 3, 5, 5, 6, 7], "Sliding window maximum mismatch!"
    print("  -> Monotonic sliding window max verified.")

    print("\n" + "=" * 65)
    print("ALL CH03 STACK, QUEUE & DEQUE TESTS PASSED (Exit 0)")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(main())
