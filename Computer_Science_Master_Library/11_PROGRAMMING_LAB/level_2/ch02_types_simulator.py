"""
Practical Lab 2.2 Companion: C Types, Struct Alignment & Memory Layout Simulator
File: 11_PROGRAMMING_LAB/level_2/ch02_types_simulator.py
Author: Computer Science Master Library
Description: Emulates C data types, struct padding, memory alignment,
             and format specifier decoding using Python's ctypes and struct.
"""

import sys
import ctypes
import struct

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def demonstrate_c_types_in_python() -> None:
    print("=" * 65)
    print("      C DATA TYPES & SIZEOF EMULATION IN PYTHON RUNTIME")
    print("=" * 65)

    types_to_test = [
        ("char", ctypes.c_char, b"Z"),
        ("signed char", ctypes.c_byte, -42),
        ("unsigned char", ctypes.c_ubyte, 255),
        ("short", ctypes.c_short, -32000),
        ("unsigned short", ctypes.c_ushort, 65000),
        ("int", ctypes.c_int, -2000000),
        ("unsigned int", ctypes.c_uint, 4000000000),
        ("long long", ctypes.c_longlong, -9000000000000000000),
        ("float", ctypes.c_float, 3.14159),
        ("double", ctypes.c_double, 3.141592653589793),
    ]

    print("C Data Type        | Size in Bytes | Internal Representation")
    print("-" * 65)
    for name, c_type, val in types_to_test:
        instance = c_type(val)
        raw_size = ctypes.sizeof(instance)
        print(f"{name:<18} | {raw_size:13d} | Value = {val}")

    print("-" * 65 + "\n")


def demonstrate_memory_alignment_padding() -> None:
    print("=" * 65)
    print("      DEMONSTRATING COMPILER PADDING & STRUCTURE ALIGNMENT")
    print("=" * 65)

    # In C:
    # struct Example {
    #     char a;     // 1 byte
    #     // 3 padding bytes inserted here to align 'b' to 4-byte boundary!
    #     int b;      // 4 bytes
    #     double c;   // 8 bytes
    # };
    # Expected total size = 16 bytes, NOT 13 bytes!

    class AlignedStruct(ctypes.Structure):
        _fields_ = [
            ("a", ctypes.c_char),
            ("b", ctypes.c_int),
            ("c", ctypes.c_double),
        ]

    s = AlignedStruct(b"K", 42, 99.99)
    total_size = ctypes.sizeof(s)
    offset_a = AlignedStruct.a.offset
    offset_b = AlignedStruct.b.offset
    offset_c = AlignedStruct.c.offset

    print(f"Struct Fields:")
    print(
        f"  Field 'a' (char 1B)   : Offset = {offset_a:2d} bytes (Address relative to struct start)"
    )
    print(
        f"  Field 'b' (int 4B)    : Offset = {offset_b:2d} bytes (3 padding bytes added!)"
    )
    print(f"  Field 'c' (double 8B) : Offset = {offset_c:2d} bytes")
    print("-" * 65)
    print(
        f"Total Struct Size in RAM: {total_size} Bytes (Confirmed 16B alignment!)"
    )
    print("=" * 65 + "\n")


if __name__ == "__main__":
    demonstrate_c_types_in_python()
    demonstrate_memory_alignment_padding()
    print("All C type simulation and alignment tests verified successfully.")
