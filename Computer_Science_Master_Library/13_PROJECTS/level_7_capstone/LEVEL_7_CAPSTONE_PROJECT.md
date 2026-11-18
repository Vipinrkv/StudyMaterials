# LEVEL 7 CAPSTONE PROJECT: AXIOM FAULT-TOLERANT TRADING & STREAMING ENGINE

---

## 1. EXECUTIVE SUMMARY & ARCHITECTURAL SPECIFICATION

At the frontier of specialist systems engineering, mission-critical infrastructure demands the seamless convergence of four advanced disciplines:
1. **Multi-Decree Consensus & Quorum State Machines:** Replicating transactions across physical server clusters with zero data divergence (Multi-Paxos / Raft).
2. **Ultra-Low-Latency Order Execution & Kernel Bypass Design:** Processing financial limit order book transitions in sub-microseconds with zero heap allocation and lock-free ring buffers (Disruptor pattern).
3. **High-Throughput Stateful Stream Processing:** Event-time windowing, watermarks, and Two-Phase Commit Exactly-Once Semantics (EOS).
4. **Zero-Trust Workload Identity & Cryptographic Policy:** Mutual TLS (mTLS) enforcement with short-lived X.509 SPIFFE/SVID identity validation.

The **Axiom Engine** is an industrial-grade, single-binary distributed high-frequency trading and streaming platform. It unifies:
- A Multi-Paxos consensus group coordinating cluster state transitions and fencing tokens.
- A lock-free Level-3 Limit Order Book executing binary ITCH market data matching.
- A streaming aggregation pipeline calculating rolling event-time VWAP (Volume-Weighted Average Price) with watermark triggers.
- Cryptographic SPIFFE/SVID mutual workload authentication and policy enforcement.

```
+───────────────────────────────────────────────────────────────────────────────+
|                           AXIOM DISTRIBUTED ENGINE                            |
|                                                                               |
|   +─────────────────────────+   +─────────────────────────+   +─────────────+ |
|   |       AxiomNode 1       |   |       AxiomNode 2       |   | AxiomNode 3 | |
|   |       (LEADER)          |<─>|       (FOLLOWER)        |<─>| (FOLLOWER)  | |
|   +─────────────────────────+   +─────────────────────────+   +─────────────+ |
|        │                                                                      |
|        ▼ Replicated Multi-Paxos Consensus Log (Ballots & Fencing Tokens)      |
|   +─────────────────────────────────────────────────────────────────────────+ |
|   |                 Zero-Trust Cryptographic Ingress (mTLS)                 |
|   |  - SPIFFE ID: spiffe://axiom.trading/hft/gateway                        |
|   |  - Ephemeral X.509 SVID Validation with Automated Expiry Rejection      |
|   +─────────────────────────────────────────────────────────────────────────+ |
|        │                                                                      |
|        ▼ Lock-Free LMAX Disruptor Ring Buffer                                 |
|   +─────────────────────────────────────────────────────────────────────────+ |
|   |                   Level-3 Limit Order Matching Engine                   |
|   |  - Pre-allocated price level arrays; zero dynamic allocations           |
|   |  - FIFO price-time priority execution                                   |
|   +─────────────────────────────────────────────────────────────────────────+ |
|        │                                                                      |
|        ▼ Event-Time Stream Analytics Engine                                   |
|   +─────────────────────────────────────────────────────────────────────────+ |
|   |                   Rolling Event-Time VWAP Aggregator                    |
|   |  - Watermark generation (T_max - delta) handling out-of-order ticks     |
|   |  - Two-Phase Commit (2PC) Exactly-Once transactional sink               |
|   +─────────────────────────────────────────────────────────────────────────+ |
+───────────────────────────────────────────────────────────────────────────────+
```

---

## 2. COMPONENT SPECIFICATIONS & CONTRACTS

1. **`AxiomPaxosCoordinator`:**
   - Multi-decree ballot numbering, Phase 1 stable leader acquisition, and 1 RTT Phase 2 writes.
   - Issues generation fencing tokens to prevent zombie leader split-brain writes.
2. **`AxiomOrderBook`:**
   - Level-3 limit order book tracking bids and asks with deterministic Best Bid and Offer (BBO).
   - Zero-allocation binary ITCH protocol parser.
3. **`AxiomStreamAnalytics`:**
   - Ingests trade ticks, tracks event time, computes bounded out-of-order watermarks.
   - Calculates rolling Volume-Weighted Average Price: $\text{VWAP} = \frac{\sum (P_i \times V_i)}{\sum V_i}$.
   - Flushes results via Two-Phase Commit (2PC) guaranteeing Exactly-Once Semantics.
4. **`AxiomSecurityGateway`:**
   - Validates client SPIFFE X.509 SVIDs and enforces role-based access control.

---

## 3. VERIFICATION & VALIDATION PROTOCOL

The test verifier (`axiom_verifier.py`) conducts 6 comprehensive integration test suites:
1. **Consensus Quorum & Leader Election:** Multi-Paxos leadership acquisition with quorum promises.
2. **Split-Brain Fencing Token Enforcement:** Proving obsolete leader writes are unconditionally rejected.
3. **Level-3 Order Book & BBO Matching:** Adding and executing bids and asks with zero price leakage.
4. **Lock-Free Disruptor Ring Execution:** Bitwise power-of-two sequence wrapping under load.
5. **Streaming Watermark VWAP & Exactly-Once Semantics:** Out-of-order trade aggregation and 2PC commit.
6. **Zero-Trust SPIFFE Identity & mTLS Authorization:** Validating authentic SVIDs and denying rogue callers.
