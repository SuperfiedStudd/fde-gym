# Make claims pagination real

## Scenario

The mission browser reports `page` and `page_size`, but the claims endpoint returns every record. Payload size grows with the database and operators see duplicate rows when timestamps tie.

## Broken behavior

`GET /claims?page=2&page_size=10` still returns all claims. The ordering has no deterministic tiebreaker.

## Constraints

- Keep page-number pagination for this mission.
- Perform pagination in Postgres, not Python.
- `total` must describe the filtered result before pagination.
- Respect the existing maximum page size.

## Acceptance criteria

- SQL receives the correct offset and limit.
- Ordering is deterministic across equal `created_at` values.
- Empty pages return an empty `items` list with the correct `total`.
- Filtering and pagination compose correctly.

## Files likely involved

- `apps/api/app/routes/claims.py`
- `tests/missions/test_lv1_claims_pagination.py`

## How to run checks

```bash
python scripts/evaluate/run.py --mission lv1-claims-pagination
```

## What not to do

- Do not slice a fully loaded Python list.
- Do not change this endpoint to cursors yet.
- Do not calculate `total` after applying the limit.

## Interview reflection questions

- What are the tradeoffs of offset versus cursor pagination?
- Why does stable ordering matter?
- Which index supports this access pattern?

## Evaluator notes

The evaluator checks generated SQL and may use records with identical timestamps.

