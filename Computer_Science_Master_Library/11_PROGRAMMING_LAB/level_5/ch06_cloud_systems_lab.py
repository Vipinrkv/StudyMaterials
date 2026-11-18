# -*- coding: utf-8 -*-
"""
CH06: Cloud Architecture and Serverless Systems Lab
===================================================
Covers:
1. Exponential Backoff with Full Jitter and Decorrelated Jitter algorithms (AWS Architecture Pattern).
2. High-Availability Reliability Calculator (Serial, Parallel, Composite Nines calculation).
3. S3-Compatible Object Store Engine with Versioning and Multipart Upload with ETag calculation.
"""
import sys
import hashlib
import random
import time
import math
from typing import Dict, List, Optional, Tuple

sys.stdout.reconfigure(encoding="utf-8")


# ============================================================================
# Section 1: Resilient Cloud Retries & Jitter Simulation
# ============================================================================

def exponential_backoff_no_jitter(base_ms: float, cap_ms: float, attempt: int) -> float:
    """Standard exponential backoff: min(cap, base * 2^attempt)."""
    return min(cap_ms, base_ms * (2 ** attempt))


def exponential_backoff_full_jitter(base_ms: float, cap_ms: float, attempt: int, rng: random.Random) -> float:
    """AWS Full Jitter: Sleep = uniform(0, min(cap, base * 2^attempt))."""
    temp = min(cap_ms, base_ms * (2 ** attempt))
    return rng.uniform(0.0, temp)


def exponential_backoff_decorrelated_jitter(base_ms: float, cap_ms: float, prev_sleep: float, rng: random.Random) -> float:
    """AWS Decorrelated Jitter: Sleep = min(cap, uniform(base, prev_sleep * 3))."""
    return min(cap_ms, rng.uniform(base_ms, prev_sleep * 3.0))


class MockCloudRPCClient:
    """Simulates an unreliable cloud network endpoint subject to transient 503 throttling."""
    def __init__(self, failure_count: int, rng: random.Random):
        self.remaining_failures = failure_count
        self.total_attempts = 0
        self.rng = rng

    def call(self) -> str:
        self.total_attempts += 1
        if self.remaining_failures > 0:
            self.remaining_failures -= 1
            raise ConnectionResetError("503 Service Unavailable: Rate limit exceeded")
        return "200 OK: Payload Delivered"


def execute_resilient_call(client: MockCloudRPCClient, max_retries: int = 5, base_ms: float = 10.0, cap_ms: float = 500.0, rng: random.Random = None) -> Tuple[str, List[float]]:
    """Executes a call with exponential backoff and full jitter, recording sleep durations."""
    if rng is None:
        rng = random.Random(42)
    sleep_history: List[float] = []
    
    for attempt in range(max_retries):
        try:
            res = client.call()
            return res, sleep_history
        except ConnectionResetError:
            if attempt == max_retries - 1:
                raise
            sleep_time = exponential_backoff_full_jitter(base_ms, cap_ms, attempt, rng)
            sleep_history.append(sleep_time)
    raise RuntimeError("Max retries exceeded")


# ============================================================================
# Section 2: Availability & Reliability Engineering Calculator
# ============================================================================

