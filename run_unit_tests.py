"""Lightweight test runner for Magic Herb Tracker.

Discovers all ``test_*`` functions in ``tests/test_*.py`` modules and runs
them.  Exit code is 0 on success, 1 if any test fails.

Usage:
    python run_unit_tests.py
"""

import importlib
import inspect
import os
import sys
import traceback

TESTS_DIR = os.path.join(os.path.dirname(__file__), "tests")


def discover_and_run() -> tuple[int, int, list[str]]:
    """Return (passed, failed, failure_details)."""
    # Ensure the project root is on sys.path so test imports resolve
    project_root = os.path.dirname(__file__)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    passed = 0
    failed = 0
    failures: list[str] = []

    for filename in sorted(os.listdir(TESTS_DIR)):
        if not filename.startswith("test_") or not filename.endswith(".py"):
            continue
        module_name = f"tests.{filename[:-3]}"
        try:
            mod = importlib.import_module(module_name)
        except Exception:
            msg = f"IMPORT ERROR: {module_name}\n{traceback.format_exc()}"
            print(msg)
            failures.append(msg)
            failed += 1
            continue

        for name, func in inspect.getmembers(mod, inspect.isfunction):
            if not name.startswith("test_"):
                continue
            qualname = f"{module_name}::{name}"
            try:
                func()
                passed += 1
                print(f"  PASS  {qualname}")
            except Exception:
                failed += 1
                tb = traceback.format_exc()
                msg = f"  FAIL  {qualname}\n{tb}"
                print(msg)
                failures.append(msg)

    return passed, failed, failures


def main() -> int:
    print("=" * 60)
    print("Magic Herb Tracker - Unit Tests")
    print("=" * 60)
    passed, failed, failures = discover_and_run()
    print("-" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    if failures:
        print("\nFailed tests:")
        for f in failures:
            print(f)
    print("=" * 60)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
