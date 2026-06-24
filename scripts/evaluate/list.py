#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.evaluate.catalog import load_catalog


def main() -> None:
    checks = load_catalog()
    print(f"{'LEVEL':<6} {'MISSION':<38} {'SKILL':<24} CHECK")
    print("-" * 100)
    for check in checks:
        status = "configured" if check.test_file.exists() else "missing"
        print(f"{check.level:<6} {check.mission_id:<38} {check.skill:<24} {status}")
    print(f"\n{len(checks)} missions configured")


if __name__ == "__main__":
    main()
