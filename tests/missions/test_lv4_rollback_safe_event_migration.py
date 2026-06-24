from pathlib import Path


def test_runbook_has_no_placeholders_and_covers_rollback() -> None:
    runbook = Path("missions/lv4/rollback-safe-event-migration/RUNBOOK.md").read_text(encoding="utf-8")
    assert "TODO" not in runbook
    for term in ("precondition", "backfill", "monitor", "pause", "rollback", "contract"):
        assert term in runbook.lower()


def test_versioned_migrations_and_backfill_exist() -> None:
    migration_dir = Path("infra/gcp/migrations")
    names = {path.name for path in migration_dir.glob("*.sql")} if migration_dir.exists() else set()
    assert any("expand" in name for name in names)
    assert any("contract" in name for name in names)
    assert Path("scripts/migrations/backfill_claim_events.py").exists()


def test_expand_is_compatible_with_old_writers() -> None:
    migration_dir = Path("infra/gcp/migrations")
    expand = "\n".join(path.read_text(encoding="utf-8") for path in migration_dir.glob("*expand*.sql")) if migration_dir.exists() else ""
    assert "NOT NULL" not in expand.upper()

