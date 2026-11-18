"""
Practical Lab 1.10: Cyber Hygiene, Password Entropy & TOTP Simulator
File: 11_PROGRAMMING_LAB/level_1/ch10_security_tools.py
Author: Computer Science Master Library
Description: Demonstrates mathematical password entropy calculation,
             cryptographic SHA-256 data integrity checks, and TOTP authentication.
"""

import sys
import math
import hashlib
import hmac
import time
import struct
from typing import Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def calculate_password_entropy(password: str) -> Dict[str, Any]:
    """Calculates password entropy in bits and evaluates cracking vulnerability."""
    length = len(password)
    pool_size = 0

    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digits = any(c.isdigit() for c in password)
    has_symbols = any(not c.isalnum() for c in password)

    if has_lower:
        pool_size += 26
    if has_upper:
        pool_size += 26
    if has_digits:
        pool_size += 10
    if has_symbols:
        pool_size += 32

    if pool_size == 0 or length == 0:
        entropy = 0.0
    else:
        entropy = round(length * math.log2(pool_size), 2)

    if entropy < 40:
        strength = "VERY_WEAK (Cracked in seconds)"
    elif 40 <= entropy < 60:
        strength = "MODERATE (Vulnerable to targeted offline cracking)"
    elif 60 <= entropy < 80:
        strength = "STRONG (Safe against standard attacks)"
    else:
        strength = "MILITARY_GRADE (Practically uncrackable)"

    return {
        "password": password,
        "length": length,
        "pool_size": pool_size,
        "entropy_bits": entropy,
        "strength": strength,
    }


def verify_data_integrity(original_data: str, tampered_data: str) -> None:
    """Demonstrates how cryptographic hashes detect single-bit tampering."""
    print("=" * 60)
    print("      CRYPTOGRAPHIC SHA-256 INTEGRITY VERIFICATION")
    print("=" * 60)

    hash1 = hashlib.sha256(original_data.encode("utf-8")).hexdigest()
    hash2 = hashlib.sha256(tampered_data.encode("utf-8")).hexdigest()

    print(f"Original Text : '{original_data}'")
    print(f"SHA-256 Hash  : {hash1}\n")
    print(f"Tampered Text : '{tampered_data}'")
    print(f"SHA-256 Hash  : {hash2}\n")
    print(f"Integrity Intact? : {hash1 == hash2} (Avalanche Effect demonstrated!)")
    print()


def generate_totp_code(secret_key: bytes, time_step: int = 30) -> str:
    """Generates an RFC 6238 compliant 6-digit Time-Based OTP (TOTP)."""
    current_time = int(time.time())
    counter = current_time // time_step

    # Pack counter as 8-byte big-endian integer
    counter_bytes = struct.pack(">Q", counter)

    # Compute HMAC-SHA1
    hmac_hash = hmac.new(secret_key, counter_bytes, hashlib.sha1).digest()

    # Dynamic truncation (RFC 4226)
    offset = hmac_hash[-1] & 0x0F
    code_binary = (
        (struct.unpack(">I", hmac_hash[offset : offset + 4])[0]) & 0x7FFFFFFF
    )

    totp_token = str(code_binary % 1000000).zfill(6)
    return totp_token


if __name__ == "__main__":
    passwords = [
        "password",
        "P@ssw0rd1",
        "correct-horse-battery-staple",
    ]
    print("=" * 60)
    print("        PASSWORD ENTROPY & STRENGTH BENCHMARK")
    print("=" * 60)
    for p in passwords:
        res = calculate_password_entropy(p)
        print(f"Password     : '{res['password']}'")
        print(
            f"Length: {res['length']} | Pool Size: {res['pool_size']} | Entropy: {res['entropy_bits']} bits"
        )
        print(f"Strength     : {res['strength']}\n")

    verify_data_integrity(
        "Transfer ₹5,000 to Account #12345", "Transfer ₹5,000 to Account #12346"
    )

    secret = b"MASTER_LIBRARY_DEMO_KEY_123"
    code = generate_totp_code(secret)
    print("=" * 60)
    print("          TIME-BASED OTP (TOTP 2FA) GENERATOR")
    print("=" * 60)
    print(f"Current Unix Timestamp : {int(time.time())}")
    print(f"Active 6-Digit TOTP    : {code} (Valid for current 30s window)")
    assert len(code) == 6 and code.isdigit(), "Invalid TOTP format!"
    print("TOTP code successfully generated and validated.\n")

    print("All security and digital literacy lab tests passed successfully.")
