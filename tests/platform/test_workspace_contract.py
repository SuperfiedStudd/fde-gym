from pathlib import Path


def test_compose_defines_required_services() -> None:
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    for service in (
        "postgres:",
        "redis:",
        "api:",
        "worker:",
        "edge-service:",
        "web:",
        "prometheus:",
    ):
        assert service in compose


def test_intentional_bugs_are_explicitly_tagged() -> None:
    roots = [Path("apps/api"), Path("apps/worker")]
    tagged = sum(
        path.read_text(encoding="utf-8").count("MISSION_BUG")
        for root in roots
        for path in root.rglob("*.py")
    )
    assert tagged >= 10
