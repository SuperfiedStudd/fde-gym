# Ship a rollback-safe claim event migration

## Scenario

Claim event consumers need a required `schema_version` and searchable `actor_id`. The table is high-write, old workers may run for several minutes during a rolling deploy, and a direct `NOT NULL` rewrite is unsafe.

## Broken behavior

No migration exists. A naive one-step change would break old writers, lock the event table, and provide no safe application rollback.

## Constraints

- Use explicit expand, migrate/backfill, enforce, and contract phases.
- Old and new application versions must overlap safely.
- Backfill must be batched, resumable, observable, and idempotent.
- Include forward and rollback operator commands.

## Acceptance criteria

- Versioned SQL migrations and a backfill command are provided.
- The compatibility window and dual-read/write behavior are documented.
- Constraint enforcement avoids a long blocking validation path.
- A runbook defines prechecks, metrics, pause conditions, rollback, and completion.
- Tests cover old-writer and new-writer rows during the transition.

## Files likely involved

- `infra/gcp/migrations/`
- `apps/api/app/models.py`
- `apps/worker/`
- `scripts/migrations/`
- `missions/lv4/rollback-safe-event-migration/RUNBOOK.md`

## How to run checks

```bash
python scripts/evaluate/run.py --mission lv4-rollback-safe-event-migration
```

## What not to do

- Do not edit only the bootstrap schema.
- Do not add a table-wide default and `NOT NULL` in one blocking step.
- Do not assume application rollback also rolls back data.

## Interview reflection questions

- Why separate expand and contract?
- How do you validate a constraint with less lock risk?
- What makes a backfill safely resumable?

## Evaluator notes

The evaluator checks migration structure and compatibility tests; a reviewer should still assess operational realism.

