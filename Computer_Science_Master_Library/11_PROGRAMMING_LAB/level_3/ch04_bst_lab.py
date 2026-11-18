#!/usr/bin/env python3
"""
Level 3 Lab CH04: Trees and Binary Search Trees (BST) Testbed
Language: Python 3.11+

Validates:
1. BST insertion, search, and all three deletion cases (Leaf, One child, Two children).
2. In-order traversal ascending sorted guarantee.
3. Lowest Common Ancestor (LCA) query accuracy.
4. Degenerate tree height (O(n)) vs balanced tree height (O(log n)).
"""

import sys
from typing import List, Optional

# Enforce UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class BSTNode:
    def __init__(self, key: int):
        self.key = key
        self.left: Optional['BSTNode'] = None
        self.right: Optional['BSTNode'] = None


class BinarySearchTree:
    def __init__(self):
        self.root: Optional[BSTNode] = None

    def insert(self, key: int) -> None:
        self.root = self._insert_node(self.root, key)

    def _insert_node(self, node: Optional[BSTNode], key: int) -> BSTNode:
        if node is None:
            return BSTNode(key)
        if key < node.key:
            node.left = self._insert_node(node.left, key)
        elif key > node.key:
            node.right = self._insert_node(node.right, key)
        return node

    def search(self, key: int) -> bool:
        curr = self.root
        while curr:
            if curr.key == key:
                return True
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        return False

    def in_order(self) -> List[int]:
        res = []
        def _inorder(node: Optional[BSTNode]):
            if node:
                _inorder(node.left)
                res.append(node.key)
                _inorder(node.right)
        _inorder(self.root)
        return res

    def delete(self, key: int) -> None:
        self.root = self._delete_node(self.root, key)

    def _delete_node(self, node: Optional[BSTNode], key: int) -> Optional[BSTNode]:
        if node is None:
            return None

        if key < node.key:
            node.left = self._delete_node(node.left, key)
        elif key > node.key:
            node.right = self._delete_node(node.right, key)
        else:
            # Case 1 & 2: Zero or one child
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left

            # Case 3: Two children (Find In-Order Successor)
            succ = node.right
            while succ.left is not None:
                succ = succ.left
            node.key = succ.key
            node.right = self._delete_node(node.right, succ.key)

        return node

    def height(self) -> int:
        def _h(node: Optional[BSTNode]) -> int:
            if not node:
                return 0
            return 1 + max(_h(node.left), _h(node.right))
        return _h(self.root)

    def lowest_common_ancestor(self, p: int, q: int) -> Optional[int]:
        curr = self.root
        while curr:
            if p < curr.key and q < curr.key:
                curr = curr.left
            elif p > curr.key and q > curr.key:
                curr = curr.right
            else:
                return curr.key
        return None


def main() -> int:
    print("=" * 65)
    print("LEVEL 3 LAB CH04: BINARY SEARCH TREE (BST) VERIFIER")
    print("=" * 65)

    bst = BinarySearchTree()
    keys = [50, 30, 70, 20, 40, 60, 80]
    for k in keys:
        bst.insert(k)

    # Test 1: In-order traversal sorted check
    print("\n[Test 1] Verifying BST In-Order Traversal Invariant ...")
    inorder_res = bst.in_order()
    print(f"  Inserted: {keys}")
    print(f"  In-Order: {inorder_res}")
    assert inorder_res == sorted(keys), "In-order traversal is not sorted!"

    # Test 2: Search Verification
    print("\n[Test 2] Testing BST Key Search ...")
    assert bst.search(40) is True
    assert bst.search(99) is False
    print("  Search lookups verified.")

    # Test 3: Lowest Common Ancestor (LCA)
    print("\n[Test 3] Testing Lowest Common Ancestor (LCA) ...")
    lca_20_40 = bst.lowest_common_ancestor(20, 40)
    lca_20_80 = bst.lowest_common_ancestor(20, 80)
    print(f"  LCA(20, 40) = {lca_20_40} (Expected 30)")
    print(f"  LCA(20, 80) = {lca_20_80} (Expected 50)")
    assert lca_20_40 == 30 and lca_20_80 == 50

    # Test 4: Deletion Cases
    print("\n[Test 4] Testing BST Deletion Cases ...")
    # Case 1: Delete Leaf (20)
    bst.delete(20)
    assert bst.in_order() == [30, 40, 50, 60, 70, 80]
    print("  Case 1 (Delete leaf 20) passed.")

    # Case 2: Delete Node with One Child (30 has child 40)
    bst.delete(30)
    assert bst.in_order() == [40, 50, 60, 70, 80]
    print("  Case 2 (Delete node with 1 child 30) passed.")

    # Case 3: Delete Root with Two Children (50 has left 40, right 70)
    bst.delete(50)
    assert bst.in_order() == [40, 60, 70, 80]
    print("  Case 3 (Delete root with 2 children 50) passed.")

    # Test 5: Height comparison under sorted input (Degenerate tree)
    print("\n[Test 5] Measuring Skewed Tree Height Degradation ...")
    skewed_bst = BinarySearchTree()
    for x in range(1, 101):
        skewed_bst.insert(x)
    print(f"  Height of 100 sequentially inserted keys = {skewed_bst.height()} (Degenerate O(n) line!)")
    assert skewed_bst.height() == 100, "Expected linear skewed height of 100!"

    print("\n" + "=" * 65)
    print("ALL CH04 BINARY SEARCH TREE TESTS PASSED (Exit 0)")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(main())
