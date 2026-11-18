"""
Practical Lab 2.1: Programming Mental Models & State Space Simulator
File: 11_PROGRAMMING_LAB/level_2/ch01_mental_models_lab.py
Author: Computer Science Master Library
Description: Demonstrates stepwise refinement, automated trace table logging,
             and boundary-condition validation.
"""

import sys
from typing import Dict, List, Tuple, Any

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def dispense_currency(
    amount: int, denominations: List[int]
) -> Dict[str, Any]:
    """
    Decomposed Currency Dispenser.
    Demonstrates state mutation tracking and edge-case validation.
    """
    print(f"--- Processing ATM Withdrawal Request: ₹{amount:,} ---")

    if amount <= 0:
        raise ValueError("Withdrawal amount must be strictly positive.")

    min_denom = min(denominations)
    if amount % min_denom != 0:
        raise ValueError(
            f"Amount must be a multiple of the lowest note (₹{min_denom})."
        )

    sorted_denoms = sorted(denominations, reverse=True)

    remaining_balance = amount
    notes_dispensed: Dict[int, int] = {}
    trace_log: List[Tuple[int, int, int, int]] = []

    for denom in sorted_denoms:
        count = remaining_balance // denom
        prev_balance = remaining_balance
        remaining_balance = remaining_balance % denom

        if count > 0:
            notes_dispensed[denom] = count

        trace_log.append((prev_balance, denom, count, remaining_balance))

    print("Trace Table:")
    print("Starting Remainder | Denomination | Notes Count | Ending Remainder")
    print("-" * 65)
    for row in trace_log:
        print(f"₹{row[0]:17,d} | ₹{row[1]:11d} | {row[2]:11d} | ₹{row[3]:15,d}")
    print("-" * 65)

    print(f"Dispense Breakdown: {notes_dispensed}")
    print(f"Final Unresolved Remainder: ₹{remaining_balance}\n")

    return {
        "amount": amount,
        "notes": notes_dispensed,
        "remaining": remaining_balance,
        "success": remaining_balance == 0,
    }


if __name__ == "__main__":
    denoms = [500, 200, 100]
    res1 = dispense_currency(3800, denoms)
    assert res1["success"] is True
    assert res1["notes"] == {500: 7, 200: 1, 100: 1}

    res2 = dispense_currency(2000, denoms)
    assert res2["success"] is True
    assert res2["notes"] == {500: 4}

    try:
        dispense_currency(3855, denoms)
        assert False, "Should have rejected non-multiple amount!"
    except ValueError as e:
        print(f"Edge Case Successfully Caught: {e}")

    print("\nAll mental models and state tracking tests passed successfully.")
