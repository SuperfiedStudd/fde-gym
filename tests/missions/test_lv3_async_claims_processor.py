import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path("apps/worker").resolve()))
from worker.handlers import dispatch


def test_dispatch_awaits_claim_handler() -> None:
    async def scenario() -> None:
        probe = AsyncMock()
        with patch("worker.handlers.process_claim", probe):
            await dispatch(object(), "claim.process", {"claim_id": "claim-1"})
        probe.assert_awaited_once()

    asyncio.run(scenario())


def test_unknown_kind_remains_an_error() -> None:
    async def scenario() -> None:
        try:
            await dispatch(object(), "unknown", {})
        except ValueError:
            return
        raise AssertionError("unknown job kind did not fail")

    asyncio.run(scenario())

