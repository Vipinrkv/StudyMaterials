"""
Level 5 Chapter 02 Programming Lab: Creational & Structural Design Patterns
==========================================================================
Focus: Abstract Factory, Fluent Builder, Thread-Safe Singleton with Double-Checked
       Locking, Decorator stream transformation, and Adapter Pattern.
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")
from typing import Dict, Optional, Any
from abc import ABC, abstractmethod
import threading
import base64
import zlib


# ---------------------------------------------------------------------------
# 1. Creational: Abstract Factory Pattern (Multi-Cloud Storage)
# ---------------------------------------------------------------------------

class IBlobStorage(ABC):
    @abstractmethod
    def put_object(self, key: str, data: bytes) -> str:
        pass


class S3BlobStorage(IBlobStorage):
    def put_object(self, key: str, data: bytes) -> str:
        return f"s3://my-bucket/{key} ({len(data)} bytes stored)"


class GcsBlobStorage(IBlobStorage):
    def put_object(self, key: str, data: bytes) -> str:
        return f"gs://gcp-bucket/{key} ({len(data)} bytes stored)"


class ICloudResourceFactory(ABC):
    @abstractmethod
    def create_storage(self) -> IBlobStorage:
        pass


class AwsCloudFactory(ICloudResourceFactory):
    def create_storage(self) -> IBlobStorage:
        return S3BlobStorage()


class GcpCloudFactory(ICloudResourceFactory):
    def create_storage(self) -> IBlobStorage:
        return GcsBlobStorage()


# ---------------------------------------------------------------------------
# 2. Creational: Fluent Builder Pattern (HttpRequest)
# ---------------------------------------------------------------------------

class HttpRequest:
    def __init__(self, method: str, url: str, headers: Dict[str, str], body: Optional[str], timeout_ms: int):
        self.method = method
        self.url = url
        self.headers = headers
        self.body = body
        self.timeout_ms = timeout_ms

    def __repr__(self):
        return f"HttpRequest({self.method} {self.url}, headers={len(self.headers)}, timeout={self.timeout_ms}ms)"


class HttpRequestBuilder:
    def __init__(self):
        self._method = "GET"
        self._url: Optional[str] = None
        self._headers: Dict[str, str] = {}
        self._body: Optional[str] = None
        self._timeout_ms = 5000

    def with_method(self, method: str) -> 'HttpRequestBuilder':
        self._method = method.upper()
        return self

    def with_url(self, url: str) -> 'HttpRequestBuilder':
        self._url = url
        return self

    def with_header(self, key: str, value: str) -> 'HttpRequestBuilder':
        self._headers[key] = value
        return self

    def with_body(self, body: str) -> 'HttpRequestBuilder':
        self._body = body
        return self

    def with_timeout(self, timeout_ms: int) -> 'HttpRequestBuilder':
        self._timeout_ms = timeout_ms
        return self

    def build(self) -> HttpRequest:
        # Invariant checks
        if not self._url:
            raise ValueError("URL must be specified before building HttpRequest.")
        if self._method in ("POST", "PUT") and self._body is None:
            raise ValueError(f"Body is required for HTTP method {self._method}.")
        return HttpRequest(self._method, self._url, self._headers, self._body, self._timeout_ms)


# ---------------------------------------------------------------------------
# 3. Creational: Thread-Safe Singleton (Double-Checked Locking Simulation)
# ---------------------------------------------------------------------------

class DatabaseConnectionPool:
    _instance: Optional['DatabaseConnectionPool'] = None
    _lock = threading.Lock()

    def __init__(self):
        if DatabaseConnectionPool._instance is not None:
            raise RuntimeError("Use getInstance() to access DatabaseConnectionPool")
        self.pool_size = 10
        self.active_connections = 0

    @classmethod
    def get_instance(cls) -> 'DatabaseConnectionPool':
        if cls._instance is None:  # First check (unsynchronized)
            with cls._lock:         # Acquire lock
                if cls._instance is None:  # Second check (synchronized)
                    cls._instance = cls()
        return cls._instance


# ---------------------------------------------------------------------------
# 4. Structural: Decorator Pattern (Data Stream Transformation)
# ---------------------------------------------------------------------------

class IDataStream(ABC):
    @abstractmethod
    def write(self, data: str) -> bytes:
        pass


class PlainDataStream(IDataStream):
    def write(self, data: str) -> bytes:
        return data.encode("utf-8")


class StreamDecorator(IDataStream):
    def __init__(self, wrapped: IDataStream):
        self._wrapped = wrapped

    def write(self, data: str) -> bytes:
        return self._wrapped.write(data)


class CompressionDecorator(StreamDecorator):
    def write(self, data: str) -> bytes:
        raw_bytes = self._wrapped.write(data)
        return zlib.compress(raw_bytes)


class Base64EncodingDecorator(StreamDecorator):
    def write(self, data: str) -> bytes:
        compressed_or_raw = self._wrapped.write(data)
        return base64.b64encode(compressed_or_raw)


# ---------------------------------------------------------------------------
# 5. Structural: Adapter Pattern (Legacy to Modern Interface)
# ---------------------------------------------------------------------------

class ModernPaymentTarget(ABC):
    @abstractmethod
    def pay(self, amount_in_cents: int) -> str:
        pass


class LegacyPaymentService:
    """Incompatible legacy third-party service working with dollars float."""
    def make_dollar_transfer(self, dollars: float) -> str:
        return f"Legacy transferred ${dollars:.2f}"


class LegacyPaymentAdapter(ModernPaymentTarget):
    def __init__(self, legacy_service: LegacyPaymentService):
        self._legacy = legacy_service

    def pay(self, amount_in_cents: int) -> str:
        dollars = amount_in_cents / 100.0
        return self._legacy.make_dollar_transfer(dollars)


def test_patterns_suite():
    print("[TEST 1] Abstract Factory Pattern (Multi-Cloud)...")
    aws_factory = AwsCloudFactory()
    gcp_factory = GcpCloudFactory()

    aws_storage = aws_factory.create_storage()
    gcp_storage = gcp_factory.create_storage()

    res_aws = aws_storage.put_object("profile.jpg", b"image_data_123")
    res_gcp = gcp_storage.put_object("backup.tar", b"archive_data_456")

    assert res_aws.startswith("s3://"), f"AWS storage mismatch: {res_aws}"
    assert res_gcp.startswith("gs://"), f"GCP storage mismatch: {res_gcp}"
    print(f"  -> AWS Output: {res_aws}")
    print(f"  -> GCP Output: {res_gcp}")

    print("[TEST 2] Fluent Builder Pattern with Invariant Enforcement...")
    builder = HttpRequestBuilder()
    req = (
        builder.with_method("POST")
        .with_url("https://api.antigravity.dev/v1/charge")
        .with_header("Authorization", "Bearer token_xyz")
        .with_body('{"amount": 5000}')
        .with_timeout(3000)
        .build()
    )
    assert req.method == "POST"
    assert req.timeout_ms == 3000
    assert "Authorization" in req.headers
    print(f"  -> Successfully built validated HttpRequest: {req}")

    # Verify invariant enforcement
    try:
        HttpRequestBuilder().with_method("POST").with_url("https://example.com").build()
        assert False, "Should have thrown ValueError for missing body"
    except ValueError:
        print("  -> Invariant caught: Missing POST body correctly rejected.")

    print("[TEST 3] Thread-Safe Singleton Double-Checked Locking...")
    instances = []

    def fetch_singleton():
        inst = DatabaseConnectionPool.get_instance()
        instances.append(inst)

    threads = [threading.Thread(target=fetch_singleton) for _ in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()

    # Verify all 10 threads obtained the exact same object reference
    first_inst = instances[0]
    for inst in instances[1:]:
        assert inst is first_inst, "Singleton identity violated across concurrent threads!"
    print(f"  -> Verified 10 concurrent threads received identical instance id: {id(first_inst)}.")

    print("[TEST 4] Decorator Pattern (Data Stream Pipeline)...")
    payload = "Antigravity Computer Science Master Library"
    pipeline = Base64EncodingDecorator(CompressionDecorator(PlainDataStream()))
    transformed_bytes = pipeline.write(payload)

    # Verify transformation by reversing: Base64 decode -> Zlib decompress
    decoded_b64 = base64.b64decode(transformed_bytes)
    decompressed = zlib.decompress(decoded_b64).decode("utf-8")
    assert decompressed == payload, "Decorator chain corrupted data integrity!"
    print(f"  -> Raw text ({len(payload)} chars) transformed to {len(transformed_bytes)} bytes and successfully verified.")

    print("[TEST 5] Adapter Pattern (Legacy Interface Bridge)...")
    legacy = LegacyPaymentService()
    adapter = LegacyPaymentAdapter(legacy)
    msg = adapter.pay(amount_in_cents=4999)  # $49.99
    assert msg == "Legacy transferred $49.99", f"Adapter output mismatch: {msg}"
    print(f"  -> Adapter bridged 4999 cents to: '{msg}'")

    print("ALL Level 5 Chapter 02 Creational & Structural lab tests passed successfully!")


if __name__ == "__main__":
    test_patterns_suite()
