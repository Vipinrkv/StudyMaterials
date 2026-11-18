# LEVEL 1: MODULES 3 & 4 HIGH-YIELD REVISION & FORMULA SHEET

**Subjects Covered:**
- Chapter 06: Algorithms, Flowcharts and Pseudocode
- Chapter 07: Introduction to Operating Systems
- Chapter 08: Networking and How the Internet Works
- Chapter 09: Introduction to Programming and Compilers
- Chapter 10: Digital Literacy, Cyber Hygiene and Computing Ethics

---

## 🧮 1. Algorithmic & Complexity Formulas

### Knuth's 5 Algorithm Criteria:
$$\text{Algorithm} = \{\text{Input}, \text{Output}, \text{Definiteness}, \text{Finiteness}, \text{Effectiveness}\}$$

### Böhm-Jacopini Control Structures:
All computable algorithms are expressible using:
$$\text{Logic} = \text{Sequence} + \text{Selection (IF-THEN-ELSE)} + \text{Iteration (WHILE/FOR)}$$

### Linear Search Complexity:
- Best-case comparisons: $1$ (Target at index 0).
- Worst-case comparisons: $N$ (Target at end or absent).
- Average comparisons: $\approx \frac{N+1}{2}$.

---

## ⚙️ 2. Operating System Scheduling & Metrics

### Key Metrics:
- **Turnaround Time:**
  $$\text{Turnaround Time} = \text{Completion Time} - \text{Arrival Time}$$
- **Waiting Time:**
  $$\text{Waiting Time} = \text{Turnaround Time} - \text{Total CPU Burst Time}$$
- **Round-Robin Scheduling:** Each process receives a fixed slice of CPU time (time quantum $Q$). Preempts and re-queues processes that have remaining burst time.

---

## 🌐 3. Networking Latency & Checksum Formulas

### Network Latencies:
- **Transmission Delay ($D_{trans}$):**
  $$D_{trans} = \frac{L\text{ (Packet size in bits)}}{R\text{ (Bandwidth in bits/second)}}$$
- **Propagation Delay ($D_{prop}$):**
  $$D_{prop} = \frac{d\text{ (Distance in meters)}}{s\text{ (Propagation speed in media, } \approx 2 \times 10^8\text{ m/s)}}$$
- **Total Nodal Latency:**
  $$D_{nodal} = D_{proc} + D_{queue} + D_{trans} + D_{prop}$$

### Checksum & Address Formats:
- **RFC 1071 Checksum:** Sum 16-bit words $\rightarrow$ Fold 32-bit carry to 16 bits $\rightarrow$ Invert bits (One's Complement).
- **MAC Address:** 48 bits (6 bytes, e.g., `6C:40:08:9B:F3:12`).
- **IPv4 Address:** 32 bits (4 bytes, e.g., `192.168.1.1`).
- **IPv6 Address:** 128 bits (16 bytes, e.g., `2404:6800:4009:81b::200e`).

---

## 🔐 4. Cyber Hygiene & Security Mathematics

### Password Information Entropy:
$$H = L \times \log_2(N)$$
- $H$ = Entropy (bits).
- $L$ = Password character length.
- $N$ = Character pool size ($10$ digits, $26$ lower, $52$ alpha, $94$ symbols).
- **Entropy Benchmarks:**
  - $< 40\text{ bits}$: Very weak (cracked in seconds by GPU).
  - $60 - 80\text{ bits}$: Strong.
  - $> 100\text{ bits}$: Military-grade / uncrackable against brute-force.

### Time-Based One-Time Password (TOTP - RFC 6238):
$$\text{Counter } C = \left\lfloor \frac{\text{Current Unix Time}}{30} \right\rfloor$$
$$\text{TOTP} = \text{HMAC-SHA1}(K, C) \pmod{10^6}$$

### The 3-2-1 Backup Rule:
$$\text{Resilience} = 3\text{ Data Copies} + 2\text{ Media Types} + 1\text{ Off-site / Cloud Immutable Replica}$$
