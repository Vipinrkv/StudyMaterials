# -*- coding: utf-8 -*-
"""
CH07: DevOps, CI/CD, Containerization, and IaC Lab
==================================================
Covers:
1. Container Isolation Simulator: PID Namespaces and Cgroups (Memory limit & OOM Killer).
2. Storage Driver Simulator: OverlayFS Copy-on-Write (CoW) and Whiteout Deletion.
3. Canary Deployment Controller: Incremental Traffic Shifting with Automated Rollback.
"""
import sys
import copy
from typing import Dict, List, Optional, Set, Tuple

sys.stdout.reconfigure(encoding="utf-8")


# ============================================================================
# Section 1: Linux Namespaces & Cgroup Resource Enforcer Simulator
# ============================================================================

class Process:
    def __init__(self, host_pid: int, command: str, memory_mb: float):
        self.host_pid = host_pid
        self.command = command
        self.memory_mb = memory_mb


class PidNamespace:
    """Simulates PID virtualization (host PID maps to isolated container PID starting at 1)."""
    def __init__(self, ns_name: str):
        self.ns_name = ns_name
        self.host_to_ns_map: Dict[int, int] = {}
        self.ns_to_host_map: Dict[int, int] = {}
        self._next_virtual_pid = 1

    def attach_process(self, host_pid: int) -> int:
        if host_pid in self.host_to_ns_map:
            return self.host_to_ns_map[host_pid]
        vpid = self._next_virtual_pid
        self._next_virtual_pid += 1
        self.host_to_ns_map[host_pid] = vpid
        self.ns_to_host_map[vpid] = host_pid
        return vpid

    def get_virtual_pid(self, host_pid: int) -> Optional[int]:
        return self.host_to_ns_map.get(host_pid)


class MemoryCgroup:
    """Simulates Linux Cgroups v2 memory controller with hard limits and OOM termination."""
    def __init__(self, limit_mb: float):
        self.limit_mb = limit_mb
        self.attached_processes: Dict[int, Process] = {}

    def attach(self, proc: Process) -> None:
        self.attached_processes[proc.host_pid] = proc

    @property
    def current_usage_mb(self) -> float:
        return sum(p.memory_mb for p in self.attached_processes.values())

    def allocate(self, host_pid: int, additional_mb: float) -> Tuple[bool, str]:
        if host_pid not in self.attached_processes:
            raise KeyError(f"Host PID {host_pid} not attached to cgroup")
        
        projected_usage = self.current_usage_mb + additional_mb
        if projected_usage > self.limit_mb:
            # Trigger OOM killer: kill the offending process
            killed = self.attached_processes.pop(host_pid)
            return False, f"OOMKilled: host_pid={killed.host_pid} cmd='{killed.command}' exceeded limit {self.limit_mb}MB"
        
        self.attached_processes[host_pid].memory_mb += additional_mb
        return True, "Allocated successfully"


# ============================================================================
# Section 2: OverlayFS Copy-on-Write (CoW) Storage Simulator
# ============================================================================

class OverlayFS:
    """
    Simulates Linux OverlayFS union mount:
    - Lower layer (read-only base image layers).
    - Upper layer (read-write container layer).
    - Merged view presented to the user.
    - Copy-up semantics on write.
    - Whiteout files ('.wh.<name>') on file deletion.
    """
    def __init__(self, lower_layers: List[Dict[str, str]]):
        # lower_layers ordered from lowest to highest priority lower layer
        self.lower_layers: List[Dict[str, str]] = [copy.deepcopy(layer) for layer in lower_layers]
        self.upper_layer: Dict[str, str] = {}
        self.whiteouts: Set[str] = set()

    def read_file(self, filepath: str) -> Optional[str]:
        if filepath in self.whiteouts:
            return None  # Deleted via whiteout
        if filepath in self.upper_layer:
            return self.upper_layer[filepath]
        # Search lower layers from top to bottom
        for layer in reversed(self.lower_layers):
            if filepath in layer:
                return layer[filepath]
        return None

    def write_file(self, filepath: str, content: str) -> str:
        """Copy-on-write: if file exists in lower layer, it is copied up to upper layer on modification."""
        was_in_lower = any(filepath in layer for layer in self.lower_layers)
        
        # Remove any existing whiteout
        self.whiteouts.discard(filepath)
        
        # Write to upper layer
        self.upper_layer[filepath] = content
        
        if was_in_lower:
            return f"COPY_UP_MODIFIED: {filepath}"
        return f"CREATED_NEW_IN_UPPER: {filepath}"

    def delete_file(self, filepath: str) -> str:
        """Deletes a file. If in lower layer, creates a whiteout marker."""
        in_upper = filepath in self.upper_layer
        if in_upper:
            del self.upper_layer[filepath]
            
        in_lower = any(filepath in layer for layer in self.lower_layers)
        if in_lower:
            self.whiteouts.add(filepath)
            return f"WHITEOUT_CREATED: .wh.{filepath}"
        elif in_upper:
            return f"DELETED_FROM_UPPER: {filepath}"
        return f"FILE_NOT_FOUND: {filepath}"

    def get_merged_files(self) -> Dict[str, str]:
        """Returns the synthesized merged filesystem view."""
        merged: Dict[str, str] = {}
        for layer in self.lower_layers:
            for k, v in layer.items():
                merged[k] = v
        # Apply whiteouts
        for wh in self.whiteouts:
            merged.pop(wh, None)
        # Apply upper layer
        for k, v in self.upper_layer.items():
            merged[k] = v
        return merged


