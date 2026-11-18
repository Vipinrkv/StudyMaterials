/*
 * Chapter 07 Lab: Dynamic Memory Allocation and Heap Management in C
 * Language: C99 / C11
 *
 * Demonstrates:
 * 1. Safe dynamic array allocation (malloc/calloc) and NULL verification.
 * 2. Geometric capacity growth with temporary pointer handling in realloc.
 * 3. Linear Arena / Bump Allocator implementation.
 * 4. Defensive pointer zeroing after free (SAFE_FREE).
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define SAFE_FREE(p) do { free(p); (p) = NULL; } while(0)

// Demonstration of a high-speed linear Arena Allocator
typedef struct {
    uint8_t *buffer;
    size_t capacity;
    size_t offset;
} Arena;

Arena arena_create(size_t capacity) {
    Arena a;
    a.capacity = capacity;
    a.offset = 0;
    a.buffer = (uint8_t *)malloc(capacity);
    return a;
}

void* arena_alloc(Arena *a, size_t size) {
    // Align to 8 bytes
    size_t aligned_size = (size + 7) & ~7;
    if (a->offset + aligned_size > a->capacity) {
        return NULL; // Out of arena memory
    }
    void *ptr = &a->buffer[a->offset];
    a->offset += aligned_size;
    return ptr;
}

void arena_reset(Arena *a) {
    a->offset = 0; // Instantaneous zero-cost reclamation
}

void arena_destroy(Arena *a) {
    free(a->buffer);
    a->buffer = NULL;
    a->capacity = 0;
    a->offset = 0;
}

int main(void) {
    printf("=== Demonstration 1: Standard Dynamic Array ===\n");
    int count = 5;
    int *arr = (int *)calloc(count, sizeof(int));
    if (!arr) {
        perror("calloc failed");
        return 1;
    }

    for (int i = 0; i < count; ++i) arr[i] = (i + 1) * 10;

    // Geometric resizing
    int new_count = 10;
    int *temp = (int *)realloc(arr, new_count * sizeof(int));
    if (!temp) {
        perror("realloc failed");
        free(arr);
        return 1;
    }
    arr = temp;
    for (int i = count; i < new_count; ++i) arr[i] = (i + 1) * 10;

    printf("Resized array contents: ");
    for (int i = 0; i < new_count; ++i) printf("%d ", arr[i]);
    printf("\n");
    SAFE_FREE(arr);

    printf("\n=== Demonstration 2: High-Speed Arena Allocator ===\n");
    Arena arena = arena_create(1024);
    int *num = (int *)arena_alloc(&arena, sizeof(int));
    char *str = (char *)arena_alloc(&arena, 32);
    if (num && str) {
        *num = 42;
        strcpy(str, "Arena Allocated String");
        printf("Arena num = %d, str = \"%s\"\n", *num, str);
        printf("Arena used: %zu / %zu bytes\n", arena.offset, arena.capacity);
    }
    arena_reset(&arena);
    printf("Arena after reset: used = %zu bytes (Instant free)\n", arena.offset);
    arena_destroy(&arena);

    return 0;
}