class AvailabilityCalculator:
    """Calculates system uptime percentages and downtime budgets across serial and redundant components."""
    
    @staticmethod
    def serial_availability(components: List[float]) -> float:
        """Serial system: System works iff ALL components work -> A_total = product(A_i)."""
        product = 1.0
        for c in components:
            if not (0.0 <= c <= 1.0):
                raise ValueError("Availability must be between 0 and 1.0")
            product *= c
        return product

    @staticmethod
    def parallel_redundancy_availability(components: List[float]) -> float:
        """Parallel system: System works if AT LEAST ONE component works -> A_total = 1 - product(1 - A_i)."""
        unavailability_prod = 1.0
        for c in components:
            if not (0.0 <= c <= 1.0):
                raise ValueError("Availability must be between 0 and 1.0")
            unavailability_prod *= (1.0 - c)
        return 1.0 - unavailability_prod

    @staticmethod
    def composite_architecture_availability(tiers: List[Dict[str, any]]) -> float:
        """
        Calculates composite availability for a tiered architecture.
        Each tier can be 'serial' (single component) or 'redundant' (parallel components).
        The overall end-to-end architecture is a serial pipeline of tiers.
        """
        overall_availability = 1.0
        for tier in tiers:
            tier_type = tier.get("type", "serial")
            rates = tier["rates"]
            if tier_type == "redundant":
                tier_avail = AvailabilityCalculator.parallel_redundancy_availability(rates)
            else:
                tier_avail = AvailabilityCalculator.serial_availability(rates)
            overall_availability *= tier_avail
        return overall_availability

    @staticmethod
    def annual_downtime_minutes(availability: float) -> float:
        """Computes annual allowed downtime in minutes (365.25 days / year)."""
        total_annual_minutes = 365.25 * 24.0 * 60.0  # 525,960 minutes
        return (1.0 - availability) * total_annual_minutes


# ============================================================================
# Section 3: S3-Compatible Object Store Engine with Versioning & Multipart Upload
# ============================================================================

class S3ObjectVersion:
    def __init__(self, version_id: str, data: bytes, is_delete_marker: bool = False):
        self.version_id = version_id
        self.data = data
        self.is_delete_marker = is_delete_marker
        self.etag = hashlib.md5(data).hexdigest() if not is_delete_marker else ""
        self.size_bytes = len(data) if not is_delete_marker else 0
        self.timestamp = time.time()


class S3MultipartUploadSession:
    def __init__(self, upload_id: str, bucket: str, key: str):
        self.upload_id = upload_id
        self.bucket = bucket
        self.key = key
        self.parts: Dict[int, bytes] = {}  # part_number -> part_data

    def add_part(self, part_number: int, data: bytes) -> str:
        if part_number < 1 or part_number > 10000:
            raise ValueError("Part number must be between 1 and 10000")
        self.parts[part_number] = data
        return hashlib.md5(data).hexdigest()

    def complete(self) -> Tuple[bytes, str]:
        if not self.parts:
            raise ValueError("No parts uploaded")
        # Combine parts in sequential order
        sorted_keys = sorted(self.parts.keys())
        combined = bytearray()
        part_md5_hashes = []
        for p in sorted_keys:
            data = self.parts[p]
            combined.extend(data)
            part_md5_hashes.append(hashlib.md5(data).digest())
        
        # S3 multi-part ETag format: md5(concatenated_part_md5_bytes) + '-' + count_of_parts
        s3_multipart_etag = f"{hashlib.md5(b''.join(part_md5_hashes)).hexdigest()}-{len(sorted_keys)}"
        return bytes(combined), s3_multipart_etag