# ============================================================================
# Section 3: Progressive Canary Deployment Controller
# ============================================================================

class CanaryDeploymentController:
    """
    Manages progressive canary rollouts:
    - Incremental traffic weight steps (e.g. [5%, 25%, 50%, 100%]).
    - Evaluates error rate threshold at each step.
    - If error rate exceeds error_threshold, triggers immediate rollback to stable baseline.
    """
    def __init__(self, stable_version: str, canary_version: str, error_threshold: float = 0.02):
        self.stable_version = stable_version
        self.canary_version = canary_version
        self.error_threshold = error_threshold
        self.current_canary_weight = 0.0  # Range 0.0 to 1.0
        self.status = "INITIALIZED"  # INITIALIZED, ROLLING_OUT, SUCCESS, ROLLED_BACK
        self.audit_log: List[str] = []

    def log(self, message: str) -> None:
        self.audit_log.append(message)

    def route_traffic(self, request_id: int) -> str:
        """Routes request based on current weight using deterministic hashing."""
        bucket = (request_id * 31) % 100  # 0 to 99
        threshold = int(self.current_canary_weight * 100)
        if bucket < threshold:
            return self.canary_version
        return self.stable_version

    def evaluate_step(self, target_weight: float, requests_count: int, failed_requests: int) -> bool:
        """
        Applies target traffic weight and tests telemetry.
        Returns True if step succeeded, False if error threshold breached and rollback executed.
        """
        self.current_canary_weight = target_weight
        self.status = "ROLLING_OUT"
        
        error_rate = failed_requests / max(1, requests_count)
        self.log(f"Step {int(target_weight*100)}%: {requests_count} reqs, {failed_requests} errs (Error Rate: {error_rate*100:.2f}%)")
        
        if error_rate > self.error_threshold:
            # Trigger automated rollback
            self.current_canary_weight = 0.0
            self.status = "ROLLED_BACK"
            self.log(f"ALERT: Error rate {error_rate*100:.2f}% breached threshold {self.error_threshold*100:.2f}%. IMMEDIATE ROLLBACK TO {self.stable_version}.")
            return False
            
        if target_weight >= 1.0:
            self.status = "SUCCESS"
            self.log(f"Canary rollout to {self.canary_version} completed successfully (100% traffic routed).")
            
        return True


# ============================================================================
# Section 4: Automated Verification Test Suite
# ============================================================================

