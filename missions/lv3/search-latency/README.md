# Reduce claim search p95 latency

## Scenario

Search p95 rose above 650 ms as the claims table grew. The endpoint lowercases a column and applies a leading wildcard, producing sequential scans even when users enter a full external id or claimant prefix.

## Broken behavior

One broad predicate handles every search mode. Existing indexes cannot support it, and the item/count queries repeat the expensive scan.

## Constraints

- Capture a before/after `EXPLAIN (ANALYZE, BUFFERS)` in your technical note.
- Preserve case-insensitive claimant prefix search and exact external-id lookup.
- Add indexes through a migration, not only the seed schema.
- Avoid an index that blocks writes for an unreasonable period.

## Acceptance criteria

- Exact external ids and claimant prefixes use appropriate plans.
- Search semantics and pagination totals remain correct.
- Migration includes a rollback and production-safe index creation rationale.
- The note explains expected read/write/storage tradeoffs.

## Files likely involved

- `apps/api/app/routes/claims.py`
- `infra/docker/postgres/`
- `missions/lv3/search-latency/TECHNICAL-NOTE.md`
- `tests/missions/test_lv3_search_latency.py`

## How to run checks

```bash
python scripts/evaluate/run.py --mission lv3-search-latency
```

## What not to do

- Do not claim improvement without query-plan evidence.
- Do not load all rows into Python.
- Do not remove supported search behavior to make the benchmark pass.

## Interview reflection questions

- Why did the original expression defeat a normal index?
- When is `pg_trgm` appropriate?
- How would you validate performance under production cardinality?

## Evaluator notes

Static checks validate the migration and note; integration checks verify query semantics. Plan quality still requires your recorded evidence.

