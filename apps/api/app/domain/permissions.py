def can_add_claim_note(role: str, is_active_assignee: bool) -> bool:
    # MISSION_BUG(lv2-notes-rbac): assignment ownership is ignored.
    del is_active_assignee
    return role in {"admin", "supervisor", "adjuster"}