def run_tests():
    print("=== Level 5 Chapter 7: DevOps, CI/CD, Containerization & IaC Lab ===")

    # Test 1: PID Namespace Isolation
    ns1 = PidNamespace("ns-app-worker")
    vpid1 = ns1.attach_process(host_pid=40892)
    vpid2 = ns1.attach_process(host_pid=40893)
    assert vpid1 == 1, f"Initial process in PID namespace must be virtual PID 1 (init), got {vpid1}"
    assert vpid2 == 2
    assert ns1.get_virtual_pid(40892) == 1
    assert ns1.get_virtual_pid(99999) is None
    print("  [PASS] PID Namespace Isolation Virtualization (Host 40892 -> VPID 1)")

    # Test 2: Memory Cgroup and OOM Killer
    cgroup = MemoryCgroup(limit_mb=512.0)
    p1 = Process(host_pid=1001, command="nginx", memory_mb=128.0)
    p2 = Process(host_pid=1002, command="node_api", memory_mb=256.0)
    
    cgroup.attach(p1)
    cgroup.attach(p2)
    assert cgroup.current_usage_mb == 384.0
    
    # Safe allocation
    ok, msg = cgroup.allocate(1001, 64.0)
    assert ok is True
    assert cgroup.current_usage_mb == 448.0
    
    # Allocation that exceeds 512MB limit -> triggers OOM kill
    ok, oom_msg = cgroup.allocate(1002, 100.0)
    assert ok is False
    assert "OOMKilled" in oom_msg
    assert 1002 not in cgroup.attached_processes  # Process 1002 was terminated
    assert cgroup.current_usage_mb == 192.0  # Only p1 remains (128 + 64 = 192)
    print(f"  [PASS] Memory Cgroup Limit & OOM Killer Verified: '{oom_msg}'")

    # Test 3: OverlayFS CoW and Whiteout
    base_os_layer = {"/etc/os-release": "NAME=Alpine Linux", "/bin/sh": "[ELF Binary]"}
    app_layer = {"/app/server.py": "print('hello')", "/etc/config.json": '{"debug": false}'}
    
    overlay = OverlayFS(lower_layers=[base_os_layer, app_layer])
    
    # Read untouched lower files
    assert overlay.read_file("/etc/os-release") == "NAME=Alpine Linux"
    assert overlay.read_file("/app/server.py") == "print('hello')"
    assert len(overlay.upper_layer) == 0  # Upper layer completely empty
    
    # Modify an existing file (Triggers Copy-Up)
    action = overlay.write_file("/etc/config.json", '{"debug": true}')
    assert action == "COPY_UP_MODIFIED: /etc/config.json"
    assert "/etc/config.json" in overlay.upper_layer
    assert overlay.read_file("/etc/config.json") == '{"debug": true}'
    # Lower layer remains unmodified (immutable image)
    assert app_layer["/etc/config.json"] == '{"debug": false}'

    # Delete lower file (Triggers Whiteout marker)
    del_action = overlay.delete_file("/bin/sh")
    assert del_action == "WHITEOUT_CREATED: .wh./bin/sh"
    assert overlay.read_file("/bin/sh") is None
    
    merged = overlay.get_merged_files()
    assert "/bin/sh" not in merged
    assert merged["/etc/config.json"] == '{"debug": true}'
    assert merged["/etc/os-release"] == "NAME=Alpine Linux"
    print("  [PASS] OverlayFS Copy-on-Write (CoW) and Whiteout Deletion Validated")

    # Test 4: Canary Deployment Controller with Happy Path
    canary = CanaryDeploymentController(stable_version="v1.0.0", canary_version="v1.1.0", error_threshold=0.02)
    steps = [0.05, 0.25, 0.50, 1.0]
    
    for weight in steps:
        ok = canary.evaluate_step(target_weight=weight, requests_count=1000, failed_requests=5)  # 0.5% error rate < 2%
        assert ok is True
    assert canary.status == "SUCCESS"
    assert canary.current_canary_weight == 1.0
    print("  [PASS] Canary Progressive Rollout (5% -> 25% -> 50% -> 100%) Succeeded")

    # Test 5: Canary Rollback on Incident
    canary_bad = CanaryDeploymentController(stable_version="v1.0.0", canary_version="v2.0.0-buggy", error_threshold=0.02)
    step1_ok = canary_bad.evaluate_step(target_weight=0.05, requests_count=1000, failed_requests=5)
    assert step1_ok is True
    
    # Step 2 experiences 50 errors out of 1000 (5.0% error rate > 2.0% threshold)
    step2_ok = canary_bad.evaluate_step(target_weight=0.25, requests_count=1000, failed_requests=50)
    assert step2_ok is False
    assert canary_bad.status == "ROLLED_BACK"
    assert canary_bad.current_canary_weight == 0.0
    # Confirm 100% traffic reverts to stable
    routes = [canary_bad.route_traffic(i) for i in range(100)]
    assert all(r == "v1.0.0" for r in routes)
    print("  [PASS] Canary Automated Rollback Breached Threshold Verified (100% traffic restored to v1.0.0)")

    print("ALL TESTS PASSED: Level 5 Chapter 7 DevOps, Container & Canary Engine verified successfully.")


if __name__ == "__main__":
    run_tests()
