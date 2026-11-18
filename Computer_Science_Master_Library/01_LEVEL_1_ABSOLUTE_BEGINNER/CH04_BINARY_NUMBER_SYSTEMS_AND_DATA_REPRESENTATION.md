# CHAPTER 04: BINARY NUMBER SYSTEMS AND DATA REPRESENTATION

---

## 1. Chapter Introduction
Have you ever wondered how a YouTube video, a high-resolution selfie, a WhatsApp voice note, or a bank balance of ₹50,000 can all exist inside a computer as nothing more than an endless stream of `0`s and `1`s?

In this chapter, we crack the foundational code of computing: **Binary Number Systems and Digital Data Representation**. We will master conversions between Decimal, Binary, Octal, and Hexadecimal, uncover why modern processors use **Two's Complement** for negative numbers, understand why `0.1 + 0.2` does not equal `0.3` in Python or JavaScript (the **IEEE 754 Floating-Point standard**), and see how text, emojis, audio, and images are converted into electrical bits.

---

## 2. Why Should I Learn This?
- **Prevent Catastrophic Software Bugs:** Integer overflows have caused rocket explosions (Ariane 5 flight 501), crashed stock markets, and broke YouTube's view counter on the *Gangnam Style* video.
- **Master Memory & Network Optimization:** Hexadecimal and bitwise manipulation allow systems engineers to pack 8 boolean flags into a single byte, reducing cloud data transfer costs by millions of dollars.
- **Core Interview Requirement:** Every technical interview at companies like Google, Microsoft, and Amazon tests bitwise arithmetic, masking, and numerical precision.

---

## 3. Everyday-Life Example
### The Light Switches & Odometer Analogy
Imagine a hallway with 8 ordinary wall light switches in a row:
- Each switch can only be **DOWN (OFF = 0)** or **UP (ON = 1)**.
- If all switches are DOWN: `00000000` (Value = 0).
- If only the rightmost switch is UP: `00000001` (Value = 1).
- If the second switch is UP and the first is DOWN: `00000010` (Value = 2).

Now think of your car or scooter's mechanical **odometer** (the distance counter):
- When the rightmost digit reaches its maximum symbol (`9`) and you roll forward one more kilometer, it wraps around to `0` and triggers a **carry** to the next wheel to the left: $09 \rightarrow 10$.
- Binary operates identically, except its maximum symbol is `1` instead of `9`!
  $$00 \rightarrow 01 \rightarrow 10 \rightarrow 11 \rightarrow 100$$

---

## 4. Industry Example
### The Ariane 5 Rocket Failure & The YouTube 32-Bit Overflow
1. **The Ariane 5 Explosion (1996):**
   Thirty-seven seconds after liftoff, the European Space Agency's $500,000,000 Ariane 5 rocket veered off course and self-destructed. The post-mortem inquiry revealed that guidance software attempted to convert a 64-bit floating-point velocity measurement into a 16-bit signed integer. The measured number ($32,768$) was larger than the maximum value a 16-bit signed integer can hold ($+32,767$). The CPU triggered an unhandled hardware overflow exception, causing the flight computer to crash and the rocket to veer out of control.
2. **YouTube Gangnam Style Integer Overflow (2014):**
   YouTube originally stored video view counts as a signed **32-bit integer**. The maximum positive number a signed 32-bit integer can store is:
   $$2^{31} - 1 = 2,147,483,647$$
   When Psy's *Gangnam Style* music video hit 2,147,483,648 views, the number rolled over into negative numbers, displaying `-2,147,483,648` views! Google was forced to immediately rewrite their database infrastructure to use signed **64-bit integers** ($2^{63} - 1 \approx 9.22\text{ quintillion}$ views).

---

## 5. Prerequisites
- Basic elementary arithmetic (addition, subtraction, multiplication, division).
- Completion of **Chapter 01: Introduction to Computers and Data**.

---

## 6. Basic Explanation
Human beings use the **Decimal (Base-10)** system because we were born with 10 fingers. We count using ten distinct digits:
$$0, 1, 2, 3, 4, 5, 6, 7, 8, 9$$

Computers do not have 10 fingers; they are built from silicon transistors that operate as electronic switches. A switch is either conducting electricity (High Voltage = `1`) or not conducting (Low Voltage = `0`). Therefore, computers use the **Binary (Base-2)** system.

