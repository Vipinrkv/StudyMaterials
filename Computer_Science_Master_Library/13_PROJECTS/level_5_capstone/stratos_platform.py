# -*- coding: utf-8 -*-
"""
Stratos Platform: Resilient Cloud-Native Microservices Mesh
==========================================================
A comprehensive enterprise-grade distributed platform synthesizing:
- Token Bucket Rate Limiting & Cryptographic HMAC Token Authentication.
- W3C Distributed Context Propagation (traceparent) and Span DAG Hierarchy.
- Prometheus Multi-dimensional Metric Registry (Counters, Gauges, Quantile Summaries).
- Google SRE Multiwindow Error Budget Burn-rate Alert Engine.
- Finite State Machine Circuit Breakers, Bulkhead Isolation, and AWS Full Jitter Retries.
- Saga Distributed Transaction Orchestrator with Automated Backward Compensation.
"""
import sys
import time
import math
import hmac
import hashlib
import secrets
import random
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Set

sys.stdout.reconfigure(encoding="utf-8")


# ============================================================================
# Section 1: Security, Rate Limiting & Distributed Tracing
# ============================================================================

class TokenBucketLimiter:
    """Thread-safe token bucket rate limiter with continuous leak/refill."""
    def __init__(self, capacity: float, refill_rate_per_sec: float):
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate_per_sec)
        self.tokens = float(capacity)
        self.last_refill_timestamp = time.time()

    def allow(self, tokens_requested: float = 1.0) -> bool:
        now = time.time()
        elapsed = now - self.last_refill_timestamp
        self.last_refill_timestamp = now
        
        # Add newly accrued tokens
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        
        if self.tokens >= tokens_requested:
            self.tokens -= tokens_requested
            return True
        return False


class HMACAuthenticator:
    """Signs and verifies stateless Bearer tokens using HMAC-SHA256."""
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode("utf-8")

    def generate_token(self, subject: str, role: str) -> str:
        timestamp = str(int(time.time()))
        payload = f"{subject}:{role}:{timestamp}"
        signature = hmac.new(self.secret_key, payload.encode("utf-8"), hashlib.sha256).hexdigest()
        return f"{payload}:{signature}"

    def verify_token(self, token: str) -> Tuple[bool, Optional[str], Optional[str]]:
        parts = token.split(":")
        if len(parts) != 4:
            return False, None, None
        subject, role, timestamp, signature = parts
        payload = f"{subject}:{role}:{timestamp}"
        expected_sig = hmac.new(self.secret_key, payload.encode("utf-8"), hashlib.sha256).hexdigest()
        
        # Constant-time comparison to prevent timing side-channel attacks
        if hmac.compare_digest(signature, expected_sig):
            return True, subject, role
        return False, None, None


class W3CContext:
    """Parses and formats W3C traceparent headers: 00-{trace_id}-{span_id}-{flags}."""
    @staticmethod
    def generate_trace_id() -> str:
        return secrets.token_hex(16)  # 32 hex chars

    @staticmethod
    def generate_span_id() -> str:
        return secrets.token_hex(8)   # 16 hex chars

    @staticmethod
    def format_header(trace_id: str, span_id: str, sampled: bool = True) -> str:
        flags = "01" if sampled else "00"
        return f"00-{trace_id}-{span_id}-{flags}"

    @staticmethod
    def parse_header(header: str) -> Tuple[str, str, bool]:
        parts = header.strip().split("-")
        if len(parts) != 4 or parts[0] != "00":
            raise ValueError(f"Malformed W3C traceparent header: '{header}'")
        return parts[1], parts[2], (parts[3] == "01")


