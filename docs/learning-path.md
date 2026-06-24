# Four-week learning path

## Week 1: LV1 fundamentals

Work in order: request validation, unit test repair, status transitions, pagination, SQL filtering. Practice reading the call path before editing, reproducing each failure, keeping diffs narrow, and explaining API/database boundaries.

Suggested cadence: one mission per focused session, then one review session to compare the five fixes and extract interview stories.

## Week 2: LV2 backend ownership and tests

Work through worker retries, submission idempotency, note authorization, cache invalidation, and structured payment logging. Emphasize integration boundaries: transaction scope, resource authorization, acknowledgment, failure policy, and searchable context.

For each mission, draw the failure sequence before coding and add one test for the unhappy path that caused the incident.

## Week 3: LV3 reliability and debugging

Start with the async processor, then assignment concurrency and search latency. Finish with the deployment incident. Collect hard evidence: coroutine lifecycle, concurrent outcomes, query plans, timestamps, and release diffs.

Write the technical note or postmortem as part of the engineering work—not as cleanup after the code.

## Week 4: LV4 production ownership

Run the multi-service incident, rollback-safe event migration, and observability design. These missions are intentionally broader. State your assumptions, choose a narrow mitigation, and distinguish must-have safety from speculative architecture.

Ask another engineer—or Codex in review-only mode—to challenge the incident note and tradeoffs without implementing your solution.

## Ongoing: interview story extraction

After every mission, fill one entry in [interview-story-bank.md](interview-story-bank.md). Practice a 90-second version and a five-minute deep dive. Focus on:

- how you found the root cause;
- the invariant your fix restored;
- tests and rollout safety;
- a real tradeoff, not a generic best practice;
- what you would change at greater scale.

