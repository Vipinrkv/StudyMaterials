"""
Practical Lab 1.8: Network Protocols, DNS Resolver & TCP Handshake Simulator
File: 11_PROGRAMMING_LAB/level_1/ch08_network_sim.py
Author: Computer Science Master Library
Description: Simulates DNS hierarchical name resolution, packet checksum
             verification, and the TCP 3-way handshake state machine.
"""

import sys
from typing import Dict

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


class DNSResolverSimulator:

    def __init__(self):
        self.cache: Dict[str, str] = {}
        self.authoritative_zone: Dict[str, str] = {
            "google.com": "142.250.190.46",
            "github.com": "140.82.121.4",
            "wikipedia.org": "208.80.154.224",
            "bharatconnect.in": "103.14.120.5",
        }

    def resolve(self, domain: str) -> str:
        domain = domain.lower()
        print(f"[DNS Lookup] Request for: '{domain}'")
        if domain in self.cache:
            print(f"  --> CACHE HIT: Found IP {self.cache[domain]} in local cache.")
            return self.cache[domain]

        print("  --> CACHE MISS: Querying Authoritative Root & TLD servers...")
        if domain in self.authoritative_zone:
            resolved_ip = self.authoritative_zone[domain]
            self.cache[domain] = resolved_ip
            print(f"  --> RESOLVED: {domain} -> {resolved_ip} (Saved to cache)\n")
            return resolved_ip
        else:
            raise ValueError(f"NXDOMAIN: Domain '{domain}' does not exist.")


class TCPHandshakeSimulator:

    def __init__(self):
        self.state: str = "CLOSED"

    def perform_handshake(
        self, client_ip: str, server_ip: str, port: int = 443
    ) -> bool:
        print("=" * 60)
        print(
            f"   INITIATING TCP 3-WAY HANDSHAKE: {client_ip} -> {server_ip}:{port}"
        )
        print("=" * 60)

        # Step 1: Client sends SYN
        client_seq = 1000
        print(
            f"Step 1 [Client -> Server]: Flag=SYN, Client_Seq={client_seq}, Port={port}"
        )
        self.state = "SYN_SENT"

        # Step 2: Server responds SYN-ACK
        server_seq = 5000
        server_ack = client_seq + 1
        print(
            f"Step 2 [Server -> Client]: Flag=SYN-ACK, Server_Seq={server_seq}, ACK_Num={server_ack}"
        )
        self.state = "SYN_RECEIVED"

        # Step 3: Client acknowledges with ACK
        client_ack = server_seq + 1
        print(
            f"Step 3 [Client -> Server]: Flag=ACK, Seq={server_ack}, ACK_Num={client_ack}"
        )
        self.state = "ESTABLISHED"

        print(
            f"--> TCP CONNECTION ESTABLISHED: Socket ({client_ip} <-> {server_ip}:{port})\n"
        )
        return True


def compute_internet_checksum(words: list[int]) -> int:
    """Computes RFC 1071 16-bit Internet Checksum over a list of 16-bit words."""
    checksum_sum = sum(words)
    while (checksum_sum >> 16) > 0:
        checksum_sum = (checksum_sum & 0xFFFF) + (checksum_sum >> 16)
    return (~checksum_sum) & 0xFFFF


if __name__ == "__main__":
    # Test 1: DNS Resolution & Caching
    dns = DNSResolverSimulator()
    ip1 = dns.resolve("google.com")
    ip2 = dns.resolve("google.com")
    assert ip1 == "142.250.190.46" and ip2 == ip1

    # Test 2: TCP 3-Way Handshake
    tcp = TCPHandshakeSimulator()
    success = tcp.perform_handshake("192.168.1.15", ip1, port=443)
    assert success is True and tcp.state == "ESTABLISHED"

    # Test 3: Checksum verification
    test_words = [0x4500, 0x003C]
    calculated_cs = compute_internet_checksum(test_words)
    print(f"Calculated 16-bit Checksum: 0x{calculated_cs:04X}")
    assert calculated_cs == 0xBAC3, (
        f"Expected 0xBAC3, got 0x{calculated_cs:04X}"
    )

    total = sum(test_words) + calculated_cs
    while (total >> 16) > 0:
        total = (total & 0xFFFF) + (total >> 16)
    assert total == 0xFFFF, "Checksum verification failed!"
    print("Checksum mathematically verified (folded sum = 0xFFFF).")

    print("\nAll network simulation tests verified successfully.")
