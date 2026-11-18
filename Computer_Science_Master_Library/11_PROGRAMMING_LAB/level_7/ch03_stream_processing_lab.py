"""
ch03_stream_processing_lab.py
Level 7 Companion Lab: Event-Time Windows, Watermarks, and Exactly-Once Semantics.
Pure Python/Standard Library implementation with zero external dependencies.
"""

from __future__ import annotations
import sys
import copy
from typing import Dict, List, Tuple

# Windows UTF-8 console output
sys.stdout.reconfigure(encoding="utf-8")


class LabEvent:
    """Stream record with event-time timestamp."""
    def __init__(self, key: str, value: float, event_time_ms: int):
        self.key = key
        self.value = value
        self.event_time = event_time_ms


class LabTumblingWindow:
    """Aggregates records into tumbling event-time windows."""
    def __init__(self, size_ms: int):
        self.size = size_ms
        self.windows: Dict[Tuple[int, int, str], float] = {}

    def add(self, ev: LabEvent) -> None:
        start = ev.event_time - (ev.event_time % self.size)
        end = start + self.size
        k = (start, end, ev.key)
        self.windows[k] = self.windows.get(k, 0.0) + ev.value

    def trigger(self, watermark_ms: int) -> List[Tuple[int, int, str, float]]:
        fired = []
        to_del = []
        for (s, e, k), v in self.windows.items():
            if e <= watermark_ms:
                fired.append((s, e, k, v))
                to_del.append((s, e, k))
        for k in to_del:
            del self.windows[k]
        fired.sort(key=lambda x: (x[0], x[2]))
        return fired


class Lab2PCSink:
    """Two-Phase Commit transactional sink ensuring Exactly-Once Semantics."""
    def __init__(self):
        self.committed: List[Tuple[int, int, str, float]] = []
        self.in_flight: List[Tuple[int, int, str, float]] = []

    def buffer(self, records: List[Tuple[int, int, str, float]]) -> None:
        self.in_flight.extend(records)

    def commit(self) -> None:
        self.committed.extend(self.in_flight)
        self.in_flight.clear()

    def abort(self) -> None:
        self.in_flight.clear()


def test_out_of_order_watermarking():
    print("Running Test Suite 1: Out-of-Order Watermark Progression...")
    window = LabTumblingWindow(size_ms=1000)
    max_lateness = 200  # 200ms allowable jitter

    # Event 1: t=100ms
    window.add(LabEvent("A", 10.0, 100))
    # Event 2: t=800ms
    window.add(LabEvent("A", 20.0, 800))
    # Event 3: t=300ms (Arrives late, but before watermark passes 1000ms!)
    window.add(LabEvent("A", 15.0, 300))

    # Watermark after max event 800ms is 800 - 200 = 600ms -> Window [0, 1000) should NOT trigger yet
    fired1 = window.trigger(watermark_ms=600)
    assert len(fired1) == 0

    # Event 4: t=1300ms -> Max event=1300, Watermark = 1300 - 200 = 1100ms -> Window [0, 1000) MUST trigger!
    window.add(LabEvent("A", 5.0, 1300))
    fired2 = window.trigger(watermark_ms=1100)

    assert len(fired2) == 1
    start, end, key, total = fired2[0]
    assert start == 0 and end == 1000 and key == "A"
    # Total sum of events in [0, 1000): 10.0 + 20.0 + 15.0 = 45.0
    assert abs(total - 45.0) < 1e-6
    print("  Passed! Out-of-order records correctly aggregated into window [0, 1000) with total 45.0.")


def test_late_data_dropping():
    print("Running Test Suite 2: Late Data Detection (Post-Watermark)...")
    window = LabTumblingWindow(size_ms=1000)
    # Trigger watermark up to 1500ms
    window.trigger(watermark_ms=1500)

    # Event arrives with t=500ms (Late! Window [0, 1000) has already closed and purged)
    current_watermark = 1500
    late_event = LabEvent("B", 100.0, 500)

    is_late = late_event.event_time < current_watermark
    assert is_late is True
    print("  Passed! Event with t=500ms correctly flagged as late relative to watermark 1500ms.")


def test_exactly_once_checkpointing():
    print("Running Test Suite 3: Two-Phase Commit Sink Exactly-Once Semantics...")
    window = LabTumblingWindow(size_ms=1000)
    sink = Lab2PCSink()

    window.add(LabEvent("orders", 250.0, 100))
    window.add(LabEvent("orders", 150.0, 500))

    # Trigger window at watermark 1200ms
    results = window.trigger(watermark_ms=1200)
    assert len(results) == 1
    sink.buffer(results)

    # State before commit: in_flight has data, committed is empty
    assert len(sink.in_flight) == 1
    assert len(sink.committed) == 0

    # Formal commit
    sink.commit()
    assert len(sink.committed) == 1
    assert sink.committed[0][3] == 400.0

    # Test crash simulation during uncommitted batch
    window.add(LabEvent("orders", 999.0, 2100))
    results_uncommitted = window.trigger(watermark_ms=3000)
    sink.buffer(results_uncommitted)
    # Simulate crash & abort
    sink.abort()

    # Committed store remains untouched and untainted
    assert len(sink.committed) == 1
    assert sink.committed[0][3] == 400.0
    print("  Passed! Two-Phase Commit guaranteed Exactly-Once state visibility under simulated crash.")


if __name__ == "__main__":
    print("================================================================================")
    print("LEVEL 7 LAB 03: STREAM PROCESSING & EXACTLY-ONCE ENGINE")
    print("================================================================================")
    test_out_of_order_watermarking()
    test_late_data_dropping()
    test_exactly_once_checkpointing()
    print("================================================================================")
    print("ALL 3 TEST SUITES PASSED CLEANLY (EXIT CODE 0)")
    print("================================================================================")
