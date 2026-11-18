# LEVEL 1 CAPSTONE PROJECT: SECURE IOT TELEMETRY & OS SIMULATOR

---

## 1. Project Title & Overview
**Project Title:** End-to-End Secure IoT Edge Telemetry & Operating System Dispatcher  
**Difficulty:** Level 1 (Absolute Beginner Capstone)  
**Target Qualifications:** BCS, BCA, BESE, B.Tech SE (Year 1 Engineering Foundation)  
**Primary Language:** Python 3.11+  

This capstone project synthesizes all ten foundational subjects mastered in Level 1 into a cohesive, verified software system. Students will simulate an industrial IoT sensor reading physical environmental data, converting it to digital binary bytes, computing cryptographic SHA-256 integrity checksums, packaging it into network datagrams, and scheduling it for execution through an OS Round-Robin process queue.

---

## 2. Learning Objectives
1. Implement the complete **Input-Process-Output (IPO)** cycle from physical sensor to human-readable telemetry.
2. Demonstrate **Binary Data Packing** and **Two's Complement** handling in application code.
3. Apply the **CIA Triad** by securing telemetry with cryptographic hashing (Integrity) and basic encryption tokens (Confidentiality).
4. Simulate **Network Packet Framing** with sequence numbers and CRC/checksum error detection.
5. Emulate an **Operating System Kernel Scheduler** managing multiple process tasks in a Round-Robin queue.

---

## 3. Architecture Specification

```
+--------------------+        +--------------------+        +--------------------+
|  1. SENSOR INPUT   | =====> |  2. SECURITY LAYER | =====> | 3. NETWORK PACKET  |
| Voltage -> Celsius |        | SHA-256 Integrity  |        | Header + Payload   |
| 12-bit ADC Read    |        | TOTP Auth Token    |        | Checksum Framing   |
+--------------------+        +--------------------+        +--------------------+
                                                                      |
                                                                      v
+--------------------+        +--------------------+        +--------------------+
| 6. HUMAN DASHBOARD | <===== |  5. CPU ALU ENGINE | <===== |   4. OS SCHEDULER  |
| Alert Status Output|        | Threshold Checks   |        | Round-Robin Ready  |
| Verified Telemetry |        | Logic Gate Decisions|       | Process Execution  |
+--------------------+        +--------------------+        +--------------------+
```

---

## 4. Source Code Implementation
The complete executable implementation is available at:
[`13_PROJECTS/level_1_capstone/iot_telemetry_system.py`](iot_telemetry_system.py)

---

## 5. Verification & Testing Procedure
1. Execute the capstone test suite:
   ```bash
   python Computer_Science_Master_Library/13_PROJECTS/level_1_capstone/iot_telemetry_system.py
   ```
2. Verify that:
   - Analog voltages linearly convert to correct Celsius temperatures.
   - Tampered sensor packets are immediately detected and rejected by the SHA-256 integrity check.
   - Valid packets are queued into the OS scheduler and execute across 4ms Round-Robin time slices until completion.
   - All unit test assertions pass with exit code 0.
