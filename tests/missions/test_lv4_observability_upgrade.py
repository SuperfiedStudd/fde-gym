from pathlib import Path


def test_design_answers_incident_questions_and_alerts() -> None:
    design = Path("missions/lv4/observability-upgrade/DESIGN.md").read_text(encoding="utf-8")
    assert "TODO" not in design
    assert design.lower().count("alert") >= 2
    for term in ("rate", "errors", "duration", "queue delay", "runbook", "cardinality"):
        assert term in design.lower()


def test_worker_propagates_correlation_context() -> None:
    api_source = Path("apps/api/app/main.py").read_text(encoding="utf-8")
    worker_source = Path("apps/worker/worker/main.py").read_text(encoding="utf-8")
    assert "correlation_id" in api_source
    assert "correlation_id" in worker_source


def test_metrics_avoid_unbounded_identity_labels() -> None:
    source = Path("apps/api/app/metrics.py").read_text(encoding="utf-8")
    for unsafe in ('"claim_id"', '"user_id"', '"request_id"'):
        assert unsafe not in source

