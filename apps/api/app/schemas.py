from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ClaimCreate(BaseModel):
    external_id: str
    claimant_name: str
    amount_cents: int
    category: str
    priority: Literal["low", "normal", "high", "urgent"] = "normal"
    created_by: UUID

    # MISSION_BUG(lv1-request-validation): important constraints are intentionally absent.


class ClaimRead(BaseModel):
    id: UUID
    external_id: str
    claimant_name: str
    amount_cents: int
    status: str
    priority: str
    category: str
    version: int
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClaimList(BaseModel):
    items: list[ClaimRead]
    page: int
    page_size: int
    total: int


class StatusTransition(BaseModel):
    status: Literal["draft", "submitted", "reviewing", "approved", "denied", "closed"]


class NoteCreate(BaseModel):
    body: str = Field(min_length=1, max_length=4000)
    internal: bool = True


class AssignmentCreate(BaseModel):
    user_id: UUID
    expected_version: int | None = None


class Mission(BaseModel):
    id: str
    title: str
    level: Literal["LV1", "LV2", "LV3", "LV4"]
    skill: str
    labels: list[str]
    summary: str
    estimated_minutes: int
    checks: list[str]
    readme_path: str


class ProgressRecord(BaseModel):
    completed_at: datetime
    notes: str | None = None


class Progress(BaseModel):
    completed: dict[str, ProgressRecord]
    version: int = 1


class CompleteMission(BaseModel):
    notes: str | None = Field(default=None, max_length=1000)


class HealthComponent(BaseModel):
    status: Literal["healthy", "degraded", "critical"]
    latency_ms: float
    detail: str | None = None


class SystemHealth(BaseModel):
    generated_at: datetime
    overall: Literal["healthy", "degraded", "critical"]
    queue_depth: int
    error_rate: float
    p95_latency_ms: int
    components: dict[str, HealthComponent]
