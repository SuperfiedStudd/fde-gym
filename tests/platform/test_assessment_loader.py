import json
from pathlib import Path

import pytest

from scripts.assessment.load import load_bundle, validate_bundle


def write_bundle(root: Path, resource_path: str = "input.csv") -> Path:
    root.mkdir()
    root.joinpath("resources").mkdir()
    root.joinpath("prompt.md").write_text("# Candidate prompt\n", encoding="utf-8")
    root.joinpath("resources", "input.csv").write_text("id,value\n1,ok\n", encoding="utf-8")
    root.joinpath("interviewer-answer-key.md").write_text("hidden", encoding="utf-8")
    root.joinpath("assessment.json").write_text(
        json.dumps(
            {
                "id": "test-assessment",
                "title": "Test assessment",
                "duration_minutes": 30,
                "difficulty": "introductory",
                "focus": ["diagnosis"],
                "resources": [{"path": resource_path, "label": "Input"}],
            }
        ),
        encoding="utf-8",
    )
    return root


def test_load_bundle_replaces_current_slot(tmp_path: Path) -> None:
    source = write_bundle(tmp_path / "source")
    destination = tmp_path / "current"
    destination.mkdir()
    destination.joinpath("stale.txt").write_text("stale", encoding="utf-8")

    payload = load_bundle(source, destination)

    assert payload["id"] == "test-assessment"
    assert destination.joinpath("prompt.md").is_file()
    assert destination.joinpath("resources", "input.csv").is_file()
    assert not destination.joinpath("stale.txt").exists()
    assert not destination.joinpath("interviewer-answer-key.md").exists()


def test_validate_bundle_rejects_resource_traversal(tmp_path: Path) -> None:
    source = write_bundle(tmp_path / "source", "../secret.txt")

    with pytest.raises(ValueError, match="must be a filename"):
        validate_bundle(source)


def test_tracked_example_is_valid() -> None:
    payload = validate_bundle(Path("assessment/examples/customer-support-triage"))
    assert payload["id"] == "customer-support-triage"
