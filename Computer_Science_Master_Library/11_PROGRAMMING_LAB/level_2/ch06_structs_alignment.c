/*
 * Chapter 06 Lab: Structures, Unions, and Memory Alignment in C
 * Language: C99 / C11
 *
 * Demonstrates:
 * 1. Struct member padding and natural alignment on word boundaries.
 * 2. Optimized member ordering for minimal memory footprint.
 * 3. Union type-punning and raw byte inspection.
 * 4. Packed structures for network serialization.
 */

#include <stdio.h>
#include <stddef.h>
#include <stdint.h>

// Unoptimized layout with wasted padding
struct Unoptimized {
    char c1;      // 1 byte
    double d;     // 8 bytes (Padding: 7 bytes)
    char c2;      // 1 byte
    int i;        // 4 bytes (Padding: 3 bytes; reaches offset 24)
}; // Total: 24 bytes

// Optimized layout sorted by descending alignment
struct Optimized {
    double d;     // 8 bytes
    int i;        // 4 bytes
    char c1;      // 1 byte
    char c2;      // 1 byte
                  // 2 tail padding bytes
}; // Total: 16 bytes

#pragma pack(push, 1)
struct PackedRecord {
    char c1;
    double d;
    char c2;
    int i;
}; // Total: 14 bytes (Zero padding)
#pragma pack(pop)

typedef union {
    float f;
    uint32_t raw_bits;
    uint8_t bytes[4];
} FloatInspector;

int main(void) {
    printf("=== Demonstration 1: Memory Alignment & Padding ===\n");
    printf("sizeof(struct Unoptimized) = %zu bytes (Wasteful)\n", sizeof(struct Unoptimized));
    printf("sizeof(struct Optimized)   = %zu bytes (50%% memory saved!)\n", sizeof(struct Optimized));
    printf("sizeof(struct PackedRecord)= %zu bytes (Packed wire format)\n", sizeof(struct PackedRecord));

    printf("\n=== Demonstration 2: Member Offsets ===\n");
    printf("Unoptimized -> c1: %zu, d: %zu, c2: %zu, i: %zu\n",
           offsetof(struct Unoptimized, c1),
           offsetof(struct Unoptimized, d),
           offsetof(struct Unoptimized, c2),
           offsetof(struct Unoptimized, i));

    printf("Optimized   -> d: %zu, i: %zu, c1: %zu, c2: %zu\n",
           offsetof(struct Optimized, d),
           offsetof(struct Optimized, i),
           offsetof(struct Optimized, c1),
           offsetof(struct Optimized, c2));

    printf("\n=== Demonstration 3: Union Type Punning ===\n");
    FloatInspector fi;
    fi.f = 3.14159f;
    printf("Float value: %f\n", fi.f);
    printf("IEEE 754 raw hex: 0x%08X\n", fi.raw_bits);
    printf("Bytes (Little Endian): [0x%02X, 0x%02X, 0x%02X, 0x%02X]\n",
           fi.bytes[0], fi.bytes[1], fi.bytes[2], fi.bytes[3]);

    return 0;
}
