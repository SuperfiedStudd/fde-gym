def retry_delay_seconds(attempt: int) -> int:
    # MISSION_BUG(lv2-worker-retries): retries are not scheduled.
    del attempt
    return 0


def should_retry(attempt: int, max_attempts: int, retryable: bool) -> bool:
    # MISSION_BUG(lv2-worker-retries): every failure is treated as terminal.
    del attempt, max_attempts, retryable
    return False
