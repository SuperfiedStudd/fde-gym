# Stabilize a multi-service claims incident

## Scenario

At 09:20, claim submission latency climbs, Redis queue depth oscillates, worker restarts increase, and Postgres connections saturate. Individual services appear mostly healthy between spikes. You own diagnosis, mitigation, and the durable repair.

## Broken behavior

Several seeded defects can interact: destructive queue reads, missing awaits, aggressive concurrency, small database pools, and weak operational signals. Not every defect is causal. Establish which chain explains the evidence.

## Constraints

- Start with a reproducible hypothesis and incident timeline.
- Make the smallest safe mitigation before broad refactoring.
- Preserve at-least-once processing and bound database pressure.
- Include rollback, load verification, and residual risks.

## Acceptance criteria

- `INCIDENT-NOTE.md` correlates evidence across all four components.
- A deterministic reproduction captures the pre-fix failure mode.
- The repair prevents job loss and connection exhaustion under the supplied load profile.
- Safety checks, regression tests, and a rollback plan are included.
- Tradeoffs between throughput, latency, and durability are explicit.

## Files likely involved

- `apps/api/`
- `apps/worker/`
- `docker-compose.yml`
- `missions/lv4/multi-service-incident/evidence/`
- `missions/lv4/multi-service-incident/INCIDENT-NOTE.md`

## How to run checks

```bash
python scripts/evaluate/run.py --mission lv4-multi-service-incident
```

## What not to do

- Do not rewrite every service.
- Do not increase every pool or timeout without a capacity model.
- Do not declare success from a unit test alone.

## Interview reflection questions

- How did you narrow a noisy multi-service failure?
- Which mitigation reduced risk fastest?
- What tradeoff would you revisit at 10× traffic?

## Evaluator notes

Automated checks cover reproducibility and core invariants; diagnosis quality and scope discipline require a human review of the incident note.

