import json
from collections import Counter
from pathlib import Path

REQUIRED_SECTIONS = {
    "## Scenario",
    "## Broken behavior",
    "## Constraints",
    "## Acceptance criteria",
    "## Files likely involved",
    "## How to run checks",
    "## What not to do",
    "## Interview reflection questions",
    "## Evaluator notes",
}


def mission_manifests() -> list[Path]:
    return sorted(Path("missions").glob("lv*/*/mission.json"))


def test_catalog_has_required_level_counts() -> None:
    payloads = [json.loads(path.read_text(encoding="utf-8")) for path in mission_manifests()]
    assert Counter(item["level"] for item in payloads) == {
        "LV1": 5,
        "LV2": 5,
        "LV3": 4,
        "LV4": 3,
    }
    assert len({item["id"] for item in payloads}) == 17


def test_every_mission_has_complete_metadata_and_brief() -> None:
    for manifest in mission_manifests():
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        assert {
            "id",
            "title",
            "level",
            "skill",
            "labels",
            "summary",
            "estimated_minutes",
            "checks",
        } <= payload.keys()
        brief = manifest.with_name("README.md").read_text(encoding="utf-8")
        missing = REQUIRED_SECTIONS - set(brief.splitlines())
        assert not missing, f"{manifest.parent}: missing {sorted(missing)}"
