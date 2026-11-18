"""
Practical Lab 1.7: Operating System Process & Round-Robin Scheduler Simulator
File: 11_PROGRAMMING_LAB/level_1/ch07_os_simulator.py
Author: Computer Science Master Library
Description: Simulates process state transitions (NEW, READY, RUNNING, TERMINATED),
             PCB accounting, and preemptive Round-Robin CPU scheduling.
"""

import sys
from typing import List
from collections import deque

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


class ProcessControlBlock:

    def __init__(self, pid: int, name: str, burst_time: int):
        self.pid: int = pid
        self.name: str = name
        self.total_burst: int = burst_time
        self.remaining_burst: int = burst_time
        self.state: str = "NEW"
        self.arrival_time: int = 0
        self.completion_time: int = 0
        self.waiting_time: int = 0

    def __repr__(self) -> str:
        return f"[PID={self.pid} '{self.name}' State={self.state} Rem={self.remaining_burst}ms]"


class RoundRobinScheduler:

    def __init__(self, time_quantum: int = 4):
        self.time_quantum: int = time_quantum
        self.ready_queue: deque[ProcessControlBlock] = deque()
        self.terminated_list: List[ProcessControlBlock] = []
        self.current_time: int = 0

    def add_process(self, pcb: ProcessControlBlock) -> None:
        pcb.state = "READY"
        self.ready_queue.append(pcb)
        print(f"[Time {self.current_time:2d}ms] Admitted to Ready Queue: {pcb}")

    def run(self) -> None:
        print("=" * 65)
        print(f" STARTING CPU SCHEDULING SIMULATION (Quantum = {self.time_quantum}ms)")
        print("=" * 65)

        while self.ready_queue:
            current_pcb = self.ready_queue.popleft()
            current_pcb.state = "RUNNING"

            exec_time = min(self.time_quantum, current_pcb.remaining_burst)
            start_slice = self.current_time
            self.current_time += exec_time
            current_pcb.remaining_burst -= exec_time

            print(
                f"[Time {start_slice:2d}-{self.current_time:2d}ms] RUNNING: {current_pcb.name} (PID {current_pcb.pid}) for {exec_time}ms"
            )

            if current_pcb.remaining_burst == 0:
                current_pcb.state = "TERMINATED"
                current_pcb.completion_time = self.current_time
                current_pcb.waiting_time = (
                    current_pcb.completion_time
                    - current_pcb.arrival_time
                    - current_pcb.total_burst
                )
                self.terminated_list.append(current_pcb)
                print(
                    f"  --> Process {current_pcb.name} COMPLETED at time {self.current_time}ms!"
                )
            else:
                current_pcb.state = "READY"
                self.ready_queue.append(current_pcb)
                print(
                    f"  --> Preempted: {current_pcb.name} re-queued (Remaining: {current_pcb.remaining_burst}ms)"
                )

        print("=" * 65)
        print("              CPU SCHEDULER EXECUTION REPORT")
        print("=" * 65)
        total_wait = 0
        print(
            "PID | Process Name  | Burst Time | Completion Time | Waiting Time"
        )
        print("-" * 65)
        for p in self.terminated_list:
            total_wait += p.waiting_time
            print(
                f"{p.pid:3d} | {p.name:<13} | {p.total_burst:7d} ms | {p.completion_time:12d} ms | {p.waiting_time:9d} ms"
            )
        avg_wait = total_wait / len(self.terminated_list)
        print("-" * 65)
        print(f"Average Waiting Time: {avg_wait:.2f} ms\n")


if __name__ == "__main__":
    scheduler = RoundRobinScheduler(time_quantum=4)
    p1 = ProcessControlBlock(pid=101, name="WebBrowser", burst_time=12)
    p2 = ProcessControlBlock(pid=102, name="MusicPlayer", burst_time=4)
    p3 = ProcessControlBlock(pid=103, name="CodeEditor", burst_time=6)

    scheduler.add_process(p1)
    scheduler.add_process(p2)
    scheduler.add_process(p3)

    scheduler.run()

    # Verification assertions
    assert p2.completion_time == 8, (
        f"Expected P2 to complete at 8ms, got {p2.completion_time}"
    )
    assert p3.completion_time == 18, (
        f"Expected P3 to complete at 18ms, got {p3.completion_time}"
    )
    assert p1.completion_time == 22, (
        f"Expected P1 to complete at 22ms, got {p1.completion_time}"
    )
    print("All operating system simulation tests verified successfully.")
