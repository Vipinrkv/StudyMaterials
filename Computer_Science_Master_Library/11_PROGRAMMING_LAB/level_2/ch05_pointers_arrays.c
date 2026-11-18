/*
 * Chapter 05 Lab: Arrays, Strings, and Pointer Foundations in C
 * Language: C99 / C11
 *
 * Demonstrates:
 * 1. 1D and 2D contiguous array memory layout.
 * 2. Unification theorem: arr[i] == *(arr + i).
 * 3. Pointer arithmetic scaling by sizeof(T).
 * 4. Pass-by-reference simulation via pointers: swap(&a, &b).
 * 5. String null termination and safe concatenation.
 */

#include <stdio.h>
#include <string.h>

void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

void print_matrix_row_major(const int *mat, int rows, int cols) {
    printf("Matrix contents via row-major pointer arithmetic:\n");
    for (int r = 0; r < rows; ++r) {
        printf("  Row %d: ", r);
        for (int c = 0; c < cols; ++c) {
            // Address formula: Base + (r * cols + c)
            int val = *(mat + (r * cols + c));
            printf("%4d", val);
        }
        printf("\n");
    }
}

int main(void) {
    printf("=== Demonstration 1: Pointer Swapping ===\n");
    int x = 100, y = 200;
    printf("Before swap: x = %d, y = %d\n", x, y);
    swap(&x, &y);
    printf("After swap:  x = %d, y = %d\n", x, y);

    printf("\n=== Demonstration 2: Array-Pointer Unification ===\n");
    int arr[5] = {10, 20, 30, 40, 50};
    for (int i = 0; i < 5; ++i) {
        printf("Index %d: arr[%d] = %d | *(arr + %d) = %d | %d[arr] = %d\n",
               i, i, arr[i], i, *(arr + i), i, i[arr]);
    }

    printf("\n=== Demonstration 3: 2D Array Flattening & Memory Strides ===\n");
    int matrix[2][3] = {
        {11, 22, 33},
        {44, 55, 66}
    };
    print_matrix_row_major((const int *)matrix, 2, 3);

    printf("\n=== Demonstration 4: Safe C-String Manipulation ===\n");
    char dest[32] = "Hello, ";
    const char *src = "BharatConnect!";
    strncat(dest, src, sizeof(dest) - strlen(dest) - 1);
    printf("Safe concatenated string: \"%s\" (Length: %zu)\n", dest, strlen(dest));

    return 0;
}
