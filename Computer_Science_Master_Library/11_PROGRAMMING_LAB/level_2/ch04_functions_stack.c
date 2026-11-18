/*
 * Chapter 04 Lab: Functions, Variable Scope, and Call Stack Simulation
 * Language: C99 / C11
 *
 * Demonstrates:
 * 1. Activation records and recursive stack frames (Factorial & Fibonacci).
 * 2. Static vs Automatic local variable lifetime.
 * 3. Scope shadowing and lexical blocks.
 */

#include <stdio.h>

// Static variable demonstrating persistent lifetime across function invocations
void counter_demo(void) {
    static int persistent_counter = 0; // Initialized once in .data / .bss segment
    int automatic_counter = 0;         // Re-allocated on stack each time

    persistent_counter++;
    automatic_counter++;

    printf("[counter_demo] persistent = %d, automatic = %d\n",
           persistent_counter, automatic_counter);
}

// Recursive function demonstrating stack frame accumulation and unwinding
long long factorial(int n) {
    if (n <= 1) {
        printf("  [Base Case Reached: n = %d, stack bottom]\n", n);
        return 1;
    }
    printf("  [Push Frame: n = %d] -> calling factorial(%d)\n", n, n - 1);
    long long result = n * factorial(n - 1);
    printf("  [Pop Frame:  n = %d] -> returning %lld\n", n, result);
    return result;
}

int main(void) {
    printf("=== Demonstration 1: Variable Lifetime & Scope ===\n");
    counter_demo();
    counter_demo();
    counter_demo();

    printf("\n=== Demonstration 2: Recursion & Call Stack Walkthrough ===\n");
    int num = 4;
    printf("Calculating factorial(%d):\n", num);
    long long fact = factorial(num);
    printf("Result: %d! = %lld\n", num, fact);

    return 0;
}
