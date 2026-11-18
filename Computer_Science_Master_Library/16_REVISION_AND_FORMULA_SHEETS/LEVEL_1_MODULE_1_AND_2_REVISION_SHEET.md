# LEVEL 1: MODULES 1 & 2 HIGH-YIELD REVISION & FORMULA SHEET

**Subjects Covered:**
- Chapter 01: Introduction to Computers and Data
- Chapter 02: How Computer Hardware Works (CPU Architecture & Instruction Cycle)
- Chapter 03: Memory and Storage Hierarchy
- Chapter 04: Binary Number Systems and Data Representation
- Chapter 05: Logic Gates and Boolean Algebra

---

## 🧮 1. Essential Formulas & Mathematics

### Time & Frequency
- **Clock Period ($T$):**
  $$T = \frac{1}{f}$$
  Example: At $4.0\text{ GHz}$, $T = \frac{1}{4 \times 10^9} = 0.25\text{ ns}$.
- **CPU Execution Time:**
  $$\text{CPU Time} = \frac{\text{Instruction Count} \times \text{CPI}}{f} = \text{Instruction Count} \times \text{CPI} \times T$$
  *(CPI = Average Cycles Per Instruction)*
- **Dynamic Power Dissipation:**
  $$P = C \times V^2 \times f$$

### Memory & Addresses
- **Addressable Memory Space:**
  $$\text{Max Addressable Space} = 2^N\text{ bytes}$$
  - $N = 32\text{ bits} \implies 2^{32}\text{ bytes} = 4\text{ GB}$
  - $N = 64\text{ bits} \implies 2^{64}\text{ bytes} \approx 18.4\text{ Exabytes}$
- **Average Memory Access Time (AMAT):**
  $$\text{AMAT} = T_{hit} + (\text{Miss Rate} \times \text{Miss Penalty})$$
  $$\text{AMAT}_{\text{2-Level}} = T_{L1} + M_1 \times (T_{L2} + M_2 \times T_{RAM})$$

### Positional Number Systems
- **Positional Expansion Formula:**
  $$\text{Value} = \sum_{i=-m}^{n-1} d_i \times b^i$$
- **Signed Integer Ranges ($N$ bits, Two's Complement):**
  $$\text{Range} = \left[-2^{N-1}, +2^{N-1} - 1\right]$$
  - 8-bit: $[-128, +127]$
  - 16-bit: $[-32,768, +32,767]$
  - 32-bit: $[-2,147,483,648, +2,147,483,647]$
  - 64-bit: $[-9.22 \times 10^{18}, +9.22 \times 10^{18}]$
- **Two's Complement Algorithm:**
  $$\text{Two's Comp}(X) = \text{NOT}(X) + 1$$

---

## ⚡ 2. Logic Gates & Boolean Algebra Reference

### Master Truth Table
| A | B | NOT A | AND ($A \cdot B$) | OR ($A + B$) | NAND ($\overline{A \cdot B}$) | NOR ($\overline{A + B}$) | XOR ($A \oplus B$) | XNOR ($\overline{A \oplus B}$) |
| :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| 0 | 0 | 1 | 0 | 0 | 1 | 1 | 0 | 1 |
| 0 | 1 | 1 | 0 | 1 | 1 | 0 | 1 | 0 |
| 1 | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0 |
| 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 1 |

### De Morgan's Laws
$$\overline{A \cdot B} = \overline{A} + \overline{B}$$
$$\overline{A + B} = \overline{A} \cdot \overline{B}$$

### Full Adder Boolean Equations
$$\text{Sum } S = A \oplus B \oplus C_{in}$$
$$C_{out} = (A \cdot B) + (C_{in} \cdot (A \oplus B))$$

---

## 🏛️ 3. Memory Hierarchy at a Glance

| Level | Typical Latency | Scaled Human Time (1 cycle = 1s) | Volatile? | Primary Technology |
| :--- | :--- | :--- | :--- | :--- |
| **Registers** | $< 0.5\text{ ns}$ | 1 second | Yes | Flip-Flops in CPU core |
| **L1 Cache** | $\sim 1\text{ ns}$ | 3.3 seconds | Yes | 6T SRAM |
| **L2 Cache** | $\sim 4\text{ ns}$ | 13 seconds | Yes | 6T SRAM |
| **L3 Cache** | $\sim 15 - 20\text{ ns}$ | 50 seconds | Yes | SRAM (Shared die) |
| **Main RAM** | $\sim 60 - 80\text{ ns}$ | 3.3 minutes | Yes | 1T-1C DRAM (DDR5) |
| **NVMe SSD** | $\sim 20 - 50\text{ µs}$ | 23 hours | No | 3D NAND Flash |
| **Mechanical HDD**| $\sim 5 - 12\text{ ms}$ | 12 months | No | Magnetic Platters |
| **Cloud Object** | $> 50 - 150\text{ ms}$ | 5 - 15 years | No | Distributed Disks/Tape |
