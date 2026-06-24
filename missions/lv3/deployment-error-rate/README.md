# Investigate the post-deployment error spike

## Scenario

Five minutes after release `2026.06.17-rc3`, API error rate rises from 0.4% to 7.8%. Claim reads remain healthy; submission and payment simulation errors increase. A captured log bundle and deployment diff are provided.

## Broken behavior

This mission is intentionally ambiguous. The evidence under `evidence/` contains both relevant signals and noise. Determine the causal chain before changing code.

## Constraints

- Write a timeline before implementing a fix.
- Distinguish mitigation from permanent correction.
- Preserve raw evidence; add annotations separately.
- Add a regression guard tied to the demonstrated root cause.

## Acceptance criteria

- `POSTMORTEM.md` identifies impact, detection, timeline, root cause, contributing factors, mitigation, and follow-ups.
- Claims are supported by timestamps or code/config evidence.
- The mitigation is safe to roll back.
- The regression test fails against the captured faulty condition.

## Files likely involved

- `missions/lv3/deployment-error-rate/evidence/`
- `missions/lv3/deployment-error-rate/POSTMORTEM.md`
- `.github/workflows/ci.yml`
- Service configuration identified during investigation

## How to run checks

```bash
python scripts/evaluate/run.py --mission lv3-deployment-error-rate
```

## What not to do

- Do not edit evidence files.
- Do not assert root cause from temporal correlation alone.
- Do not write “add more monitoring” without a concrete signal and owner.

## Interview reflection questions

- What evidence changed your leading hypothesis?
- Why was the chosen mitigation lower risk?
- How would you communicate uncertainty during the incident?

## Evaluator notes

The evaluator checks required postmortem sections and a regression artifact, while human judgment is required for causal quality.

