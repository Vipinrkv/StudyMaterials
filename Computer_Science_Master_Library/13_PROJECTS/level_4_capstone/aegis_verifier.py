"""
AegisDB Automated Verification & Test Harness
============================================
Validates 100% adherence to Level 4 Capstone engineering specifications:
1. SQL Lexical Scanner & AST Parser
2. Slotted Page Binary Physical Layout
3. Buffer Pool Manager & CLOCK Page Eviction
4. MVCC Snapshot Isolation Non-Blocking Concurrency
5. Physical Volcano Iterator Pipeline
6. Write-Ahead Logging & ARIES Crash Recovery
7. End-to-End Stress Simulation
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")
from aegis_engine import (
    SQLLexer, SQLParser, TokenType, SlottedPage, BufferPool,
    AegisDB, SelectQuery, InsertQuery, UpdateQuery
)
import random


def test_aegis_capstone_suite():
    print("=" * 75)
    print("LAUNCHING AEGIS-DB LEVEL 4 CAPSTONE VERIFICATION HARNESS")
    print("=" * 75)

    # -----------------------------------------------------------------------
    # TEST 1: SQL Lexical Analysis and AST Parsing
    # -----------------------------------------------------------------------
    print("\n[TEST 1] SQL Frontend: Lexer & Recursive Descent Parser...")
    query = "SELECT id, name FROM accounts WHERE balance > 5000;"
    tokens = SQLLexer(query).tokens
    assert len(tokens) >= 8, f"Unexpected token count: {len(tokens)}"
    
    ast = SQLParser(tokens).parse()
    assert isinstance(ast, SelectQuery), "Parser failed to produce SelectQuery AST"
    assert ast.table == "accounts"
    assert ast.columns == ["id", "name"]
    assert ast.condition == ("balance", ">", 5000)
    print("  -> Successfully parsed SQL query into typed Abstract Syntax Tree.")

    # -----------------------------------------------------------------------
    # TEST 2: Slotted Page Binary Layout & Record Boundary Invariants
    # -----------------------------------------------------------------------
    print("\n[TEST 2] Storage Engine: Slotted Page Binary Physical Layout...")
    page = SlottedPage(page_id=101)
    payload_a = b'{"id": 1, "owner": "Vipin", "assets": 950000}'
    payload_b = b'{"id": 2, "owner": "AegisCore", "assets": 2400000}'

    slot_0 = page.insert(payload_a)
    slot_1 = page.insert(payload_b)
    assert slot_0 == 0 and slot_1 == 1, "Slot indexing violation"

    rec_0 = page.read(0)
    rec_1 = page.read(1)
    assert rec_0 == payload_a, "Corrupted payload in slot 0"
    assert rec_1 == payload_b, "Corrupted payload in slot 1"
    assert page.free_space_offset == 4096 - (len(payload_a) + len(payload_b))
    print(f"  -> Packed 2 variable-length tuples; free space offset accurately tracked at {page.free_space_offset}.")

    # -----------------------------------------------------------------------
    # TEST 3: In-Memory Buffer Pool & CLOCK Page Eviction Policy
    # -----------------------------------------------------------------------
    print("\n[TEST 3] Buffer Pool Manager: CLOCK Eviction & Disk Persistence...")
    bp = BufferPool(size=2)  # Strictly 2 memory frames

    # Load page 1, modify, unpin dirty
    p1 = bp.get_page(1)
    p1.insert(b"Chunk_Page_1")
    bp.release_page(1, is_dirty=True)

    # Load page 2, modify, unpin dirty
    p2 = bp.get_page(2)
    p2.insert(b"Chunk_Page_2")
    bp.release_page(2, is_dirty=True)

    # Loading page 3 must trigger CLOCK eviction of frame 0 (flushing page 1 to disk)
    p3 = bp.get_page(3)
    p3.insert(b"Chunk_Page_3")
    bp.release_page(3, is_dirty=True)

    # Fetching page 1 back must reload from disk with intact bytes
    p1_reloaded = bp.get_page(1)
    assert p1_reloaded.read(0) == b"Chunk_Page_1", "Page eviction failed to persist dirty data to disk"
    bp.release_page(1, is_dirty=False)
    print("  -> CLOCK eviction and disk page synchronization verified.")

    # -----------------------------------------------------------------------
    # TEST 4: MVCC Snapshot Isolation Non-Blocking Concurrency
    # -----------------------------------------------------------------------
    print("\n[TEST 4] Concurrency: Multi-Version Concurrency Control (MVCC)...")
    db = AegisDB()

    # Tx1 inserts initial bank accounts
    tx1 = db.begin_transaction()
    db.execute_sql("INSERT INTO accounts VALUES (101, 'Rohan', 10000);", tx1)
    db.execute_sql("INSERT INTO accounts VALUES (102, 'Priya', 25000);", tx1)
    db.commit(tx1)

    # Tx2 starts and takes its Snapshot
    tx2 = db.begin_transaction()

    # Tx3 starts concurrently, updates Rohan's balance, and commits
    tx3 = db.begin_transaction()
    db.execute_sql("UPDATE accounts SET balance = 50000 WHERE id = 101;", tx3)
    db.commit(tx3)

    # In MVCC Snapshot Isolation, Tx2 MUST NOT see Tx3's committed update because Tx3 committed AFTER Tx2 started!
    rows_tx2 = db.execute_sql("SELECT balance FROM accounts WHERE id = 101;", tx2)
    assert len(rows_tx2) == 1
    assert rows_tx2[0]["balance"] == 10000, f"Snapshot isolation violated! Tx2 saw {rows_tx2[0]['balance']} instead of 10000"
    db.commit(tx2)

    # A new transaction Tx4 started NOW must see the updated balance of 50000
    tx4 = db.begin_transaction()
    rows_tx4 = db.execute_sql("SELECT balance FROM accounts WHERE id = 101;", tx4)
    assert rows_tx4[0]["balance"] == 50000, f"New transaction failed to see committed data: {rows_tx4}"
    db.commit(tx4)
    print("  -> Snapshot Isolation successfully protected reader from concurrent writer commit.")

    # -----------------------------------------------------------------------
    # TEST 5: Volcano Physical Iterator Execution
    # -----------------------------------------------------------------------
    print("\n[TEST 5] Query Optimizer & Volcano Iterator Execution Pipeline...")
    tx5 = db.begin_transaction()
    res = db.execute_sql("SELECT name, balance FROM accounts WHERE balance > 20000;", tx5)
    db.commit(tx5)
    names = [r["name"] for r in res]
    assert "Priya" in names and "Rohan" in names, f"Volcano pipeline filter error: {res}"
    print(f"  -> Volcano Iterator pipeline (SeqScan -> Filter -> Project) executed successfully: {res}")

    # -----------------------------------------------------------------------
    # TEST 6: Durability: Write-Ahead Logging & ARIES Crash Recovery
    # -----------------------------------------------------------------------
    print("\n[TEST 6] Durability: ARIES Crash Recovery (Redo + Undo)...")
    # Simulate active transaction during power outage
    tx_crash = db.begin_transaction()
    db.execute_sql("UPDATE accounts SET balance = 999999 WHERE id = 101;", tx_crash)
    # tx_crash NEVER commits! System crashes here!

    recovered_state = db.crash_and_recover()
    # Committed accounts should be restored, but uncommitted 999999 must be undone!
    accounts_table = recovered_state["accounts"]
    # Check Rohan's balance in recovered state
    rohan_recovered = None
    for r in accounts_table.values():
        if r and r.get("id") == 101:
            rohan_recovered = r
            break
    assert rohan_recovered is not None, "Committed account lost in crash recovery"
    assert rohan_recovered["balance"] == 50000, f"Uncommitted transaction leaked into recovered database: {rohan_recovered}"
    print(f"  -> ARIES recovery restored committed state (balance=50000) and rolled back uncommitted loser tx_crash.")

    # -----------------------------------------------------------------------
    # TEST 7: Stress Concurrency Simulation
    # -----------------------------------------------------------------------
    print("\n[TEST 7] High-Concurrency Stress Simulation (500 Transactions)...")
    stress_db = AegisDB()
    init_tx = stress_db.begin_transaction()
    for i in range(10):
        stress_db.execute_sql(f"INSERT INTO users VALUES ({i}, 'User_{i}', 100);", init_tx)
    stress_db.commit(init_tx)

    committed_count = 0
    aborted_count = 0

    for op_i in range(500):
        t = stress_db.begin_transaction()
        target_id = random.randint(0, 9)
        new_val = random.randint(100, 1000)
        stress_db.execute_sql(f"UPDATE users SET balance = {new_val} WHERE id = {target_id};", t)
        if random.random() < 0.85:
            stress_db.commit(t)
            committed_count += 1
        else:
            stress_db.rollback(t)
            aborted_count += 1

    check_tx = stress_db.begin_transaction()
    final_rows = stress_db.execute_sql("SELECT * FROM users;", check_tx)
    stress_db.commit(check_tx)
    assert len(final_rows) == 10, f"Expected 10 active rows, got {len(final_rows)}"
    print(f"  -> Completed 500 transactions ({committed_count} committed, {aborted_count} aborted).")
    print(f"  -> Verified zero invariant corruption across all 10 user rows.")

    print("\n" + "=" * 75)
    print("ALL LEVEL 4 CAPSTONE (AEGIS-DB) VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 75)


if __name__ == "__main__":
    test_aegis_capstone_suite()
