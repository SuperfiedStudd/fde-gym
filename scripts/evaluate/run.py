#!/usr/bin/env python3
import argparse
import importlib
import importlib.util
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.evaluate.catalog import MissionCheck, get_check, load_catalog

BOOTSTRAP_COMMAND = (
    "powershell -ExecutionPolicy Bypass -File "
    "./scripts/dev/bootstrap.ps1 -Recreate"
)
REQUIRED_HOST_IMPORTS = {
    "asyncpg compiled extension": "asyncpg.protocol.protocol",
    "FastAPI": "fastapi",
    "pydantic-core compiled extension": "pydantic_core._pydantic_core",
    "pytest": "pytest",
    "Redis client": "redis",
    "Ruff": "ruff",
    "SQLAlchemy": "sqlalchemy",
    "structured logging": "pythonjsonlogger",
}


@dataclass(frozen=True)
class CommandResult:
    exit_code: int
    output: str


def host_environment_errors() -> list[str]:
    errors: list[str] = []
    if sys.version_info[:2] != (3, 12):
        errors.append(
            f"Python 3.12 is required; current interpreter is "
            f"{sys.version_info.major}.{sys.version_info.minor}."
        )

    for label, module_name in REQUIRED_HOST_IMPORTS.items():
        try:
            importlib.import_module(module_name)
        except (ImportError, OSError) as exc:
            errors.append(f"{label}: {type(exc).__name__}: {exc}")
    return errors


def run_command(command: list[str], env: dict[str, str]) -> CommandResult:
    printable = " ".join(command)
    print(f"\n$ {printable}", flush=True)
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
    )
    print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n")
    return CommandResult(exit_code=completed.returncode, output=completed.stdout)


def classify_pytest_exit(exit_code: int) -> str:
    if exit_code == 0:
        return "passed"
    if exit_code == 1:
        return "intended_failure"
    return "setup_error"


def evaluate(check: MissionCheck, run_lint: bool) -> dict[str, object]:
    env = os.environ.copy()
    python_paths = [str(ROOT / "apps/api"), str(ROOT / "apps/worker"), str(ROOT)]
    env["PYTHONPATH"] = os.pathsep.join(python_paths + [env.get("PYTHONPATH", "")])
    results: list[dict[str, object]] = []

    if not check.test_file.exists():
        results.append(
            {
                "name": "mission tests",
                "status": "setup_error",
                "reason": f"missing test file: {check.test_file}",
                "exit_code": 2,
            }
        )
    else:
        command_result = run_command(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(check.test_file)],
            env,
        )
        results.append(
            {
                "name": "mission tests",
                "status": classify_pytest_exit(command_result.exit_code),
                "exit_code": command_result.exit_code,
            }
        )

    if run_lint and check.lint_targets:
        if importlib.util.find_spec("ruff") is None:
            results.append(
                {
                    "name": "ruff",
                    "status": "setup_error",
                    "reason": "ruff is not installed",
                    "exit_code": 2,
                }
            )
        else:
            command = [
                sys.executable,
                "-m",
                "ruff",
                "check",
                *[str(path) for path in check.lint_targets],
            ]
            command_result = run_command(command, env)
            results.append(
                {
                    "name": "ruff",
                    "status": classify_pytest_exit(command_result.exit_code),
                    "exit_code": command_result.exit_code,
                }
            )

    setup_error = any(result["status"] == "setup_error" for result in results)
    passed = bool(results) and all(result["status"] == "passed" for result in results)
    return {
        "mission": check.mission_id,
        "passed": passed,
        "setup_error": setup_error,
        "results": results,
    }


def print_setup_error(details: list[str] | None = None) -> None:
    print("\nSetup error: host Python environment is not ready.")
    if details:
        for detail in details:
            print(f"  - {detail}")
    print(f"Run: {BOOTSTRAP_COMMAND}")


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

    environment_errors = host_environment_errors()
    if environment_errors:
        print_setup_error(environment_errors)
        return 2

    summaries = [evaluate(check, run_lint=not args.no_lint) for check in checks]
    passed = all(summary["passed"] for summary in summaries)
    has_setup_error = any(summary["setup_error"] for summary in summaries)

    if args.json:
        print(
            json.dumps(
                {
                    "passed": passed,
                    "setup_error": has_setup_error,
                    "missions": summaries,
                },
                indent=2,
            )
        )
    else:
        print("\n" + "=" * 72)
        for summary in summaries:
            if summary["setup_error"]:
                marker = "SETUP ERROR"
            elif summary["passed"]:
                marker = "PASS"
            else:
                marker = "INTENDED MISSION FAILURE"
            print(f"[{marker}] {summary['mission']}")

        if has_setup_error:
            print_setup_error()
        elif not passed:
            print("Expected baseline: mission checks fail until you complete that mission.")

    if has_setup_error:
        return 2
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
