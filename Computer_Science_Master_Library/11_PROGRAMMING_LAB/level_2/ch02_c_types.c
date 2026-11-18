/*
 * Practical Lab 2.2: C Data Types, Sizeof, and Formatted I/O
 * File: 11_PROGRAMMING_LAB/level_2/ch02_c_types.c
 * Author: Computer Science Master Library
 * Description: Demonstrates primitive C data types, sizes, ranges, and formatted printing.
 */

#include <stdio.h>

int main(void) {
    char letter = 'A';
    short small_num = 32000;
    int integer_val = 42;
    long long massive_val = 9000000000000000000LL;
    float pi_float = 3.14159f;
    double pi_double = 3.141592653589793;
    unsigned int large_val = 4000000000U;

    printf("============================================================\n");
    printf("         C DATA TYPES & SIZEOF ARCHITECTURE REPORT          \n");
    printf("============================================================\n");
    printf("Type: char          | Size: %zu Byte(s)  | Value: %c (ASCII %d)\n", sizeof(char), letter, letter);
    printf("Type: short         | Size: %zu Byte(s)  | Value: %hd\n", sizeof(short), small_num);
    printf("Type: int           | Size: %zu Byte(s)  | Value: %d\n", sizeof(int), integer_val);
    printf("Type: long long     | Size: %zu Byte(s)  | Value: %lld\n", sizeof(long long), massive_val);
    printf("Type: float         | Size: %zu Byte(s)  | Value: %.5f\n", sizeof(float), pi_float);
    printf("Type: double        | Size: %zu Byte(s)  | Value: %.15lf\n", sizeof(double), pi_double);
    printf("Type: unsigned int  | Size: %zu Byte(s)  | Value: %u\n", sizeof(unsigned int), large_val);
    printf("============================================================\n");

    return 0;
}
