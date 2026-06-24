# Repair role-based access for claim notes

## Scenario

An adjuster can add internal notes to any claim by guessing its UUID. Authentication works, but authorization stops at the user's role and never considers the claim assignment.

## Broken behavior

All active adjusters are allowed to write all claim notes. Successful note writes also lack an audit entry.

## Constraints

- Admins and supervisors may write any note.
- Adjusters may write only on claims actively assigned to them.
- Auditors remain read-only.
- Keep authorization server-side and return `403` without revealing assignment details.

## Acceptance criteria

- The complete role/assignment matrix is tested.
- Inactive assignments do not grant access.
- Authorized writes create a note and audit record atomically.
- Denied writes create neither.

## Files likely involved

- `apps/api/app/auth.py`
- `apps/api/app/routes/claims.py`
- `apps/api/app/models.py`
- `tests/missions/test_lv2_notes_rbac.py`

## How to run checks

```bash
python scripts/evaluate/run.py --mission lv2-notes-rbac
```

## What not to do

- Do not trust a role or claim id supplied in the body.
- Do not return assignment data in an authorization error.
- Do not duplicate policy logic across route handlers.

## Interview reflection questions

- What is the difference between authentication and authorization?
- Why include resource ownership in policy tests?
- Where would centralized policy tooling become worthwhile?

## Evaluator notes

The evaluator includes inactive users, released assignments, and unauthorized-resource cases.

