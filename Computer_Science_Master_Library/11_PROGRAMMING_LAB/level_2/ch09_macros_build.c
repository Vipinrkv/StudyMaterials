/*
 * Chapter 09 Lab: Preprocessor Directives, Macros, and Build Systems
 * Language: C99 / C11
 *
 * Demonstrates:
 * 1. Safe parameterized macros with parentheses.
 * 2. Multi-line macros using do { ... } while(0).
 * 3. Stringification (#) and Token Pasting (##) operators.
 * 4. Conditional compilation guards.
 */

#include <stdio.h>

// Safe macro
#define SAFE_MAX(a, b) (((a) > (b)) ? (a) : (b))

// Multi-statement macro
#define SWAP_INTEGERS(x, y) do { \
    int _swap_temp = (x);        \
    (x) = (y);                   \
    (y) = _swap_temp;            \
} while (0)

// Stringification operator
#define DEBUG_PRINT_VAR(var) printf("[DEBUG] " #var " = %d\n", (var))

// Token pasting operator: declares a typed getter function
#define DECLARE_GETTER(type, name) \
    type get_##name(type val) { return val; }

DECLARE_GETTER(int, score)
DECLARE_GETTER(double, ratio)

int main(void) {
    printf("=== Demonstration 1: Safe vs Unsafe Macro Expansion ===\n");
    int a = 10, b = 25;
    printf("SAFE_MAX(%d, %d) = %d\n", a, b, SAFE_MAX(a, b));

    printf("\n=== Demonstration 2: Multi-Statement do-while(0) Macro ===\n");
    int x = 111, y = 999;
    printf("Before swap: x = %d, y = %d\n", x, y);
    if (x < y)
        SWAP_INTEGERS(x, y); // No curly braces in if-block!
    else
        printf("Not swapped\n");
    printf("After swap:  x = %d, y = %d\n", x, y);

    printf("\n=== Demonstration 3: Stringification & Token Concatenation ===\n");
    int test_variable = 42;
    DEBUG_PRINT_VAR(test_variable);

    printf("Token pasted get_score(100) = %d\n", get_score(100));
    printf("Token pasted get_ratio(0.75) = %.2f\n", get_ratio(0.75));

    return 0;
}