To make long binary strings easier for human engineers to read, we group bits into:
- **Octal (Base-8):** Groups of 3 bits ($2^3 = 8$). Uses digits $0$ to $7$.
- **Hexadecimal (Base-16):** Groups of 4 bits ($2^4 = 16$). Uses digits $0$ to $9$ and letters $A$ to $F$.

---

## 7. Detailed Technical Explanation

### 7.1 Positional Number Systems
In any positional number system with base $b$, the value of a number is determined by summing each digit $d_i$ multiplied by the base raised to its position power $b^i$:
$$\text{Value} = \sum_{i=-m}^{n-1} d_i \times b^i$$

#### Decimal (Base-10):
The number $752_{10}$ means:
$$752 = (7 \times 10^2) + (5 \times 10^1) + (2 \times 10^0) = 700 + 50 + 2 = 752$$

#### Binary (Base-2):
The binary number $1101_2$ means:
$$1101_2 = (1 \times 2^3) + (1 \times 2^2) + (0 \times 2^1) + (1 \times 2^0)$$
$$= (1 \times 8) + (1 \times 4) + (0 \times 2) + (1 \times 1) = 8 + 4 + 0 + 1 = 13_{10}$$

#### Hexadecimal (Base-16):
Since base-16 requires 16 unique symbols, we use:
$$0, 1, 2, 3, 4, 5, 6, 7, 8, 9, A(10), B(11), C(12), D(13), E(14), F(15)$$
The hexadecimal number $2F_{16}$ means:
$$2F_{16} = (2 \times 16^1) + (15 \times 16^0) = 32 + 15 = 47_{10}$$

```
+---------------+---------------+---------------+--------------------+
|  Decimal (10) |   Binary (2)  |   Octal (8)   |  Hexadecimal (16)  |
+---------------+---------------+---------------+--------------------+
|       0       |     0000      |       0       |         0          |
|       1       |     0001      |       1       |         1          |
|       2       |     0010      |       2       |         2          |
|       3       |     0011      |       3       |         3          |
|       4       |     0100      |       4       |         4          |
|       5       |     0101      |       5       |         5          |
|       6       |     0110      |       6       |         6          |
|       7       |     0111      |       7       |         7          |
|       8       |     1000      |      10       |         8          |
|       9       |     1001      |      11       |         9          |
|      10       |     1010      |      12       |         A          |
|      11       |     1011      |      13       |         B          |
|      12       |     1100      |      14       |         C          |
|      13       |     1101      |      15       |         D          |
|      14       |     1110      |      16       |         E          |
|      15       |     1111      |      17       |         F          |
+---------------+---------------+---------------+--------------------+
```

### 7.2 Conversions Across Bases

#### 1. Decimal to Binary (Successive Division by 2)
Convert $53_{10}$ to Binary:
- $53 \div 2 = 26 \text{ remainder } \mathbf{1} \quad (\text{LSB - Least Significant Bit})$
- $26 \div 2 = 13 \text{ remainder } \mathbf{0}$
- $13 \div 2 = 6 \text{ remainder } \mathbf{1}$
- $6 \div 2 = 3 \text{ remainder } \mathbf{0}$
- $3 \div 2 = 1 \text{ remainder } \mathbf{1}$
- $1 \div 2 = 0 \text{ remainder } \mathbf{1} \quad (\text{MSB - Most Significant Bit})$

Reading remainders from bottom to top:
$$53_{10} = \mathbf{110101}_2$$

#### 2. Hexadecimal to Binary (4-Bit Nibble Substitution)
Because $16 = 2^4$, every hexadecimal digit corresponds **exactly** to a 4-bit binary nibble!
Convert $0x\text{A7E}_{16}$ to Binary:
- $\text{A}_{16} = 1010_2$
- $7_{16} = 0111_2$
- $\text{E}_{16} = 1110_2$
- Concatenate: $0x\text{A7E} = \mathbf{1010\ 0111\ 1110}_2$

### 7.3 Representing Negative Numbers: Two's Complement
How do we represent negative numbers like $-5$ when hardware only understands `0` and `1`?

#### Attempt 1: Sign-Magnitude
Reserve the leftmost bit for sign: $0 = \text{Positive}$, $1 = \text{Negative}$.
- $+5 = 00000101_2$
- $-5 = 10000101_2$
- **Fatal Flaw:** There are two representations for zero: $+0 = 00000000$ and $-0 = 10000000$. Furthermore, regular hardware addition fails:
  $$5 + (-5) = 00000101 + 10000101 = 10001010_2 = -10 \quad (\text{WRONG!})$$

