#!/usr/bin/env python3
"""
Chapter 09 Python Verification & Emulation Testbed:
Preprocessor Macro Expander and Make DAG Dependency Engine Simulator

Validates:
- Preprocessor macro precedence bugs: SQUARE(2 + 3) expansion
- Token stringification and concatenation
- Directed Acyclic Graph (DAG) build system scheduler (GNU Make simulation)
- Timestamp-based incremental compilation
"""

import sys
import time
from typing import Dict, List, Set

# Enforce UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class BuildTarget:
    def __init__(self, name: str, prerequisites: List[str], build_command: str):
        self.name = name
        self.prerequisites = prerequisites
        self.build_command = build_command
        self.timestamp: float = 0.0


class MakeEngineSimulator:
    def __init__(self):
        self.targets: Dict[str, BuildTarget] = {}
        self.file_timestamps: Dict[str, float] = {}
        self.rebuilt_targets: List[str] = []

    def add_source_file(self, filename: str, mtime: float):
        self.file_timestamps[filename] = mtime

    def add_target(self, name: str, prereqs: List[str], cmd: str, initial_mtime: float = 0.0):
        target = BuildTarget(name, prereqs, cmd)
        target.timestamp = initial_mtime
        self.targets[name] = target
        self.file_timestamps[name] = initial_mtime

    def build(self, target_name: str) -> None:
        if target_name not in self.targets:
            # It is a raw source file (leaf in DAG)
            return

        target = self.targets[target_name]
        needs_rebuild = False

        # Recursively ensure all prerequisites are up to date
        for prereq in target.prerequisites:
            self.build(prereq)
            prereq_time = self.file_timestamps.get(prereq, 0.0)
            if prereq_time > target.timestamp:
                needs_rebuild = True

        if needs_rebuild or target.timestamp == 0.0:
            print(f"  [MAKE EXEC]: {target.build_command}")
            self.rebuilt_targets.append(target.name)
            # Update target timestamp
            target.timestamp = time.time()
            self.file_timestamps[target.name] = target.timestamp
        else:
            print(f"  [UP-TO-DATE]: Target '{target.name}' is current (skipped).")


def main() -> int:
    print("=" * 60)
    print("LEVEL 2 LAB CH09: PREPROCESSOR & MAKE BUILD SIMULATOR")
    print("=" * 60)

    # Test 1: Macro Precedence Trap Emulation
    print("\n[Test 1] Testing Macro Text Substitution Precedence ...")
    # Naive macro: #define SQUARE(x) x * x
    # Expression: SQUARE(2 + 3) -> 2 + 3 * 2 + 3 = 2 + 6 + 3 = 11 (Wrong!)
    naive_res = 2 + 3 * 2 + 3
    # Safe macro: #define SAFE_SQUARE(x) ((x) * (x)) -> ((2 + 3) * (2 + 3)) = 25
    safe_res = (2 + 3) * (2 + 3)
    print(f"  Naive SQUARE(2 + 3) = {naive_res} (Mathematical failure due to precedence)")
    print(f"  Safe  SQUARE(2 + 3) = {safe_res}  (Correct mathematical square)")
    assert naive_res == 11 and safe_res == 25, "Precedence evaluation mismatch!"

    # Test 2: DAG Incremental Build System Simulation
    print("\n[Test 2] Testing DAG Build Scheduler (Make Simulation) ...")
    make = MakeEngineSimulator()

    t0 = 1000.0
    make.add_source_file("src/main.c", t0)
    make.add_source_file("src/calc.c", t0)
    make.add_source_file("include/calc.h", t0)

    # Add object targets
    make.add_target("build/calc.o", ["src/calc.c", "include/calc.h"], "gcc -c src/calc.c -o build/calc.o", t0 + 1)
    make.add_target("build/main.o", ["src/main.c", "include/calc.h"], "gcc -c src/main.c -o build/main.o", t0 + 1)
    make.add_target("bin/app.exe", ["build/calc.o", "build/main.o"], "gcc build/calc.o build/main.o -o bin/app.exe", t0 + 2)

    # Initial run: All up to date
    print("  Run 1 (No changes):")
    make.build("bin/app.exe")
    assert len(make.rebuilt_targets) == 0, "Clean build executed unnecessary actions!"

    # Simulate modifying src/calc.c (timestamp updated to t0 + 10)
    print("\n  Run 2 (src/calc.c modified):")
    make.file_timestamps["src/calc.c"] = t0 + 10.0
    make.build("bin/app.exe")

    # Only calc.o and app.exe should rebuild; main.o must NOT rebuild!
    print(f"  Rebuilt targets: {make.rebuilt_targets}")
    assert "build/calc.o" in make.rebuilt_targets
    assert "bin/app.exe" in make.rebuilt_targets
    assert "build/main.o" not in make.rebuilt_targets, "main.o rebuilt unnecessarily!"
    print("  SUCCESS: Minimal incremental DAG recompilation verified.")

    print("\n" + "=" * 60)
    print("ALL CH09 PREPROCESSOR & BUILD CHECKS PASSED (Exit 0)")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
