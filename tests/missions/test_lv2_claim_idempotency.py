import sys
from pathlib import Path

sys.path.insert(0, str(Path("apps/api").resolve()))
from app.domain.idempotency import request_fingerprint


def test_fingerprint_is_stable_across_key_order() -> None:
    left = {"external_id": "CLM-2026-0042", "amount_cents": 1200, "category": "auto"}
    right = {"category": "auto", "amount_cents": 1200, "external_id": "CLM-2026-0042"}
    assert request_fingerprint(left) == request_fingerprint(right)


def test_submission_route_enforces_idempotency() -> None:
    source = Path("apps/api/app/routes/claims.py").read_text(encoding="utf-8")
    assert "del idempotency_key" not in source
    assert "request_fingerprint" in source
    assert "MISSION_BUG(lv2-claim-idempotency)" not in source

