"""
Level 5 Chapter 04 Programming Lab: Web Architecture, API Design & Protocols
===========================================================================
Focus: RESTful Idempotent Gateway simulation with Redis lock/cache semantics,
       DataLoader solving the GraphQL N+1 problem, and Protocol Buffer Varint
       binary serialization benchmarking against JSON.
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")
from typing import Dict, List, Set, Tuple, Optional, Any, Callable
import json
import time


# ---------------------------------------------------------------------------
# 1. RESTful Idempotent API Gateway Simulator
# ---------------------------------------------------------------------------

class IdempotencyRecord:
    def __init__(self, status: str, response_payload: Optional[Dict[str, Any]] = None):
        self.status = status  # "IN_PROGRESS", "COMPLETED"
        self.response = response_payload


class IdempotentPaymentGateway:
    """
    Simulates Stripe-style Idempotency-Key header handling backed by an in-memory Redis cache.
    """
    def __init__(self):
        self._cache: Dict[str, IdempotencyRecord] = {}
        self.processed_transactions: List[Dict[str, Any]] = []

    def handle_charge_request(self, idempotency_key: str, user_id: str, amount: float) -> Tuple[int, Dict[str, Any]]:
        # Check cache
        if idempotency_key in self._cache:
            record = self._cache[idempotency_key]
            if record.status == "IN_PROGRESS":
                return 409, {"error": "Concurrent request in progress with same idempotency key."}
            elif record.status == "COMPLETED":
                # Return cached response directly without re-charging
                return 200, record.response

        # Acquire lock: Mark IN_PROGRESS
        self._cache[idempotency_key] = IdempotencyRecord(status="IN_PROGRESS")

        # Execute business logic (charge card)
        tx_id = f"TXN_{len(self.processed_transactions) + 1001}"
        record_data = {"transaction_id": tx_id, "user_id": user_id, "amount": amount, "status": "PAID"}
        self.processed_transactions.append(record_data)

        # Store response and mark COMPLETED
        response = {"success": True, "data": record_data}
        self._cache[idempotency_key] = IdempotencyRecord(status="COMPLETED", response_payload=response)

        return 201, response


# ---------------------------------------------------------------------------
# 2. DataLoader: Solving the GraphQL N+1 Query Problem
# ---------------------------------------------------------------------------

class MockDatabase:
    def __init__(self):
        self.query_count = 0
        self.posts_table = {
            1: [{"id": 101, "title": "Intro to CS"}, {"id": 102, "title": "Compilers"}],
            2: [{"id": 201, "title": "Database Internals"}],
            3: [{"id": 301, "title": "Distributed Systems"}, {"id": 302, "title": "Raft"}],
        }

    def batch_fetch_posts_by_user_ids(self, user_ids: List[int]) -> Dict[int, List[Dict[str, Any]]]:
        self.query_count += 1
        # Simulates: SELECT * FROM posts WHERE user_id IN (...)
        return {uid: self.posts_table.get(uid, []) for uid in user_ids}


class DataLoader:
    def __init__(self, batch_fn: Callable[[List[int]], Dict[int, Any]]):
        self._batch_fn = batch_fn
        self._queue: List[int] = []
        self._cache: Dict[int, Any] = {}

    def queue_load(self, key: int):
        if key not in self._cache and key not in self._queue:
            self._queue.append(key)

    def execute_batch(self):
        if not self._queue:
            return
        results = self._batch_fn(self._queue)
        for k, v in results.items():
            self._cache[k] = v
        self._queue.clear()

    def get(self, key: int) -> Any:
        return self._cache.get(key)


# ---------------------------------------------------------------------------
# 3. Protocol Buffer Binary Varint Serialization Engine
# ---------------------------------------------------------------------------

def encode_varint(value: int) -> bytes:
    """
    Encodes an integer into Protocol Buffer 7-bit Varint wire format.
    The most significant bit (MSB) of each byte indicates if more bytes follow.
    """
    out = bytearray()
    while value >= 0x80:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    out.append(value & 0x7F)
    return bytes(out)


def decode_varint(data: bytes) -> Tuple[int, int]:
    """
    Decodes a Varint from bytes.
    Returns (decoded_integer, bytes_consumed).
    """
    res = 0
    shift = 0
    for i, b in enumerate(data):
        res |= (b & 0x7F) << shift
        if not (b & 0x80):
            return res, i + 1
        shift += 7
    raise ValueError("Truncated Varint payload")


def encode_protobuf_field(field_num: int, wire_type: int, value: int) -> bytes:
    """
    Protobuf wire layout: Tag = (field_num << 3) | wire_type, followed by value.
    wire_type 0 = Varint.
    """
    tag = (field_num << 3) | wire_type
    tag_bytes = encode_varint(tag)
    val_bytes = encode_varint(value)
    return tag_bytes + val_bytes


def test_web_api_suite():
    print("[TEST 1] RESTful Idempotent Payment Gateway...")
    gw = IdempotentPaymentGateway()
    key = "idem-key-uuid-9988-7766"

    # First request: new payment creation (HTTP 201)
    status1, resp1 = gw.handle_charge_request(key, user_id="U1", amount=150.0)
    assert status1 == 201, f"Expected 201 Created, got {status1}"
    assert len(gw.processed_transactions) == 1, "Expected exactly 1 processed transaction"
    print(f"  -> Initial charge: HTTP {status1}, TxID: {resp1['data']['transaction_id']}")

    # Second request: retry with identical key (must return HTTP 200 without charging again!)
    status2, resp2 = gw.handle_charge_request(key, user_id="U1", amount=150.0)
    assert status2 == 200, f"Expected 200 OK from cache, got {status2}"
    assert len(gw.processed_transactions) == 1, "Idempotency violated: duplicate transaction created!"
    assert resp2 == resp1, "Cached response payload mismatch"
    print(f"  -> Retried charge: HTTP {status2} (Idempotency cache replay verified).")

    print("[TEST 2] DataLoader Solving GraphQL N+1 Query Bottleneck...")
    db = MockDatabase()
    loader = DataLoader(db.batch_fetch_posts_by_user_ids)

    # 3 user nodes in GraphQL AST request posts simultaneously
    users = [1, 2, 3]
    for u in users:
        loader.queue_load(u)

    # Coalesced single batch execution
    loader.execute_batch()

    # Resolvers retrieve results from DataLoader in-memory cache
    for u in users:
        posts = loader.get(u)
        assert len(posts) >= 1, f"Missing posts for user {u}"

    # Verify query count is strictly 1 (instead of 3 separate queries!)
    assert db.query_count == 1, f"Expected 1 batched query, got {db.query_count} (N+1 regression)"
    print(f"  -> Successfully resolved {len(users)} user post associations in exactly {db.query_count} SQL batch query.")

    print("[TEST 3] Protocol Buffer Binary Varint Serialization Benchmark...")
    test_values = [0, 1, 127, 128, 300, 1000000]
    for val in test_values:
        encoded = encode_varint(val)
        decoded, consumed = decode_varint(encoded)
        assert decoded == val, f"Varint roundtrip failed for {val}"

    # Comparison: Protobuf payload vs JSON payload for integer {id: 1042}
    json_bytes = json.dumps({"id": 1042}).encode("utf-8")
    proto_bytes = encode_protobuf_field(field_num=1, wire_type=0, value=1042)

    print(f"  -> JSON Payload: {json_bytes} ({len(json_bytes)} bytes)")
    print(f"  -> Protobuf Wire: {proto_bytes.hex()} ({len(proto_bytes)} bytes)")
    assert len(proto_bytes) < len(json_bytes), "Protobuf should be significantly more compact than JSON"
    print(f"  -> Protobuf achieved {((len(json_bytes) - len(proto_bytes)) / len(json_bytes)) * 100:.1f}% size reduction over JSON.")

    print("ALL Level 5 Chapter 04 Web API lab tests passed successfully!")


if __name__ == "__main__":
    test_web_api_suite()
