# Correct the claim status filter

## Scenario

Supervisors know submitted claims exist, but `GET /claims?status=submitted` returns an empty list. The total count agrees with the wrong result, which initially makes the endpoint look internally consistent.

## Broken behavior

The status parameter is bound against an unrelated column in both the data and count queries.

## Constraints

- Fix the predicate in both query paths.
- Keep values parameterized through SQLAlchemy.
- Preserve behavior when the filter is absent.
- Add a focused regression test.

## Acceptance criteria

- `status=submitted` filters on `claims.status`.
- Items and `total` use identical filtering semantics.
- The unfiltered endpoint still returns all eligible claims.
- No raw string interpolation is introduced.

## Files likely involved

- `apps/api/app/routes/claims.py`
- `tests/missions/test_lv1_sql_status_filter.py`

## How to run checks

```bash
python scripts/evaluate/run.py --mission lv1-sql-status-filter
```

## What not to do

- Do not special-case seeded values.
- Do not filter results after fetching them.
- Do not suppress a failing count assertion.

## Interview reflection questions

- How would you inspect generated SQL?
- Why must count and item queries share semantics?
- What test catches this with the least setup?

## Evaluator notes

The evaluator inspects query behavior rather than searching for a particular source string.

