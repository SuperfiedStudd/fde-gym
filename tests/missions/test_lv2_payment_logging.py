from pathlib import Path


def test_payment_flow_uses_structured_logging() -> None:
    source = Path("apps/api/app/routes/claims.py").read_text(encoding="utf-8")
    payment_flow = source[source.index("async def simulate_payment") :]
    assert "print(" not in payment_flow
    assert "logger." in payment_flow
    for field in ("request_id", "claim_id", "outcome", "duration_ms"):
        assert field in payment_flow
    assert "MISSION_BUG(lv2-payment-logging)" not in payment_flow


def test_payment_flow_avoids_sensitive_logging() -> None:
    source = Path("apps/api/app/routes/claims.py").read_text(encoding="utf-8")
    payment_flow = source[source.index("async def simulate_payment") :]
    assert "claimant_name" not in payment_flow

