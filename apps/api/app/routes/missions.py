from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.mission_store import MissionStore
from app.progress_store import ProgressStore
from app.schemas import CompleteMission, Mission, Progress

router = APIRouter(tags=["gym"])


def mission_store(request: Request) -> MissionStore:
    return request.app.state.missions


def progress_store(request: Request) -> ProgressStore:
    return request.app.state.progress


@router.get("/missions", response_model=list[Mission])
def list_missions(
    store: Annotated[MissionStore, Depends(mission_store)],
    level: str | None = Query(default=None, pattern="^LV[1-4]$"),
    skill: str | None = None,
) -> list[Mission]:
    missions = store.list()
    if level:
        missions = [mission for mission in missions if mission.level == level]
    if skill:
        missions = [mission for mission in missions if mission.skill.casefold() == skill.casefold()]
    return missions


@router.get("/missions/{mission_id}")
def get_mission(
    mission_id: str, store: Annotated[MissionStore, Depends(mission_store)]
) -> dict[str, object]:
    mission = store.get(mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail="mission not found")
    return {**mission.model_dump(), "brief": store.read_brief(mission)}


@router.get("/progress", response_model=Progress)
async def get_progress(store: Annotated[ProgressStore, Depends(progress_store)]) -> Progress:
    return await store.get()


@router.post("/progress/{mission_id}/complete", response_model=Progress)
async def complete_mission(
    mission_id: str,
    payload: CompleteMission,
    missions: Annotated[MissionStore, Depends(mission_store)],
    progress: Annotated[ProgressStore, Depends(progress_store)],
) -> Progress:
    if missions.get(mission_id) is None:
        raise HTTPException(status_code=404, detail="mission not found")
    return await progress.complete(mission_id, payload.notes)
