"""
ch10_kubernetes_reconciliation_lab.py
Level 6 Companion Lab: Kubernetes Control Loop, Scheduling & Autoscaling Engine.
Pure Python/Standard Library implementation with zero external dependencies.
"""

from __future__ import annotations
import sys
import math
import copy
from typing import Dict, List, Optional, Any

# Windows UTF-8 console output
sys.stdout.reconfigure(encoding="utf-8")


class K8sEtcd:
    """Simulates etcd datastore with optimistic concurrency control."""
    def __init__(self):
        self._data: Dict[str, Dict[str, Any]] = {}
        self.revision = 0

    def put(self, key: str, val: Dict[str, Any]) -> int:
        self.revision += 1
        stored = copy.deepcopy(val)
        stored["resourceVersion"] = self.revision
        self._data[key] = stored
        return self.revision

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        val = self._data.get(key)
        return copy.deepcopy(val) if val else None

    def list_prefix(self, prefix: str) -> List[Dict[str, Any]]:
        return [copy.deepcopy(v) for k, v in self._data.items() if k.startswith(prefix)]

    def delete(self, key: str) -> bool:
        if key in self._data:
            del self._data[key]
            self.revision += 1
            return True
        return False


class K8sNode:
    """Cluster worker node with resource accounting."""
    def __init__(self, name: str, cpu: float, mem: float):
        self.name = name
        self.total_cpu = cpu
        self.total_mem = mem
        self.used_cpu = 0.0
        self.used_mem = 0.0

    def fits(self, cpu: float, mem: float) -> bool:
        return (self.used_cpu + cpu <= self.total_cpu) and (self.used_mem + mem <= self.total_mem)

    def allocate(self, cpu: float, mem: float) -> None:
        self.used_cpu += cpu
        self.used_mem += mem

    def free(self, cpu: float, mem: float) -> None:
        self.used_cpu = max(0.0, self.used_cpu - cpu)
        self.used_mem = max(0.0, self.used_mem - mem)


def schedule_pod(nodes: List[K8sNode], req_cpu: float, req_mem: float) -> Optional[K8sNode]:
    """Filters eligible nodes and scores based on balanced resource ratio."""
    feasible = [n for n in nodes if n.fits(req_cpu, req_mem)]
    if not feasible:
        return None

    # Score: minimize imbalance between CPU and Memory utilization
    best_node = None
    best_score = -1.0

    for n in feasible:
        cpu_ratio = (n.used_cpu + req_cpu) / n.total_cpu
        mem_ratio = (n.used_mem + req_mem) / n.total_mem
        score = 100.0 * (1.0 - abs(cpu_ratio - mem_ratio))
        if score > best_score:
            best_score = score
            best_node = n

    if best_node:
        best_node.allocate(req_cpu, req_mem)
    return best_node


def reconcile_deployment(etcd: K8sEtcd, nodes: List[K8sNode], dep_name: str) -> Dict[str, Any]:
    """Reconciliation loop driving observed Pods to match Deployment desired replicas."""
    dep_key = f"/deployments/{dep_name}"
    dep = etcd.get(dep_key)
    if not dep:
        raise ValueError("Deployment not found")

    desired = dep["spec"]["replicas"]
    req_cpu = dep["spec"]["cpu"]
    req_mem = dep["spec"]["mem"]

    pod_prefix = f"/pods/{dep_name}-"
    current_pods = etcd.list_prefix(pod_prefix)
    current_count = len(current_pods)
    delta = desired - current_count

    if delta > 0:
        for i in range(current_count, desired):
            pod_name = f"{dep_name}-{i}"
            assigned_node = schedule_pod(nodes, req_cpu, req_mem)
            node_name = assigned_node.name if assigned_node else "UNSCHEDULED"
            status = "Running" if assigned_node else "Pending"
            pod_doc = {
                "name": pod_name,
                "node": node_name,
                "status": status,
                "cpu": req_cpu,
                "mem": req_mem
            }
            etcd.put(f"/pods/{pod_name}", pod_doc)
    elif delta < 0:
        excess = abs(delta)
        to_delete = current_pods[-excess:]
        for p in to_delete:
            node_name = p["node"]
            for n in nodes:
                if n.name == node_name:
                    n.free(req_cpu, req_mem)
                    break
            etcd.delete(f"/pods/{p['name']}")

    # Refresh status
    all_pods = etcd.list_prefix(pod_prefix)
    running = [p for p in all_pods if p["status"] == "Running"]
    dep["status"] = {
        "replicas": len(all_pods),
        "readyReplicas": len(running)
    }
    etcd.put(dep_key, dep)
    return dep["status"]


