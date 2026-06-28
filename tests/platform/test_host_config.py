from pathlib import Path

from app.config import Settings


def test_host_settings_do_not_load_compose_dotenv(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("MISSION_ROOT", raising=False)
    (tmp_path / ".env").write_text("MISSION_ROOT=/workspace/missions\n", encoding="utf-8")

    settings = Settings()

    assert settings.mission_root == Path("missions")
