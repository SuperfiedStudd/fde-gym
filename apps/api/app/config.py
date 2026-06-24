from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "claimops-api"
    environment: str = "local"
    database_url: str = "postgresql+asyncpg://claimops:claimops-local@localhost:5432/claimops"
    redis_url: str = "redis://localhost:6379/0"
    mission_root: Path = Path("missions")
    progress_file: Path = Path("data/progress.json")
    edge_service_url: str = "http://localhost:3001"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
