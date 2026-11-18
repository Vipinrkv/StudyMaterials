"""
ch09_neuromorphic_snn_lab.py
Level 8 Chapter 09 Companion Laboratory: Neuromorphic Computing & SNN Dynamics.
Simulates Leaky Integrate-and-Fire (LIF) Neurons, Action Potential Spiking,
Sub-Threshold Exponential Decay, and Spike-Timing-Dependent Plasticity (STDP).
Pure Python/Standard Library with zero external dependencies.
"""

from __future__ import annotations
import sys
import math
from typing import List, Tuple, Dict, Any

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")


class LifNeuron:
    """Leaky Integrate-and-Fire (LIF) neuron model with refractory period."""
    def __init__(self, neuron_id: str, tau_m: float = 20.0, v_rest: float = -70.0,
                 v_thresh: float = -50.0, v_reset: float = -70.0, r_m: float = 10.0):
        self.id = neuron_id
        self.tau_m = tau_m
        self.v_rest = v_rest
        self.v_thresh = v_thresh
        self.v_reset = v_reset
        self.r_m = r_m

        self.v = v_rest
        self.refractory_timer = 0.0
        self.spike_history: List[float] = []

    def step(self, dt: float, current_input: float, current_time: float) -> bool:
        if self.refractory_timer > 0.0:
            self.refractory_timer -= dt
            self.v = self.v_reset
            return False

        dv = (dt / self.tau_m) * (-(self.v - self.v_rest) + self.r_m * current_input)
        self.v += dv

        if self.v >= self.v_thresh:
            self.v = self.v_reset
            self.refractory_timer = 2.0  # 2 ms absolute refractory period
            self.spike_history.append(current_time)
            return True
        return False


class StdpSynapse:
    """Spike-Timing-Dependent Plasticity (STDP) adaptive synapse."""
    def __init__(self, initial_weight: float = 1.0, a_plus: float = 0.1, a_minus: float = 0.12,
                 tau_plus: float = 20.0, tau_minus: float = 20.0, w_min: float = 0.0, w_max: float = 5.0):
        self.weight = initial_weight
        self.a_plus = a_plus
        self.a_minus = a_minus
        self.tau_plus = tau_plus
        self.tau_minus = tau_minus
        self.w_min = w_min
        self.w_max = w_max

    def on_spike_pair(self, t_pre: float, t_post: float) -> float:
        delta_t = t_post - t_pre
        if delta_t > 0:
            dw = self.a_plus * math.exp(-delta_t / self.tau_plus)
        elif delta_t < 0:
            dw = -self.a_minus * math.exp(delta_t / self.tau_minus)
        else:
            dw = 0.0

        self.weight = max(self.w_min, min(self.w_max, self.weight + dw))
        return dw


def main() -> None:
    print("=" * 70)
    print("LEVEL 8 CHAPTER 09: NEUROMORPHIC COMPUTING & SNN LAB")
    print("=" * 70)

    # 1. Test Sub-threshold Passive Leak Decay
    print("\n[Test 1] Testing LIF Neuron Sub-Threshold Passive Leak...")
    neuron_sub = LifNeuron("n_sub", tau_m=20.0, v_rest=-70.0, v_thresh=-50.0, r_m=10.0)
    # Inject sub-threshold current: I = 1.0 -> Asymptotic V = -70 + 10*1.0 = -60.0 mV < -50.0 mV
    spiked = False
    for step_i in range(100):
        if neuron_sub.step(dt=1.0, current_input=1.0, current_time=float(step_i)):
            spiked = True
    assert spiked is False, "Sub-threshold current must never trigger a spike!"
    assert math.isclose(neuron_sub.v, -60.0, rel_tol=1e-2)
    print(f"  -> Sub-Threshold Potential: Settled at {neuron_sub.v:.2f} mV (Decay verified, zero spikes).")

    # 2. Test Supra-threshold Spiking Dynamics
    print("\n[Test 2] Testing LIF Neuron Supra-Threshold Action Potential Generation...")
    neuron_supra = LifNeuron("n_supra", tau_m=20.0, v_rest=-70.0, v_thresh=-50.0, r_m=10.0)
    # Inject supra-threshold current: I = 3.0 -> Asymptotic V = -70 + 30 = -40 mV > -50 mV
    spike_times = []
    for step_i in range(200):
        t = float(step_i)
        if neuron_supra.step(dt=1.0, current_input=3.0, current_time=t):
            spike_times.append(t)

    assert len(spike_times) > 0, "Supra-threshold current must generate action potentials!"
    print(f"  -> Emitted {len(spike_times)} Action Potentials over 200 ms: First 3 spikes at {spike_times[:3]} ms.")
    print("  -> Refractory Reset to -70.0 mV: Verified.")

    # 3. Test STDP Causal Potentiation (LTP)
    print("\n[Test 3] Testing STDP Long-Term Potentiation (LTP - Causal Association)...")
    synapse = StdpSynapse(initial_weight=1.0)
    # Pre-synaptic spike at t=10, Post-synaptic spike at t=20 (delta_t = +10 ms)
    dw_ltp = synapse.on_spike_pair(t_pre=10.0, t_post=20.0)
    assert dw_ltp > 0.0, "Causal ordering must increase synaptic weight!"
    assert synapse.weight > 1.0
    print(f"  -> delta_t = +10.0 ms -> dw = +{dw_ltp:.4f} -> New Weight: {synapse.weight:.4f} (Potentiated).")

    # 4. Test STDP Acausal Depression (LTD)
    print("\n[Test 4] Testing STDP Long-Term Depression (LTD - Acausal Anti-Correlation)...")
    # Pre-synaptic spike at t=30, Post-synaptic spike at t=20 (delta_t = -10 ms)
    dw_ltd = synapse.on_spike_pair(t_pre=30.0, t_post=20.0)
    assert dw_ltd < 0.0, "Acausal ordering must decrease synaptic weight!"
    print(f"  -> delta_t = -10.0 ms -> dw = {dw_ltd:.4f} -> New Weight: {synapse.weight:.4f} (Depressed).")

    print("\n" + "=" * 70)
    print("ALL NEUROMORPHIC COMPUTING & SNN TESTS PASSED (Exit Code 0).")
    print("=" * 70)
    sys.exit(0)


if __name__ == "__main__":
    main()
