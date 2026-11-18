# -*- coding: utf-8 -*-
"""
Stratos Platform: Resilient Microservices Mesh Verifier
======================================================
Automated test suite verifying:
1. HMAC Token Authentication & Token Bucket Rate Limiting.
2. W3C Distributed Context Propagation and Span Tree.
3. Happy-path Distributed Saga Transaction.
4. Out-of-Stock Distributed Saga Compensating Transaction (Reverse Rollback).
5. Resilient Retries with AWS Full Jitter Backoff.
6. State-Machine Circuit Breaker (CLOSED -> OPEN -> HALF_OPEN -> CLOSED).
7. Bulkhead Resource Partitioning.
8. Prometheus Metrics & Google SRE Multiwindow Burn Rate Alerting.
"""
import sys
import time
import random
from typing import Dict, Any

# Ensure import from same directory
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stratos_platform import (
    StratosGateway,
    TokenBucketLimiter,
    HMACAuthenticator,
    W3CContext,
    ResilientCircuitBreaker,
    CircuitBreakerState,
    CircuitBreakerTrippedException,
    BulkheadLimiter,
    BulkheadFullException,
    ResilientRetryEngine,
    SREBurnRateMonitor
)

sys.stdout.reconfigure(encoding="utf-8")


def run_all_tests():
    print("=====================================================================")
    print("  STRATOS PLATFORM: LEVEL 5 CAPSTONE VERIFICATION TESTBED")
    print("=====================================================================\n")

    SECRET = "super_secure_enterprise_cloud_key_2026"
    gateway = StratosGateway(secret_key=SECRET)
    
    # -------------------------------------------------------------------------
    # Test 1: HMAC Token Authentication & Tamper Detection
    # -------------------------------------------------------------------------
    print("Test 1: HMAC Cryptographic Authentication & Tamper Detection...")
    auth = HMACAuthenticator(SECRET)
    valid_token = auth.generate_token(subject="user_vip_001", role="ADMIN")
    ok, sub, role = auth.verify_token(valid_token)
    assert ok is True and sub == "user_vip_001" and role == "ADMIN"

    # Tampered token: change role or signature
    tampered = valid_token.replace("ADMIN", "ROOT_SUPERUSER")
    tampered_ok, _, _ = auth.verify_token(tampered)
    assert tampered_ok is False
    print("  [PASS] HMAC Token Signature Validated & Tampering Prevented")

    # -------------------------------------------------------------------------
    # Test 2: Token Bucket Rate Limiting
    # -------------------------------------------------------------------------
    print("\nTest 2: Token Bucket Rate Limiting Burst Defense...")
    bucket = TokenBucketLimiter(capacity=5.0, refill_rate_per_sec=10.0)
    
    # Consume all 5 tokens
    for i in range(5):
        assert bucket.allow(1.0) is True, f"Token {i+1} should be granted"
    
    # 6th immediate request must be rejected
    assert bucket.allow(1.0) is False, "Burst beyond capacity must be rejected"
    
    # Wait 0.15s -> should refill at least 1 token (10 tokens/sec * 0.15s = 1.5 tokens)
    time.sleep(0.15)
    assert bucket.allow(1.0) is True, "Token should be allowed after refill"
    print("  [PASS] Token Bucket Rate Limiter Enforced Burst Boundaries (HTTP 429 semantics)")

    # -------------------------------------------------------------------------
    # Test 3: W3C Distributed Context Propagation
    # -------------------------------------------------------------------------
    print("\nTest 3: W3C Traceparent Distributed Context Propagation...")
    tid = W3CContext.generate_trace_id()
    sid = W3CContext.generate_span_id()
    hdr = W3CContext.format_header(tid, sid, sampled=True)
    
    assert hdr.startswith("00-") and hdr.endswith("-01")
    parsed_tid, parsed_sid, sampled = W3CContext.parse_header(hdr)
    assert parsed_tid == tid and parsed_sid == sid and sampled is True
    print(f"  [PASS] W3C traceparent standard ({hdr}) parsed and validated")

    # -------------------------------------------------------------------------
    # Test 4: Happy-path Distributed Saga Transaction
    # -------------------------------------------------------------------------
    print("\nTest 4: Happy-Path Distributed Saga Execution...")
    gateway.payment_service.set_balance("user_vip_001", 500.0)
    gateway.inventory_service.set_stock("SKU_PRO_LAPTOP", 10)
    
    res = gateway.handle_checkout(
        token=valid_token,
        order_id="ORD_1001",
        user_id="user_vip_001",
        sku="SKU_PRO_LAPTOP",
        amount=199.99
    )
    
    assert res["status"] == 200, f"Expected 200 OK, got {res}"
    assert res["executed_steps"] == ["CreateOrder", "ProcessPayment", "ReserveInventory"]
    assert gateway.order_service.orders["ORD_1001"].status == "CONFIRMED"
    assert round(gateway.payment_service.user_balances["user_vip_001"], 2) == 300.01
    assert gateway.inventory_service.stock["SKU_PRO_LAPTOP"] == 9
    assert gateway.metrics.get_counter("http_requests_total", {"path": "/checkout", "status": "200"}) == 1.0
    print("  [PASS] Happy-Path Saga Committed: Order Confirmed, Balance Deducted, Stock Decremented")

    # -------------------------------------------------------------------------
    # Test 5: Distributed Saga Compensation (Out-of-Stock Rollback)
    # -------------------------------------------------------------------------
    print("\nTest 5: Out-of-Stock Distributed Saga Backward Compensation...")
    gateway.inventory_service.set_stock("SKU_RARE_BOOK", 0)  # Empty stock!
    
    res_stockout = gateway.handle_checkout(
        token=valid_token,
        order_id="ORD_1002",
        user_id="user_vip_001",
        sku="SKU_RARE_BOOK",
        amount=50.0
    )
    
    assert res_stockout["status"] == 500
    assert "out of stock" in res_stockout["error"]
    assert res_stockout["executed_steps"] == ["CreateOrder", "ProcessPayment"]
    # Compensations must reverse in opposite order: ProcessPayment, then CreateOrder
    assert res_stockout["compensated_steps"] == ["ProcessPayment", "CreateOrder"]
    
    # Verify balance was refunded (still 300.01)
    assert round(gateway.payment_service.user_balances["user_vip_001"], 2) == 300.01
    # Verify order was cancelled
    assert "CANCELLED" in gateway.order_service.orders["ORD_1002"].status
    # Verify inventory was untouched
    assert gateway.inventory_service.stock["SKU_RARE_BOOK"] == 0
    print("  [PASS] Saga Backward Compensation: Payment Refunded & Order Cancelled on Failure")

    # -------------------------------------------------------------------------
    # Test 6: AWS Full Jitter Retry Engine
    # -------------------------------------------------------------------------
    print("\nTest 6: Resilient Retries with AWS Full Jitter Backoff...")
    transient_attempts = 0
    def flaky_service():
        nonlocal transient_attempts
        transient_attempts += 1
        if transient_attempts < 3:
            raise ConnectionError("Transient network blip")
        return "SUCCESS_DATA"

    retry_rng = random.Random(1337)
    retry_res = ResilientRetryEngine.execute_with_jitter(flaky_service, max_retries=4, base_ms=5.0, cap_ms=50.0, rng=retry_rng)
    assert retry_res == "SUCCESS_DATA"
    assert transient_attempts == 3
    print(f"  [PASS] Flaky service recovered on attempt {transient_attempts} using AWS Full Jitter")

    # -------------------------------------------------------------------------
    # Test 7: Circuit Breaker State Machine & Fast-Fail
    # -------------------------------------------------------------------------
    print("\nTest 7: Circuit Breaker State Machine (CLOSED -> OPEN -> HALF_OPEN -> CLOSED)...")
    cb = ResilientCircuitBreaker("auth_breaker", failure_threshold=3, recovery_timeout_s=0.2, half_open_needed=2)
    assert cb.state == CircuitBreakerState.CLOSED

    def failing_call():
        raise RuntimeError("Downstream microservice 500 Internal Error")

    # Trip the breaker
    for _ in range(3):
        try:
            cb.execute(failing_call)
        except RuntimeError:
            pass
    assert cb.state == CircuitBreakerState.OPEN
    print("  [PASS] Circuit Breaker tripped from CLOSED -> OPEN after 3 consecutive errors")

    # Subsequent call fast-fails immediately without touching downstream
    try:
        cb.execute(lambda: "SHOULD_NOT_EXECUTE")
        assert False, "Should raise CircuitBreakerTrippedException"
    except CircuitBreakerTrippedException as e:
        assert "is OPEN" in str(e)
    print("  [PASS] Fast-fail verified while OPEN")

    # Sleep past recovery timeout
    time.sleep(0.25)

    # First probe success -> enters HALF_OPEN
    p1 = cb.execute(lambda: "PROBE_1_OK")
    assert p1 == "PROBE_1_OK"
    assert cb.state == CircuitBreakerState.HALF_OPEN

    # Second probe success -> meets half_open_needed=2 -> resets to CLOSED
    p2 = cb.execute(lambda: "PROBE_2_OK")
    assert p2 == "PROBE_2_OK"
    assert cb.state == CircuitBreakerState.CLOSED
    print("  [PASS] Circuit Breaker probe recovery: OPEN -> HALF_OPEN -> CLOSED verified")

    # -------------------------------------------------------------------------
    # Test 8: Bulkhead Resource Partitioning
    # -------------------------------------------------------------------------
    print("\nTest 8: Bulkhead Resource Partitioning...")
    bulkhead = BulkheadLimiter("db_pool", max_concurrent=2)
    bulkhead.active_count = 2
    try:
        bulkhead.execute(lambda: "OK")
        assert False, "Should raise BulkheadFullException"
    except BulkheadFullException as e:
        assert "capacity (2) saturated" in str(e)
    bulkhead.active_count = 0
    print("  [PASS] Bulkhead Pool Isolation verified")

    # -------------------------------------------------------------------------
    # Test 9: Observability & SRE Multiwindow Burn-Rate Alerting
    # -------------------------------------------------------------------------
    print("\nTest 9: Google SRE Multiwindow Burn Rate Alerting Engine...")
    sre = SREBurnRateMonitor(slo_target=0.999, window_days=30)
    
    # SEV-1 Critical Alert: 1.44% errors in 1h (Burn Rate 14.4x -> depletes in 50 hours)
    alert_sev1 = sre.evaluate_alert(window_hours=1.0, observed_error_rate=0.0144)
    assert abs(alert_sev1["burn_rate"] - 14.4) < 1e-4
    assert round(alert_sev1["time_to_exhaustion_hours"], 1) == 50.0
    assert alert_sev1["severity"] == "PAGE_SEV1"
    print(f"  [PASS] SRE Page Alert Triggered: '{alert_sev1['message']}'")

    # SEV-2 Ticket Warning: 0.6% errors in 6h (Burn Rate 6.0x -> depletes in 120 hours)
    alert_sev2 = sre.evaluate_alert(window_hours=6.0, observed_error_rate=0.006)
    assert abs(alert_sev2["burn_rate"] - 6.0) < 1e-4
    assert round(alert_sev2["time_to_exhaustion_hours"], 1) == 120.0
    assert alert_sev2["severity"] == "TICKET_SEV2"
    print(f"  [PASS] SRE Ticket Warning Triggered: '{alert_sev2['message']}'")

    print("\n=====================================================================")
    print("  ALL 9 CAPSTONE VERIFICATION TESTS PASSED SUCCESSFULLY (Exit Code 0)")
    print("=====================================================================")


if __name__ == "__main__":
    run_all_tests()