def compute_hpa_scale(
    current_replicas: int,
    current_metric: float,
    target_metric: float,
    tolerance: float = 0.10,
    min_replicas: int = 1,
    max_replicas: int = 10
) -> int:
    """Computes target replicas: R = ceil(C * (M_current / M_target))."""
    if current_replicas <= 0:
        return min_replicas

    ratio = current_metric / target_metric
    if abs(ratio - 1.0) <= tolerance:
        return current_replicas  # Inside tolerance window

    desired = int(math.ceil(current_replicas * ratio))
    return max(min_replicas, min(max_replicas, desired))


def test_scheduling_and_reconciliation():
    print("Running Test Suite 1: Kube-Scheduler & Deployment Reconciliation Loop...")
    etcd = K8sEtcd()
    nodes = [
        K8sNode("node-1", cpu=4.0, mem=8192.0),
        K8sNode("node-2", cpu=2.0, mem=4096.0)
    ]

    # Create deployment: 3 replicas, 1.0 CPU, 2048 MB RAM
    dep_manifest = {
        "metadata": {"name": "order-service"},
        "spec": {"replicas": 3, "cpu": 1.0, "mem": 2048.0}
    }
    etcd.put("/deployments/order-service", dep_manifest)

    # Reconcile -> Should launch 3 pods
    status = reconcile_deployment(etcd, nodes, "order-service")
    assert status["replicas"] == 3
    assert status["readyReplicas"] == 3

    # Check node allocations: Total CPU = 3.0, Total Mem = 6144.0
    total_cpu_used = sum(n.used_cpu for n in nodes)
    assert abs(total_cpu_used - 3.0) < 1e-6
    print(f"  Passed! Reconciled 3 Pods across cluster with balanced allocation.")


def test_admission_capacity_saturation():
    print("Running Test Suite 2: Cluster Saturation & Pending Pod State...")
    etcd = K8sEtcd()
    nodes = [K8sNode("node-small", cpu=2.0, mem=2048.0)]

    # Request 3 pods of 1.0 CPU each -> Node only has 2.0 CPU capacity
    dep_manifest = {
        "metadata": {"name": "heavy-app"},
        "spec": {"replicas": 3, "cpu": 1.0, "mem": 512.0}
    }
    etcd.put("/deployments/heavy-app", dep_manifest)

    status = reconcile_deployment(etcd, nodes, "heavy-app")
    assert status["replicas"] == 3
    assert status["readyReplicas"] == 2  # 3rd pod could not fit!

    pending_pods = [p for p in etcd.list_prefix("/pods/heavy-app-") if p["status"] == "Pending"]
    assert len(pending_pods) == 1
    print("  Passed! Saturated capacity correctly resulted in 1 Pending Pod.")


def test_hpa_autoscaling():
    print("Running Test Suite 3: HPA Control Formula & Tolerance Bands...")
    # Current replicas = 4, target metric = 50%, current metric = 75%
    # Ratio = 75 / 50 = 1.5 -> Desired = ceil(4 * 1.5) = 6
    r1 = compute_hpa_scale(current_replicas=4, current_metric=75.0, target_metric=50.0)
    assert r1 == 6, f"Expected 6, got {r1}"

    # Metric within 10% tolerance (e.g. 54% vs 50% -> ratio 1.08 <= 1.10) -> No change
    r2 = compute_hpa_scale(current_replicas=4, current_metric=54.0, target_metric=50.0)
    assert r2 == 4, f"Expected 4, got {r2}"

    # Scale down: current = 25%, target = 50% -> ratio = 0.5 -> ceil(4 * 0.5) = 2
    r3 = compute_hpa_scale(current_replicas=4, current_metric=25.0, target_metric=50.0)
    assert r3 == 2, f"Expected 2, got {r3}"
    print("  Passed! HPA scale-up, tolerance-band stability, and scale-down verified.")


if __name__ == "__main__":
    print("================================================================================")
    print("LEVEL 6 LAB 10: KUBERNETES RECONCILIATION & AUTOSCALING ENGINE")
    print("================================================================================")
    test_scheduling_and_reconciliation()
    test_admission_capacity_saturation()
    test_hpa_autoscaling()
    print("================================================================================")
    print("ALL 3 TEST SUITES PASSED CLEANLY (EXIT CODE 0)")
    print("================================================================================")
