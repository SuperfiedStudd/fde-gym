#!/usr/bin/env python3
import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.evaluate.catalog import MissionCheck, get_check, load_catalog


def run_command(command: list[str], env: dict[str, str]) -> int:
    printable = " ".join(command)
    print(f"\n$ {printable}", flush=True)
    return subprocess.run(command, cwd=ROOT, env=env, check=False).returncode


def evaluate(check: MissionCheck, run_lint: bool) -> dict[str, object]:
    env = os.environ.copy()
    python_paths = [str(ROOT / "apps/api"), str(ROOT / "apps/worker"), str(ROOT)]
    env["PYTHONPATH"] = os.pathsep.join(python_paths + [env.get("PYTHONPATH", "")])
    results: list[dict[str, object]] = []

    if not check.test_file.exists():
        results.append({"name": "mission tests", "status": "missing", "exit_code": 2})
    else:
        exit_code = run_command([sys.executable, "-m", "pytest", "-q", str(check.test_file)], env)
        results.append(
            {
                "name": "mission tests",
                "status": "passed" if exit_code == 0 else "failed",
                "exit_code": exit_code,
            }
        )

    if run_lint and check.lint_targets:
        if importlib.util.find_spec("ruff") is None:
            results.append({"name": "ruff", "status": "skipped", "reason": "ruff is not installed"})
        else:
            command = [
                sys.executable,
                "-m",
                "ruff",
                "check",
                *[str(path) for path in check.lint_targets],
            ]
            exit_code = run_command(command, env)
            results.append(
                {
                    "name": "ruff",
                    "status": "passed" if exit_code == 0 else "failed",
                    "exit_code": exit_code,
                }
            )

    passed = all(result["status"] in {"passed", "skipped"} for result in results)
    return {"mission": check.mission_id, "passed": passed, "results": results}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run fde-gym mission checks")
    parser.add_argument("--mission", required=True, help="mission id or 'all'")
    parser.add_argument("--no-lint", action="store_true", help="skip targeted Ruff checks")
    parser.add_argument("--json", action="store_true", help="emit a final JSON summary")
    args = parser.parse_args()

    if args.mission == "all":
        checks = load_catalog()
    else:
        check = get_check(args.mission)
        if check is None:
            print(f"unknown mission: {args.mission}", file=sys.stderr)
            print("Run: python scripts/evaluate/list.py", file=sys.stderr)
            return 2
        checks = [check]

    summaries = [evaluate(check, run_lint=not args.no_lint) for check in checks]
    passed = all(summary["passed"] for summary in summaries)
    if args.json:
        print(json.dumps({"passed": passed, "missions": summaries}, indent=2))
    else:
        print("\n" + "=" * 72)
        for summary in summaries:
            marker = "PASS" if summary["passed"] else "NEEDS WORK"
            print(f"[{marker}] {summary['mission']}")
        print("Expected baseline: mission checks fail until you complete that mission.")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
