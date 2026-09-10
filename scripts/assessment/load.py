#!/usr/bin/env python3
"""Validate and load a candidate-safe assessment bundle into the local current slot."""

import argparse
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CURRENT = ROOT / "assessment" / "current"
REQUIRED_FIELDS = {
    "id",
    "title",
    "duration_minutes",
    "difficulty",
    "focus",
    "resources",
}


def validate_bundle(source: Path) -> dict[str, object]:
    if not source.is_dir():
        raise ValueError(f"assessment directory does not exist: {source}")

    manifest_path = source / "assessment.json"
    prompt_path = source / "prompt.md"
    if not manifest_path.is_file() or not prompt_path.is_file():
        raise ValueError("bundle must contain assessment.json and prompt.md")

    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"cannot read assessment.json: {exc}") from exc

    if not isinstance(payload, dict) or set(payload) != REQUIRED_FIELDS:
        raise ValueError(
            "assessment.json must contain exactly: " + ", ".join(sorted(REQUIRED_FIELDS))
        )
    string_fields = ("id", "title", "difficulty")
    if not all(
        isinstance(payload[field], str) and payload[field].strip() for field in string_fields
    ):
        raise ValueError("id, title, and difficulty must be non-empty strings")
    duration = payload["duration_minutes"]
    if not isinstance(duration, int) or isinstance(duration, bool) or duration <= 0:
        raise ValueError("duration_minutes must be a positive integer")
    focus = payload["focus"]
    if (
        not isinstance(focus, list)
        or not focus
        or not all(isinstance(item, str) and item.strip() for item in focus)
    ):
        raise ValueError("focus must be a non-empty list of strings")
    resources = payload["resources"]
    if not isinstance(resources, list):
        raise ValueError("resources must be a list")

    resources_root = source / "resources"
    for resource in resources:
        if (
            not isinstance(resource, dict)
            or not {"path", "label"}
            <= set(resource)
            <= {"path", "label", "description"}
        ):
            raise ValueError("each resource requires path and label, with optional description")
        if not all(
            isinstance(resource.get(field), str) and resource[field].strip()
            for field in ("path", "label")
        ):
            raise ValueError("resource path and label must be non-empty strings")
        resource_path = Path(resource["path"])
        if resource_path.name != resource["path"] or resource_path.is_absolute():
            raise ValueError(f"resource path must be a filename: {resource['path']}")
        if not resources_root.joinpath(resource_path).is_file():
            raise ValueError(f"listed resource does not exist: {resource['path']}")

    return payload


def load_bundle(source: Path, destination: Path = CURRENT) -> dict[str, object]:
    source = source.resolve()
    payload = validate_bundle(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".assessment-", dir=destination.parent))
    try:
        bundle = temporary / "bundle"
        bundle.joinpath("resources").mkdir(parents=True)
        shutil.copy2(source / "assessment.json", bundle / "assessment.json")
        shutil.copy2(source / "prompt.md", bundle / "prompt.md")
        for resource in payload["resources"]:
            resource_path = resource["path"]
            shutil.copy2(
                source / "resources" / resource_path,
                bundle / "resources" / resource_path,
            )
        if destination.exists():
            shutil.rmtree(destination)
        bundle.replace(destination)
    finally:
        shutil.rmtree(temporary, ignore_errors=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("assessment_directory", type=Path)
    args = parser.parse_args()
    try:
        payload = load_bundle(args.assessment_directory)
    except ValueError as exc:
        parser.error(str(exc))
    print(f"Loaded {payload['id']} into {CURRENT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
