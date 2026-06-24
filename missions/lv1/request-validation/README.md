# Harden claim request validation

## Scenario

ClaimOps is accepting incomplete claimant names, zero-value claims, and malformed external IDs. Downstream jobs assume those fields are valid and fail much later, making the source of the problem hard to see.

## Broken behavior

`POST /claims` does not enforce the domain boundary. Several invalid `ClaimCreate` payloads currently pass model validation.

## Constraints

- Keep the existing JSON field names and successful response shape.
- Return FastAPI's normal `422` validation response for invalid input.
- Put validation at the typed request boundary, not in the route body.
- Do not add a new validation dependency.

## Acceptance criteria

- `claimant_name` is nonblank after whitespace is considered.
- `external_id` follows `CLM-YYYY-NNNN`.
- `amount_cents` is strictly positive and capped at 100,000,000.
- Existing valid seed-style payloads remain valid.
- Focused tests cover boundary values, not only happy paths.

## Files likely involved

- `apps/api/app/schemas.py`
- `tests/missions/test_lv1_request_validation.py`

## How to run checks

```bash
python scripts/evaluate/run.py --mission lv1-request-validation
```

## What not to do

- Do not silently coerce invalid values.
- Do not catch every validation error and return `500`.
- Do not change the database constraint to compensate for a weak API contract.

## Interview reflection questions

- Why validate at both the API and database layers?
- Which compatibility risks did you consider?
- How did you choose the boundary cases in your tests?

## Evaluator notes

The evaluator exercises several invalid inputs and one valid control payload. Exact implementation details are intentionally not checked.