#### Attempt 2: One's Complement
Invert every bit ($0 \rightarrow 1$, $1 \rightarrow 0$).
- $+5 = 00000101_2 \implies -5 = 11111010_2$
- **Still Flawed:** Still has two zeroes ($00000000$ and $11111111$) and requires end-around carry logic.

#### The Universal Solution: Two's Complement
To find the Two's Complement of a negative number:
1. Write the positive number in binary.
2. Invert all bits (One's Complement).
3. Add $1$ to the result.

**Example: Find $-5$ in 8-bit Two's Complement:**
- Step 1: $+5 = 00000101_2$
- Step 2 (Invert): $11111010_2$
- Step 3 (Add 1): $11111010 + 1 = \mathbf{11111011}_2$

**The Miracle of Two's Complement:**
Let us test hardware addition: $5 + (-5)$:
$$\begin{array}{r@{\quad}l}
  00000101 & (+5) \\
+ 11111011 & (-5) \\
\hline
(1)00000000 & (\text{Carry bit discarded} \implies 00000000_2 = 0!)
\end{array}$$
It yields exactly zero! The ALU does not need separate subtraction circuitry; it simply negates the subtrahend using Two's Complement and adds it using the exact same hardware adder!

### 7.4 Floating-Point Numbers & IEEE 754 Standard
How do computers represent decimal fractions like $3.14159$ or $0.00045$?
In modern hardware, real numbers follow the **IEEE 754 standard**:

```
+-------+-------------------------+-----------------------------------+
| Sign  |        Exponent         |      Fraction / Mantissa          |
| 1 bit |   8 bits (Single)       |    23 bits (Single Precision)     |
| 1 bit |   11 bits (Double)      |    52 bits (Double Precision)     |
+-------+-------------------------+-----------------------------------+
```
The value is computed as:
$$V = (-1)^{\text{Sign}} \times (1 + \text{Mantissa}) \times 2^{(\text{Exponent} - \text{Bias})}$$

#### Why does `0.1 + 0.2 != 0.3` in Python/JavaScript?
In base-10, the fraction $\frac{1}{3} = 0.333333\dots$ has an infinite repeating decimal and cannot be represented cleanly.
Similarly, in base-2 (binary), the fractions $\frac{1}{10} = 0.1$ and $\frac{2}{10} = 0.2$ are **infinite repeating binary fractions**:
$$0.1_{10} = 0.0001100110011001100110011\dots_2$$
Because a 64-bit float has only 52 bits of mantissa, the computer must round and truncate:
- $0.1 \rightarrow 0.100000000000000005551115123126$
- $0.2 \rightarrow 0.200000000000000022204460492503$
- $0.1 + 0.2 = \mathbf{0.300000000000000044408920985006}$
In financial and banking applications, engineers never use standard floats; they use fixed-point `Decimal` libraries to avoid accumulating fractional rounding errors!

### 7.5 Character Encoding: From ASCII to Unicode (UTF-8)
1. **ASCII (American Standard Code for Information Interchange):**
   - 7-bit encoding ($2^7 = 128$ symbols).
   - Maps English letters, numbers, and symbols: `'A' = 65 (01000001_2)`, `'a' = 97`, `'0' = 48`, `' ' = 32`.
   - **Problem:** Cannot represent Hindi, Arabic, Japanese, accents, or emojis!
2. **Unicode Standard:**
   - Universal character set assigning a unique number called a **Code Point** to every character in every human language, plus emojis.
   - Example: `'A' \rightarrow \text{U+0041}`; Sanskrit `'अ'` $\rightarrow \text{U+0905}$; Laughing Emoji `'😂'` $\rightarrow \text{U+1F602}$.
3. **UTF-8 (Variable-Length Encoding):**
   - The undisputed standard of the web (>98% of all websites).
   - Backwards-compatible with ASCII: English ASCII characters take exactly **1 byte**.
   - European and Indic characters take **2 to 3 bytes**.
   - Emojis and historic scripts take **4 bytes**.

---

## 8. Important Terminology
- **Bit:** Smallest binary digit (`0` or `1`).
- **Nibble:** A cluster of 4 bits; corresponds to exactly one hexadecimal digit.
- **Byte (Octet):** A cluster of 8 bits ($0\text{ to }255$ unsigned).
- **Most Significant Bit (MSB):** The leftmost bit with the highest positional weight.
- **Least Significant Bit (LSB):** The rightmost bit with the lowest positional weight ($2^0$).
- **Radix (Base):** The number of unique digits available in a positional numbering system.
- **Two's Complement:** Standard mathematical encoding for signed integers in digital processors.
- **Integer Overflow:** An arithmetic condition occurring when a calculation exceeds the maximum representable value of a register.
- **IEEE 754:** Global IEEE standard for representing floating-point real numbers in hardware.
- **Mantissa (Significand):** The fractional part of a floating-point number.
- **Unicode Code Point:** The unique hexadecimal number assigned to a character or emoji (e.g., `U+1F600`).
- **UTF-8:** Variable-width byte encoding format for Unicode characters.

---

## 9. Diagrams and Illustrations
### How Text and Emojis are Encoded into Binary Bytes

```
Character:      'A'                   'अ' (Devanagari)             '🚀' (Rocket)
Code Point:    U+0041                    U+0905                      U+1F680
UTF-8 Bytes:   1 Byte                    3 Bytes                     4 Bytes
Hex Bytes:       41                     E0 A4 85                   F0 9F 9A 80
Binary:      01000001             11100000 10100100 10000101     11110000 10011111 10011010 10000000
```

---

## 10. Step-by-Step Examples

### Example 4.1: Converting Decimal to Hexadecimal and Octal
Convert $437_{10}$ into Octal (Base-8) and Hexadecimal (Base-16):

1. **Decimal to Octal (Divide by 8):**
   - $437 \div 8 = 54 \text{ remainder } \mathbf{5} \quad (\text{LSB})$
   - $54 \div 8 = 6 \text{ remainder } \mathbf{6}$
   - $6 \div 8 = 0 \text{ remainder } \mathbf{6} \quad (\text{MSB})$
   - Read bottom-to-top: $437_{10} = \mathbf{665}_8$

2. **Decimal to Hexadecimal (Divide by 16):**
   - $437 \div 16 = 27 \text{ remainder } \mathbf{5} \quad (\text{LSB})$
   - $27 \div 16 = 1 \text{ remainder } \mathbf{11} \implies \mathbf{B}$
   - $1 \div 16 = 0 \text{ remainder } \mathbf{1} \quad (\text{MSB})$
   - Read bottom-to-top: $437_{10} = \mathbf{1B5}_{16}$

3. **Verification via Binary Nibble Expansion:**
   - Hex $1B5_{16} \implies 0001\ 1011\ 0101_2$
   - Group into 3 bits from right for Octal:
     $$(000)\ (110)\ (110)\ (101)_2 \implies 0\ 6\ 6\ 5_8 = \mathbf{665}_8 \quad (\text{VERIFIED!})$$

---

## 11. Practical Implementation
Let us write a comprehensive Python tool to demonstrate base conversions, Two's complement bit extraction, and IEEE 754 float inspection.

```python
"""
Practical Lab 1.4: Number Systems, Two's Complement, and Encoding Inspector
File: 11_PROGRAMMING_LAB/level_1/number_converter.py
Author: Computer Science Master Library
Description: Demonstrates binary, octal, hexadecimal conversions,
             signed 8-bit Two's complement arithmetic, and UTF-8 encoding.
"""

import struct


def inspect_integer(n: int, bits: int = 8) -> None:
    """Displays representation of a number across bases and 2's complement."""
    print(f"--- Integer Inspection: {n} (Target: {bits}-bit) ---")
    if 0 <= n < (1 << bits):
        print(f"Decimal (Unsigned) : {n}")
        print(f"Binary             : {bin(n)[2:].zfill(bits)}")
        print(f"Octal              : {oct(n)}")
        print(f"Hexadecimal        : {hex(n).upper()}")

    # Two's complement calculation for signed integers
    min_val = -(1 << (bits - 1))
    max_val = (1 << (bits - 1)) - 1
    if min_val <= n <= max_val:
        # Mask with (2^bits - 1) to get Two's complement bit pattern
        twos_comp = n & ((1 << bits) - 1)
        binary_str = bin(twos_comp)[2:].zfill(bits)
        print(f"Signed {bits}-bit Range: [{min_val} to {max_val}]")
        print(f"Two's Comp Binary  : {binary_str}")
        print(f"Two's Comp Hex     : 0x{twos_comp:02X}")
    else:
        print(
            f"OVERFLOW WARNING: {n} cannot fit in signed {bits}-bit integer!"
        )
    print()


def inspect_float_precision() -> None:
    """Demonstrates IEEE 754 precision quirk and bit layout."""
    print("--- IEEE 754 Floating-Point Precision Inspection ---")
    a = 0.1
    b = 0.2
    c = a + b
    print(f"0.1 + 0.2 == 0.3 ?  Result: {c == 0.3}")
    print(f"Actual computed sum : {c:.30f}")
    print(f"Theoretical 0.3     : {0.3:.30f}")

    # Inspect exact IEEE 754 32-bit single precision bits for 0.1
    float_bytes = struct.pack(">f", 0.1)  # Big-endian float
    bits_str = "".join(f"{byte:08b}" for byte in float_bytes)
    sign = bits_str[0]
    exponent = bits_str[1:9]
    mantissa = bits_str[9:]
    print(f"\nIEEE 754 32-bit Float Representation of 0.1:")
    print(
        f"Sign bit (1): {sign} | Exponent (8): {exponent} | Mantissa (23): {mantissa}\n"
    )


def inspect_utf8_string(text: str) -> None:
    """Inspects UTF-8 byte representation of multilingual text and emojis."""
    print(f"--- UTF-8 Character Encoding Inspector for: '{text}' ---")
    for char in text:
        code_point = f"U+{ord(char):04X}"
        utf8_bytes = char.encode("utf-8")
        hex_bytes = " ".join(f"{b:02X}" for b in utf8_bytes)
        bin_bytes = " ".join(f"{b:08b}" for b in utf8_bytes)
        print(f"Char: '{char}' | Code Point: {code_point:<8} | Bytes ({len(utf8_bytes)}): {hex_bytes:<12} | Bits: {bin_bytes}")
    print()


if __name__ == "__main__":
    inspect_integer(42, bits=8)
    inspect_integer(-42, bits=8)
    inspect_float_precision()
    inspect_utf8_string("Hi अ 🚀")
```

---

## 12. Industry Implementation
### Network Protocols & Hardware Packets (Binary Bitfields)
In production networking (e.g., TCP/IP packets traveling across Cisco or Juniper routers):
- A standard **IPv4 packet header** cannot waste space sending human-readable text like `Version: 4`.
- Instead, engineers use raw binary bitfields:
  - Bits 0–3: IP Version (`0100` for IPv4, `0110` for IPv6).
  - Bits 4–7: Internet Header Length (IHL).
  - Bits 8–15: Type of Service (QoS priorities).
  - Bits 16–31: Total Length (16-bit integer holding packet byte count).
Because network bandwidth is expensive, packing binary data at the individual bit level enables routers to process billions of packets per second purely through hardware shift registers.

---

## 13. Advantages and Limitations
### Advantages of Binary & Hexadecimal
1. **Unambiguous Noise Margin:** High/Low voltage logic guarantees high signal fidelity in silicon.
2. **Compact Human Notation:** Hexadecimal condenses long binary strings by a factor of 4 ($11111111_2 \rightarrow \text{FF}_{16}$).
3. **Unified Arithmetic Hardware:** Two's complement eliminates the need for separate subtraction circuits in the CPU ALU.

### Limitations & Trade-Offs
1. **Inherent Floating-Point Rounding Error:** Numbers with non-terminating binary representations cannot be represented with infinite precision in finite bits.
2. **Human Inaccessibility:** Binary and hex are unnatural for human calculation, requiring translation layers in compilers and runtimes.

---

## 14. Common Mistakes
1. **Assuming Positive and Negative Ranges are Symmetric in Two's Complement:**
   In an 8-bit signed integer, the range is **$-128$ to $+127$**, NOT $-128$ to $+128$! Because `0` is treated as non-negative, there is one more negative number than positive numbers.
2. **Confusing Character Codes with Numerical Values:**
   The character `'5'` is NOT the integer `5`. In ASCII/Unicode, the character `'5'` has decimal code $53$ ($00110101_2$).
3. **Using Standard Floating-Point for Financial Transactions:**
   Writing `price = 19.99` using `float` types in Java, Python, or C++ will eventually accumulate rounding discrepancies that corrupt accounting balances. Always use `BigDecimal` or store values in smallest integer units (e.g., paisa or cents).

---

## 15. AI Connection
### Quantization in Large Language Models (FP32 $\rightarrow$ INT4)
Training a massive AI model like LLaMA-3 requires **FP16 (16-bit floating point)** or **BF16 (Bfloat16)** parameters.
- A 70-billion parameter model in 16-bit float requires:
  $$70 \times 10^9 \times 2\text{ bytes} = 140\text{ Gigabytes of VRAM}$$
- Through **Model Quantization**, AI researchers mathematically compress the weights from 16-bit floats down to **INT4 (4-bit signed integers)**!
- This compresses the model from 140 GB down to ~35 GB, allowing cutting-edge AI models to run locally on consumer laptops and smartphones without requiring a $30,000 datacenter GPU!

---

## 16. AI Future Insights
- **Established Technology:** Mixed-precision training (combining FP16 and FP32) on NVIDIA Tensor Cores.
- **Emerging Technology:** FP8 (8-bit floating point) and Microscaling formats (MXFP4) officially standardized for AI accelerators.
- **Reasonable Future Projection:** Ternary Computing & 1-bit LLMs (BitNet $b1.58$), where every neural network weight is constrained to only three states: $\{-1, 0, +1\}$. This completely replaces expensive hardware multipliers with simple addition and subtraction!
- **Speculative Possibility:** True non-binary quantum qubit superposition architectures replacing discrete binary gates for NP-hard optimization problems.

---

## 17. Career Relevance
- **Embedded Software & Firmware Engineers:** Write bitmasks, shift registers, and low-level protocol parsers.
- **Game Engine Developers:** Optimize memory layouts, physics vectors, and color buffers using SIMD integer/float packing.
- **Financial Software Developers:** Architect transaction engines with zero-loss fixed-point precision.
- **Security & Reverse Engineers:** Disassemble compiled binary machine code (Hex dumps) to discover buffer overflows and vulnerabilities.

---

## 18. Interview Preparation

### Category A: Beginner / Fresher Level
#### Q1: Why is Two's Complement universally used to represent signed integers in computers?
- **Answer:** Two's Complement solves two fundamental engineering problems of older systems (Sign-Magnitude and One's Complement): (1) It provides a **single unique representation for zero** (`00000000`), eliminating the ambiguity of having $+0$ and $-0$. (2) It allows the **exact same hardware addition circuitry** to perform both addition and subtraction ($A - B = A + (-B)$), simplifying CPU ALU design.

