from pathlib import Path


def test_postmortem_is_complete_and_evidence_based() -> None:
    note = Path("missions/lv3/deployment-error-rate/POSTMORTEM.md").read_text(encoding="utf-8")
    assert "TODO" not in note
    for section in ("Impact", "Detection", "Timeline", "Root cause", "Contributing factors", "Mitigation", "Regression", "Follow-up"):
        assert section.lower() in note.lower()
    assert "2026-06-17" in note


def test_regression_artifact_exists() -> None:
    artifacts = list(Path("tests/missions/regressions").glob("*deployment*")) if Path("tests/missions/regressions").exists() else []
    assert artifacts, "add a focused regression test for the demonstrated faulty condition"

