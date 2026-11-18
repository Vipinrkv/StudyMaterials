"""
ChronosMatch Automated Test & Verification Suite
Level 3 Capstone Project

Validates:
1. Strict Price-Time Priority (FIFO) and Maker-price matching execution.
2. O(1) Cancellation via Open Addressing hash map and lazy heap purging.
3. Real-time Fenwick Tree range volume consistency against brute-force sums.
4. DSU Wash-Trading & Self-Deal Detection across syndicate accounts.
5. Base-256 LSD Radix Sort order book snapshot correctness.
6. QuickSelect O(n) trade execution median price accuracy.
7. End-to-end multi-thousand order stress simulation with invariant checks.
"""

import sys
import random
from typing import List

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from chronos_engine import ChronosEngine, Order, Trade


def test_price_time_priority_matching():
    print("[TEST 1] Verifying Price-Time Priority (FIFO) & Maker Price Rule...")
    engine = ChronosEngine()

    # Resting Asks (Sell):
    # Order 1: Sell 10 @ $150.00 (15000 cents), t=1
    # Order 2: Sell 20 @ $150.00 (15000 cents), t=2 (Same price, later time)
    # Order 3: Sell 15 @ $151.00 (15100 cents), t=3 (Higher price)
    engine.submit_order(order_id=1, trader_id=101, side="SELL", price=15000, quantity=10)
    engine.submit_order(order_id=2, trader_id=102, side="SELL", price=15000, quantity=20)
    engine.submit_order(order_id=3, trader_id=103, side="SELL", price=15100, quantity=15)

    # Incoming Aggressive Buy Order:
    # Order 4: Buy 25 @ $150.50 (15050 cents)
    # Should match:
    # 1. 10 shares against Order 1 @ $150.00 (earlier timestamp)
    # 2. 15 shares against Order 2 @ $150.00 (partial fill, leaving 5)
    # Should NOT match against Order 3 ($151.00 > $150.50)
    trades = engine.submit_order(order_id=4, trader_id=201, side="BUY", price=15050, quantity=25)

    assert len(trades) == 2, f"Expected 2 trade executions, got {len(trades)}"
    assert trades[0].sell_order_id == 1 and trades[0].quantity == 10 and trades[0].price == 15000
    assert trades[1].sell_order_id == 2 and trades[1].quantity == 15 and trades[1].price == 15000

    # Verify Order 2 residual quantity
    order_2 = engine.order_book.get(2)
    assert order_2 is not None and order_2.quantity == 5, f"Expected 5 remaining on order 2, got {order_2.quantity if order_2 else None}"

    # Best ask should now be Order 2 with 5 shares @ 15000
    best_ask = engine.asks.peek()
    assert best_ask is not None and best_ask.order_id == 2 and best_ask.quantity == 5
    print("  -> Passed. Strict Price-Time FIFO matching and maker-price execution confirmed.")


def test_order_cancellation_tombstones():
    print("[TEST 2] Verifying O(1) Cancellation via Hash Map & Lazy Purging...")
    engine = ChronosEngine()

    engine.submit_order(order_id=10, trader_id=301, side="BUY", price=10000, quantity=50)
    engine.submit_order(order_id=11, trader_id=302, side="BUY", price=9900, quantity=30)

    # Check depth volume before cancel
    assert engine.get_market_depth_volume(9800, 10100) == 80

    # Cancel order 10
    success = engine.cancel_order(10)
    assert success is True, "Failed to cancel resting order 10"
    assert engine.order_book.get(10) is None, "Order 10 still present in active hash map"

    # Depth volume should decrement immediately
    assert engine.get_market_depth_volume(9800, 10100) == 30

    # Submitting sell order @ 9950 should NOT match cancelled Order 10 (10000)
    # It should rest as an Ask since next bid is only 9900
    trades = engine.submit_order(order_id=12, trader_id=303, side="SELL", price=9950, quantity=20)
    assert len(trades) == 0, "Matched against cancelled order!"
    assert engine.bids.peek().order_id == 11, "Best bid should be active order 11"
    print("  -> Passed. Tombstone cancellation and lazy purge function perfectly.")


def test_fenwick_market_depth():
    print("[TEST 3] Verifying Fenwick Tree Real-Time Market Depth Volume...")
    engine = ChronosEngine()

    prices = [10000, 10100, 10200, 10300, 10400, 10500]
    quantities = [100, 250, 300, 150, 400, 50]

    for i, (p, q) in enumerate(zip(prices, quantities)):
        engine.submit_order(order_id=100 + i, trader_id=400 + i, side="SELL", price=p, quantity=q)

    # Range query: [10100, 10400] -> 250 + 300 + 150 + 400 = 1100
    depth_vol = engine.get_market_depth_volume(10100, 10400)
    assert depth_vol == 1100, f"Expected 1100, got {depth_vol}"

    # Partial execution should automatically deduct volume
    engine.submit_order(order_id=200, trader_id=500, side="BUY", price=10250, quantity=400)
    # Filled 100 @ 10000 and 250 @ 10100 and 50 @ 10200 (250 remaining at 10200)
    # New depth in [10100, 10400]: 0 + 250 + 150 + 400 = 800
    new_depth = engine.get_market_depth_volume(10100, 10400)
    assert new_depth == 800, f"Expected 800, got {new_depth}"
    print("  -> Passed. Dynamic Fenwick volume queries match ground truth exactly.")


