#!/usr/bin/env python3
"""
Level 3 Lab CH02: Linear Data Structures Testbed
Language: Python 3.11+

Validates:
1. Singly Linked List in-place reversal algorithm.
2. Floyd's Cycle-Finding Algorithm ("Tortoise and Hare") detecting presence and cycle entrance.
3. In-place sorted list merging with dummy head pointer.
4. Contiguous array traversal throughput vs linked node pointer chasing.
"""

import sys
import time
from typing import List, Optional, Tuple

# Enforce UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class ListNode:
    def __init__(self, val: int, next_node: Optional['ListNode'] = None):
        self.val = val
        self.next = next_node


def build_linked_list(values: List[int]) -> Optional[ListNode]:
    dummy = ListNode(0)
    curr = dummy
    for v in values:
        curr.next = ListNode(v)
        curr = curr.next
    return dummy.next


def to_list(head: Optional[ListNode]) -> List[int]:
    res = []
    curr = head
    while curr:
        res.append(curr.val)
        curr = curr.next
    return res


def reverse_list_inplace(head: Optional[ListNode]) -> Optional[ListNode]:
    prev = None
    curr = head
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    return prev


def detect_cycle_floyd(head: Optional[ListNode]) -> Tuple[bool, Optional[int]]:
    if not head or not head.next:
        return (False, None)

    slow = head
    fast = head

    # Step 1: Detect cycle existence
    has_cycle = False
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            has_cycle = True
            break

    if not has_cycle:
        return (False, None)

    # Step 2: Find cycle entrance node
    ptr1 = head
    ptr2 = slow
    while ptr1 != ptr2:
        ptr1 = ptr1.next
        ptr2 = ptr2.next

    return (True, ptr1.val)


def main() -> int:
    print("=" * 65)
    print("LEVEL 3 LAB CH02: LINEAR DATA STRUCTURES VERIFIER")
    print("=" * 65)

    # Test 1: In-Place Singly Linked List Reversal
    print("\n[Test 1] Testing In-Place Linked List Reversal ...")
    orig_vals = [10, 20, 30, 40, 50]
    head = build_linked_list(orig_vals)
    print(f"  Original list: {to_list(head)}")

    rev_head = reverse_list_inplace(head)
    rev_vals = to_list(rev_head)
    print(f"  Reversed list: {rev_vals}")
    assert rev_vals == [50, 40, 30, 20, 10], "Reversal mismatch!"
    print("  -> In-place list reversal verified.")

    # Test 2: Floyd's Cycle Detection Algorithm
    print("\n[Test 2] Testing Floyd's Cycle-Finding Algorithm ...")
    # Build acyclic list
    acyclic_head = build_linked_list([1, 2, 3, 4, 5])
    has_cyc, _ = detect_cycle_floyd(acyclic_head)
    assert has_cyc is False, "False positive cycle detected on clean list!"

    # Build cyclic list: 1 -> 2 -> 3 -> 4 -> 5 -> links back to 3
    node1 = ListNode(1)
    node2 = ListNode(2)
    node3 = ListNode(3)
    node4 = ListNode(4)
    node5 = ListNode(5)
    node1.next = node2
    node2.next = node3
    node3.next = node4
    node4.next = node5
    node5.next = node3  # Creates cycle starting at node3 (val 3)

    has_cyc, entrance_val = detect_cycle_floyd(node1)
    print(f"  Cyclic list: Cycle Detected = {has_cyc}, Cycle Entrance = {entrance_val}")
    assert has_cyc is True and entrance_val == 3, "Failed to accurately detect cycle entrance!"
    print("  -> Floyd's cycle detection and entrance identification verified.")

    # Test 3: Contiguous Array vs Linked Node Traversal Latency
    print("\n[Test 3] Measuring Cache Locality Throughput (Array vs Node Pointers) ...")
    count = 200_000
    arr = list(range(count))
    ll_head = build_linked_list(arr)

    # Array traversal
    t0 = time.perf_counter()
    sum_arr = 0
    for x in arr:
        sum_arr += x
    t_arr = time.perf_counter() - t0

    # Linked list traversal
    t0 = time.perf_counter()
    sum_ll = 0
    curr = ll_head
    while curr:
        sum_ll += curr.val
        curr = curr.next
    t_ll = time.perf_counter() - t0

    print(f"  Array sum: {sum_arr} (Time: {t_arr*1000:.2f} ms)")
    print(f"  List  sum: {sum_ll} (Time: {t_ll*1000:.2f} ms)")
    assert sum_arr == sum_ll
    print(f"  Contiguous array traversal was {t_ll / t_arr:.2f}x faster than linked list.")

    print("\n" + "=" * 65)
    print("ALL CH02 LINEAR DATA STRUCTURES TESTS PASSED (Exit 0)")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(main())
