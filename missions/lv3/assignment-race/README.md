# Eliminate the claim assignment race

## Scenario

Two supervisors assign the same claim within milliseconds. Both requests return success and two active assignment rows remain, causing duplicate work.

## Broken behavior

The endpoint ignores `expected_version`, deactivates existing rows, and inserts a replacement without a database invariant that limits one active assignment.

## Constraints

- Enforce the invariant in Postgres and application logic.
- Use the supplied optimistic `expected_version` contract.
- Return `409` for a stale version.
- Keep assignment, claim version, and audit write atomic.

## Acceptance criteria

- Under concurrent requests, exactly one active assignment remains.
- At most one request succeeds for the same expected version.
- Database constraints protect non-API writers.
- The migration is safe for pre-existing duplicate rows.

## Files likely involved

- `apps/api/app/routes/claims.py`
- `apps/api/app/models.py`
- `infra/docker/postgres/`
- `tests/missions/test_lv3_assignment_race.py`

## How to run checks

```bash
python scripts/evaluate/run.py --mission lv3-assignment-race
```

## What not to do

- Do not use a process-local lock.
- Do not depend on request timing.
- Do not leave cleanup of existing duplicates undefined.

## Interview reflection questions

- Why combine optimistic concurrency with a database constraint?
- Which transaction isolation level is sufficient?
- How would retries interact with this endpoint?

## Evaluator notes

The integration evaluator issues concurrent transactions and independently checks the active-row invariant.