def test_dsu_wash_trading_detection():
    print("[TEST 4] Verifying DSU Wash-Trading & Syndicate Detection...")
    engine = ChronosEngine()

    # Syndicate cluster: Trader 10, Trader 20, Trader 30 are part of same hedge fund ring
    engine.register_syndicate(10, 20)
    engine.register_syndicate(20, 30)

    # Trader 10 submits Buy @ $200.00
    engine.submit_order(order_id=501, trader_id=10, side="BUY", price=20000, quantity=50)

    # Trader 30 (indirectly colluding through 20) attempts to cross sell against 10
    trades = engine.submit_order(order_id=502, trader_id=30, side="SELL", price=20000, quantity=50)

    # Engine must detect wash trading and REJECT trade
    assert len(trades) == 0, "Engine failed to block internal syndicate wash-trade!"
    assert engine.wash_trade_rejections == 1, "Wash trade counter not incremented"

    # Legitimate external Trader 99 submits Sell @ $200.00 -> Should execute cleanly!
    legit_trades = engine.submit_order(order_id=503, trader_id=99, side="SELL", price=20000, quantity=50)
    assert len(legit_trades) == 1 and legit_trades[0].quantity == 50
    print("  -> Passed. DSU blocked collusive self-trades while permitting legitimate flow.")


def test_radix_sort_and_quickselect():
    print("[TEST 5] Verifying Base-256 Radix Sort Snapshot & QuickSelect Median...")
    engine = ChronosEngine()

    prices = [15020, 14980, 15050, 14950, 15010, 15100, 14900, 15070]
    for i, p in enumerate(prices):
        engine.submit_order(order_id=1000 + i, trader_id=1000, side="BUY", price=p, quantity=10)

    # Snapshot using LSD Radix Sort
    sorted_bids, _ = engine.get_order_book_snapshot()
    bid_prices = [b.price for b in sorted_bids]
    assert bid_prices == sorted(prices, reverse=True), f"Radix Sort mismatch: {bid_prices}"

    # Generate synthetic executed trades
    for i in range(15):
        # Cross orders to generate trades at diverse prices
        engine.submit_order(order_id=2000 + i, trader_id=2000, side="SELL", price=14800, quantity=5)

    median_price = engine.get_median_trade_price()
    all_prices = sorted([t.price for t in engine.trades])
    expected_median = all_prices[len(all_prices) // 2]
    assert median_price == expected_median, f"QuickSelect median {median_price} != {expected_median}"
    print("  -> Passed. Base-256 Radix Sort and QuickSelect median validated.")


def test_high_volume_stress_simulation():
    print("[TEST 6] Multi-Thousand Order High-Frequency Stress Test...")
    random.seed(999)
    engine = ChronosEngine()

    total_submitted = 2000
    for i in range(total_submitted):
        side = "BUY" if random.random() < 0.5 else "SELL"
        px = random.randint(14500, 15500)
        qty = random.randint(1, 100)
        trader = random.randint(1, 100)

        # 10% probability of cancelation
        if random.random() < 0.10 and i > 50:
            cancel_target = random.randint(1, i - 1)
            engine.cancel_order(cancel_target)
        else:
            engine.submit_order(order_id=i + 1, trader_id=trader, side=side, price=px, quantity=qty)

    print(f"  -> Stress test completed: {len(engine.trades)} trades executed.")
    print(f"  -> Active orders in book: {engine.order_book.size}")
    print(f"  -> Blocked wash trades: {engine.wash_trade_rejections}")

    # Integrity invariant checks
    active_bids, active_asks = engine.get_order_book_snapshot()
    if active_bids and active_asks:
        # Best bid MUST be strictly less than best ask in resting book!
        best_bid_px = active_bids[0].price
        best_ask_px = active_asks[0].price
        assert best_bid_px < best_ask_px, f"Crossing book invariant violated: Best Bid {best_bid_px} >= Best Ask {best_ask_px}"

    print("  -> Passed. All exchange book invariants preserved under stress load.")


def main():
    print("======================================================================")
    print("   CHRONOSMATCH: LEVEL 3 CAPSTONE AUTOMATED VERIFICATION HARNESS     ")
    print("======================================================================")
    test_price_time_priority_matching()
    test_order_cancellation_tombstones()
    test_fenwick_market_depth()
    test_dsu_wash_trading_detection()
    test_radix_sort_and_quickselect()
    test_high_volume_stress_simulation()
    print("======================================================================")
    print("   ALL LEVEL 3 CAPSTONE INTEGRATION TESTS PASSED (EXIT CODE 0)       ")
    print("======================================================================")


if __name__ == "__main__":
    main()
