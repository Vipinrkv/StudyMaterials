"""
axiom_trading_engine.py
Level 7 Capstone Project: Axiom Fault-Tolerant Trading & Streaming Platform.
Synthesizes Multi-Paxos Consensus, Lock-Free Disruptor Ring, L3 Order Book,
Event-Time Watermark Streaming (VWAP), and Zero-Trust SPIFFE mTLS Security.
Pure Python/Standard Library implementation with zero external dependencies.
"""

from __future__ import annotations
import sys
import math
import struct
import secrets
import hashlib
import hmac
from urllib.parse import urlparse
from typing import Dict, List, Optional, Tuple, Any, Set

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")


# ==============================================================================
# MODULE 1: ZERO-TRUST SPIFFE IDENTITY & MTLS AUTHORIZATION
# ==============================================================================

class AxiomSpiffeId:
    """Standardized SPIFFE workload identifier."""
    def __init__(self, trust_domain: str, path: str):
        self.trust_domain = trust_domain.lower()
        self.path = path if path.startswith("/") else f"/{path}"

    def uri(self) -> str:
        return f"spiffe://{self.trust_domain}{self.path}"

    @classmethod
    def parse(cls, spiffe_uri: str) -> AxiomSpiffeId:
        parsed = urlparse(spiffe_uri)
        if parsed.scheme != "spiffe" or not parsed.netloc:
            raise ValueError(f"Invalid SPIFFE URI: {spiffe_uri}")
        return cls(parsed.netloc, parsed.path)


class AxiomX509SVID:
    """Ephemeral X.509 SVID certificate with cryptographic signature and expiration."""
    def __init__(self, spiffe_id: AxiomSpiffeId, ttl_sec: int = 3600, key: str = "AXIOM_ROOT_CA"):
        self.spiffe_id = spiffe_id
        self.issued_at = int(time_now())
        self.expires_at = self.issued_at + ttl_sec
        self.serial = secrets.token_hex(8)
        self.signature = self._sign(key)

    def _sign(self, key: str) -> str:
        data = f"{self.spiffe_id.uri()}:{self.expires_at}:{self.serial}"
        return hmac.new(key.encode("utf-8"), data.encode("utf-8"), hashlib.sha256).hexdigest()

    def is_valid(self, key: str = "AXIOM_ROOT_CA") -> bool:
        if int(time_now()) >= self.expires_at:
            return False
        return hmac.compare_digest(self.signature, self._sign(key))


# Global time helper for deterministic testing
_SIMULATED_TIME = 1700000000

def time_now() -> int:
    global _SIMULATED_TIME
    return _SIMULATED_TIME

def advance_time(seconds: int) -> None:
    global _SIMULATED_TIME
    _SIMULATED_TIME += seconds


# ==============================================================================
# MODULE 2: MULTI-PAXOS CONSENSUS & FENCING TOKENS
# ==============================================================================

class AxiomPaxosAcceptor:
    """Acceptor role handling Phase 1 Prepare and Phase 2 Accept."""
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.max_promised_ballot = 0
        self.slots: Dict[int, Dict[str, Any]] = {}
        self.is_alive = True

    def prepare(self, ballot: int, slot_id: int) -> Tuple[bool, int, Optional[Dict[str, Any]]]:
        if not self.is_alive:
            return False, 0, None
        slot = self.slots.get(slot_id, {"b": 0, "v": None, "committed": False})
        if ballot >= self.max_promised_ballot and ballot >= slot["b"]:
            self.max_promised_ballot = ballot
            slot["b"] = ballot
            self.slots[slot_id] = slot
            return True, slot["b"], slot["v"]
        return False, self.max_promised_ballot, None

    def accept(self, ballot: int, slot_id: int, value: Dict[str, Any]) -> bool:
        if not self.is_alive:
            return False
        slot = self.slots.get(slot_id, {"b": 0, "v": None, "committed": False})
        if ballot >= slot["b"] and ballot >= self.max_promised_ballot:
            slot["b"] = ballot
            slot["v"] = value
            self.slots[slot_id] = slot
            return True
        return False

    def mark_committed(self, slot_id: int) -> None:
        if slot_id in self.slots:
            self.slots[slot_id]["committed"] = True


class AxiomFencedStorage:
    """Cluster storage target protected by generation fencing tokens."""
    def __init__(self):
        self.current_epoch = 0
        self.data: Dict[str, Any] = {}

    def write(self, epoch: int, key: str, value: Any) -> bool:
        if epoch < self.current_epoch:
            return False  # Fenced out!
        if epoch > self.current_epoch:
            self.current_epoch = epoch
        self.data[key] = value
        return True


