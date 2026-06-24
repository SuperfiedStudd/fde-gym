from pathlib import Path


def test_route_uses_expected_version() -> None:
    source = Path("apps/api/app/routes/claims.py").read_text(encoding="utf-8")
    assert "claim.version != payload.expected_version" in source
    assert "status_code=409" in source
    assert "MISSION_BUG(lv3-assignment-race)" not in source


def test_database_enforces_one_active_assignment() -> None:
    migration_dir = Path("infra/gcp/migrations")
    sql = "\n".join(path.read_text(encoding="utf-8") for path in migration_dir.glob("*.sql")) if migration_dir.exists() else ""
    assert "UNIQUE" in sql.upper()
    assert "WHERE active" in sql

