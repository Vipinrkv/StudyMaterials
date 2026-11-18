"""
Level 9 Programming Lab - Chapter 01: Substructural Types & Borrow Checker
Implements an Affine and Linear Type Environment with Move Semantics and Aliasing Invariants.
"""
import sys
from typing import Dict, Set, Optional, List
from enum import Enum

sys.stdout.reconfigure(encoding="utf-8")

class BorrowKind(Enum):
    SHARED = 1
    EXCLUSIVE = 2

class AffineError(Exception):
    pass

class AffineUseAfterMoveError(AffineError):
    pass

class BorrowConflictError(AffineError):
    pass

class LinearResourceLeakError(AffineError):
    pass

class AffineVariable:
    def __init__(self, name: str, val_type: str, is_linear: bool = False):
        self.name = name
        self.val_type = val_type
        self.is_linear = is_linear
        self.is_moved = False
        self.shared_borrows: int = 0
        self.exclusive_borrow: bool = False

class SubstructuralTypeChecker:
    def __init__(self):
        self.env: Dict[str, AffineVariable] = {}
        self.active_borrows: Dict[str, BorrowKind] = {}

    def declare(self, name: str, val_type: str, is_linear: bool = False) -> None:
        if name in self.env:
            raise AffineError(f"Variable {name} already declared.")
        self.env[name] = AffineVariable(name, val_type, is_linear)

    def read(self, name: str) -> None:
        var = self._get_valid(name)
        if var.exclusive_borrow:
            raise BorrowConflictError(f"Cannot read {name} while an exclusive borrow is active.")

    def move(self, src: str, dst: str) -> None:
        var = self._get_valid(src)
        if var.shared_borrows > 0 or var.exclusive_borrow:
            raise BorrowConflictError(f"Cannot move {src} while actively borrowed.")
        var.is_moved = True
        self.declare(dst, var.val_type, is_linear=var.is_linear)

    def borrow_shared(self, name: str, borrow_id: str) -> None:
        var = self._get_valid(name)
        if var.exclusive_borrow:
            raise BorrowConflictError(f"Cannot borrow {name} as shared while exclusively borrowed.")
        var.shared_borrows += 1
        self.active_borrows[borrow_id] = BorrowKind.SHARED

    def borrow_exclusive(self, name: str, borrow_id: str) -> None:
        var = self._get_valid(name)
        if var.shared_borrows > 0:
            raise BorrowConflictError(f"Cannot borrow {name} as exclusive while {var.shared_borrows} shared borrows exist.")
        if var.exclusive_borrow:
            raise BorrowConflictError(f"Cannot borrow {name} as exclusive while already exclusively borrowed.")
        var.exclusive_borrow = True
        self.active_borrows[borrow_id] = BorrowKind.EXCLUSIVE

    def release_borrow(self, name: str, borrow_id: str) -> None:
        if borrow_id not in self.active_borrows:
            raise AffineError(f"Borrow {borrow_id} not found.")
        kind = self.active_borrows.pop(borrow_id)
        var = self.env[name]
        if kind == BorrowKind.SHARED:
            var.shared_borrows -= 1
        elif kind == BorrowKind.EXCLUSIVE:
            var.exclusive_borrow = False

    def consume(self, name: str) -> None:
        var = self._get_valid(name)
        if var.shared_borrows > 0 or var.exclusive_borrow:
            raise BorrowConflictError(f"Cannot consume {name} while actively borrowed.")
        var.is_moved = True

    def close_scope(self) -> None:
        # Check for linear leaks
        for name, var in self.env.items():
            if var.is_linear and not var.is_moved:
                raise LinearResourceLeakError(f"Linear resource '{name}' went out of scope without being consumed!")

    def _get_valid(self, name: str) -> AffineVariable:
        if name not in self.env:
            raise AffineError(f"Variable '{name}' not found.")
        var = self.env[name]
        if var.is_moved:
            raise AffineUseAfterMoveError(f"Use of moved value: '{name}'.")
        return var


def test_substructural_type_checker():
    print("===========================================================================")
    print("SUBSTRUCTURAL TYPE CHECKER & BORROW VERIFICATION TESTBED")
    print("LEVEL 9 LAB - CHAPTER 01")
    print("===========================================================================")

    tc = SubstructuralTypeChecker()

    # 1. Test Affine Move Semantics
    print("[Test 1/4] Affine Move Semantics & Use-After-Move Detection...")
    tc.declare("buffer_a", "RawBuffer")
    tc.read("buffer_a")
    tc.move("buffer_a", "buffer_b")
    try:
        tc.read("buffer_a")
        assert False, "Should have raised AffineUseAfterMoveError"
    except AffineUseAfterMoveError as e:
        print(f"  -> Successfully caught use-after-move: {e}")

    # 2. Test Aliasing XOR Mutability Invariant
    print("[Test 2/4] Aliasing XOR Mutability Invariant...")
    tc.declare("packet", "NetworkPacket")
    tc.borrow_shared("packet", "ref_shared_1")
    tc.borrow_shared("packet", "ref_shared_2")
    try:
        tc.borrow_exclusive("packet", "ref_mut_1")
        assert False, "Should have raised BorrowConflictError"
    except BorrowConflictError as e:
        print(f"  -> Successfully caught mutable borrow conflict: {e}")

    # Release shared borrows
    tc.release_borrow("packet", "ref_shared_1")
    tc.release_borrow("packet", "ref_shared_2")
    # Now exclusive borrow must succeed
    tc.borrow_exclusive("packet", "ref_mut_1")
    print("  -> Exclusive borrow granted after shared borrows expired (NLL simulation).")
    tc.release_borrow("packet", "ref_mut_1")

    # 3. Test Cannot Move While Borrowed
    print("[Test 3/4] Move Prevention While Active Borrows Exist...")
    tc.borrow_shared("packet", "ref_shared_3")
    try:
        tc.move("packet", "forwarded_packet")
        assert False, "Should have raised BorrowConflictError"
    except BorrowConflictError as e:
        print(f"  -> Successfully prevented move during active borrow: {e}")
    tc.release_borrow("packet", "ref_shared_3")

    # 4. Test Linear Resource Leak Detection
    print("[Test 4/4] Linear Resource Leak Detection at Scope Exit...")
    tc_linear = SubstructuralTypeChecker()
    tc_linear.declare("file_handle", "FileDescriptor", is_linear=True)
    try:
        tc_linear.close_scope()
        assert False, "Should have raised LinearResourceLeakError"
    except LinearResourceLeakError as e:
        print(f"  -> Successfully caught linear resource leak: {e}")

    # Explicitly consuming the linear resource satisfies the linear requirement
    tc_linear.consume("file_handle")
    tc_linear.close_scope()
    print("  -> Consumed linear resource cleanly passed scope close check.")

    print("===========================================================================")
    print("ALL 4 SUBSTRUCTURAL TYPE SYSTEM TESTS PASSED (Exit Code 0).")
    print("===========================================================================")

if __name__ == "__main__":
    test_substructural_type_checker()
