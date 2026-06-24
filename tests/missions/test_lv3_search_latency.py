from pathlib import Path


def test_search_query_has_separate_exact_and_prefix_paths() -> None:
    source = Path("apps/api/app/routes/claims.py").read_text(encoding="utf-8")
    assert 'f"%{search.lower()}%"' not in source
    assert "external_id" in source[source.index("async def list_claims") : source.index("async def get_claim")]


def test_performance_note_contains_evidence() -> None:
    note = Path("missions/lv3/search-latency/TECHNICAL-NOTE.md").read_text(encoding="utf-8")
    assert "TODO" not in note
    assert "EXPLAIN" in note.upper()
    assert "rollback" in note.lower()


def test_index_change_is_versioned() -> None:
    migrations = list(Path("infra/gcp/migrations").glob("*.sql")) if Path("infra/gcp/migrations").exists() else []
    assert migrations, "add a versioned SQL migration; do not edit only the bootstrap schema"

