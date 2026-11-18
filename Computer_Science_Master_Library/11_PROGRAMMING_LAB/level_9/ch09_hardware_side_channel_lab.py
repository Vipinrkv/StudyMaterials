"""
Level 9 Programming Lab - Chapter 09: Hardware Side Channels & SCADA Diode
Implements Flush+Reload Cache Covert Channels, DRAM Rowhammer Leakage, and Data Diode Simplex.
"""
import sys
from typing import Dict, List, Optional, Tuple

sys.stdout.reconfigure(encoding="utf-8")

# -------------------------------------------------------------------------
# 1. Flush+Reload Cache Side-Channel Simulator
# -------------------------------------------------------------------------
class CacheTimingSimulator:
    def __init__(self, num_entries: int = 256):
        self.num_entries = num_entries
        self.cache_lines: Dict[int, bool] = {i: False for i in range(num_entries)}

    def flush_all(self) -> None:
        for i in range(self.num_entries):
            self.cache_lines[i] = False  # Evicted to RAM

    def speculative_access(self, secret_byte: int) -> None:
        # Speculatively loads cache line corresponding to secret byte
        if 0 <= secret_byte < self.num_entries:
            self.cache_lines[secret_byte] = True

    def measure_access_latency(self, index: int) -> float:
        # Cache hit: ~15 cycles. Cache miss (DRAM): ~200 cycles
        if self.cache_lines[index]:
            return 15.0
        return 200.0

    def recover_secret(self) -> int:
        best_index = -1
        min_latency = float("inf")
        for i in range(self.num_entries):
            lat = self.measure_access_latency(i)
            if lat < min_latency:
                min_latency = lat
                best_index = i
        return best_index

# -------------------------------------------------------------------------
# 2. DRAM Rowhammer Disturbance Simulator
# -------------------------------------------------------------------------
class DramRowhammerSimulator:
    def __init__(self, initial_charge_fc: float = 100.0, threshold_fc: float = 40.0):
        self.initial_charge = initial_charge_fc
        self.charge = initial_charge_fc
        self.threshold = threshold_fc
        self.leakage_per_activation = 0.0008  # fC per activation

    def hammer(self, activations: int, trr_active: bool = False, trr_interval: int = 50000) -> Tuple[bool, float]:
        self.charge = self.initial_charge
        bit_flipped = False

        for act in range(1, activations + 1):
            self.charge -= self.leakage_per_activation
            if trr_active and act % trr_interval == 0:
                # Target Row Refresh replenishes victim capacitor
                self.charge = self.initial_charge

            if self.charge <= self.threshold:
                bit_flipped = True
                break

        return bit_flipped, self.charge

# -------------------------------------------------------------------------
# 3. Unidirectional Optical Data Diode
# -------------------------------------------------------------------------
class DiodeViolationError(Exception):
    pass

class UnidirectionalDataDiode:
    def __init__(self):
        # Physical transmit laser connected ONLY to receive photodiode
        self.egress_buffer: List[str] = []

    def send_telemetry(self, packet: str) -> None:
        # Forward simplex transmit (Allowed: Plant -> Corporate Historian)
        self.egress_buffer.append(packet)

    def inject_reverse_command(self, command: str) -> None:
        # Reverse path has no physical receiver/transmitter (Physically Blocked)
        raise DiodeViolationError(f"Physical Diode Failure: Reverse ingress packet '{command}' dropped by hardware air-gap.")


def test_cyber_warfare_resilience():
    print("===========================================================================")
    print("HARDWARE SIDE CHANNELS & CRITICAL DEFENSE VERIFICATION TESTBED")
    print("LEVEL 9 LAB - CHAPTER 09")
    print("===========================================================================")

    # 1. Flush+Reload Cache Timing Attack Test
    print("[Test 1/3] Flush+Reload Cache Timing Covert Channel...")
    cache_sim = CacheTimingSimulator(num_entries=256)
    secret_byte = 42

    cache_sim.flush_all()
    cache_sim.speculative_access(secret_byte)

    extracted_byte = cache_sim.recover_secret()
    assert extracted_byte == secret_byte, f"Extracted secret {extracted_byte} must match true secret {secret_byte}"
    print(f"  -> Secret byte '{secret_byte}' recovered with 100% accuracy via L1 cache timing differential.")

    # 2. DRAM Rowhammer Disturbance & TRR Mitigation Test
    print("[Test 2/3] DRAM Rowhammer Disturbance & Hardware TRR Defense...")
    hammer_sim = DramRowhammerSimulator(initial_charge_fc=100.0, threshold_fc=40.0)

    # Hammering without mitigation (100,000 activations)
    flipped, final_charge = hammer_sim.hammer(activations=100_000, trr_active=False)
    assert flipped is True, "100k unmitigated activations must trigger capacitor bit flip"
    print(f"  -> Unmitigated Rowhammer: Bit flip confirmed (Capacitor charge dropped to {final_charge:.1f} fC <= 40.0 fC).")

    # Hammering with Target Row Refresh (TRR enabled every 50,000 activations)
    flipped_trr, charge_trr = hammer_sim.hammer(activations=100_000, trr_active=True, trr_interval=50000)
    assert flipped_trr is False, "TRR must prevent capacitor charge depletion"
    print(f"  -> TRR-Mitigated Rowhammer: Zero bit flips (Charge maintained at {charge_trr:.1f} fC > threshold).")

    # 3. Unidirectional Optical Data Diode Simplex Enforcement
    print("[Test 3/3] SCADA Unidirectional Optical Data Diode Simplex...")
    diode = UnidirectionalDataDiode()

    # Valid egress telemetry
    diode.send_telemetry("TELEMETRY: TURBINE_TEMP=350C, RPM=3600")
    assert len(diode.egress_buffer) == 1
    print("  -> Outbound operational telemetry successfully traversed optical diode.")

    # Reverse command injection attempt
    try:
        diode.inject_reverse_command("PLC_OVERRIDE: TRIP_CIRCUIT_BREAKER")
        assert False, "Reverse injection must be blocked by diode"
    except DiodeViolationError as e:
        print(f"  -> Reverse attack intercepted: {e}")

    print("===========================================================================")
    print("ALL 3 HARDWARE SECURITY & DEFENSE TESTS PASSED (Exit Code 0).")
    print("===========================================================================")

if __name__ == "__main__":
    test_cyber_warfare_resilience()
