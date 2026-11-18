/*
 * Practical Lab 2.3: Operators, Control Flow, and Loops in C
 * File: 11_PROGRAMMING_LAB/level_2/ch03_operators_flow.c
 * Author: Computer Science Master Library
 * Description: Demonstrates conditional branching, switch-case, short-circuiting,
 *              and loop control statements.
 */

#include <stdio.h>

int main(void) {
    int score = 85;
    char grade;

    printf("============================================================\n");
    printf("        C OPERATORS AND CONTROL FLOW EXECUTION REPORT       \n");
    printf("============================================================\n");

    // 1. Ternary Operator
    printf("Evaluation (Ternary): %s\n", (score >= 50) ? "PASSED" : "FAILED");

    // 2. Cascade if-else
    if (score >= 90) {
        grade = 'A';
    } else if (score >= 80) {
        grade = 'B';
    } else if (score >= 70) {
        grade = 'C';
    } else {
        grade = 'F';
    }
    printf("Calculated Grade: %c\n", grade);

    // 3. Switch-Case with break
    printf("Feedback: ");
    switch (grade) {
        case 'A':
            printf("Outstanding performance!\n");
            break;
        case 'B':
            printf("Very good understanding.\n");
            break;
        case 'C':
            printf("Satisfactory.\n");
            break;
        default:
            printf("Needs improvement.\n");
            break;
    }

    // 4. For Loop with Break & Continue
    printf("Loop Demonstration (Evens < 10, skipping 4):\n  ");
    for (int i = 0; i < 10; i++) {
        if (i % 2 != 0) continue; // Skip odd numbers
        if (i == 4) continue;     // Explicitly skip 4
        printf("%d ", i);
    }
    printf("\n============================================================\n");

    return 0;
}