#### Q2: What causes an integer overflow, and what happens when it occurs?
- **Answer:** An integer overflow occurs when an arithmetic operation produces a value that exceeds the maximum numerical limit that can be stored in the designated number of bits. For example, adding $1$ to an 8-bit unsigned integer holding $255$ (`11111111`) yields `100000000` (9 bits); since only 8 bits can be stored, the upper bit is discarded, wrapping the value around to `0`. In signed integers, adding to the maximum positive number wraps around to the largest negative number.

---

## 19. Practice Questions

### Multiple-Choice Questions (MCQs)
1. What is the decimal value of the binary number $10110_2$?
   - A) 18
   - B) 20
   - C) 22
   - D) 26
   *(Answer: C; $16 + 4 + 2 = 22$)*

2. What is the 8-bit Two's Complement representation of $-1_{10}$?
   - A) `10000001`
   - B) `11111111`
   - C) `01111111`
   - D) `11111110`
   *(Answer: B)*

3. What is the range of values that can be stored in a signed 8-bit integer using Two's Complement?
   - A) $0\text{ to }255$
   - B) $-127\text{ to }+128$
   - C) $-128\text{ to }+127$
   - D) $-256\text{ to }+255$
   *(Answer: C)*

### Short Answer Questions
1. Convert the hexadecimal number $0x\text{3D}_{16}$ into decimal and binary.
2. Why does the expression `0.1 + 0.2 == 0.3` evaluate to `False` in Python?
3. What is the difference between ASCII and Unicode UTF-8?

