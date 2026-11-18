"""
Level 5 Chapter 05 Programming Lab: Application Security, Auth & Rate Limiting
=============================================================================
Focus: Cryptographic password hashing with salt and constant-time verification,
       JSON Web Token (JWT) generation, HMAC-SHA256 signing & tampering detection,
       distributed Token Bucket rate limiter, and IDOR mitigation.
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")
from typing import Dict, List, Optional, Tuple, Any
import hashlib
import hmac
import base64
import json
import time
import secrets


# ---------------------------------------------------------------------------
# 1. Cryptographic Password Hashing (PBKDF2-HMAC-SHA256)
# ---------------------------------------------------------------------------

def hash_password(password: str, iterations: int = 100000) -> Tuple[str, str]:
    """
    Generates a cryptographically secure 128-bit salt and derives
    a 256-bit key using PBKDF2 with HMAC-SHA256.
    """
    salt = secrets.token_hex(16)  # 16 bytes = 32 hex chars
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations=iterations,
        dklen=32
    )
    return key.hex(), salt


def verify_password(password: str, salt: str, expected_hash_hex: str, iterations: int = 100000) -> bool:
    """
    Verifies password candidate using constant-time comparison (hmac.compare_digest)
    to mathematically neutralize side-channel timing attacks.
    """
    candidate_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations=iterations,
        dklen=32
    )
    return hmac.compare_digest(candidate_key.hex(), expected_hash_hex)


# ---------------------------------------------------------------------------
# 2. JSON Web Token (JWT) HS256 Engine
# ---------------------------------------------------------------------------

def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def base64url_decode(data_str: str) -> bytes:
    # Restore padding
    rem = len(data_str) % 4
    if rem > 0:
        data_str += "=" * (4 - rem)
    return base64.urlsafe_b64decode(data_str)


def generate_jwt(payload: Dict[str, Any], secret_key: str, ttl_seconds: int = 3600) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload_copy = dict(payload)
    payload_copy["exp"] = int(time.time()) + ttl_seconds

    header_b64 = base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = base64url_encode(json.dumps(payload_copy, separators=(",", ":")).encode("utf-8"))

    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b64 = base64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def verify_jwt(token: str, secret_key: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    parts = token.split(".")
    if len(parts) != 3:
        return False, None, "Malformed JWT structure"

    header_b64, payload_b64, sig_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    expected_sig = hmac.new(secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()

    try:
        actual_sig = base64url_decode(sig_b64)
    except Exception:
        return False, None, "Invalid base64 signature"

    # Constant-time signature comparison
    if not hmac.compare_digest(expected_sig, actual_sig):
        return False, None, "Signature verification failed (tampered token)"

    payload = json.loads(base64url_decode(payload_b64).decode("utf-8"))
    exp = payload.get("exp", 0)
    if time.time() > exp:
        return False, None, "Token has expired"

    return True, payload, "Valid"


# ---------------------------------------------------------------------------
# 3. Distributed Token Bucket Rate Limiter
# ---------------------------------------------------------------------------

class TokenBucketRateLimiter:
    """
    Token Bucket rate limiter simulating atomic Redis token refills.
    Capacity C: max burst size.
    Refill Rate r: tokens generated per second.
    """
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        # Storage: key -> (current_tokens, last_refill_timestamp)
        self._buckets: Dict[str, Tuple[float, float]] = {}

    def allow_request(self, client_ip: str, current_time: Optional[float] = None) -> bool:
        now = time.time() if current_time is None else current_time
        tokens, last_time = self._buckets.get(client_ip, (self.capacity, now))

        # Refill tokens proportional to elapsed time
        elapsed = max(0.0, now - last_time)
        tokens = min(float(self.capacity), tokens + elapsed * self.refill_rate)

        if tokens >= 1.0:
            tokens -= 1.0
            self._buckets[client_ip] = (tokens, now)
            return True
        else:
            self._buckets[client_ip] = (tokens, now)
            return False


# ---------------------------------------------------------------------------
# 4. Insecure Direct Object Reference (IDOR) Mitigation
# ---------------------------------------------------------------------------

class DocumentRepository:
    def __init__(self):
        # Table: doc_id -> {"id": doc_id, "owner_id": user_id, "data": content}
        self.docs = {
            101: {"id": 101, "owner_id": "USER_ALICE", "data": "Alice Confidential Medical Chart"},
            102: {"id": 102, "owner_id": "USER_BOB", "data": "Bob Tax Assessment Records"}
        }

    def vulnerable_fetch(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """VULNERABLE: Direct object reference without tenant ownership verification."""
        return self.docs.get(doc_id)

    def secure_fetch(self, doc_id: int, authenticated_user_id: str) -> Optional[Dict[str, Any]]:
        """SECURE: Context-bound query enforcing tenant ownership at data layer."""
        doc = self.docs.get(doc_id)
        if not doc or doc["owner_id"] != authenticated_user_id:
            return None  # Denied
        return doc


def test_security_auth_suite():
    print("[TEST 1] Cryptographic Password Hashing with Salt & Constant-Time Check...")
    pwd = "UltraSecurePassword#2026"
    hash_val, salt = hash_password(pwd, iterations=10000)

    # Valid candidate
    assert verify_password(pwd, salt, hash_val, iterations=10000) is True, "Password verification failed on valid secret"
    # Invalid candidate
    assert verify_password("WrongPassword!", salt, hash_val, iterations=10000) is False, "Accepted invalid candidate"
    print("  -> PBKDF2-HMAC-SHA256 password hashing and constant-time match verified.")

    print("[TEST 2] JSON Web Token (JWT) Generation, Signature & Tampering...")
    secret = "production_super_secret_signing_key_4096"
    claims = {"sub": "U42", "role": "STUDENT", "aud": "master-academic-library"}
    jwt_token = generate_jwt(claims, secret, ttl_seconds=3600)

    # Verify valid token
    valid, verified_payload, msg = verify_jwt(jwt_token, secret)
    assert valid is True and verified_payload["sub"] == "U42"
    print(f"  -> Successfully generated & verified HS256 JWT: {jwt_token[:30]}... ({msg})")

    # Tampering test: Attacker alters payload claim from STUDENT to ADMIN
    parts = jwt_token.split(".")
    tampered_payload_dict = {"sub": "U42", "role": "ADMIN", "aud": "master-academic-library", "exp": int(time.time()) + 3600}
    tampered_b64 = base64url_encode(json.dumps(tampered_payload_dict, separators=(",", ":")).encode("utf-8"))
    tampered_token = f"{parts[0]}.{tampered_b64}.{parts[2]}"

    valid_tampered, _, err_msg = verify_jwt(tampered_token, secret)
    assert valid_tampered is False, "Security failure: Tampered token accepted!"
    print(f"  -> Tampering attack successfully trapped: '{err_msg}'")

    print("[TEST 3] Distributed Token Bucket Rate Limiting...")
    limiter = TokenBucketRateLimiter(capacity=3, refill_rate=1.0)  # 3 burst tokens, 1 token/sec
    client_ip = "192.168.1.100"
    base_time = 1000.0

    # Exhaust burst capacity (3 requests)
    assert limiter.allow_request(client_ip, current_time=base_time) is True
    assert limiter.allow_request(client_ip, current_time=base_time) is True
    assert limiter.allow_request(client_ip, current_time=base_time) is True

    # 4th immediate request must be rejected (HTTP 429)
    assert limiter.allow_request(client_ip, current_time=base_time) is False, "Rate limit burst failed to trigger"
    print("  -> Initial 3 burst requests allowed; 4th immediate request successfully rate-limited (HTTP 429).")

    # Advance time by 1.5 seconds: 1 token refilled
    assert limiter.allow_request(client_ip, current_time=base_time + 1.5) is True, "Refill token not granted"
    # Immediate subsequent request rejected
    assert limiter.allow_request(client_ip, current_time=base_time + 1.5) is False
    print("  -> Refill rate (1 token/sec) mathematically verified.")

    print("[TEST 4] Insecure Direct Object Reference (IDOR) Defense...")
    repo = DocumentRepository()
    # Alice attempts to access Bob's document (ID 102)
    leaked_doc = repo.vulnerable_fetch(102)
    assert leaked_doc is not None and leaked_doc["owner_id"] == "USER_BOB", "Vulnerable fetch failed to simulate IDOR"

    # Secure fetch with Alice's identity
    secure_doc = repo.secure_fetch(102, authenticated_user_id="USER_ALICE")
    assert secure_doc is None, "IDOR protection failed: Alice accessed Bob's document!"

    # Secure fetch with Bob's identity
    bob_doc = repo.secure_fetch(102, authenticated_user_id="USER_BOB")
    assert bob_doc is not None and bob_doc["id"] == 102, "Legitimate owner denied access"
    print("  -> IDOR successfully mitigated via context-bound tenant filtering.")

    print("ALL Level 5 Chapter 05 Application Security & Auth lab tests passed successfully!")


if __name__ == "__main__":
    test_security_auth_suite()
