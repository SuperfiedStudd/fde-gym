# Debug stale claim cache invalidation

## Scenario

After assignment or status changes, `GET /claims/{id}` can show the previous version for a minute. Operators refresh repeatedly and believe their write failed.

## Broken behavior

Point reads populate Redis, but mutation routes do not consistently delete or update the same key.

## Constraints

- Keep the cache-aside read path.
- Invalidate only after a successful database commit.
- Define whether Redis failure should fail or degrade the mutation.
- Centralize cache key construction.

## Acceptance criteria

- Assignment and transition mutations provide immediate read-after-write behavior.
- Failed database writes do not evict valid cached data.
- Cache deletion failures follow the documented policy and are logged.
- Tests use a fake Redis client and cover key consistency.

## Files likely involved

- `apps/api/app/routes/claims.py`
- `apps/api/app/cache.py`
- `tests/missions/test_lv2_cache_invalidation.py`

## How to run checks

```bash
python scripts/evaluate/run.py --mission lv2-cache-invalidation
```

## What not to do

- Do not disable caching or reduce TTL to hide the issue.
- Do not invalidate before the transaction commits.
- Do not use broad Redis key scans.

## Interview reflection questions

- Why is cache invalidation ordered after commit?
- When is write-through preferable?
- How would you monitor stale-read risk?

## Evaluator notes

The evaluator checks commit/invalidation ordering and simulated Redis outages.

