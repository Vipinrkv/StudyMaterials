"""
ch07_crdt_collaborative_lab.py
Level 8 Chapter 07 Companion Laboratory: Conflict-Free Replicated Data Types (CRDTs).
Implements PN-Counter (Positive-Negative), OR-Set (Observed-Remove with Tombstones),
and Replicated Growable Array (RGA) for Concurrent Text Editing.
Pure Python/Standard Library with zero external dependencies.
"""

from __future__ import annotations
import sys
import uuid
from typing import Dict, List, Set, Tuple, Optional, Any

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")


class PnCounter:
    """Positive-Negative Counter CRDT supporting concurrent increments and decrements."""
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.P: Dict[str, int] = {}
        self.N: Dict[str, int] = {}

    def increment(self, val: int = 1) -> None:
        self.P[self.node_id] = self.P.get(self.node_id, 0) + val

    def decrement(self, val: int = 1) -> None:
        self.N[self.node_id] = self.N.get(self.node_id, 0) + val

    def value(self) -> int:
        return sum(self.P.values()) - sum(self.N.values())

    def merge(self, other: PnCounter) -> PnCounter:
        merged = PnCounter(self.node_id)
        all_nodes = set(self.P.keys()) | set(other.P.keys()) | set(self.N.keys()) | set(other.N.keys())
        for n in all_nodes:
            merged.P[n] = max(self.P.get(n, 0), other.P.get(n, 0))
            merged.N[n] = max(self.N.get(n, 0), other.N.get(n, 0))
        return merged


class OrSet:
    """Observed-Remove Set (OR-Set) supporting concurrent additions and deletions."""
    def __init__(self):
        self.add_set: Set[Tuple[str, str]] = set()   # (element, tag)
        self.rem_set: Set[Tuple[str, str]] = set()   # (element, tag)

    def add(self, element: str) -> str:
        tag = str(uuid.uuid4())[:8]
        self.add_set.add((element, tag))
        return tag

    def remove(self, element: str) -> None:
        for item in self.add_set:
            if item[0] == element:
                self.rem_set.add(item)

    def read(self) -> Set[str]:
        active = self.add_set - self.rem_set
        return {item[0] for item in active}

    def merge(self, other: OrSet) -> OrSet:
        merged = OrSet()
        merged.add_set = self.add_set | other.add_set
        merged.rem_set = self.rem_set | other.rem_set
        return merged


class RgaNode:
    """Node in Replicated Growable Array (RGA) linked list."""
    def __init__(self, node_id: str, char: str, parent_id: Optional[str] = None):
        self.id = node_id
        self.char = char
        self.parent_id = parent_id
        self.deleted = False

    def __repr__(self) -> str:
        return f"Node({self.id}, '{self.char}', del={self.deleted})"


class RgaTextEngine:
    """Replicated Growable Array (RGA) for collaborative text document synchronization."""
    def __init__(self, site_id: str):
        self.site_id = site_id
        self.seq = 0
        self.nodes: List[RgaNode] = []

    def insert_after(self, parent_id: Optional[str], char: str) -> str:
        self.seq += 1
        new_id = f"{self.site_id}_{self.seq}"
        new_node = RgaNode(new_id, char, parent_id)

        if parent_id is None:
            self.nodes.insert(0, new_node)
        else:
            idx = next(i for i, n in enumerate(self.nodes) if n.id == parent_id)
            insert_pos = idx + 1
            while insert_pos < len(self.nodes) and self.nodes[insert_pos].parent_id == parent_id:
                if self.nodes[insert_pos].id > new_id:
                    insert_pos += 1
                else:
                    break
            self.nodes.insert(insert_pos, new_node)
        return new_id

    def delete(self, node_id: str) -> None:
        for n in self.nodes:
            if n.id == node_id:
                n.deleted = True
                break

    def text(self) -> str:
        return "".join(n.char for n in self.nodes if not n.deleted)

    def merge(self, other: RgaTextEngine) -> None:
        existing_ids = {n.id: n for n in self.nodes}
        for remote_node in other.nodes:
            if remote_node.id in existing_ids:
                if remote_node.deleted:
                    existing_ids[remote_node.id].deleted = True
            else:
                p_id = remote_node.parent_id
                if p_id is None:
                    insert_pos = 0
                    while insert_pos < len(self.nodes) and self.nodes[insert_pos].parent_id is None:
                        if self.nodes[insert_pos].id > remote_node.id:
                            insert_pos += 1
                        else:
                            break
                    self.nodes.insert(insert_pos, RgaNode(remote_node.id, remote_node.char, None))
                else:
                    p_idx = next((i for i, n in enumerate(self.nodes) if n.id == p_id), -1)
                    if p_idx != -1:
                        insert_pos = p_idx + 1
                        while insert_pos < len(self.nodes) and self.nodes[insert_pos].parent_id == p_id:
                            if self.nodes[insert_pos].id > remote_node.id:
                                insert_pos += 1
                            else:
                                break
                        self.nodes.insert(insert_pos, RgaNode(remote_node.id, remote_node.char, p_id))


