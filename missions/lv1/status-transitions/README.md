# Enforce claim status transitions

## Scenario

An operator accidentally moved a closed claim back to draft. The transition endpoint currently accepts every target state, so audit history can no longer be trusted.

## Broken behavior

`POST /claims/{id}/transition` applies the requested status without checking the current status.

## Constraints

- Model the policy in a pure, unit-testable function.
- Return `409 Conflict` for a known but invalid transition.
- Do not allow transitions out of `closed`.
- Keep the existing endpoint and request model.

## Acceptance criteria

- Allowed paths are `draft→submitted`, `submitted→reviewing`, `reviewing→approved|denied`, and `approved|denied→closed`.
- Same-state requests are rejected.
- Invalid transitions do not increment the version.
- Unit tests cover every state.

## Files likely involved

- `apps/api/app/routes/claims.py`
- `apps/api/app/domain/transitions.py`
- `tests/missions/test_lv1_status_transitions.py`

## How to run checks

```bash
python scripts/evaluate/run.py --mission lv1-status-transitions
```

## What not to do

- Do not scatter conditionals through the route.
- Do not return `404` for a transition-policy violation.
- Do not broaden the status enum.

## Interview reflection questions

- Why use an explicit state machine?
- Where should transition rules live in a larger system?
- What concurrent update risk remains after this mission?

## Evaluator notes

The transition matrix includes terminal and same-state cases that are not listed individually above.

