import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path("apps/api").resolve()))

from app.main import app


def test_health_and_mission_catalog_contract() -> None:
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"

        response = client.get("/missions")
        assert response.status_code == 200
        missions = response.json()
        assert len(missions) == 17
        assert {mission["level"] for mission in missions} == {"LV1", "LV2", "LV3", "LV4"}


def test_unknown_mission_returns_404() -> None:
    with TestClient(app) as client:
        response = client.get("/missions/not-a-real-mission")
        assert response.status_code == 404

