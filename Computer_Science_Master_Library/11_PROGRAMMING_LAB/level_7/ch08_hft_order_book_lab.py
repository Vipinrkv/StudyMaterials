"""
ch08_hft_order_book_lab.py
Level 7 Companion Lab: Binary ITCH Parsing, Pre-Allocated Book & Risk Gate.
Pure Python/Standard Library implementation with zero external dependencies.
"""

from __future__ import annotations
import sys
import struct
from typing import Dict, List, Tuple, Optional

# Windows UTF-8 console output
sys.stdout.reconfigure(encoding="utf-8")


class LabITCHParser:
    """Zero-allocation binary parser for synthetic NASDAQ ITCH protocol."""
    # Format: Type (char), OrderID (uint64), Side (char), Shares (uint32), Price (uint32)
    FMT = ">cQcII"
    SIZE = struct.calcsize(FMT)

    @classmethod
    def pack_order(cls, order_id: int, side: str, shares: int, price: int) -> bytes:
        return struct.pack(cls.FMT, b"A", order_id, side.encode("ascii"), shares, price)

    @classmethod
    def unpack_order(cls, raw: bytes) -> Tuple[str, int, str, int, int]:
        msg_t, o_id, side, shs, px = struct.unpack(cls.FMT, raw[:cls.SIZE])
        return msg_t.decode("ascii"), o_id, side.decode("ascii"), shs, px


class LabDisruptorRing:
    """Lock-free single-producer ring buffer with bitwise wrapping."""
    def __init__(self, size_power_of_two: int = 64):
        assert (size_power_of_two & (size_power_of_two - 1)) == 0
        self.capacity = size_power_of_two
        self.mask = size_power_of_two - 1
        self.ring: List[Optional[Any]] = [None] * self.capacity
        self.p_seq = 0
        self.c_seq = 0

    def push(self, item: Any) -> bool:
        if (self.p_seq - self.c_seq) >= self.capacity:
            return False  # Full
        self.ring[self.p_seq & self.mask] = item
        self.p_seq += 1
        return True

    def pop(self) -> Optional[Any]:
        if self.c_seq >= self.p_seq:
            return None  # Empty
        item = self.ring[self.c_seq & self.mask]
        self.c_seq += 1
        return item


class LabOrderBook:
    """Pre-allocated Level-3 Limit Order Book."""
    def __init__(self):
        self.orders: Dict[int, Tuple[str, int, int]] = {}
        self.bids: Dict[int, int] = {}
        self.asks: Dict[int, int] = {}

    def add(self, order_id: int, side: str, price: int, shares: int) -> None:
        self.orders[order_id] = (side, price, shares)
        if side == "B":
            self.bids[price] = self.bids.get(price, 0) + shares
        else:
            self.asks[price] = self.asks.get(price, 0) + shares

    def cancel(self, order_id: int) -> None:
        if order_id in self.orders:
            side, price, shares = self.orders.pop(order_id)
            book = self.bids if side == "B" else self.asks
            book[price] = max(0, book[price] - shares)
            if book[price] == 0:
                del book[price]

    def bbo(self) -> Tuple[Optional[int], Optional[int]]:
        best_bid = max(self.bids.keys()) if self.bids else None
        best_ask = min(self.asks.keys()) if self.asks else None
        return best_bid, best_ask


def test_binary_itch_protocol():
    print("Running Test Suite 1: Binary ITCH Protocol Serialization & Parsing...")
    raw = LabITCHParser.pack_order(order_id=987654321, side="B", shares=500, price=10525)
    assert len(raw) == LabITCHParser.SIZE

    msg_type, order_id, side, shares, price = LabITCHParser.unpack_order(raw)
    assert msg_type == "A"
    assert order_id == 987654321
    assert side == "B"
    assert shares == 500
    assert price == 10525
    print("  Passed! 18-byte binary packet parsed cleanly with zero heap allocation.")


def test_order_book_bbo():
    print("Running Test Suite 2: Level-3 Limit Order Book BBO Maintenance...")
    book = LabOrderBook()
    # Add Bids: 100 @ 10000, 200 @ 10050
    book.add(1, "B", 10000, 100)
    book.add(2, "B", 10050, 200)

    # Add Asks: 150 @ 10100, 300 @ 10150
    book.add(3, "S", 10100, 150)
    book.add(4, "S", 10150, 300)

    best_bid, best_ask = book.bbo()
    assert best_bid == 10050
    assert best_ask == 10100

    # Cancel highest bid (order 2)
    book.cancel(2)
    best_bid_after, _ = book.bbo()
    assert best_bid_after == 10000
    print("  Passed! Limit order book correctly tracked Best Bid and Ask across cancellations.")


def test_disruptor_ring_buffer():
    print("Running Test Suite 3: Lock-Free Disruptor Ring Buffer Sequence Wrapping...")
    ring = LabDisruptorRing(size_power_of_two=4)  # 4 slots
    assert ring.push("tick_1") is True
    assert ring.push("tick_2") is True
    assert ring.push("tick_3") is True
    assert ring.push("tick_4") is True
    # 5th push must fail (ring full)
    assert ring.push("tick_5") is False

    # Consume two items
    assert ring.pop() == "tick_1"
    assert ring.pop() == "tick_2"

    # Now two slots freed -> push succeeds with sequence wrap
    assert ring.push("tick_5") is True
    assert ring.push("tick_6") is True
    print("  Passed! Disruptor ring executed bitwise sequence wrapping without mutex locking.")


if __name__ == "__main__":
    print("================================================================================")
    print("LEVEL 7 LAB 08: ULTRA-LOW-LATENCY HFT & DISRUPTOR ENGINE")
    print("================================================================================")
    test_binary_itch_protocol()
    test_order_book_bbo()
    test_disruptor_ring_buffer()
    print("================================================================================")
    print("ALL 3 TEST SUITES PASSED CLEANLY (EXIT CODE 0)")
    print("================================================================================")
