import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path("apps/api").resolve()))
from app.domain.fees import calculate_review_fee

CASES = [
    {"amount": 0, "expected": 500},
    {"amount": 100_000, "expected": 1_000},
    {"amount": 2_000_000, "expected": 2_000},
]


@pytest.mark.parametrize("case", CASES)
def test_review_fee_policy(case: dict[str, int]) -> None:
    # The expectations above are intentionally stale. Repair this suite, not production code.
    assert calculate_review_fee(case["amount"]) == case["expected"]

