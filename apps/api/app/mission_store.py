import json
from pathlib import Path

from app.schemas import Mission


class MissionStore:
    def __init__(self, root: Path) -> None:
        self.root = root

    def list(self) -> list[Mission]:
        missions: list[Mission] = []
        for path in sorted(self.root.glob("lv*/*/mission.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["readme_path"] = str(path.parent.joinpath("README.md").relative_to(self.root))
            missions.append(Mission.model_validate(payload))
        return sorted(missions, key=lambda mission: (mission.level, mission.id))

    def get(self, mission_id: str) -> Mission | None:
        return next((mission for mission in self.list() if mission.id == mission_id), None)

    def read_brief(self, mission: Mission) -> str:
        return self.root.joinpath(mission.readme_path).read_text(encoding="utf-8")
