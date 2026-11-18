# -*- coding: utf-8 -*-
"""
CH08: Microservices Architecture and Distributed Data Lab
=========================================================
Covers:
1. Finite State Machine Circuit Breaker (CLOSED, OPEN, HALF_OPEN states with time-decay recovery).
2. Bulkhead Resource Partitioning Pattern (Independent capacity isolation).
3. Saga Distributed Transaction Coordinator with Automated Compensating Transactions.
"""
import sys
import time
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple, Any

sys.stdout.reconfigure(encoding="utf-8")


# ============================================================================
# Section 1: Finite State Machine Circuit Breaker
# ============================================================================

class CircuitState(Enum):
    CLOSED = "CLOSED"          # Normal operation: traffic flows through
    OPEN = "OPEN"              # Tripped: fast-fail immediately without touching downstream
    HALF_OPEN = "HALF_OPEN"    # Canary probe: allow limited test requests to assess recovery


class CircuitBreakerOpenException(Exception):
    """Raised when downstream call is rejected because Circuit Breaker is OPEN."""
    pass


class CircuitBreaker:
    """
    Production-grade state-machine Circuit Breaker (Michael Nygard pattern).
    """
    def __init__(self, failure_threshold: int = 3, recovery_timeout_s: float = 2.0, half_open_success_needed: int = 2):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_s = recovery_timeout_s
        self.half_open_success_needed = half_open_success_needed
        
        self.state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        self.last_failure_timestamp = 0.0

    def call(self, func: Callable, *args, **kwargs) -> Any:
        current_time = time.time()
        
        # State transition check: OPEN -> HALF_OPEN after timeout
        if self.state == CircuitState.OPEN:
            if current_time - self.last_failure_timestamp >= self.recovery_timeout_s:
                self.state = CircuitState.HALF_OPEN
                self.consecutive_successes = 0
                self.consecutive_failures = 0
            else:
                raise CircuitBreakerOpenException("Circuit is OPEN: fast-failing call to protect downstream service")

        # Execute downstream action
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self) -> None:
        if self.state == CircuitState.HALF_OPEN:
            self.consecutive_successes += 1
            if self.consecutive_successes >= self.half_open_success_needed:
                # Recovered fully
                self.state = CircuitState.CLOSED
                self.consecutive_failures = 0
                self.consecutive_successes = 0
        elif self.state == CircuitState.CLOSED:
            self.consecutive_failures = 0

    def _on_failure(self) -> None:
        self.last_failure_timestamp = time.time()
        self.consecutive_failures += 1
        
        if self.state == CircuitState.CLOSED:
            if self.consecutive_failures >= self.failure_threshold:
                self.state = CircuitState.OPEN
        elif self.state == CircuitState.HALF_OPEN:
            # Immediate re-trip to OPEN if probe fails
            self.state = CircuitState.OPEN


# ============================================================================
# Section 2: Bulkhead Resource Partitioning Pattern
# ============================================================================

class BulkheadFullException(Exception):
    """Raised when bulkhead capacity pool is exhausted."""
    pass


class BulkheadPool:
    """Isolates service resources (e.g. concurrency capacity) so failure in one pool does not starve others."""
    def __init__(self, name: str, max_concurrent: int):
        self.name = name
        self.max_concurrent = max_concurrent
        self.active_slots = 0

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        if self.active_slots >= self.max_concurrent:
            raise BulkheadFullException(f"Bulkhead pool '{self.name}' capacity ({self.max_concurrent}) exhausted")
        
        self.active_slots += 1
        try:
            return func(*args, **kwargs)
        finally:
            self.active_slots -= 1


# ============================================================================
# Section 3: Saga Distributed Transaction Coordinator
# ============================================================================

class SagaStep:
    def __init__(self, name: str, action: Callable[[], bool], compensate: Callable[[], None]):
        self.name = name
        self.action = action
        self.compensate = compensate


class SagaExecutionResult:
    def __init__(self, success: bool, executed_steps: List[str], compensated_steps: List[str], error: Optional[str] = None):
        self.success = success
        self.executed_steps = executed_steps
        self.compensated_steps = compensated_steps
        self.error = error


class SagaCoordinator:
    """
    Orchestrates distributed Saga transactions across multiple microservices.
    If any step fails, executes compensating transactions for already-completed steps in reverse order.
    """
    def __init__(self):
        self.steps: List[SagaStep] = []

    def add_step(self, step: SagaStep) -> 'SagaCoordinator':
        self.steps.append(step)
        return self

    def execute(self) -> SagaExecutionResult:
        completed_steps: List[SagaStep] = []
        
        for step in self.steps:
            try:
                ok = step.action()
                if not ok:
                    raise RuntimeError(f"Step '{step.name}' returned failure status")
                completed_steps.append(step)
            except Exception as e:
                # Trigger compensation in reverse order
                compensated_names: List[str] = []
                for comp_step in reversed(completed_steps):
                    try:
                        comp_step.compensate()
                        compensated_names.append(comp_step.name)
                    except Exception as comp_err:
                        # In production: write to Dead Letter Queue (DLQ)
                        pass
                
                return SagaExecutionResult(
                    success=False,
                    executed_steps=[s.name for s in completed_steps],
                    compensated_steps=compensated_names,
                    error=str(e)
                )
        
        return SagaExecutionResult(
            success=True,
            executed_steps=[s.name for s in completed_steps],
            compensated_steps=[]
        )


