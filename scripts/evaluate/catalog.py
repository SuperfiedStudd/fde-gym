import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class MissionCheck:
    mission_id: str
    title: str
    level: str
    skill: str
    labels: tuple[str, ...]
    test_file: Path
    lint_targets: tuple[Path, ...]


LINT_TARGETS: dict[str, tuple[str, ...]] = {
    "lv1-request-validation": ("apps/api/app/schemas.py",),
    "lv1-unit-test-repair": ("tests/missions/test_lv1_unit_test_repair.py",),
    "lv1-status-transitions": ("apps/api/app/domain/transitions.py",),
    "lv1-claims-pagination": ("apps/api/app/domain/pagination.py", "apps/api/app/routes/claims.py"),
    "lv1-sql-status-filter": ("apps/api/app/domain/filters.py",),
    "lv2-worker-retries": ("apps/worker/worker",),
    "lv2-claim-idempotency": (
        "apps/api/app/domain/idempotency.py",
        "apps/api/app/routes/claims.py",
    ),
    "lv2-notes-rbac": ("apps/api/app/domain/permissions.py", "apps/api/app/routes/claims.py"),
    "lv2-cache-invalidation": ("apps/api/app/cache.py", "apps/api/app/routes/claims.py"),
    "lv2-payment-logging": ("apps/api/app/routes/claims.py",),
    "lv3-async-claims-processor": ("apps/worker/worker/handlers.py",),
    "lv3-search-latency": ("apps/api/app/routes/claims.py",),
    "lv3-deployment-error-rate": (),
    "lv3-assignment-race": ("apps/api/app/routes/claims.py",),
    "lv4-multi-service-incident": ("apps/api/app", "apps/worker/worker"),
    "lv4-rollback-safe-event-migration": ("apps/api/app", "apps/worker/worker"),
    "lv4-observability-upgrade": ("apps/api/app", "apps/worker/worker"),
}


def load_catalog() -> list[MissionCheck]:
    checks: list[MissionCheck] = []
    for path in sorted((ROOT / "missions").glob("lv*/*/mission.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        mission_id = payload["id"]
        checks.append(
            MissionCheck(
                mission_id=mission_id,
                title=payload["title"],
                level=payload["level"],
                skill=payload["skill"],
                labels=tuple(payload["labels"]),
                test_file=ROOT / "tests" / "missions" / f"test_{mission_id.replace('-', '_')}.py",
                lint_targets=tuple(ROOT / target for target in LINT_TARGETS.get(mission_id, ())),
            )
        )
    return checks


def get_check(mission_id: str) -> MissionCheck | None:
    return next((check for check in load_catalog() if check.mission_id == mission_id), None)
