"""
ch05_sre_telemetry_lab.py
Level 7 Companion Lab: W3C Distributed Tracing, Multi-Burn SRE Alerting & Load Shedding.
Pure Python/Standard Library implementation with zero external dependencies.
"""

from __future__ import annotations
import sys
import secrets
from typing import Dict, List, Optional

# Windows UTF-8 console output
sys.stdout.reconfigure(encoding="utf-8")


class LabTraceContext:
    """W3C traceparent standard context propagation."""
    def __init__(self, trace_id: Optional[str] = None, span_id: Optional[str] = None):
        self.trace_id = trace_id or secrets.token_hex(16)
        self.span_id = span_id or secrets.token_hex(8)

    def to_header(self) -> str:
        return f"00-{self.trace_id}-{self.span_id}-01"

    @classmethod
    def parse_header(cls, header: str) -> LabTraceContext:
        parts = header.strip().split("-")
        if len(parts) == 4 and parts[0] == "00":
            return cls(trace_id=parts[1], span_id=parts[2])
        return cls()

    def make_child(self) -> LabTraceContext:
        return LabTraceContext(trace_id=self.trace_id, span_id=secrets.token_hex(8))


class LabBurnRateEvaluator:
    """Google SRE Multiwindow Burn Rate Evaluator."""
    def __init__(self, slo: float = 0.999):
        self.slo = slo
        self.budget = 1.0 - slo  # e.g., 0.001

    def calculate_burn_rate(self, errors: int, total: int) -> float:
        if total == 0:
            return 0.0
        error_rate = errors / total
        return error_rate / self.budget

    def should_page_sev1(self, w1h_err: int, w1h_tot: int, w5m_err: int, w5m_tot: int) -> bool:
        # SEV-1 condition: both 1h long window and 5m short window burn rate >= 14.4x
        b_1h = self.calculate_burn_rate(w1h_err, w1h_tot)
        b_5m = self.calculate_burn_rate(w5m_err, w5m_tot)
        return (b_1h >= 14.4) and (b_5m >= 14.4)


class LabConcurrencyLimiter:
    """Little's Law load shedder based on max concurrency."""
    def __init__(self, limit: int = 10):
        self.limit = limit
        self.current = 0

    def acquire(self) -> bool:
        if self.current >= self.limit:
            return False  # Shed load (HTTP 429 / 503)
        self.current += 1
        return True

    def release(self) -> None:
        self.current = max(0, self.current - 1)


def test_w3c_trace_propagation():
    print("Running Test Suite 1: W3C TraceContext Propagation...")
    parent = LabTraceContext()
    header = parent.to_header()
    assert header.startswith("00-")

    # Downstream service parses header
    downstream = LabTraceContext.parse_header(header)
    assert downstream.trace_id == parent.trace_id
    assert downstream.span_id == parent.span_id

    # Create child span
    child = downstream.make_child()
    assert child.trace_id == parent.trace_id  # Trace ID preserved!
    assert child.span_id != parent.span_id    # Unique span ID!
    print("  Passed! Trace context correctly formatted and propagated across child spans.")


def test_multi_burn_rate_alerting():
    print("Running Test Suite 2: Google SRE Multiwindow Burn Rate Alerting...")
    sre = LabBurnRateEvaluator(slo=0.999)  # 0.1% budget

    # Normal traffic: 1 error in 10,000 requests (0.01% error rate) -> Burn rate = 0.01% / 0.1% = 0.1x
    b_norm = sre.calculate_burn_rate(errors=1, total=10000)
    assert abs(b_norm - 0.1) < 1e-4

    # Outage: 15 errors in 1,000 requests in 1h window (1.5% error rate) -> Burn rate = 1.5% / 0.1% = 15.0x
    # And 2 errors in 100 requests in 5m window (2.0% error rate) -> Burn rate = 2.0% / 0.1% = 20.0x
    is_paged = sre.should_page_sev1(w1h_err=15, w1h_tot=1000, w5m_err=2, w5m_tot=100)
    assert is_paged is True

    # Transient glitch: 5m spike (20.0x), but 1h window is only 1.0x -> Should NOT page!
    is_paged_false = sre.should_page_sev1(w1h_err=1, w1h_tot=1000, w5m_err=2, w5m_tot=100)
    assert is_paged_false is False
    print("  Passed! Multiwindow alerting strictly suppresses transient spikes and pages on sustained outages.")


def test_littles_law_load_shedding():
    print("Running Test Suite 3: Adaptive Concurrency Load Shedding...")
    limiter = LabConcurrencyLimiter(limit=3)

    assert limiter.acquire() is True
    assert limiter.acquire() is True
    assert limiter.acquire() is True
    # 4th request exceeds concurrency limit -> Must be shed
    assert limiter.acquire() is False

    limiter.release()
    # Now slot is free
    assert limiter.acquire() is True
    print("  Passed! Concurrency limiter successfully sheds excess load to prevent resource starvation.")


if __name__ == "__main__":
    print("================================================================================")
    print("LEVEL 7 LAB 05: SRE OBSERVABILITY & TELEMETRY ENGINE")
    print("================================================================================")
    test_w3c_trace_propagation()
    test_multi_burn_rate_alerting()
    test_littles_law_load_shedding()
    print("================================================================================")
    print("ALL 3 TEST SUITES PASSED CLEANLY (EXIT CODE 0)")
    print("================================================================================")
