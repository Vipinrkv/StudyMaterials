#!/usr/bin/env python3
"""
Level 3 Lab CH05: Self-Balancing Trees (AVL & Red-Black) Testbed
Language: Python 3.11+

Validates:
1. Complete AVL Tree insertion with the four rebalancing rotations:
   - Left-Left (LL): Single Right Rotation
   - Right-Right (RR): Single Left Rotation
   - Left-Right (LR): Double Left-Right Rotation
   - Right-Left (RL): Double Right-Left Rotation
2. Balance Factor invariant enforcement: |BF| <= 1 for all nodes.
3. Strict logarithmic height bound (h <= 1.44 * log2(n)) under worst-case sorted inputs.
4. Red-Black Tree 5-Property Validator.
"""

import math
import sys
from typing import List, Optional, Tuple

# Enforce UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class AVLNode:
    def __init__(self, key: int):
        self.key = key
        self.height = 1
        self.left: Optional['AVLNode'] = None
        self.right: Optional['AVLNode'] = None


class AVLTree:
    def __init__(self):
        self.root: Optional[AVLNode] = None

    def _get_height(self, node: Optional[AVLNode]) -> int:
        return node.height if node else 0

    def _get_balance(self, node: Optional[AVLNode]) -> int:
        return self._get_height(node.left) - self._get_height(node.right) if node else 0

    def _rotate_right(self, y: AVLNode) -> AVLNode:
        x = y.left
        assert x is not None
        T2 = x.right

        # Perform rotation
        x.right = y
        y.left = T2

        # Update heights (Child first!)
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        x.height = 1 + max(self._get_height(x.left), self._get_height(x.right))
        return x

    def _rotate_left(self, x: AVLNode) -> AVLNode:
        y = x.right
        assert y is not None
        T2 = y.left

        # Perform rotation
        y.left = x
        x.right = T2

        # Update heights
        x.height = 1 + max(self._get_height(x.left), self._get_height(x.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        return y

    def insert(self, key: int) -> None:
        self.root = self._insert_node(self.root, key)

    def _insert_node(self, node: Optional[AVLNode], key: int) -> AVLNode:
        if node is None:
            return AVLNode(key)

        if key < node.key:
            node.left = self._insert_node(node.left, key)
        elif key > node.key:
            node.right = self._insert_node(node.right, key)
        else:
            return node  # Duplicate keys ignored

        # Update height
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))

        # Check balance factor
        balance = self._get_balance(node)

        # Case 1: Left-Left (LL)
        if balance > 1 and node.left and key < node.left.key:
            return self._rotate_right(node)

        # Case 2: Right-Right (RR)
        if balance < -1 and node.right and key > node.right.key:
            return self._rotate_left(node)

        # Case 3: Left-Right (LR)
        if balance > 1 and node.left and key > node.left.key:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # Case 4: Right-Left (RL)
        if balance < -1 and node.right and key < node.right.key:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def is_balanced(self) -> bool:
        """Verifies that EVERY node in the tree strictly satisfies |BF| <= 1."""
        def _check(node: Optional[AVLNode]) -> bool:
            if not node:
                return True
            bf = self._get_balance(node)
            if abs(bf) > 1:
                return False
            return _check(node.left) and _check(node.right)
        return _check(self.root)

    def get_height(self) -> int:
        return self._get_height(self.root)

    def in_order(self) -> List[int]:
        res = []
        def _inorder(node: Optional[AVLNode]):
            if node:
                _inorder(node.left)
                res.append(node.key)
                _inorder(node.right)
        _inorder(self.root)
        return res


# Red-Black Tree Invariant Validator
RED = 0
BLACK = 1


class RBNode:
    def __init__(self, key: int, color: int = RED):
        self.key = key
        self.color = color
        self.left: Optional['RBNode'] = None
        self.right: Optional['RBNode'] = None