class S3MockStorageEngine:
    """In-memory S3 storage engine providing versioning, deletion markers, and multipart uploads."""
    def __init__(self):
        self.buckets: Dict[str, Dict[str, List[S3ObjectVersion]]] = {}
        self.versioning_enabled: Dict[str, bool] = {}
        self.multipart_sessions: Dict[str, S3MultipartUploadSession] = {}
        self._version_counter = 1000
        self._upload_counter = 5000

    def create_bucket(self, bucket_name: str, enable_versioning: bool = False) -> None:
        if bucket_name in self.buckets:
            raise ValueError(f"Bucket {bucket_name} already exists")
        self.buckets[bucket_name] = {}
        self.versioning_enabled[bucket_name] = enable_versioning

    def put_object(self, bucket_name: str, key: str, data: bytes) -> Tuple[str, str]:
        if bucket_name not in self.buckets:
            raise KeyError(f"Bucket {bucket_name} not found")
        
        is_versioned = self.versioning_enabled.get(bucket_name, False)
        self._version_counter += 1
        vid = f"v{self._version_counter}" if is_versioned else "null"
        
        obj_version = S3ObjectVersion(vid, data)
        bucket_objects = self.buckets[bucket_name]
        
        if key not in bucket_objects:
            bucket_objects[key] = []
        
        if is_versioned:
            bucket_objects[key].insert(0, obj_version)  # Newest first
        else:
            bucket_objects[key] = [obj_version]
            
        return obj_version.version_id, obj_version.etag

    def get_object(self, bucket_name: str, key: str, version_id: Optional[str] = None) -> bytes:
        if bucket_name not in self.buckets:
            raise KeyError(f"Bucket {bucket_name} not found")
        bucket_objects = self.buckets[bucket_name]
        if key not in bucket_objects or not bucket_objects[key]:
            raise KeyError(f"Key {key} not found")
        
        versions = bucket_objects[key]
        if version_id is None:
            # Latest version
            top = versions[0]
            if top.is_delete_marker:
                raise KeyError(f"Key {key} has been deleted (DeleteMarker active)")
            return top.data
        else:
            for v in versions:
                if v.version_id == version_id:
                    if v.is_delete_marker:
                        raise KeyError(f"Version {version_id} is a delete marker")
                    return v.data
            raise KeyError(f"Version {version_id} not found for key {key}")

    def delete_object(self, bucket_name: str, key: str) -> str:
        """Deletes object. In versioned bucket, writes a DeleteMarker. In unversioned, removes it."""
        if bucket_name not in self.buckets:
            raise KeyError(f"Bucket {bucket_name} not found")
        bucket_objects = self.buckets[bucket_name]
        if key not in bucket_objects or not bucket_objects[key]:
            return "null"
        
        is_versioned = self.versioning_enabled.get(bucket_name, False)
        if is_versioned:
            self._version_counter += 1
            marker_vid = f"del-v{self._version_counter}"
            marker = S3ObjectVersion(marker_vid, b"", is_delete_marker=True)
            bucket_objects[key].insert(0, marker)
            return marker_vid
        else:
            del bucket_objects[key]
            return "null"

    def initiate_multipart_upload(self, bucket_name: str, key: str) -> str:
        if bucket_name not in self.buckets:
            raise KeyError(f"Bucket {bucket_name} not found")
        self._upload_counter += 1
        upload_id = f"mp-upload-{self._upload_counter}"
        session = S3MultipartUploadSession(upload_id, bucket_name, key)
        self.multipart_sessions[upload_id] = session
        return upload_id

    def upload_part(self, upload_id: str, part_number: int, data: bytes) -> str:
        if upload_id not in self.multipart_sessions:
            raise KeyError(f"Upload ID {upload_id} not found")
        return self.multipart_sessions[upload_id].add_part(part_number, data)

    def complete_multipart_upload(self, upload_id: str) -> Tuple[str, str]:
        if upload_id not in self.multipart_sessions:
            raise KeyError(f"Upload ID {upload_id} not found")
        session = self.multipart_sessions.pop(upload_id)
        combined_bytes, s3_etag = session.complete()
        vid, _ = self.put_object(session.bucket, session.key, combined_bytes)
        return vid, s3_etag


# ============================================================================
# Section 4: Automated Verification Test Suite
# ============================================================================

