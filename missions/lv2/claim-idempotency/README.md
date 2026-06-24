# Make claim submission idempotent

## Scenario

A client times out after submitting a claim and retries with the same `Idempotency-Key`. The API ignores the header, and side effects can be duplicated even if the external claim id catches one database insert.

## Broken behavior

`POST /claims` reads and discards `Idempotency-Key`. Claim creation and its initial event are committed separately.

## Constraints

- Require a nonblank idempotency key for submission.
- Make claim and initial event atomic.
- The same key and same payload returns the original response.
- The same key with a different payload returns `409`.

## Acceptance criteria

- Sequential and concurrent replays create one claim and one submission event.
- Replays have an explicit response signal or documented status behavior.
- Payload mismatch is detected using a stable representation.
- Database uniqueness is the final concurrency guard.

## Files likely involved

- `apps/api/app/routes/claims.py`
- `apps/api/app/models.py`
- `infra/docker/postgres/001_schema.sql`
- `tests/missions/test_lv2_claim_idempotency.py`

## How to run checks

```bash
python scripts/evaluate/run.py --mission lv2-claim-idempotency
```

## What not to do

- Do not rely on an in-memory dictionary.
- Do not treat `external_id` as a substitute for request idempotency.
- Do not commit the claim before its submission event.

## Interview reflection questions

- Where is the linearization point?
- How long should keys be retained?
- How would this change under Pub/Sub delivery?

## Evaluator notes

The evaluator includes two requests racing on one key and checks side-effect counts.

