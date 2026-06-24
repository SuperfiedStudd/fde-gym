import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path("apps/api").resolve()))

from app.progress_store import ProgressStore


def test_progress_store_round_trip(tmp_path: Path) -> None:
    async def scenario() -> None:
        store = ProgressStore(tmp_path / "progress.json")
        empty = await store.get()
        assert empty.completed == {}
        saved = await store.complete("lv1-request-validation", "good boundary practice")
        assert "lv1-request-validation" in saved.completed
        loaded = await store.get()
        assert loaded.completed["lv1-request-validation"].notes == "good boundary practice"

    asyncio.run(scenario())
