from pathlib import Path


def test_incident_note_is_complete() -> None:
    note = Path("missions/lv4/multi-service-incident/INCIDENT-NOTE.md").read_text(encoding="utf-8")
    assert "TODO" not in note
    for term in ("Redis", "Postgres", "worker", "API", "rollback", "residual risk"):
        assert term.lower() in note.lower()


def test_reproduction_and_load_regression_exist() -> None:
    mission = Path("missions/lv4/multi-service-incident")
    assert (mission / "reproduce.py").exists()
    assert (mission / "verify_load.py").exists()