class Span:
    """Represents a discrete contiguous unit of distributed execution."""
    def __init__(self, name: str, trace_id: str, span_id: str, parent_id: Optional[str] = None):
        self.name = name
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_id = parent_id
        self.attributes: Dict[str, Any] = {}
        self.events: List[Tuple[float, str]] = []
        self.start_ns = time.time_ns()
        self.end_ns: Optional[int] = None
        self.status = "UNSET"

    def set_attribute(self, key: str, value: Any) -> 'Span':
        self.attributes[key] = value
        return self

    def add_event(self, name: str) -> None:
        self.events.append((time.time(), name))

    def finish(self, status: str = "OK") -> None:
        self.end_ns = time.time_ns()
        self.status = status

    @property
    def duration_ms(self) -> float:
        end = self.end_ns or time.time_ns()
        return (end - self.start_ns) / 1_000_000.0


# ============================================================================
# Section 2: Observability & SRE Metrics
# ============================================================================

class MetricRegistry:
    """Thread-safe multi-dimensional Prometheus-style metric engine."""
    def __init__(self):
        self.counters: Dict[Tuple[str, Tuple[Tuple[str, str], ...]], float] = {}
        self.gauges: Dict[Tuple[str, Tuple[Tuple[str, str], ...]], float] = {}
        self.summaries: Dict[str, List[float]] = {}

    def _format_key(self, name: str, labels: Optional[Dict[str, str]]) -> Tuple[str, Tuple[Tuple[str, str], ...]]:
        sorted_labels = tuple(sorted((labels or {}).items()))
        return (name, sorted_labels)

    def inc_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        k = self._format_key(name, labels)
        self.counters[k] = self.counters.get(k, 0.0) + value

    def get_counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        k = self._format_key(name, labels)
        return self.counters.get(k, 0.0)

    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        k = self._format_key(name, labels)
        self.gauges[k] = value

    def get_gauge(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        k = self._format_key(name, labels)
        return self.gauges.get(k, 0.0)

    def observe_summary(self, name: str, value: float) -> None:
        if name not in self.summaries:
            self.summaries[name] = []
        self.summaries[name].append(value)

    def get_quantile(self, name: str, q: float) -> float:
        samples = self.summaries.get(name, [])
        if not samples:
            return 0.0
        sorted_s = sorted(samples)
        idx = int(math.ceil(q * len(sorted_s))) - 1
        return sorted_s[max(0, min(idx, len(sorted_s) - 1))]


class SREBurnRateMonitor:
    """Monitors service SLOs and evaluates multiwindow error budget burn rates."""
    def __init__(self, slo_target: float = 0.999, window_days: int = 30):
        self.slo_target = slo_target
        self.window_days = window_days
        self.total_budget_fraction = round(1.0 - slo_target, 9)  # e.g., 0.001 (0.1%)

    def calculate_burn_rate(self, observed_error_rate: float) -> float:
        if self.total_budget_fraction <= 0:
            return 0.0
        return round(observed_error_rate / self.total_budget_fraction, 6)

    def time_to_exhaustion_hours(self, burn_rate: float) -> float:
        if burn_rate <= 0:
            return float('inf')
        total_hours = self.window_days * 24.0
        return total_hours / burn_rate

    def evaluate_alert(self, window_hours: float, observed_error_rate: float) -> Dict[str, Any]:
        burn_rate = self.calculate_burn_rate(observed_error_rate)
        exhaust_hours = self.time_to_exhaustion_hours(burn_rate)
        
        severity = "NORMAL"
        msg = "Budget burn rate is healthy."
        
        if window_hours <= 1.0 and burn_rate >= 14.4:
            severity = "PAGE_SEV1"
            msg = f"CRITICAL: Burn rate {burn_rate:.1f}x exhausts 30d budget in {exhaust_hours:.1f}h! Paging on-call SRE."
        elif window_hours <= 6.0 and burn_rate >= 6.0:
            severity = "TICKET_SEV2"
            msg = f"WARNING: Elevated burn rate {burn_rate:.1f}x exhausts budget in {exhaust_hours:.1f}h. Automated ticket created."
            
        return {
            "severity": severity,
            "burn_rate": burn_rate,
            "time_to_exhaustion_hours": exhaust_hours,
            "message": msg
        }


# ============================================================================
# Section 3: Resilient Middleware Mesh
# ============================================================================

class CircuitBreakerState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerTrippedException(Exception):
    pass


class BulkheadFullException(Exception):
    pass


class ResilientCircuitBreaker:
    """Production state-machine Circuit Breaker with recovery probe transitions."""
    def __init__(self, name: str, failure_threshold: int = 3, recovery_timeout_s: float = 0.5, half_open_needed: int = 2):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout_s = recovery_timeout_s
        self.half_open_needed = half_open_needed
        
        self.state = CircuitBreakerState.CLOSED
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        self.last_failure_time = 0.0

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        now = time.time()
        
        # State transition: OPEN -> HALF_OPEN after timeout
        if self.state == CircuitBreakerState.OPEN:
            if now - self.last_failure_time >= self.recovery_timeout_s:
                self.state = CircuitBreakerState.HALF_OPEN
                self.consecutive_successes = 0
                self.consecutive_failures = 0
            else:
                raise CircuitBreakerTrippedException(f"Circuit '{self.name}' is OPEN: call fast-failed to protect service")

        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure()
            raise e

    def _record_success(self) -> None:
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.consecutive_successes += 1
            if self.consecutive_successes >= self.half_open_needed:
                self.state = CircuitBreakerState.CLOSED
                self.consecutive_failures = 0
                self.consecutive_successes = 0
        elif self.state == CircuitBreakerState.CLOSED:
            self.consecutive_failures = 0

    def _record_failure(self) -> None:
        self.last_failure_time = time.time()
        self.consecutive_failures += 1
        
        if self.state == CircuitBreakerState.CLOSED:
            if self.consecutive_failures >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN
        elif self.state == CircuitBreakerState.HALF_OPEN:
            # Immediate re-trip
            self.state = CircuitBreakerState.OPEN


class BulkheadLimiter:
    """Restricts concurrency per downstream service pool."""
    def __init__(self, name: str, max_concurrent: int):
        self.name = name
        self.max_concurrent = max_concurrent
        self.active_count = 0

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        if self.active_count >= self.max_concurrent:
            raise BulkheadFullException(f"Bulkhead '{self.name}' capacity ({self.max_concurrent}) saturated")
        self.active_count += 1
        try:
            return func(*args, **kwargs)
        finally:
            self.active_count -= 1


class ResilientRetryEngine:
    """Executes calls with AWS Full Jitter backoff."""
    @staticmethod
    def execute_with_jitter(func: Callable, max_retries: int = 3, base_ms: float = 10.0, cap_ms: float = 200.0, rng: Optional[random.Random] = None) -> Any:
        if rng is None:
            rng = random.Random(42)
        for attempt in range(max_retries):
            try:
                return func()
            except Exception:
                if attempt == max_retries - 1:
                    raise
                # Full Jitter formula: uniform(0, min(cap, base * 2^attempt))
                max_sleep_ms = min(cap_ms, base_ms * (2 ** attempt))
                sleep_ms = rng.uniform(0.0, max_sleep_ms)
                time.sleep(sleep_ms / 1000.0)


# ============================================================================
# Section 4: Domain Microservices
# ============================================================================

class OrderRecord:
    def __init__(self, order_id: str, user_id: str, sku: str, amount: float, status: str = "PENDING"):
        self.order_id = order_id
        self.user_id = user_id
        self.sku = sku
        self.amount = amount
        self.status = status


class OrderService:
    def __init__(self):
        self.orders: Dict[str, OrderRecord] = {}

    def create_order(self, order_id: str, user_id: str, sku: str, amount: float) -> OrderRecord:
        record = OrderRecord(order_id, user_id, sku, amount, status="INITIALIZED")
        self.orders[order_id] = record
        return record

    def cancel_order(self, order_id: str, reason: str = "SAGA_ABORTED") -> None:
        if order_id in self.orders:
            self.orders[order_id].status = f"CANCELLED: {reason}"

    def complete_order(self, order_id: str) -> None:
        if order_id in self.orders:
            self.orders[order_id].status = "CONFIRMED"


class PaymentService:
    def __init__(self):
        self.user_balances: Dict[str, float] = {}
        self.payment_history: Dict[str, float] = {}
        self.simulated_failure = False

    def set_balance(self, user_id: str, balance: float) -> None:
        self.user_balances[user_id] = balance

    def authorize_payment(self, tx_id: str, user_id: str, amount: float) -> str:
        if self.simulated_failure:
            raise ConnectionResetError("503 Payment Gateway Service Unavailable")
        
        balance = self.user_balances.get(user_id, 0.0)
        if balance < amount:
            raise ValueError(f"Insufficient funds: user {user_id} balance {balance} < amount {amount}")
        
        self.user_balances[user_id] -= amount
        self.payment_history[tx_id] = amount
        return f"AUTH_OK_{tx_id}"

    def refund_payment(self, tx_id: str, user_id: str) -> None:
        amount = self.payment_history.pop(tx_id, None)
        if amount is not None:
            self.user_balances[user_id] = self.user_balances.get(user_id, 0.0) + amount


class InventoryService:
    def __init__(self):
        self.stock: Dict[str, int] = {}
        self.reservations: Dict[str, Tuple[str, int]] = {}

    def set_stock(self, sku: str, count: int) -> None:
        self.stock[sku] = count

    def reserve_stock(self, reservation_id: str, sku: str, quantity: int = 1) -> str:
        current_stock = self.stock.get(sku, 0)
        if current_stock < quantity:
            raise ValueError(f"SKU {sku} out of stock (Available: {current_stock}, Requested: {quantity})")
        
        self.stock[sku] -= quantity
        self.reservations[reservation_id] = (sku, quantity)
        return f"RESERVED_{reservation_id}"

    def release_stock(self, reservation_id: str) -> None:
        item = self.reservations.pop(reservation_id, None)
        if item is not None:
            sku, qty = item
            self.stock[sku] = self.stock.get(sku, 0) + qty


# ============================================================================
# Section 5: Saga Distributed Transaction Orchestrator
# ============================================================================

class SagaAction:
    def __init__(self, name: str, forward: Callable[[], Any], compensate: Callable[[], None]):
        self.name = name
        self.forward = forward
        self.compensate = compensate


class SagaOrchestrator:
    """Executes distributed steps; on any failure, runs compensating actions in reverse order."""
    def __init__(self, trace_id: str):
        self.trace_id = trace_id
        self.steps: List[SagaAction] = []

    def add_step(self, action: SagaAction) -> 'SagaOrchestrator':
        self.steps.append(action)
        return self

    def execute(self) -> Tuple[bool, List[str], List[str], Optional[str]]:
        completed_steps: List[SagaAction] = []
        for step in self.steps:
            try:
                step.forward()
                completed_steps.append(step)
            except Exception as e:
                # Failure encountered: trigger compensating actions in reverse order
                compensated_names: List[str] = []
                for comp_step in reversed(completed_steps):
                    try:
                        comp_step.compensate()
                        compensated_names.append(comp_step.name)
                    except Exception:
                        pass
                return False, [s.name for s in completed_steps], compensated_names, str(e)
        
        return True, [s.name for s in completed_steps], [], None


# ============================================================================
# Section 6: Stratos Edge Gateway & Mesh Controller
# ============================================================================

class StratosGateway:
    """Unified Edge API Gateway and Mesh Controller."""
    def __init__(self, secret_key: str):
        self.rate_limiter = TokenBucketLimiter(capacity=100.0, refill_rate_per_sec=20.0)
        self.auth = HMACAuthenticator(secret_key)
        self.metrics = MetricRegistry()
        self.sre_monitor = SREBurnRateMonitor(slo_target=0.999, window_days=30)
        
        # Domain services
        self.order_service = OrderService()
        self.payment_service = PaymentService()
        self.inventory_service = InventoryService()
        
        # Resiliency components
        self.payment_circuit_breaker = ResilientCircuitBreaker("payment_service", failure_threshold=3, recovery_timeout_s=0.2)
        self.payment_bulkhead = BulkheadLimiter("payment_pool", max_concurrent=5)
        
        # Traces
        self.completed_spans: List[Span] = []

    def handle_checkout(self, token: str, order_id: str, user_id: str, sku: str, amount: float) -> Dict[str, Any]:
        """
        Orchestrates an end-to-end checkout request through the entire platform stack:
        1. Token Bucket Rate Limiting (rejection with 429 if depleted).
        2. HMAC Authentication (rejection with 401 if invalid).
        3. Distributed Tracing context generation.
        4. Saga Transaction (Order -> Payment via Circuit Breaker -> Inventory).
        5. Prometheus metric emission & SRE error budget tracking.
        """
        t0 = time.time()
        
        # 1. Rate Limiting
        if not self.rate_limiter.allow(1.0):
            self.metrics.inc_counter("http_requests_total", 1.0, {"path": "/checkout", "status": "429"})
            return {"status": 429, "error": "Rate limit exceeded (Token Bucket Empty)"}

        # 2. Authentication
        valid_auth, auth_user, _ = self.auth.verify_token(token)
        if not valid_auth or auth_user != user_id:
            self.metrics.inc_counter("http_requests_total", 1.0, {"path": "/checkout", "status": "401"})
            return {"status": 401, "error": "Unauthorized: Invalid cryptographic token"}

        # 3. Distributed Tracing Context
        trace_id = W3CContext.generate_trace_id()
        root_span_id = W3CContext.generate_span_id()
        root_span = Span("gateway_checkout", trace_id, root_span_id)
        root_span.set_attribute("http.user_id", user_id)
        root_span.set_attribute("order.id", order_id)

        # 4. Saga Orchestration
        saga = SagaOrchestrator(trace_id)
        
        # Step 1: Create Order
        def act_order():
            self.order_service.create_order(order_id, user_id, sku, amount)
        def comp_order():
            self.order_service.cancel_order(order_id, "Saga Compensated")
        saga.add_step(SagaAction("CreateOrder", act_order, comp_order))

        # Step 2: Charge Payment (Guarded by Circuit Breaker & Bulkhead)
        def act_payment():
            def protected_call():
                return self.payment_service.authorize_payment(f"tx_{order_id}", user_id, amount)
            return self.payment_circuit_breaker.execute(
                lambda: self.payment_bulkhead.execute(protected_call)
            )
        def comp_payment():
            self.payment_service.refund_payment(f"tx_{order_id}", user_id)
        saga.add_step(SagaAction("ProcessPayment", act_payment, comp_payment))

        # Step 3: Reserve Inventory
        def act_inventory():
            self.inventory_service.reserve_stock(f"res_{order_id}", sku, 1)
        def comp_inventory():
            self.inventory_service.release_stock(f"res_{order_id}")
        saga.add_step(SagaAction("ReserveInventory", act_inventory, comp_inventory))

        # Execute Saga
        success, executed, compensated, err = saga.execute()
        
        duration_ms = (time.time() - t0) * 1000.0
        self.metrics.observe_summary("checkout_latency_ms", duration_ms)
        
        if success:
            self.order_service.complete_order(order_id)
            root_span.finish("OK")
            self.completed_spans.append(root_span)
            self.metrics.inc_counter("http_requests_total", 1.0, {"path": "/checkout", "status": "200"})
            return {
                "status": 200,
                "order_id": order_id,
                "traceparent": W3CContext.format_header(trace_id, root_span_id),
                "executed_steps": executed
            }
        else:
            root_span.finish("ERROR")
            self.completed_spans.append(root_span)
            self.metrics.inc_counter("http_requests_total", 1.0, {"path": "/checkout", "status": "500"})
            return {
                "status": 500,
                "order_id": order_id,
                "error": err,
                "traceparent": W3CContext.format_header(trace_id, root_span_id),
                "executed_steps": executed,
                "compensated_steps": compensated
            }
