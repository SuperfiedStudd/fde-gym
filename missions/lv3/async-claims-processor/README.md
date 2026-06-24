# Fix the asynchronous claims processor

## Scenario

The queue drains and jobs become `completed`, yet no `claim.processed` events appear. Runtime warnings mention a coroutine that was never awaited, but only under some logging configurations.

## Broken behavior

The `claim.process` dispatch path creates asynchronous work without waiting for it. The worker marks the job complete before the database effect exists.

## Constraints

- Preserve sequential completion semantics for one job.
- A handler exception must prevent `completed` status.
- Do not hide the warning or schedule untracked background tasks.
- Add a regression test that proves the database call completes first.

## Acceptance criteria

- Dispatch awaits all supported async handlers.
- Handler failures propagate to the retry/failure policy.
- A job is marked complete only after side effects complete.
- Unknown kinds remain explicit failures.

## Files likely involved

- `apps/worker/worker/handlers.py`
- `apps/worker/worker/main.py`
- `tests/missions/test_lv3_async_claims_processor.py`

## How to run checks

```bash
python scripts/evaluate/run.py --mission lv3-async-claims-processor
```

## What not to do

- Do not suppress `RuntimeWarning`.
- Do not use `asyncio.create_task` without ownership and lifecycle handling.
- Do not mark jobs complete optimistically.

## Interview reflection questions

- Why can a missing `await` look like success?
- How would task supervision change for parallel handlers?
- Which telemetry would have shortened detection time?

## Evaluator notes

The evaluator uses an async probe that remains incomplete unless dispatch truly awaits it.

