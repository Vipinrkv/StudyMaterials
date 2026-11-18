"""
Practical Lab 1.4: Number Systems, Two's Complement, and Encoding Inspector
File: 11_PROGRAMMING_LAB/level_1/number_converter.py
Author: Computer Science Master Library
Description: Demonstrates binary, octal, hexadecimal conversions,
             signed 8-bit Two's complement arithmetic, and UTF-8 encoding.
"""

import struct
import sys

# Configure UTF-8 output encoding for cross-platform and Windows console support
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def inspect_integer(n: int, bits: int = 8) -> None:
    """Displays representation of a number across bases and 2's complement."""
    print(f"--- Integer Inspection: {n} (Target: {bits}-bit) ---")
    if 0 <= n < (1 << bits):
        print(f"Decimal (Unsigned) : {n}")
        print(f"Binary             : {bin(n)[2:].zfill(bits)}")
        print(f"Octal              : {oct(n)}")
        print(f"Hexadecimal        : {hex(n).upper()}")

    min_val = -(1 << (bits - 1))
    max_val = (1 << (bits - 1)) - 1
    if min_val <= n <= max_val:
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

    float_bytes = struct.pack(">f", 0.1)
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
        try:
            print(
                f"Char: '{char}' | Code Point: {code_point:<8} | Bytes ({len(utf8_bytes)}): {hex_bytes:<12} | Bits: {bin_bytes}"
            )
        except UnicodeEncodeError:
            print(
                f"Char: [U+{ord(char):04X}] | Code Point: {code_point:<8} | Bytes ({len(utf8_bytes)}): {hex_bytes:<12} | Bits: {bin_bytes}"
            )
    print()


if __name__ == "__main__":
    inspect_integer(42, bits=8)
    inspect_integer(-42, bits=8)
    inspect_float_precision()
    inspect_utf8_string("Hi अ 🚀")
    print("Number converter tests passed successfully.")
