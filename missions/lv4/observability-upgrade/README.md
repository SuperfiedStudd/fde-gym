# Build a cross-service observability upgrade

## Scenario

ClaimOps has JSON API access logs and a few Prometheus metrics, but correlation stops at service boundaries. Worker incidents require manual grep across unrelated ids and there are no actionable service objectives.

## Broken behavior

Request ids are not propagated into events/jobs, job logs lack a stable trace/correlation model, and metrics cannot distinguish queue delay from processing duration.

## Constraints

- Stay OpenTelemetry-friendly without requiring a paid backend.
- Define a small, consistent semantic field vocabulary.
- Bound metric label cardinality.
- Provide local Prometheus value and a Cloud Logging/Trace path for GCP.

## Acceptance criteria

- Correlation context propagates API → event/job → worker logs.
- RED metrics exist for APIs and queue delay/processing/outcome metrics for jobs.
- A dashboard answers the three incident questions in `DESIGN.md`.
- Two actionable alerts include thresholds, windows, and runbook links.
- Tests prove propagation and reject unsafe metric labels.

## Files likely involved

- `apps/api/app/main.py`
- `apps/api/app/metrics.py`
- `apps/worker/`
- `infra/docker/prometheus.yml`
- `missions/lv4/observability-upgrade/DESIGN.md`

## How to run checks

```bash
python scripts/evaluate/run.py --mission lv4-observability-upgrade
```

## What not to do

- Do not put claim ids, user ids, or raw paths in metric labels.
- Do not add telemetry with no question it answers.
- Do not make local development depend on a cloud exporter.

## Interview reflection questions

- How did you divide information among logs, metrics, and traces?
- Which labels were tempting but unsafe?
- How would you set SLOs with limited baseline data?

## Evaluator notes

Automated checks validate propagation and cardinality rules. Alert usefulness and dashboard narrative need design review.

