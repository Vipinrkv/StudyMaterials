/*
 * Chapter 10 Lab: Defensive Programming, Debugging, and Memory Leaks
 * Language: C99 / C11
 *
 * Demonstrates:
 * 1. Design by Contract using assert() for preconditions and invariants.
 * 2. Defensive runtime input validation and explicit error codes.
 * 3. Tracked heap memory allocator detecting double frees and leaks.
 * 4. Safe string copy idiom (safe_strcpy).
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <assert.h>

// Safe string copy with guaranteed null termination and bounds checking
bool safe_strcpy(char *dest, size_t dest_size, const char *src) {
    if (!dest || !src || dest_size == 0) {
        return false;
    }
    size_t src_len = strlen(src);
    if (src_len >= dest_size) {
        // Truncate safely and null terminate
        memcpy(dest, src, dest_size - 1);
        dest[dest_size - 1] = '\0';
        return false; // Signal truncation
    }
    memcpy(dest, src, src_len + 1);
    return true;
}

// Tracked allocator header
typedef struct {
    size_t size;
    uint32_t magic;
} AllocHeader;

#define MAGIC_ACTIVE 0xABCD1234
#define MAGIC_FREED  0xDEAD0000

static size_t g_allocated_bytes = 0;

void* dbg_malloc(size_t sz) {
    if (sz == 0) return NULL;
    AllocHeader *hdr = (AllocHeader *)malloc(sizeof(AllocHeader) + sz);
    if (!hdr) return NULL;

    hdr->size = sz;
    hdr->magic = MAGIC_ACTIVE;
    g_allocated_bytes += sz;
    return (void *)(hdr + 1);
}

void dbg_free(void *ptr) {
    if (!ptr) return;
    AllocHeader *hdr = ((AllocHeader *)ptr) - 1;

    assert(hdr->magic != MAGIC_FREED && "FATAL: Double free detected!");
    assert(hdr->magic == MAGIC_ACTIVE && "FATAL: Invalid memory free!");

    g_allocated_bytes -= hdr->size;
    hdr->magic = MAGIC_FREED;
    free(hdr);
}

int main(void) {
    printf("=== Demonstration 1: Safe Defensive String Copy ===\n");
    char buffer[8];
    const char *long_text = "BharatConnect";
    bool ok = safe_strcpy(buffer, sizeof(buffer), long_text);
    printf("Copied to buffer: \"%s\" (Success flag: %s)\n", buffer, ok ? "true" : "false (truncated)");
    assert(buffer[sizeof(buffer) - 1] == '\0');

    printf("\n=== Demonstration 2: Tracked Heap Allocator ===\n");
    int *numbers = (int *)dbg_malloc(10 * sizeof(int));
    if (numbers) {
        for (int i = 0; i < 10; ++i) numbers[i] = i * i;
        printf("Active allocated memory: %zu bytes\n", g_allocated_bytes);
        dbg_free(numbers);
    }
    printf("Active memory after free: %zu bytes (Leak balanced!)\n", g_allocated_bytes);
    assert(g_allocated_bytes == 0);

    return 0;
}
