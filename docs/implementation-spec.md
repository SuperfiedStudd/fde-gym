# Spec: fde-gym first pass

## Goal

Create a runnable ClaimOps engineering practice monorepo with a Next.js cockpit, FastAPI API, Python worker, TypeScript edge service, Postgres/Redis dependencies, 17 intentionally broken missions, evaluation tooling, and optional GCP deployment assets.

## Assumptions

- Local Docker Compose is the primary path; GCP is documented and opt-in.
- Platform smoke tests and mission tests are separate: smoke tests prove the gym works, while mission tests intentionally expose bugs.
- Mission metadata is stored in versioned JSON manifests and progress is stored in a local JSON file.
- MinIO, Grafana, and Playwright are deferred to keep the first pass manageable; Prometheus metrics and structured logs provide the observability foundation.

## Files Involved

- `apps/`: Next.js web, FastAPI API, Python worker, TypeScript edge service
- `infra/`: Docker Compose, Postgres initialization, GCP Terraform and deploy helpers
- `missions/`: LV1-LV4 briefs and machine-readable manifests
- `scripts/`: seed/reset, evaluation, and development helpers
- `docs/`: architecture, setup, learning path, authoring, troubleshooting, interview notes

## Constraints

- Use Python and TypeScript.
- Do not run `npm run build`.
- Do not solve intentional mission defects.
- Use only local open-source dependencies or GCP services.
- Keep code typed, production-shaped, and understandable by one engineer.

## Success Criteria

- Docker Compose defines web, API, worker, edge service, Postgres, Redis, and Prometheus.
- The API exposes health, missions, progress, ClaimOps, events, system health, and metrics endpoints.
- The web app exposes dashboard, mission list/detail, filters, and progress views in a black/green theme.
- Postgres schema and deterministic seed data cover all required entities.
- Exactly 17 mission briefs exist: 5 LV1, 5 LV2, 4 LV3, and 3 LV4.
- Evaluation CLI lists missions and runs mission-specific checks.
- Local and GCP setup/teardown paths are documented.
- Verification avoids the forbidden frontend build command.

## Open Questions

None blocking. Optional object storage and full Grafana dashboards are explicit follow-up work.