def validate_red_black_invariants(root: Optional[RBNode]) -> Tuple[bool, str]:
    if root is None:
        return (True, "Empty tree is valid RB-Tree")

    # Property 2: Root must be BLACK
    if root.color != BLACK:
        return (False, "Violation: Root node must be BLACK")

    def _check_properties(node: Optional[RBNode]) -> Tuple[bool, int, str]:
        if node is None:
            # Property 3: NIL leaves are BLACK (contributes 1 to black-height)
            return (True, 1, "")

        # Property 4: No two consecutive RED nodes
        if node.color == RED:
            if (node.left and node.left.color == RED) or (node.right and node.right.color == RED):
                return (False, -1, f"Violation: Consecutive RED nodes found at key {node.key}")

        left_ok, left_bh, err_l = _check_properties(node.left)
        if not left_ok:
            return (False, -1, err_l)

        right_ok, right_bh, err_r = _check_properties(node.right)
        if not right_ok:
            return (False, -1, err_r)

        # Property 5: Equal black-height across all paths
        if left_bh != right_bh:
            return (False, -1, f"Violation: Black-height mismatch at key {node.key} (L={left_bh}, R={right_bh})")

        bh = left_bh + (1 if node.color == BLACK else 0)
        return (True, bh, "")

    valid, _, msg = _check_properties(root)
    return (valid, msg if not valid else "Valid Red-Black Tree")


def main() -> int:
    print("=" * 65)
    print("LEVEL 3 LAB CH05: AVL & RED-BLACK TREE BALANCING VERIFIER")
    print("=" * 65)

    # Test 1: AVL Tree Rotations & Invariant Verification
    print("\n[Test 1] Testing AVL Tree Rotations on Sequential Input ...")
    avl = AVLTree()
    # Insert 1 to 31 in sorted order (Would create a height 31 line in naive BST!)
    for x in range(1, 32):
        avl.insert(x)

    print(f"  Inserted 31 sequential keys into AVL tree.")
    print(f"  Measured AVL Tree Height = {avl.get_height()}")
    # Theoretical ideal height of 31 nodes = ceil(log2(32)) = 5
    assert avl.get_height() <= 6, f"AVL height {avl.get_height()} exceeds bound!"
    assert avl.is_balanced() is True, "AVL balance factor invariant violated!"
    assert avl.in_order() == list(range(1, 32)), "In-order traversal corrupted!"
    print("  -> AVL balance factor |BF| <= 1 maintained at all 31 nodes.")

    # Test 2: Large-Scale Worst-Case Insertion (1,000 Sorted Elements)
    print("\n[Test 2] Testing 1,000 Sorted Elements Worst-Case AVL Balancing ...")
    large_avl = AVLTree()
    for x in range(1, 1001):
        large_avl.insert(x)

    measured_h = large_avl.get_height()
    max_allowed_h = math.floor(1.4404 * math.log2(1000 + 2))
    print(f"  Nodes: 1,000 | Measured Height: {measured_h} | Max Theoretical Bound: {max_allowed_h}")
    assert measured_h <= max_allowed_h, f"Height {measured_h} exceeded AVL theoretical bound {max_allowed_h}!"
    assert large_avl.is_balanced() is True
    print("  -> 1,000-node AVL tree strictly bounded to logarithmic height.")

    # Test 3: Red-Black Tree Invariant Validator
    print("\n[Test 3] Testing Red-Black Tree 5-Property Invariant Validator ...")
    # Build valid Red-Black tree:
    #         20 (B)
    #        /      \
    #     10 (B)   30 (B)
    #               /
    #            25 (R)
    rb_root = RBNode(20, BLACK)
    rb_root.left = RBNode(10, BLACK)
    rb_root.right = RBNode(30, BLACK)
    rb_root.right.left = RBNode(25, RED)

    is_valid, msg = validate_red_black_invariants(rb_root)
    print(f"  Valid RB-Tree Check: {is_valid} ({msg})")
    assert is_valid is True

    # Intentionally violate Property 4 (Consecutive REDs)
    rb_root.right.left.left = RBNode(22, RED)  # Red parent 25, Red child 22!
    is_valid_bad, msg_bad = validate_red_black_invariants(rb_root)
    print(f"  Corrupted Tree Check (Consecutive RED): {is_valid_bad} -> {msg_bad}")
    assert is_valid_bad is False and "Consecutive RED" in msg_bad
    print("  -> Red-Black Property 4 violation successfully trapped.")

    print("\n" + "=" * 65)
    print("ALL CH05 AVL & RED-BLACK TREE TESTS PASSED (Exit 0)")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(main())
