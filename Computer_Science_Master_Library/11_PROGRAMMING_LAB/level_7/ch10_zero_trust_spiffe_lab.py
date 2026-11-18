"""
ch10_zero_trust_spiffe_lab.py
Level 7 Companion Lab: SPIFFE IDs, Ephemeral SVIDs & Zero-Trust mTLS Policy.
Pure Python/Standard Library implementation with zero external dependencies.
"""

from __future__ import annotations
import sys
import time
import secrets
import hashlib
import hmac
from urllib.parse import urlparse
from typing import Dict, Set

# Windows UTF-8 console output
sys.stdout.reconfigure(encoding="utf-8")


class LabSpiffeId:
    """SPIFFE workload identifier standard."""
    def __init__(self, trust_domain: str, path: str):
        self.trust_domain = trust_domain.lower()
        self.path = path if path.startswith("/") else f"/{path}"

    def uri(self) -> str:
        return f"spiffe://{self.trust_domain}{self.path}"

    @classmethod
    def parse(cls, spiffe_uri: str) -> LabSpiffeId:
        parsed = urlparse(spiffe_uri)
        if parsed.scheme != "spiffe" or not parsed.netloc:
            raise ValueError(f"Invalid SPIFFE URI: {spiffe_uri}")
        return cls(parsed.netloc, parsed.path)


class LabX509SVID:
    """Simulated X.509 SVID certificate with cryptographic signature and TTL."""
    def __init__(self, spiffe_id: LabSpiffeId, ttl_sec: int = 3600, key: str = "SECRET_CA_KEY"):
        self.spiffe_id = spiffe_id
        self.issued_at = int(time.time())
        self.expires_at = self.issued_at + ttl_sec
        self.serial = secrets.token_hex(8)
        self.signature = self._sign(key)

    def _sign(self, key: str) -> str:
        data = f"{self.spiffe_id.uri()}:{self.expires_at}:{self.serial}"
        return hmac.new(key.encode("utf-8"), data.encode("utf-8"), hashlib.sha256).hexdigest()

    def is_valid(self, key: str = "SECRET_CA_KEY") -> bool:
        if int(time.time()) >= self.expires_at:
            return False  # Expired
        return hmac.compare_digest(self.signature, self._sign(key))


class LabZeroTrustGateway:
    """Policy Decision Point authorizing client SVIDs."""
    def __init__(self):
        # Maps target_service_uri -> Set of authorized caller URIs
        self.policy: Dict[str, Set[str]] = {}

    def allow(self, server_uri: str, client_uri: str) -> None:
        if server_uri not in self.policy:
            self.policy[server_uri] = set()
        self.policy[server_uri].add(client_uri)

    def authorize(self, server_svid: LabX509SVID, client_svid: LabX509SVID) -> bool:
        if not server_svid.is_valid() or not client_svid.is_valid():
            return False  # Invalid or expired certificate!
        allowed = self.policy.get(server_svid.spiffe_id.uri(), set())
        return client_svid.spiffe_id.uri() in allowed


def test_spiffe_uri_parsing():
    print("Running Test Suite 1: SPIFFE ID URI Parsing & Normalization...")
    uri = "spiffe://prod.corp/ns/finance/sa/ledger"
    spiffe = LabSpiffeId.parse(uri)
    assert spiffe.trust_domain == "prod.corp"
    assert spiffe.path == "/ns/finance/sa/ledger"
    assert spiffe.uri() == uri
    print("  Passed! SPIFFE URI parsed and validated according to SPIFFE specification.")


def test_ephemeral_svid_validation():
    print("Running Test Suite 2: Ephemeral X.509 SVID Validation & Expiration...")
    spiffe = LabSpiffeId("prod.corp", "/sa/payment")

    # Valid SVID
    svid_valid = LabX509SVID(spiffe, ttl_sec=3600)
    assert svid_valid.is_valid() is True

    # Expired SVID
    svid_expired = LabX509SVID(spiffe, ttl_sec=-5)  # Expired in past
    assert svid_expired.is_valid() is False

    # Tampered signature
    svid_tampered = LabX509SVID(spiffe, ttl_sec=3600)
    svid_tampered.signature = "tampered_bad_hex"
    assert svid_tampered.is_valid() is False
    print("  Passed! SVID validates authentic signatures and strictly rejects expired or tampered certs.")


def test_zero_trust_policy_authorization():
    print("Running Test Suite 3: Zero-Trust mTLS Policy Decision Point...")
    payment_spiffe = LabSpiffeId("prod.corp", "/sa/payment-service")
    checkout_spiffe = LabSpiffeId("prod.corp", "/sa/checkout-service")
    rogue_spiffe = LabSpiffeId("prod.corp", "/sa/rogue-attacker")

    payment_svid = LabX509SVID(payment_spiffe)
    checkout_svid = LabX509SVID(checkout_spiffe)
    rogue_svid = LabX509SVID(rogue_spiffe)

    gateway = LabZeroTrustGateway()
    # Explicitly permit checkout-service to call payment-service
    gateway.allow(payment_spiffe.uri(), checkout_spiffe.uri())

    # Authorized call
    assert gateway.authorize(payment_svid, checkout_svid) is True

    # Unauthorized rogue call
    assert gateway.authorize(payment_svid, rogue_svid) is False
    print("  Passed! Policy engine strictly authorized valid SVID and rejected rogue caller.")


if __name__ == "__main__":
    print("================================================================================")
    print("LEVEL 7 LAB 10: ZERO-TRUST SPIFFE/SPIRE & MTLS POLICY ENGINE")
    print("================================================================================")
    test_spiffe_uri_parsing()
    test_ephemeral_svid_validation()
    test_zero_trust_policy_authorization()
    print("================================================================================")
    print("ALL 3 TEST SUITES PASSED CLEANLY (EXIT CODE 0)")
    print("================================================================================")
