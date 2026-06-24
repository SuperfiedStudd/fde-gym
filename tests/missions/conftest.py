from pathlib import Path

import pytest


ROUTE_GUARDS = {
    "test_lv1_status_transitions": "is_transition_allowed",
    "test_lv1_claims_pagination": "pagination_window",
    "test_lv1_sql_status_filter": "apply_status_filter",
    "test_lv2_claim_idempotency": "request_fingerprint",
    "test_lv2_notes_rbac": "can_add_claim_note",
}


@pytest.fixture(autouse=True)
def require_route_integration(request: pytest.FixtureRequest) -> None:
    """Prevent a pure helper repair from leaving the HTTP behavior unchanged."""
    required_symbol = ROUTE_GUARDS.get(request.module.__name__.rsplit(".", 1)[-1])
    if required_symbol is None:
        return
    source = Path("apps/api/app/routes/claims.py").read_text(encoding="utf-8")
    assert required_symbol in source, f"integrate {required_symbol} into the claims route"

