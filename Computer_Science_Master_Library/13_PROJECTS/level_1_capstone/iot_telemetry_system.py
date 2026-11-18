"""
Level 1 Capstone Project: End-to-End Secure IoT Edge Telemetry & OS Dispatcher
File: 13_PROJECTS/level_1_capstone/iot_telemetry_system.py
Author: Computer Science Master Library
Description: Synthesizes Level 1 concepts:
             - IPO Data Conversion (CH01)
             - Hardware & CPU ALU simulation (CH02)
             - Memory & Data Packing (CH03 & CH04)
             - Logic Gates & Boolean Decisions (CH05)
             - Algorithmic Flow & Verification (CH06)
             - OS Process Control Block & Scheduling (CH07)
             - Network Packet Framing & Checksums (CH08)
             - Runtime Execution Engine (CH09)
             - Cryptographic Integrity & Security (CH10)
"""

import sys
import hashlib
import time
import struct
from collections import deque
from typing import List, Dict, Any, Tuple, Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# -------------------------------------------------------------
# 1. Hardware Sensor & Binary Data Packing Layer
# -------------------------------------------------------------
class SensorPacket:

    def __init__(self, device_id: int, voltage: float, timestamp: int):
        self.device_id = device_id
        # Ingest analog voltage: 0.0V to 3.3V -> -20.0C to 80.0C
        self.temperature_c = round((voltage / 3.3) * 100.0 - 20.0, 2)
        self.timestamp = timestamp
        # Generate SHA-256 cryptographic signature (Integrity)
        payload_str = f"{device_id}:{self.temperature_c}:{timestamp}"
        self.signature = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

    def serialize(self) -> bytes:
        """Packs packet into compact binary network frame."""
        # Header: Device ID (2 bytes unsigned), Temp * 100 (2 bytes signed short), Timestamp (4 bytes unsigned)
        temp_encoded = int(self.temperature_c * 100)
        header = struct.pack(">HhI", self.device_id, temp_encoded, self.timestamp)
        return header + self.signature.encode("utf-8")

    @classmethod
    def deserialize(cls, raw_bytes: bytes) -> "SensorPacket":
        """Unpacks binary network frame and verifies cryptographic integrity."""
        header = raw_bytes[:8]
        signature_bytes = raw_bytes[8:]
        device_id, temp_encoded, timestamp = struct.unpack(">HhI", header)
        temp_c = temp_encoded / 100.0

        # Verify integrity
        payload_str = f"{device_id}:{temp_c}:{timestamp}"
        expected_sig = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
        received_sig = signature_bytes.decode("utf-8")

        if expected_sig != received_sig:
            raise ValueError(
                "CRITICAL SECURITY ALERT: Cryptographic signature mismatch! Packet tampered in transit."
            )

        packet = cls.__new__(cls)
        packet.device_id = device_id
        packet.temperature_c = temp_c
        packet.timestamp = timestamp
        packet.signature = received_sig
        return packet


# -------------------------------------------------------------
# 2. Operating System Process & Task Dispatcher
# -------------------------------------------------------------
class TelemetryProcess:

    def __init__(self, pid: int, packet: SensorPacket):
        self.pid = pid
        self.packet = packet
        self.burst_time = 4  # ms required to process and evaluate
        self.remaining_time = self.burst_time
        self.state = "NEW"
        self.alert_level = "UNKNOWN"

    def execute_slice(self, quantum: int) -> bool:
        """Executes task through simulated CPU ALU logic."""
        self.state = "RUNNING"
        self.remaining_time -= min(quantum, self.remaining_time)

        if self.remaining_time == 0:
            self.state = "TERMINATED"
            # Boolean logic gate decision on temperature thresholds
            temp = self.packet.temperature_c
            is_critical = temp > 50.0
            is_elevated = temp > 35.0 and not is_critical

            if is_critical:
                self.alert_level = "CRITICAL_SHUTDOWN"
            elif is_elevated:
                self.alert_level = "WARNING_COOLING_ACTIVE"
            else:
                self.alert_level = "NORMAL_OPTIMAL"
            return True
        return False


class EdgeKernel:

    def __init__(self, time_quantum: int = 2):
        self.time_quantum = time_quantum
        self.ready_queue: deque[TelemetryProcess] = deque()
        self.completed_tasks: List[TelemetryProcess] = []

    def submit_packet(self, pid: int, packet: SensorPacket) -> None:
        proc = TelemetryProcess(pid, packet)
        proc.state = "READY"
        self.ready_queue.append(proc)

    def run_scheduler(self) -> None:
        print("=" * 65)
        print("     EDGE OS KERNEL: EXECUTING ROUND-ROBIN DISPATCHER")
        print("=" * 65)
        while self.ready_queue:
            proc = self.ready_queue.popleft()
            finished = proc.execute_slice(self.time_quantum)
            if finished:
                self.completed_tasks.append(proc)
                print(
                    f"[Process {proc.pid}] Device #{proc.packet.device_id} | "
                    f"Temp: {proc.packet.temperature_c:5.2f} °C | Status: {proc.alert_level}"
                )
            else:
                proc.state = "READY"
                self.ready_queue.append(proc)
        print("=" * 65 + "\n")


# -------------------------------------------------------------
# 3. Main Capstone Verification Runner
# -------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 65)
    print("  LEVEL 1 CAPSTONE: SECURE IOT TELEMETRY & OS SIMULATOR")
    print("=" * 65)

    current_ts = int(time.time())
    # Generate 3 valid packets from edge sensors
    packet_1 = SensorPacket(device_id=101, voltage=1.65, timestamp=current_ts)
    packet_2 = SensorPacket(
        device_id=102, voltage=2.90, timestamp=current_ts + 1
    )
    packet_3 = SensorPacket(
        device_id=103, voltage=2.00, timestamp=current_ts + 2
    )

    # 1. Test Serialization and Deserialization
    wire_data = packet_1.serialize()
    reconstructed_1 = SensorPacket.deserialize(wire_data)
    assert reconstructed_1.temperature_c == packet_1.temperature_c
    print("Packet 1 successfully serialized and verified over network wire.")

    # 2. Test Tamper Detection
    tampered_wire_data = bytearray(wire_data)
    tampered_wire_data[2] ^= 0xFF  # Flip bits in temperature payload
    try:
        SensorPacket.deserialize(bytes(tampered_wire_data))
        assert False, "Tamper detection failed!"
    except ValueError as e:
        print("Tamper Detection Test Passed: Caught manipulated network bytes.")

    # 3. Submit to Edge OS Kernel
    kernel = EdgeKernel(time_quantum=2)
    kernel.submit_packet(pid=1, packet=packet_1)
    kernel.submit_packet(pid=2, packet=packet_2)
    kernel.submit_packet(pid=3, packet=packet_3)

    kernel.run_scheduler()

    # 4. Verify outcomes
    assert kernel.completed_tasks[0].alert_level == "NORMAL_OPTIMAL"
    assert kernel.completed_tasks[1].alert_level == "CRITICAL_SHUTDOWN"
    assert kernel.completed_tasks[2].alert_level == "WARNING_COOLING_ACTIVE"

    print("ALL LEVEL 1 CAPSTONE PROJECT TESTS PASSED WITH 100% SUCCESS!")