def main() -> None:
    print("=" * 70)
    print("LEVEL 8 CHAPTER 07: CONFLICT-FREE REPLICATED DATA TYPES (CRDTS) LAB")
    print("=" * 70)

    # 1. Test PN-Counter CRDT
    print("\n[Test 1] Testing PN-Counter Distributed Merge...")
    c_a = PnCounter("node_a")
    c_b = PnCounter("node_b")

    c_a.increment(10)
    c_a.decrement(3)  # Net = 7

    c_b.increment(20)
    c_b.decrement(5)  # Net = 15

    # Merge bidirectionally
    merged_a = c_a.merge(c_b)
    merged_b = c_b.merge(c_a)

    assert merged_a.value() == 22, f"Expected 22 (10-3 + 20-5), got {merged_a.value()}"
    assert merged_b.value() == 22
    print(f"  -> Merged Counter Value: {merged_a.value()} (Commutative convergence verified).")

    # 2. Test OR-Set CRDT
    print("\n[Test 2] Testing Observed-Remove Set (OR-Set) Add-Wins Semantics...")
    s_a = OrSet()
    s_b = OrSet()

    s_a.add("apple")
    s_a.add("banana")

    # Sync A to B
    s_b = s_b.merge(s_a)
    assert s_b.read() == {"apple", "banana"}

    # Concurrent actions: B removes "apple", A concurrently re-adds "apple"
    s_b.remove("apple")
    tag_readd = s_a.add("apple")

    # Merge after partition healing
    final_set = s_a.merge(s_b)
    # The new add should win over the old remove because of distinct tag
    assert "apple" in final_set.read(), "New addition must win over concurrent deletion of prior instance!"
    print(f"  -> OR-Set Active Elements: {final_set.read()} (Add-Wins verified).")

    # 3. Test RGA Collaborative Text Sequence CRDT
    print("\n[Test 3] Testing Replicated Growable Array (RGA) Text Synchronization...")
    doc_a = RgaTextEngine("userA")
    doc_b = RgaTextEngine("userB")

    # Shared initial text: "CAT"
    id_c = doc_a.insert_after(None, "C")
    id_a = doc_a.insert_after(id_c, "A")
    id_t = doc_a.insert_after(id_a, "T")
    doc_b.merge(doc_a)

    assert doc_a.text() == "CAT"
    assert doc_b.text() == "CAT"

    # User A modifies to "CHAT" (inserts 'H' after 'C')
    doc_a.insert_after(id_c, "H")

    # User B concurrently modifies to "COAT" (inserts 'O' after 'C')
    doc_b.insert_after(id_c, "O")

    # Merge both documents
    doc_a.merge(doc_b)
    doc_b.merge(doc_a)

    print(f"  -> Doc A Converged Text: '{doc_a.text()}'")
    print(f"  -> Doc B Converged Text: '{doc_b.text()}'")
    assert doc_a.text() == doc_b.text(), "RGA documents must converge to identical string!"
    assert doc_a.text() in ("CHOAT", "COHAT")
    print("  -> Deterministic Concurrent Text Convergence: VERIFIED.")

    print("\n" + "=" * 70)
    print("ALL CRDT COLLABORATION TESTS PASSED (Exit Code 0).")
    print("=" * 70)
    sys.exit(0)


if __name__ == "__main__":
    main()
