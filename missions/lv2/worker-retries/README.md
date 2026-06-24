# Stop the worker from dropping failed jobs

## Scenario

The document renderer has intermittent failures. ClaimOps marks a job failed on its first exception and Redis has already removed it, so no retry or investigation path remains.

## Broken behavior

The worker uses destructive queue reads, never increments `attempts`, never schedules retry delay, and never uses its configured dead-letter queue.

## Constraints

- Cap attempts using each job's `max_attempts`.
- Use deterministic bounded backoff that is testable without sleeping.
- Persist state before acknowledging/removing work.
- Keep Redis and Postgres responsibilities explicit.

## Acceptance criteria

- Retryable failures move to `retry`, increment attempts, and become available later.
- Exhausted or non-retryable failures move to `failed` and the dead-letter queue once.
- A worker crash cannot silently discard an acknowledged job.
- Logs include job id, kind, attempt, outcome, and error class.

## Files likely involved

- `apps/worker/worker/main.py`
- `apps/worker/worker/handlers.py`
- `tests/missions/test_lv2_worker_retries.py`

## How to run checks

```bash
python scripts/evaluate/run.py --mission lv2-worker-retries
```

## What not to do

- Do not retry forever.
- Do not retry unknown job kinds.
- Do not hide exceptions or use real sleeps in unit tests.

## Interview reflection questions

- What delivery guarantee does your design provide?
- When should a failure be dead-lettered immediately?
- How would multiple workers safely claim jobs?

## Evaluator notes

Failure classification, attempt boundaries, and duplicate dead-letter writes are exercised with fakes.

