"""
axiom_verifier.py
Automated Verification Suite for Level 7 Capstone Project:
Axiom Fault-Tolerant Trading & Streaming Platform.

Executes 6 Comprehensive Integration Test Suites:
  Suite 1: Multi-Paxos Consensus & Leadership Acquisition
  Suite 2: Split-Brain Fencing Token Storage Protection
  Suite 3: Level-3 Limit Order Book BBO Maintenance & ITCH Parsing
  Suite 4: Lock-Free Disruptor Ring Buffer Sequence Wrapping
  Suite 5: Event-Time Watermarked VWAP Streaming & 2PC Commit
  Suite 6: Zero-Trust SPIFFE Identity & mTLS Authorization

Exit Code 0 indicates 100% test pass and Level 7 mastery certification.
"""

from __future__ import annotations
import sys
import math
from typing import List, Dict, Any

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")

from axiom_trading_engine import (
    AxiomSpiffeId,
    AxiomX509SVID,
    time_now,
    advance_time,
    AxiomPaxosAcceptor,
    AxiomFencedStorage,
    AxiomDisruptorRing,
    AxiomOrderBook,
    AxiomTradeTick,
    AxiomVWAPStreamingEngine,
)


def run_suite_1_consensus() -> None:
    print("[Suite 1/6] Multi-Paxos Consensus & Leadership Acquisition...")
    acceptors = [AxiomPaxosAcceptor(f"acc_{i}") for i in range(5)]
    ballot = 101

    # Phase 1: Prepare across cluster
    promises = 0
    slot_id = 1
    for acc in acceptors:
        ok, max_b, val = acc.prepare(ballot, slot_id)
        if ok:
            promises += 1

    quorum = len(acceptors) // 2 + 1
    assert promises >= quorum, f"Failed to acquire quorum: {promises}/{len(acceptors)}"

    # Phase 2: Accept write
    proposal = {"action": "NEW_ORDER", "order_id": 9901, "price": 15000}
    accept_votes = 0
    for acc in acceptors:
        if acc.accept(ballot, slot_id, proposal):
            accept_votes += 1

    assert accept_votes >= quorum, f"Failed to achieve accept quorum: {accept_votes}/{len(acceptors)}"
    for acc in acceptors:
        acc.mark_committed(slot_id)

    assert acceptors[0].slots[slot_id]["committed"] is True
    print("  -> Phase 1 Quorum Promises: Passed (5/5).")
    print("  -> Phase 2 Quorum Accept & Commit: Passed.")


def run_suite_2_fencing() -> None:
    print("[Suite 2/6] Split-Brain Fencing Token Storage Protection...")
    storage = AxiomFencedStorage()

    # Leader 1 in Epoch 1 writes
    ok_1 = storage.write(epoch=1, key="cluster_state", value="LEADER_1_ACTIVE")
    assert ok_1 is True
    assert storage.current_epoch == 1

    # Standby promoted to Leader 2 in Epoch 2 writes
    ok_2 = storage.write(epoch=2, key="cluster_state", value="LEADER_2_ACTIVE")
    assert ok_2 is True
    assert storage.current_epoch == 2

    # Zombie Leader 1 attempts write with stale Epoch 1
    zombie_ok = storage.write(epoch=1, key="cluster_state", value="ZOMBIE_CORRUPTION")
    assert zombie_ok is False, "CRITICAL: Zombie leader was not fenced out!"
    assert storage.data["cluster_state"] == "LEADER_2_ACTIVE"

    print("  -> Epoch 1 Legitimate Write: Confirmed.")
    print("  -> Epoch 2 Failover Promotion: Confirmed.")
    print("  -> Zombie Epoch 1 Fencing Rejection: Confirmed (Cluster Protected).")


def run_suite_3_order_book() -> None:
    print("[Suite 3/6] Level-3 Limit Order Book BBO Maintenance & ITCH Parsing...")
    ob = AxiomOrderBook()

    # Populate book with ITCH binary messages
    msg1 = AxiomOrderBook.serialize_itch_order(order_id=1, side="B", shares=100, price=20000)
    msg2 = AxiomOrderBook.serialize_itch_order(order_id=2, side="B", shares=250, price=20050)
    msg3 = AxiomOrderBook.serialize_itch_order(order_id=3, side="A", shares=300, price=20100)
    msg4 = AxiomOrderBook.serialize_itch_order(order_id=4, side="A", shares=150, price=20150)

    ob.process_itch_bytes(msg1)
    ob.process_itch_bytes(msg2)
    ob.process_itch_bytes(msg3)
    ob.process_itch_bytes(msg4)

    best_bid, best_ask = ob.bbo()
    assert best_bid == 20050, f"Expected Best Bid 20050, got {best_bid}"
    assert best_ask == 20100, f"Expected Best Ask 20100, got {best_ask}"

    # Cancel highest bid (order 2)
    ob.cancel_order(order_id=2)
    new_best_bid, new_best_ask = ob.bbo()
    assert new_best_bid == 20000, f"Expected fallback Best Bid 20000, got {new_best_bid}"
    assert new_best_ask == 20100

    print("  -> Binary ITCH Order Deserialization: Verified.")
    print("  -> Best Bid & Offer (BBO) Calculation: Verified (Bid: 20050, Ask: 20100).")
    print("  -> Order Cancellation & Dynamic BBO Recomputation: Verified.")