# ==============================================================================
# MODULE 3: LOCK-FREE DISRUPTOR RING & L3 LIMIT ORDER BOOK
# ==============================================================================

class AxiomDisruptorRing:
    """Power-of-two single-producer lock-free circular ring buffer."""
    def __init__(self, capacity_power_of_two: int = 128):
        assert (capacity_power_of_two & (capacity_power_of_two - 1)) == 0
        self.capacity = capacity_power_of_two
        self.mask = capacity_power_of_two - 1
        self.ring: List[Optional[Any]] = [None] * self.capacity
        self.p_seq = 0
        self.c_seq = 0

    def push(self, item: Any) -> bool:
        if (self.p_seq - self.c_seq) >= self.capacity:
            return False
        self.ring[self.p_seq & self.mask] = item
        self.p_seq += 1
        return True

    def pop(self) -> Optional[Any]:
        if self.c_seq >= self.p_seq:
            return None
        item = self.ring[self.c_seq & self.mask]
        self.c_seq += 1
        return item


class AxiomOrderBook:
    """Pre-allocated Level-3 Limit Order Book with binary ITCH parser."""
    ITCH_FMT = ">cQcII"  # Type, OrderID, Side, Shares, Price (18 bytes)
    ITCH_SIZE = struct.calcsize(ITCH_FMT)

    def __init__(self):
        self.orders: Dict[int, Tuple[str, int, int]] = {}
        self.bids: Dict[int, int] = {}
        self.asks: Dict[int, int] = {}

    @classmethod
    def serialize_itch_order(cls, order_id: int, side: str, shares: int, price: int) -> bytes:
        return struct.pack(cls.ITCH_FMT, b"A", order_id, side.encode("ascii"), shares, price)

    def process_itch_bytes(self, raw: bytes) -> None:
        msg_t, o_id, side, shares, price = struct.unpack(self.ITCH_FMT, raw[:self.ITCH_SIZE])
        self.add_order(o_id, side.decode("ascii"), price, shares)

    def add_order(self, order_id: int, side: str, price: int, shares: int) -> None:
        self.orders[order_id] = (side, price, shares)
        if side == "B":
            self.bids[price] = self.bids.get(price, 0) + shares
        else:
            self.asks[price] = self.asks.get(price, 0) + shares

    def cancel_order(self, order_id: int) -> None:
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


# ==============================================================================
# MODULE 4: EVENT-TIME WATERMARK VWAP STREAMING ENGINE
# ==============================================================================

class AxiomTradeTick:
    """Financial trade tick with physical event timestamp."""
    def __init__(self, symbol: str, price: float, volume: int, event_time_ms: int):
        self.symbol = symbol
        self.price = price
        self.volume = volume
        self.event_time = event_time_ms


class AxiomVWAPStreamingEngine:
    """
    Computes rolling Volume-Weighted Average Price (VWAP) in event time with watermarks.
    VWAP = sum(price * volume) / sum(volume).
    """
    def __init__(self, window_size_ms: int = 1000, max_delay_ms: int = 200):
        self.window_size = window_size_ms
        self.max_delay = max_delay_ms
        self.max_event_time = 0
        # Maps (window_start, window_end, symbol) -> [sum_pv, sum_v]
        self.windows: Dict[Tuple[int, int, str], List[float]] = {}
        self.committed_vwap: List[Tuple[int, int, str, float, int]] = []

    def ingest_tick(self, tick: AxiomTradeTick) -> List[Tuple[int, int, str, float, int]]:
        if tick.event_time > self.max_event_time:
            self.max_event_time = tick.event_time

        # Tumbling window bucket
        start = tick.event_time - (tick.event_time % self.window_size)
        end = start + self.window_size
        k = (start, end, tick.symbol)

        if k not in self.windows:
            self.windows[k] = [0.0, 0.0]
        self.windows[k][0] += tick.price * tick.volume
        self.windows[k][1] += tick.volume

        # Trigger watermarked windows: W = T_max - max_delay
        watermark = self.max_event_time - self.max_delay
        fired = []
        to_del = []
        for (w_start, w_end, sym), (pv, v) in self.windows.items():
            if w_end <= watermark:
                vwap = pv / max(1.0, v)
                record = (w_start, w_end, sym, vwap, int(v))
                fired.append(record)
                to_del.append((w_start, w_end, sym))

        for key in to_del:
            del self.windows[key]

        # Two-Phase Commit simulation: directly commit closed window
        self.committed_vwap.extend(fired)
        return fired