# ============================================================================
# Section 4: Automated Verification Test Suite
# ============================================================================

def run_tests():
    print("=== Level 5 Chapter 8: Microservices Resiliency Lab ===")

    # Test 1: Circuit Breaker Normal -> Tripped (OPEN) -> Fast Fail
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout_s=0.2, half_open_success_needed=2)
    assert cb.state == CircuitState.CLOSED
    
    def unreliable_service(should_fail: bool):
        if should_fail:
            raise ConnectionError("504 Gateway Timeout")
        return "SUCCESS_DATA"

    # 2 failures do not trip
    for _ in range(2):
        try:
            cb.call(unreliable_service, True)
        except ConnectionError:
            pass
    assert cb.state == CircuitState.CLOSED
    
    # 3rd failure trips the breaker to OPEN
    try:
        cb.call(unreliable_service, True)
    except ConnectionError:
        pass
    assert cb.state == CircuitState.OPEN
    print("  [PASS] Circuit Breaker tripped from CLOSED -> OPEN after 3 consecutive errors")

    # Fast-fail while OPEN
    try:
        cb.call(unreliable_service, False)
        assert False, "Should fast-fail with CircuitBreakerOpenException"
    except CircuitBreakerOpenException as e:
        assert "Circuit is OPEN" in str(e)
    print("  [PASS] Fast-fail in OPEN state verified without touching downstream")

    # Test 2: Recovery via HALF_OPEN probe to CLOSED
    time.sleep(0.25)  # Wait for recovery timeout (0.2s)
    
    # First success probe -> changes state to HALF_OPEN
    res1 = cb.call(unreliable_service, False)
    assert res1 == "SUCCESS_DATA"
    assert cb.state == CircuitState.HALF_OPEN
    assert cb.consecutive_successes == 1

    # Second success probe -> meets half_open_success_needed=2 -> resets to CLOSED
    res2 = cb.call(unreliable_service, False)
    assert res2 == "SUCCESS_DATA"
    assert cb.state == CircuitState.CLOSED
    print("  [PASS] Circuit Breaker probe: OPEN -> HALF_OPEN -> CLOSED recovery verified")

    # Test 3: Bulkhead Resource Isolation
    bulkhead = BulkheadPool("payment_gateway", max_concurrent=2)
    
    # Fill slots
    bulkhead.active_slots = 2
    try:
        bulkhead.execute(lambda: "OK")
        assert False, "Should raise BulkheadFullException"
    except BulkheadFullException as e:
        assert "capacity (2) exhausted" in str(e)
    bulkhead.active_slots = 0
    res = bulkhead.execute(lambda: "PaymentProcessed")
    assert res == "PaymentProcessed"
    print("  [PASS] Bulkhead Resource Isolation Pool Validated")

    # Test 4: Distributed Saga - Happy Path
    ledger = []
    
    def book_hotel():
        ledger.append("HOTEL_BOOKED")
        return True
    def cancel_hotel():
        ledger.append("HOTEL_CANCELLED")
        
    def book_flight():
        ledger.append("FLIGHT_BOOKED")
        return True
    def cancel_flight():
        ledger.append("FLIGHT_CANCELLED")

    saga_happy = SagaCoordinator()
    saga_happy.add_step(SagaStep("HotelBooking", book_hotel, cancel_hotel))
    saga_happy.add_step(SagaStep("FlightBooking", book_flight, cancel_flight))
    
    res_happy = saga_happy.execute()
    assert res_happy.success is True
    assert ledger == ["HOTEL_BOOKED", "FLIGHT_BOOKED"]
    assert len(res_happy.compensated_steps) == 0
    print("  [PASS] Saga Coordinator Happy Path verified: All steps committed")

    # Test 5: Distributed Saga - Failure and Compensation Rollback
    ledger.clear()
    
    def book_car():
        ledger.append("CAR_BOOKING_ATTEMPT")
        raise RuntimeError("No rental cars available")
    def cancel_car():
        ledger.append("CAR_CANCELLED")

    saga_fail = SagaCoordinator()
    saga_fail.add_step(SagaStep("HotelBooking", book_hotel, cancel_hotel))
    saga_fail.add_step(SagaStep("FlightBooking", book_flight, cancel_flight))
    saga_fail.add_step(SagaStep("CarBooking", book_car, cancel_car))

    res_fail = saga_fail.execute()
    assert res_fail.success is False
    assert "No rental cars available" in res_fail.error
    assert res_fail.executed_steps == ["HotelBooking", "FlightBooking"]
    # Compensations must execute in reverse order: Flight, then Hotel
    assert res_fail.compensated_steps == ["FlightBooking", "HotelBooking"]
    assert ledger == ["HOTEL_BOOKED", "FLIGHT_BOOKED", "CAR_BOOKING_ATTEMPT", "FLIGHT_CANCELLED", "HOTEL_CANCELLED"]
    print("  [PASS] Saga Compensating Transactions verified: Reverse rollback executed successfully")

    print("ALL TESTS PASSED: Level 5 Chapter 8 Microservices Resiliency Engine verified successfully.")


if __name__ == "__main__":
    run_tests()
