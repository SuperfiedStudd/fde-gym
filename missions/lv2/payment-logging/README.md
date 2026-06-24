# Instrument the payment simulation flow

## Scenario

The payment simulator emits `starting payment` and `payment result`. During an incident there is no claim id, request id, duration, or searchable event name.

## Broken behavior

The route uses `print`, logs inconsistent arguments, and provides no structured context for skipped versus queued outcomes.

## Constraints

- Use the configured Python logger and structured fields.
- Emit stable event names for start and finish/failure.
- Include request id, claim id, outcome, and duration.
- Never log claimant names, raw request bodies, or credentials.

## Acceptance criteria

- Every outcome has a completion event with required context.
- Exceptions log an error class and preserve the HTTP behavior.
- No `print` remains in the payment path.
- Tests capture and assert log records rather than stdout text.

## Files likely involved

- `apps/api/app/routes/claims.py`
- `apps/api/app/main.py`
- `tests/missions/test_lv2_payment_logging.py`

## How to run checks

```bash
python scripts/evaluate/run.py --mission lv2-payment-logging
```

## What not to do

- Do not log the entire claim object.
- Do not change successful response semantics.
- Do not generate a second unrelated correlation id.

## Interview reflection questions

- What makes a log field high-cardinality?
- How do logs differ from metrics and traces?
- What information did you deliberately exclude?

## Evaluator notes

The evaluator checks queued, skipped, not-found, and exception paths for context and unsafe fields.

