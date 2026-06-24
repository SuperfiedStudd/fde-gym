import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql://claimops:claimops-local@localhost:5432/claimops"
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    queue_name: str = os.getenv("QUEUE_NAME", "claimops:jobs")
    dead_letter_queue: str = os.getenv("DEAD_LETTER_QUEUE", "claimops:jobs:dead")
    poll_timeout_seconds: int = int(os.getenv("POLL_TIMEOUT_SECONDS", "5"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