def run_tests():
    print("=== Level 5 Chapter 6: Cloud Architecture & Serverless Systems Lab ===")
    
    # Test 1: Jitter algorithms
    rng = random.Random(1337)
    no_jit_1 = exponential_backoff_no_jitter(base_ms=10.0, cap_ms=100.0, attempt=0)
    no_jit_4 = exponential_backoff_no_jitter(base_ms=10.0, cap_ms=100.0, attempt=4)
    assert no_jit_1 == 10.0, f"Expected 10.0, got {no_jit_1}"
    assert no_jit_4 == 100.0, f"Expected cap 100.0, got {no_jit_4}"
    
    for att in range(5):
        full_jit = exponential_backoff_full_jitter(10.0, 500.0, att, rng)
        assert 0.0 <= full_jit <= min(500.0, 10.0 * (2 ** att))
    
    # Test 2: Resilient client execution with retries
    mock_client = MockCloudRPCClient(failure_count=3, rng=random.Random(42))
    status, history = execute_resilient_call(mock_client, max_retries=5, base_ms=20.0, cap_ms=200.0, rng=random.Random(42))
    assert status == "200 OK: Payload Delivered"
    assert len(history) == 3, f"Expected 3 retry sleeps, got {len(history)}"
    assert mock_client.total_attempts == 4
    print("  [PASS] Exponential Backoff with Full Jitter and Resilient RPC Verified")

    # Test 3: Availability calculations
    serial_avail = AvailabilityCalculator.serial_availability([0.999, 0.999, 0.999])
    assert abs(serial_avail - 0.997002999) < 1e-6
    downtime_minutes = AvailabilityCalculator.annual_downtime_minutes(serial_avail)
    assert round(downtime_minutes, 1) == 1576.3

    redundant_avail = AvailabilityCalculator.parallel_redundancy_availability([0.99, 0.99])
    assert abs(redundant_avail - 0.9999) < 1e-9

    tiers = [
        {"name": "API_Gateway", "type": "redundant", "rates": [0.999, 0.999]},
        {"name": "App_Compute", "type": "redundant", "rates": [0.99, 0.99]},
        {"name": "Master_Database", "type": "serial", "rates": [0.9999]}
    ]
    comp_avail = AvailabilityCalculator.composite_architecture_availability(tiers)
    expected_comp = (1.0 - (0.001)**2) * (1.0 - (0.01)**2) * 0.9999
    assert abs(comp_avail - expected_comp) < 1e-9
    print(f"  [PASS] Reliability Math: Serial ({serial_avail:.6f}), Redundant ({redundant_avail:.6f}), Composite ({comp_avail:.6f})")

    # Test 4: S3 Engine with Versioning
    s3 = S3MockStorageEngine()
    s3.create_bucket("prod-analytics", enable_versioning=True)
    
    v1, etag1 = s3.put_object("prod-analytics", "report.csv", b"timestamp,revenue\n2026-01-01,5000\n")
    v2, etag2 = s3.put_object("prod-analytics", "report.csv", b"timestamp,revenue\n2026-01-01,8500\n")
    
    assert v1 != v2
    assert s3.get_object("prod-analytics", "report.csv") == b"timestamp,revenue\n2026-01-01,8500\n"
    assert s3.get_object("prod-analytics", "report.csv", version_id=v1) == b"timestamp,revenue\n2026-01-01,5000\n"

    del_vid = s3.delete_object("prod-analytics", "report.csv")
    try:
        s3.get_object("prod-analytics", "report.csv")
        assert False, "Should raise KeyError due to DeleteMarker"
    except KeyError as e:
        assert "DeleteMarker active" in str(e)
    
    assert s3.get_object("prod-analytics", "report.csv", version_id=v2) == b"timestamp,revenue\n2026-01-01,8500\n"
    print("  [PASS] S3 Object Store Engine Versioning & Soft Delete Validated")

    # Test 5: Multipart Upload
    s3.create_bucket("large-files", enable_versioning=False)
    upload_id = s3.initiate_multipart_upload("large-files", "video.mp4")
    
    part1_data = b"CHUNK1_HEADER_METADATA_" * 100
    part2_data = b"CHUNK2_BODY_STREAM_DATA_" * 100
    part3_data = b"CHUNK3_TRAILER_EOF_DATA" * 50
    
    etag_p1 = s3.upload_part(upload_id, 1, part1_data)
    etag_p2 = s3.upload_part(upload_id, 2, part2_data)
    etag_p3 = s3.upload_part(upload_id, 3, part3_data)
    
    final_vid, multipart_etag = s3.complete_multipart_upload(upload_id)
    assert multipart_etag.endswith("-3"), f"Multipart ETag should end with '-3', got {multipart_etag}"
    
    retrieved_content = s3.get_object("large-files", "video.mp4")
    assert retrieved_content == part1_data + part2_data + part3_data
    print(f"  [PASS] S3 Multipart Upload Successful: ETag={multipart_etag}, Total Size={len(retrieved_content)} bytes")
    
    print("ALL TESTS PASSED: Level 5 Chapter 6 Cloud Systems Engine verified successfully.")


if __name__ == "__main__":
    run_tests()
