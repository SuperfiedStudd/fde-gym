import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path("apps/api").resolve()))
from app.domain.transitions import is_transition_allowed


@pytest.mark.parametrize(
    ("current", "target"),
    [("draft", "submitted"), ("submitted", "reviewing"), ("reviewing", "approved"), ("reviewing", "denied"), ("approved", "closed"), ("denied", "closed")],
)
def test_allowed_transitions(current: str, target: str) -> None:
    assert is_transition_allowed(current, target)


@pytest.mark.parametrize("current,target", [("closed", "draft"), ("draft", "approved"), ("approved", "denied"), ("reviewing", "reviewing")])
def test_invalid_transitions(current: str, target: str) -> None:
    assert not is_transition_allowed(current, target)