### Long Answer Questions
1. Show step-by-step how an 8-bit ALU computes $28 - 45$ using Two's Complement addition. Clearly show the conversion of $-45$, the binary addition, and the verification of the final signed result.
2. Describe the structure of the IEEE 754 single-precision floating-point format (Sign, Exponent, Mantissa). Explain how bias is used in the exponent.

---

## 20. Solved Examples
### Problem 20.1: Step-by-Step Two's Complement Subtraction
**Question:** Compute $19 - 35$ using 8-bit Two's Complement binary arithmetic.

**Step-by-Step Solution:**
1. **Convert $+19$ to 8-bit binary:**
   $$19 = 16 + 2 + 1 = 00010011_2$$
2. **Convert $+35$ to 8-bit binary:**
   $$35 = 32 + 2 + 1 = 00100011_2$$
3. **Find Two's Complement of $-35$:**
   - Invert bits (1's comp): $11011100_2$
   - Add 1: $11011100 + 1 = 11011101_2$ (This is $-35$)
4. **Perform Binary Addition ($19 + (-35)$):**
   $$\begin{array}{r@{\quad}l}
     00010011 & (+19) \\
   + 11011101 & (-35) \\
   \hline
     11110000 & (\text{Result})
   \end{array}$$
5. **Verify the Result ($11110000_2$):**
   - The MSB is `1`, confirming the result is **negative**.
   - To find its magnitude, take Two's Complement of the result:
     - Invert bits: $00001111_2$
     - Add 1: $00001111 + 1 = 00010000_2 = 16_{10}$
   - Therefore, the result represents $\mathbf{-16}$.
   - Since $19 - 35 = -16$, the calculation is **100% mathematically correct!**

---

## 21. Unsolved Exercises
1. **Exercise 4.1:** Convert decimal $156_{10}$ into Binary, Octal, and Hexadecimal using manual division methods. Verify your answer using nibble substitution.
2. **Exercise 4.2:** Compute $45 - 28$ using 8-bit Two's Complement arithmetic. Show what happens to the carry-out bit.
3. **Exercise 4.3:** Look up the Unicode code points for your initials and favorite emoji, and encode them into UTF-8 binary bytes manually.

---

## 22. Chapter Summary
- Positional numbering systems evaluate digits based on positional powers: $\sum d_i \times b^i$.
- **Binary (Base-2)** is the native language of hardware switches; **Hexadecimal (Base-16)** provides a human-friendly compact representation (each hex digit = 4 binary bits).
- **Two's Complement** is the universal encoding for negative integers: Invert bits and add 1. It unifies addition and subtraction hardware and avoids the dual-zero problem.
- **Signed $N$-bit range:** $-2^{N-1} \text{ to } 2^{N-1} - 1$.
- **IEEE 754 Floating-Point** represents real numbers using Sign, Biased Exponent, and Mantissa. Finite bit precision causes minor rounding errors for non-terminating binary fractions ($0.1 + 0.2 \ne 0.3$).
- **Unicode & UTF-8** provide universal character mapping for all human languages and emojis, using variable-length 1 to 4 byte encodings.

---

## 23. Revision Sheet
- **Positional Powers of 2:**
  $$2^0=1, 2^1=2, 2^2=4, 2^3=8, 2^4=16, 2^5=32, 2^6=64, 2^7=128, 2^8=256, 2^{10}=1024$$
- **8-Bit Signed Limits:** $-128 \le X \le +127$
- **16-Bit Signed Limits:** $-32,768 \le X \le +32,767$
- **32-Bit Signed Limits:** $-2,147,483,648 \le X \le +2,147,483,647$
- **64-Bit Signed Limits:** $\approx -9.22 \times 10^{18} \le X \le +9.22 \times 10^{18}$
- **Two's Comp Formula:** $\text{Two's Comp}(X) = \text{NOT}(X) + 1$
- **Hex Nibbles:** $A=10, B=11, C=12, D=13, E=14, F=15$

---

## 24. References
1. **Patterson, David A., and John L. Hennessy.** *Computer Organization and Design: The Hardware/Software Interface.* RISC-V Edition, Morgan Kaufmann, 2017. Chapter 3: "Arithmetic for Computers."
2. **Stallings, William.** *Computer Organization and Architecture: Designing for Performance.* 11th Edition, Pearson, 2018. Chapter 9: "Computer Arithmetic."
3. **Petzold, Charles.** *Code: The Hidden Language of Computer Hardware and Software.* 2nd Edition, Microsoft Press, 2022. Chapter 13: "But What About Subtraction?" and Chapter 19: "ASCII and Cast of Characters."
4. **IEEE Computer Society.** *"IEEE Standard for Floating-Point Arithmetic."* IEEE Std 754-2019. (The international floating-point specification).