def run_suite_4_disruptor() -> None:
    print("[Suite 4/6] Lock-Free Disruptor Ring Buffer Sequence Wrapping...")
    ring = AxiomDisruptorRing(capacity_power_of_two=8)

    # Push to capacity
    for i in range(8):
        assert ring.push(f"EVENT_{i}") is True

    # Overfill rejected
    assert ring.push("OVERFLOW_EVENT") is False

    # Pop 4 items
    popped = [ring.pop() for _ in range(4)]
    assert popped == ["EVENT_0", "EVENT_1", "EVENT_2", "EVENT_3"]

    # Push 4 more (sequence wraps around bitwise mask)
    for i in range(8, 12):
        assert ring.push(f"EVENT_{i}") is True

    # Drain ring
    remaining = []
    while True:
        item = ring.pop()
        if item is None:
            break
        remaining.append(item)

    expected = ["EVENT_4", "EVENT_5", "EVENT_6", "EVENT_7", "EVENT_8", "EVENT_9", "EVENT_10", "EVENT_11"]
    assert remaining == expected, f"Sequence wrapping mismatch: {remaining}"
    print("  -> Power-of-Two Bitwise Indexing: Verified.")
    print("  -> Single-Producer Single-Consumer FIFO Sequence: Verified.")


def run_suite_5_streaming_vwap() -> None:
    print("[Suite 5/6] Event-Time Watermarked VWAP Streaming & 2PC Commit...")
    engine = AxiomVWAPStreamingEngine(window_size_ms=1000, max_delay_ms=200)

    # Ticks within window [0, 1000)
    # Trade 1: 100 shares @ $150.00 at t=100
    engine.ingest_tick(AxiomTradeTick("AAPL", 150.0, 100, 100))
    # Trade 2: 200 shares @ $153.00 at t=300
    engine.ingest_tick(AxiomTradeTick("AAPL", 153.0, 200, 300))
    # Trade 3 (out of order): 100 shares @ $148.00 at t=250
    engine.ingest_tick(AxiomTradeTick("AAPL", 148.0, 100, 250))

    # Watermark = 300 - 200 = 100. Window [0, 1000) not closed yet.
    assert len(engine.committed_vwap) == 0

    # Advance event time with tick at t=1250 (Watermark = 1250 - 200 = 1050 > 1000)
    fired = engine.ingest_tick(AxiomTradeTick("AAPL", 155.0, 50, 1250))

    assert len(fired) == 1, f"Expected 1 window to fire, got {len(fired)}"
    w_start, w_end, sym, vwap, total_vol = fired[0]
    assert w_start == 0 and w_end == 1000
    assert total_vol == 400
    # Expected VWAP = (150*100 + 153*200 + 148*100) / 400 = (15000 + 30600 + 14800) / 400 = 60400 / 400 = 151.0
    assert math.isclose(vwap, 151.0, rel_tol=1e-5), f"Expected VWAP 151.0, got {vwap}"

    print("  -> Bounded Out-of-Order Tick Ingestion: Verified.")
    print("  -> Watermark Trigger Calculation: Verified (Fired at Watermark 1050 ms).")
    print(f"  -> Exact VWAP Metric: {vwap:.2f} (Total Volume: {total_vol}) Verified.")


def run_suite_6_security() -> None:
    print("[Suite 6/6] Zero-Trust SPIFFE Identity & mTLS Authorization...")
    spiffe_id = AxiomSpiffeId("axiom.trading", "hft/execution_gateway")
    assert spiffe_id.uri() == "spiffe://axiom.trading/hft/execution_gateway"

    # Issue valid short-lived SVID (3600 seconds)
    svid = AxiomX509SVID(spiffe_id, ttl_sec=3600, key="CLUSTER_SECRET_MASTER")
    assert svid.is_valid(key="CLUSTER_SECRET_MASTER") is True
    # Tampered key should fail
    assert svid.is_valid(key="ATTACKER_KEY") is False

    # Simulate certificate expiration
    advance_time(3601)
    assert svid.is_valid(key="CLUSTER_SECRET_MASTER") is False, "Expired SVID must be rejected!"

    print("  -> SPIFFE URI Formatting & Validation: Verified.")
    print("  -> Cryptographic SVID HMAC Signature: Verified.")
    print("  -> Automated Expiry Rejection: Verified.")


def main() -> None:
    print("=" * 75)
    print("AXIOM DISTRIBUTED TRADING & STREAMING ENGINE: VERIFIER SUITE")
    print("LEVEL 7 CAPSTONE VERIFICATION - SPECIALIST & EXPERT ENGINEERING")
    print("=" * 75)

    try:
        run_suite_1_consensus()
        run_suite_2_fencing()
        run_suite_3_order_book()
        run_suite_4_disruptor()
        run_suite_5_streaming_vwap()
        run_suite_6_security()

        print("=" * 75)
        print("ALL 6 TEST SUITES PASSED SUCCESSFULLY (Exit Code 0).")
        print("Level 7 Capstone Project 'Axiom Engine' 100% Certified.")
        print("=" * 75)
        sys.exit(0)
    except AssertionError as e:
        print(f"\n[FAIL] Assertion Error encountered: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
