import sys
from pathlib import Path

sys.path.insert(0, str(Path("apps/worker").resolve()))
from worker.retry import retry_delay_seconds, should_retry


def test_retry_policy_is_bounded() -> None:
    assert should_retry(attempt=1, max_attempts=3, retryable=True)
    assert should_retry(attempt=2, max_attempts=3, retryable=True)
    assert not should_retry(attempt=3, max_attempts=3, retryable=True)
    assert not should_retry(attempt=1, max_attempts=3, retryable=False)


def test_retry_delay_is_positive_and_capped() -> None:
    delays = [retry_delay_seconds(attempt) for attempt in range(1, 10)]
    assert delays[0] > 0
    assert delays == sorted(delays)
    assert max(delays) <= 300


def test_worker_uses_dead_letter_and_attempt_state() -> None:
    source = Path("apps/worker/worker/main.py").read_text(encoding="utf-8")
    assert "dead_letter_queue" in source
    assert "attempts" in source
    assert "MISSION_BUG(lv2-worker-retries)" not in source

