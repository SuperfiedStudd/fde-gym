# Mission authoring

## Design rule

A good mission has one primary engineering judgment, one reproducible failure, and a boundary that keeps neighboring missions intact. Seed realistic context, not a maze of unrelated defects.

## Required files

Create `missions/lvN/<slug>/mission.json`:

```json
{
  "id": "lv2-example-id",
  "title": "Verb-led operation title",
  "level": "LV2",
  "skill": "Primary skill",
  "labels": ["bugfix", "api"],
  "summary": "One sentence describing the engineering outcome.",
  "estimated_minutes": 75,
  "checks": ["behavior signal", "regression signal"]
}
```

Add `README.md` with these exact sections:

- Scenario
- Broken behavior
- Constraints
- Acceptance criteria
- Files likely involved
- How to run checks
- What not to do
- Interview reflection questions
- Evaluator notes

Add `tests/missions/test_<mission_id_with_underscores>.py` and an entry in `LINT_TARGETS` in `scripts/evaluate/catalog.py` when targeted Ruff checks add value.

## Seed the defect

- Mark the primary seam with `MISSION_BUG(<mission-id>)`.
- Make the baseline evaluator fail for the stated behavior.
- Keep ordinary platform smoke tests green.
- Do not hide a second unrelated bug behind the first.
- Prefer pure policy helpers or dependency fakes for fast checks; use Docker integration tests when transaction, concurrency, or query behavior is the actual skill.

## Evaluation quality

Acceptance tests should assert externally meaningful behavior. Static checks are useful for artifact existence, unsafe source patterns, migration structure, or incomplete notes, but should not replace behavior tests where behavior is cheap to exercise.

The evaluator may expose check names without revealing every input. Avoid brittle implementation checks unless the mission explicitly requires an operational artifact or invariant.

## Review checklist

- Does the title describe an engineering action?
- Can the learner reproduce the failure in under ten minutes?
- Is the intended scope possible in the estimate?
- Do constraints prevent shortcuts without dictating the exact implementation?
- Does the test fail before the repair and pass after a representative repair?
- Is there at least one useful interview reflection question?
- Can local seed/reset restore the starter state?

