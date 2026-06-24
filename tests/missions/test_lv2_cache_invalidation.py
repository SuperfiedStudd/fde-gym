from pathlib import Path


def test_mutations_use_shared_cache_key_and_invalidate() -> None:
    source = Path("apps/api/app/routes/claims.py").read_text(encoding="utf-8")
    assert "claim_cache_key" in source
    assert "await redis.delete" in source
    assert "MISSION_BUG(lv2-cache-invalidation)" not in source


def test_cache_key_is_centralized() -> None:
    source = Path("apps/api/app/routes/claims.py").read_text(encoding="utf-8")
    assert 'f"claim:{claim_id}"' not in source

