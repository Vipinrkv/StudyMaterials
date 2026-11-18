"""
Level 4 Chapter 10 Programming Lab: Database Engine Internals (Storage, MVCC & WAL)
==================================================================================
Focus: Slotted Page binary physical layout, in-memory Buffer Pool with CLOCK
       eviction, Snapshot Isolation MVCC visibility, and WAL crash recovery.
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")
from typing import Dict, List, Set, Tuple, Optional, Any
import struct


# ---------------------------------------------------------------------------
# 1. Slotted Page Physical Storage Architecture
# ---------------------------------------------------------------------------

PAGE_SIZE = 4096
HEADER_FORMAT = "<III"  # page_lsn (4B), free_space_offset (4B), tuple_count (4B)
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
SLOT_FORMAT = "<HH"     # tuple_offset (2B), tuple_length (2B)
SLOT_SIZE = struct.calcsize(SLOT_FORMAT)


class SlottedPage:
    """
    Fixed 4096-byte database page.
    - Header: LSN, free_space_pointer, item_count.
    - Slot Directory: grows downward from byte offset 12.
    - Tuple Storage: grows upward from byte 4096.
    """
    def __init__(self, page_id: int):
        self.page_id = page_id
        self.data = bytearray(PAGE_SIZE)
        self.page_lsn = 0
        self.free_space_offset = PAGE_SIZE  # Starts at bottom
        self.tuple_count = 0
        self._write_header()

    def _write_header(self):
        struct.pack_into(HEADER_FORMAT, self.data, 0, self.page_lsn, self.free_space_offset, self.tuple_count)

    def insert_tuple(self, record_bytes: bytes) -> Optional[int]:
        rec_len = len(record_bytes)
        # Check space: needs slot (4B) + record bytes
        current_slots_end = HEADER_SIZE + self.tuple_count * SLOT_SIZE
        available_space = self.free_space_offset - current_slots_end
        if available_space < SLOT_SIZE + rec_len:
            return None  # Page is full

        # Allocate from page bottom
        new_tuple_offset = self.free_space_offset - rec_len
        self.data[new_tuple_offset : new_tuple_offset + rec_len] = record_bytes

        # Write slot entry
        slot_pos = HEADER_SIZE + self.tuple_count * SLOT_SIZE
        struct.pack_into(SLOT_FORMAT, self.data, slot_pos, new_tuple_offset, rec_len)

        slot_id = self.tuple_count
        self.tuple_count += 1
        self.free_space_offset = new_tuple_offset
        self._write_header()
        return slot_id

    def read_tuple(self, slot_id: int) -> Optional[bytes]:
        if slot_id < 0 or slot_id >= self.tuple_count:
            return None
        slot_pos = HEADER_SIZE + slot_id * SLOT_SIZE
        offset, length = struct.unpack_from(SLOT_FORMAT, self.data, slot_pos)
        if length == 0:
            return None  # Deleted tombstone
        return bytes(self.data[offset : offset + length])


# ---------------------------------------------------------------------------
# 2. In-Memory Buffer Pool Manager with CLOCK Eviction
# ---------------------------------------------------------------------------

class BufferFrame:
    def __init__(self, frame_id: int):
        self.frame_id = frame_id
        self.page: Optional[SlottedPage] = None
        self.pin_count = 0
        self.is_dirty = False
        self.reference_bit = False


class BufferPoolManager:
    def __init__(self, pool_size: int = 4):
        self.pool_size = pool_size
        self.frames = [BufferFrame(i) for i in range(pool_size)]
        self.page_table: Dict[int, int] = {}  # PageID -> FrameID
        self.clock_hand = 0
        self.disk_storage: Dict[int, bytes] = {}

    def fetch_page(self, page_id: int) -> SlottedPage:
        if page_id in self.page_table:
            frame = self.frames[self.page_table[page_id]]
            frame.pin_count += 1
            frame.reference_bit = True
            return frame.page

        # Find victim frame using CLOCK algorithm
        victim_frame = self._clock_victim()
        if victim_frame.is_dirty and victim_frame.page is not None:
            # Flush dirty page to disk
            self.disk_storage[victim_frame.page.page_id] = bytes(victim_frame.page.data)
            victim_frame.is_dirty = False

        if victim_frame.page is not None:
            del self.page_table[victim_frame.page.page_id]

        # Load page from disk or initialize new
        if page_id in self.disk_storage:
            page = SlottedPage(page_id)
            page.data = bytearray(self.disk_storage[page_id])
            page.page_lsn, page.free_space_offset, page.tuple_count = struct.unpack_from(HEADER_FORMAT, page.data, 0)
        else:
            page = SlottedPage(page_id)

        victim_frame.page = page
        victim_frame.pin_count = 1
        victim_frame.is_dirty = False
        victim_frame.reference_bit = True
        self.page_table[page_id] = victim_frame.frame_id
        return page

    def unpin_page(self, page_id: int, is_dirty: bool):
        if page_id not in self.page_table:
            return
        frame = self.frames[self.page_table[page_id]]
        if is_dirty:
            frame.is_dirty = True
        if frame.pin_count > 0:
            frame.pin_count -= 1

    def _clock_victim(self) -> BufferFrame:
        scanned = 0
        while scanned < self.pool_size * 2:
            frame = self.frames[self.clock_hand]
            if frame.pin_count == 0:
                if frame.reference_bit:
                    frame.reference_bit = False
                else:
                    self.clock_hand = (self.clock_hand + 1) % self.pool_size
                    return frame
            self.clock_hand = (self.clock_hand + 1) % self.pool_size
            scanned += 1
        raise RuntimeError("Buffer pool error: all frames pinned!")


# ---------------------------------------------------------------------------
# 3. MVCC Snapshot Isolation Visibility Engine
# ---------------------------------------------------------------------------

class MVCCTuple:
    def __init__(self, key: int, value: str, xmin: int, xmax: int = 0):
        self.key = key
        self.value = value
        self.xmin = xmin  # Creating transaction ID
        self.xmax = xmax  # Deleting/Updating transaction ID (0 if active)

    def is_visible_to(self, tx_id: int, active_tx_ids: Set[int], committed_tx_ids: Set[int]) -> bool:
        """
        Snapshot Isolation Visibility Check:
        1. Created by our own transaction: visible if not deleted by us.
        2. Created by uncommitted transaction: invisible.
        3. Created by committed transaction after our start: invisible.
        4. Deleted by committed transaction before our start: invisible.
        """
        # Rule 1: Check creator (xmin)
        if self.xmin == tx_id:
            # We created it: visible unless we also deleted it
            return self.xmax != tx_id

        if self.xmin not in committed_tx_ids:
            return False  # Created by uncommitted transaction

        if self.xmin in active_tx_ids or self.xmin > tx_id:
            return False  # Created after our snapshot took effect

        # Rule 2: Check deleter (xmax)
        if self.xmax == 0:
            return True  # Never deleted

        if self.xmax == tx_id:
            return False  # Deleted by our own transaction

        if self.xmax not in committed_tx_ids:
            return True  # Deleting transaction hasn't committed yet

        if self.xmax in active_tx_ids or self.xmax > tx_id:
            return True  # Deleted after our snapshot took effect

        return False  # Deleted and committed before our snapshot


# ---------------------------------------------------------------------------
# 4. Write-Ahead Logging (WAL) & ARIES Crash Recovery Simulation
# ---------------------------------------------------------------------------

class WALRecord:
    def __init__(self, lsn: int, tx_id: int, op_type: str, key: str, old_val: Optional[str], new_val: Optional[str]):
        self.lsn = lsn
        self.tx_id = tx_id
        self.op_type = op_type  # "START", "UPDATE", "COMMIT", "ABORT"
        self.key = key
        self.old_val = old_val
        self.new_val = new_val


def aries_recovery(log: List[WALRecord], state_at_crash: Dict[str, str]) -> Dict[str, str]:
    """
    Simulates ARIES Crash Recovery:
    1. Analysis: find active uncommitted transactions (Losers).
    2. Redo: repeat history forward from start to restore exact state at crash.
    3. Undo: scan backward and reverse operations of loser transactions.
    """
    # 1. Analysis Phase
    active_txs = set()
    for rec in log:
        if rec.op_type == "START":
            active_txs.add(rec.tx_id)
        elif rec.op_type in ("COMMIT", "ABORT"):
            active_txs.discard(rec.tx_id)
    losers = active_txs

    # 2. Redo Phase (Repeating history)
    recovered_state = dict(state_at_crash)
    for rec in log:
        if rec.op_type == "UPDATE":
            recovered_state[rec.key] = rec.new_val

    # 3. Undo Phase (Roll back losers backward)
    for rec in reversed(log):
        if rec.tx_id in losers and rec.op_type == "UPDATE":
            recovered_state[rec.key] = rec.old_val

    return recovered_state


def test_database_engine_suite():
    print("[TEST 1] Slotted Page Binary Physical Layout...")
    page = SlottedPage(page_id=1)
    rec1 = b"Account:Alice,Bal:1000"
    rec2 = b"Account:Bob,Bal:2500"

    slot0 = page.insert_tuple(rec1)
    slot1 = page.insert_tuple(rec2)
    assert slot0 == 0 and slot1 == 1, "Slot IDs assigned incorrectly"

    read_rec1 = page.read_tuple(0)
    read_rec2 = page.read_tuple(1)
    assert read_rec1 == rec1, "Record 1 payload corrupted"
    assert read_rec2 == rec2, "Record 2 payload corrupted"
    assert page.free_space_offset == PAGE_SIZE - (len(rec1) + len(rec2)), "Free space pointer not updated"
    print(f"  -> Slotted page packed 2 variable-length tuples (Free space: {page.free_space_offset} bytes).")

    print("[TEST 2] Buffer Pool Manager with CLOCK Page Eviction...")
    bpm = BufferPoolManager(pool_size=2)  # Pool size = 2 frames
    p1 = bpm.fetch_page(page_id=1)
    p1.insert_tuple(b"Key1")
    bpm.unpin_page(page_id=1, is_dirty=True)

    p2 = bpm.fetch_page(page_id=2)
    p2.insert_tuple(b"Key2")
    bpm.unpin_page(page_id=2, is_dirty=True)

    # Fetching page 3 forces CLOCK eviction of one unpinned frame
    p3 = bpm.fetch_page(page_id=3)
    p3.insert_tuple(b"Key3")
    bpm.unpin_page(page_id=3, is_dirty=True)

    # Re-fetch page 1: must reload from disk storage
    p1_reloaded = bpm.fetch_page(page_id=1)
    assert p1_reloaded.read_tuple(0) == b"Key1", "Data lost across buffer pool CLOCK eviction"
    bpm.unpin_page(page_id=1, is_dirty=False)
    print("  -> Buffer pool CLOCK eviction and disk persistence verified.")

    print("[TEST 3] MVCC Snapshot Isolation Visibility Checks...")
    committed = {100, 101}
    active_in_snapshot = {102}  # Transaction 102 was running when Tx 103 started

    # Row created by 101, deleted by 102
    t1 = MVCCTuple(key=1, value="OldValue", xmin=101, xmax=102)
    # Tx 103 should see t1 because Tx 102 had not committed when Tx 103 took its snapshot
    assert t1.is_visible_to(tx_id=103, active_tx_ids=active_in_snapshot, committed_tx_ids=committed), "MVCC visibility error"

    # Row created by uncommitted transaction 104
    t2 = MVCCTuple(key=2, value="UncommittedVal", xmin=104, xmax=0)
    assert not t2.is_visible_to(tx_id=103, active_tx_ids=active_in_snapshot, committed_tx_ids=committed), "Uncommitted row visible"
    print("  -> MVCC Snapshot Isolation visibility logic mathematically verified.")

    print("[TEST 4] WAL & ARIES Crash Recovery (Redo + Undo)...")
    initial_db = {"A": "100", "B": "200"}
    log = [
        WALRecord(1, 10, "START", "", None, None),
        WALRecord(2, 10, "UPDATE", "A", "100", "150"),
        WALRecord(3, 10, "COMMIT", "", None, None),
        WALRecord(4, 20, "START", "", None, None),
        WALRecord(5, 20, "UPDATE", "B", "200", "999"),  # Tx 20 never committed! CRASH!
    ]
    # At crash, memory had B = 999
    crash_state = {"A": "150", "B": "999"}
    final_db = aries_recovery(log, crash_state)
    assert final_db["A"] == "150", f"Committed Tx 10 was lost: {final_db}"
    assert final_db["B"] == "200", f"Uncommitted Tx 20 was not undone: {final_db}"
    print(f"  -> ARIES recovery correctly preserved committed Tx 10 and rolled back uncommitted Tx 20: {final_db}")

    print("ALL Level 4 Chapter 10 Database Engine lab tests passed successfully!")


if __name__ == "__main__":
    test_database_engine_suite()
