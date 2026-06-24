import asyncio
import os
from datetime import UTC, datetime
from pathlib import Path

from app.schemas import Progress, ProgressRecord


class ProgressStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = asyncio.Lock()

    def _read(self) -> Progress:
        if not self.path.exists():
            return Progress(completed={})
        return Progress.model_validate_json(self.path.read_text(encoding="utf-8"))

    async def get(self) -> Progress:
        async with self._lock:
            return self._read()

    async def complete(self, mission_id: str, notes: str | None) -> Progress:
        async with self._lock:
            progress = self._read()
            progress.completed[mission_id] = ProgressRecord(
                completed_at=datetime.now(UTC), notes=notes
            )
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix(".tmp")
            temporary.write_text(progress.model_dump_json(indent=2), encoding="utf-8")
            os.replace(temporary, self.path)
            return progress
