import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path("apps/api").resolve()))
from app.domain.permissions import can_add_claim_note


@pytest.mark.parametrize("role", ["admin", "supervisor"])
def test_privileged_roles_can_add_notes(role: str) -> None:
    assert can_add_claim_note(role, is_active_assignee=False)


def test_adjuster_requires_active_assignment() -> None:
    assert can_add_claim_note("adjuster", is_active_assignee=True)
    assert not can_add_claim_note("adjuster", is_active_assignee=False)


@pytest.mark.parametrize("role", ["auditor", "unknown"])
def test_read_only_roles_are_denied(role: str) -> None:
    assert not can_add_claim_note(role, is_active_assignee=True)


def test_route_queries_assignments_and_writes_audit() -> None:
    source = Path("apps/api/app/routes/claims.py").read_text(encoding="utf-8")
    assert "Assignment.active" in source
    assert "AuditLog(" in source
    assert "MISSION_BUG(lv2-notes-rbac)" not in source

