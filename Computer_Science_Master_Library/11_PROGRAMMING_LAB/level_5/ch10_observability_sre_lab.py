# -*- coding: utf-8 -*-
"""
CH10: Observability, Site Reliability Engineering, and Incident Management Lab
==============================================================================
Covers:
1. Prometheus-Style Metric Engine (Counters, Gauges, Quantile Summaries).
2. Distributed Context Propagation Engine (W3C traceparent headers and OpenTelemetry Span graphs).
3. Google SRE Multiwindow Error Budget Burn-Rate Calculator and Alerting Simulator.
"""
import sys
import time
import math
import secrets
from typing import Dict, List, Optional, Tuple, Any

sys.stdout.reconfigure(encoding="utf-8")


# ============================================================================
# Section 1: Prometheus-Style Metrics Engine
# ============================================================================

class Counter:
    """Monotonically increasing counter with multi-dimensional label support."""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.series: Dict[Tuple[Tuple[str, str], ...], float] = {}

    def _labels_to_key(self, labels: Dict[str, str]) -> Tuple[Tuple[str, str], ...]:
        return tuple(sorted(labels.items()))

    def inc(self, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        if value < 0:
            raise ValueError("Counter increments must be non-negative")
        key = self._labels_to_key(labels or {})
        self.series[key] = self.series.get(key, 0.0) + value

    def get(self, labels: Optional[Dict[str, str]] = None) -> float:
        key = self._labels_to_key(labels or {})
        return self.series.get(key, 0.0)


class Gauge:
    """Metric value that can arbitrarily go up and down."""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.series: Dict[Tuple[Tuple[str, str], ...], float] = {}

    def _labels_to_key(self, labels: Dict[str, str]) -> Tuple[Tuple[str, str], ...]:
        return tuple(sorted(labels.items()))

    def set(self, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        key = self._labels_to_key(labels or {})
        self.series[key] = value

    def inc(self, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        key = self._labels_to_key(labels or {})
        self.series[key] = self.series.get(key, 0.0) + value

    def dec(self, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        key = self._labels_to_key(labels or {})
        self.series[key] = self.series.get(key, 0.0) - value

    def get(self, labels: Optional[Dict[str, str]] = None) -> float:
        key = self._labels_to_key(labels or {})
        return self.series.get(key, 0.0)


class Summary:
    """Tracks values (e.g. request latencies) and computes rank percentiles (P50, P90, P99)."""
    def __init__(self, name: str):
        self.name = name
        self.samples: List[float] = []

    def observe(self, value: float) -> None:
        self.samples.append(value)

    def quantile(self, q: float) -> float:
        if not self.samples:
            return 0.0
        if not (0.0 <= q <= 1.0):
            raise ValueError("Quantile must be in range [0.0, 1.0]")
        sorted_data = sorted(self.samples)
        idx = int(math.ceil(q * len(sorted_data))) - 1
        return sorted_data[max(0, min(idx, len(sorted_data) - 1))]


# ============================================================================
# Section 2: OpenTelemetry W3C Distributed Context Propagation Engine
# ============================================================================

class Span:
    def __init__(self, name: str, trace_id: str, span_id: str, parent_id: Optional[str] = None):
        self.name = name
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_id = parent_id
        self.attributes: Dict[str, Any] = {}
        self.events: List[Tuple[float, str]] = []
        self.start_ns = time.time_ns()
        self.end_ns: Optional[int] = None

    def set_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    def add_event(self, name: str) -> None:
        self.events.append((time.time_ns(), name))

    def finish(self) -> None:
        self.end_ns = time.time_ns()


class W3CPropagator:
    """
    Parses and injects W3C Trace Context headers (traceparent specification).
    Format: version(2 hex)-traceid(32 hex)-parentid(16 hex)-traceflags(2 hex)
    e.g. 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
    """
    @staticmethod
    def generate_trace_id() -> str:
        return secrets.token_hex(16)  # 32 hex chars

    @staticmethod
    def generate_span_id() -> str:
        return secrets.token_hex(8)   # 16 hex chars

    @staticmethod
    def inject(trace_id: str, span_id: str, sampled: bool = True) -> str:
        flags = "01" if sampled else "00"
        return f"00-{trace_id}-{span_id}-{flags}"

    @staticmethod
    def extract(traceparent: str) -> Tuple[str, str, bool]:
        parts = traceparent.strip().split("-")
        if len(parts) != 4:
            raise ValueError(f"Malformed W3C traceparent header: '{traceparent}'")
        version, trace_id, parent_id, flags = parts
        if version != "00" or len(trace_id) != 32 or len(parent_id) != 16 or len(flags) != 2:
            raise ValueError(f"Invalid W3C traceparent segments: '{traceparent}'")
        sampled = (flags == "01")
        return trace_id, parent_id, sampled


# ============================================================================
# Section 3: SRE Error Budget & Multiwindow Burn Rate Calculator
# ============================================================================

class SREErrorBudgetCalculator:
    """
    Google SRE Workbook Multiwindow Multi-Burn-Rate Model:
    - Target SLO (e.g., 99.9% availability over a 30-day rolling window).
    - Error budget = 1.0 - SLO (e.g. 0.001 or 0.1%).
    - Burn Rate (B): Multiple of normal budget consumption rate.
      - B = 1.0: Budget is consumed exactly uniformly over 30 days.
      - B = 14.4: Consumes 2% of monthly budget in 1 hour (Critical Page).
      - B = 6.0:  Consumes 5% of monthly budget in 6 hours (Ticket Alert).
    """
    def __init__(self, slo_target: float = 0.999, window_days: int = 30):
        if not (0.0 < slo_target < 1.0):
            raise ValueError("SLO target must be between 0 and 1.0")
        self.slo_target = slo_target
        self.window_days = window_days
        self.total_budget_fraction = round(1.0 - slo_target, 9)  # e.g., 0.001 (0.1%)

    def calculate_burn_rate(self, window_hours: float, observed_error_rate: float) -> float:
        """
        Burn Rate B = (observed_error_rate / total_budget_fraction)
        """
        if self.total_budget_fraction == 0:
            return 0.0
        return round(observed_error_rate / self.total_budget_fraction, 6)

    def hours_until_exhaustion(self, burn_rate: float) -> float:
        """Given a constant burn rate B, hours until 100% of error budget is depleted."""
        if burn_rate <= 0:
            return float('inf')
        total_window_hours = self.window_days * 24.0
        return total_window_hours / burn_rate

    def evaluate_burn_alert(self, window_hours: float, observed_error_rate: float) -> Dict[str, Any]:
        """
        Evaluates Google SRE multiwindow alert criteria:
        - Critical Page: 1-hour window with Burn Rate >= 14.4 (consumes 2% budget in 1h).
        - Ticket Warning: 6-hour window with Burn Rate >= 6.0 (consumes 5% budget in 6h).
        """
        burn_rate = self.calculate_burn_rate(window_hours, observed_error_rate)
        time_to_exhaust_hrs = self.hours_until_exhaustion(burn_rate)
        
        severity = "NORMAL"
        alert_msg = "Error budget consumption is healthy"
        
        if window_hours <= 1.0 and burn_rate >= 14.4:
            severity = "PAGE_SEV1"
            alert_msg = f"CRITICAL INCIDENT: Burn rate {burn_rate:.1f}x exhausts budget in {time_to_exhaust_hrs:.1f} hours!"
        elif window_hours <= 6.0 and burn_rate >= 6.0:
            severity = "TICKET_SEV2"
            alert_msg = f"WARNING: Elevated burn rate {burn_rate:.1f}x exhausts budget in {time_to_exhaust_hrs:.1f} hours."
            
        return {
            "window_hours": window_hours,
            "burn_rate": burn_rate,
            "time_to_exhaust_hours": time_to_exhaust_hrs,
            "severity": severity,
            "alert_message": alert_msg
        }


# ============================================================================
# Section 4: Automated Verification Test Suite
# ============================================================================

def run_tests():
    print("=== Level 5 Chapter 10: Observability, SRE & Incident Management Lab ===")

    # Test 1: Prometheus Metrics (Counter, Gauge, Summary)
    req_counter = Counter("http_requests_total", "Total incoming HTTP requests")
    req_counter.inc(1.0, {"path": "/checkout", "status": "200"})
    req_counter.inc(2.0, {"path": "/checkout", "status": "200"})
    req_counter.inc(1.0, {"path": "/checkout", "status": "500"})
    
    assert req_counter.get({"path": "/checkout", "status": "200"}) == 3.0
    assert req_counter.get({"path": "/checkout", "status": "500"}) == 1.0
    assert req_counter.get({"path": "/missing"}) == 0.0

    worker_gauge = Gauge("active_threads", "Active worker threads")
    worker_gauge.set(10.0)
    worker_gauge.inc(5.0)
    worker_gauge.dec(2.0)
    assert worker_gauge.get() == 13.0

    latency_summary = Summary("http_latency_ms")
    # Feed 100 latency values: 1 to 100 ms
    for val in range(1, 101):
        latency_summary.observe(float(val))
    assert latency_summary.quantile(0.50) == 50.0
    assert latency_summary.quantile(0.90) == 90.0
    assert latency_summary.quantile(0.99) == 99.0
    print("  [PASS] Prometheus Counters, Gauges, and Summary Quantiles Validated")

    # Test 2: W3C Trace Context Propagation
    trace_id = W3CPropagator.generate_trace_id()
    span_id = W3CPropagator.generate_span_id()
    header_val = W3CPropagator.inject(trace_id, span_id, sampled=True)
    
    assert header_val.startswith("00-")
    assert header_val.endswith("-01")
    
    extracted_trace, extracted_parent, sampled = W3CPropagator.extract(header_val)
    assert extracted_trace == trace_id
    assert extracted_parent == span_id
    assert sampled is True
    print(f"  [PASS] W3C traceparent Propagator ({header_val}) parsed successfully")

    # Test 3: Span Graph Simulation
    root_span = Span("gateway_proxy", trace_id, span_id)
    child_span_id = W3CPropagator.generate_span_id()
    child_span = Span("order_service", trace_id, child_span_id, parent_id=span_id)
    child_span.set_attribute("http.status_code", 200)
    child_span.add_event("cache_hit")
    child_span.finish()
    root_span.finish()
    
    assert child_span.parent_id == root_span.span_id
    assert child_span.attributes["http.status_code"] == 200
    assert len(child_span.events) == 1
    print("  [PASS] Distributed Trace Span Tree Hierarchy Validated")

    # Test 4: SRE Error Budget Burn Rate Calculations
    # 99.9% SLO -> Error budget = 0.001 (0.1%)
    # Over 30 days = 720 hours
    sre = SREErrorBudgetCalculator(slo_target=0.999, window_days=30)
    assert abs(sre.total_budget_fraction - 0.001) < 1e-9

    # Normal burn rate: 0.1% errors observed -> B = 1.0 (Exhaustion in 720 hours = 30 days)
    normal_b = sre.calculate_burn_rate(window_hours=1.0, observed_error_rate=0.001)
    assert abs(normal_b - 1.0) < 1e-6
    assert abs(sre.hours_until_exhaustion(normal_b) - 720.0) < 1e-6

    # Critical burn: 1.44% errors in 1h -> B = 14.4 -> Depletes 30d budget in 50 hours!
    crit_alert = sre.evaluate_burn_alert(window_hours=1.0, observed_error_rate=0.0144)
    assert abs(crit_alert["burn_rate"] - 14.4) < 1e-4
    assert round(crit_alert["time_to_exhaust_hours"], 1) == 50.0
    assert crit_alert["severity"] == "PAGE_SEV1"
    assert "CRITICAL INCIDENT" in crit_alert["alert_message"]
    print(f"  [PASS] SRE Critical Page Alert: {crit_alert['alert_message']}")

    # Ticket warning: 0.6% errors in 6h -> B = 6.0
    warn_alert = sre.evaluate_burn_alert(window_hours=6.0, observed_error_rate=0.006)
    assert abs(warn_alert["burn_rate"] - 6.0) < 1e-4
    assert round(warn_alert["time_to_exhaust_hours"], 1) == 120.0
    assert warn_alert["severity"] == "TICKET_SEV2"
    print(f"  [PASS] SRE Ticket Warning Alert: {warn_alert['alert_message']}")

    print("ALL TESTS PASSED: Level 5 Chapter 10 Observability & SRE Engine verified successfully.")


if __name__ == "__main__":
    run_tests()
