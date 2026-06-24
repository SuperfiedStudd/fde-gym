# Repair a misleading unit test suite

## Scenario

A policy update changed the review fee thresholds. Production code was updated and peer-reviewed, but its tests still encode the old thresholds and share a mutable fixture. The suite now fails inconsistently.

## Broken behavior

The focused unit suite has stale expectations and test-order coupling. The implementation is the supplied contract for this mission.

## Constraints

- Change tests and fixtures only.
- Preserve the public `calculate_review_fee` behavior.
- Keep each test independent and readable.
- Add at least one threshold boundary case.

## Acceptance criteria

- The focused suite passes in normal and reversed order.
- Tests cover zero, the 100,000-cent boundary, and a high-value claim.
- No test mutates data shared with another test.
- Production code is unchanged.

## Files likely involved

- `apps/api/app/domain/fees.py`
- `tests/missions/test_lv1_unit_test_repair.py`

## How to run checks

```bash
python scripts/evaluate/run.py --mission lv1-unit-test-repair
```

## What not to do

- Do not change the implementation to satisfy stale assertions.
- Do not delete failing cases or replace assertions with weaker ones.
- Do not introduce network or database fixtures.

## Interview reflection questions

- How did you decide whether code or tests were wrong?
- What makes a fixture safe to reuse?
- How would you detect order-dependent tests in CI?

## Evaluator notes

The evaluator snapshots the production module and runs the suite in two deterministic orders.

