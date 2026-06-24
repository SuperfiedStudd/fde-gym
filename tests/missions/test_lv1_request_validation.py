import sys
from pathlib import Path
from uuid import UUID

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path("apps/api").resolve()))
from app.schemas import ClaimCreate

BASE = {
    "external_id": "CLM-2026-0042",
    "claimant_name": "Morgan Avery",
    "amount_cents": 12_500,
    "category": "property",
    "created_by": UUID("10000000-0000-0000-0000-000000000001"),
}


@pytest.mark.parametrize(
    ("field", "value"),
    [("claimant_name", "   "), ("external_id", "42"), ("amount_cents", 0), ("amount_cents", 100_000_001)],
)
def test_invalid_claim_payloads_are_rejected(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        ClaimCreate.model_validate({**BASE, field: value})


def test_valid_claim_payload_remains_valid() -> None:
    assert ClaimCreate.model_validate(BASE).external_id == "CLM-2026-0042"

