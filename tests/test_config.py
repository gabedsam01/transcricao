import pytest
from app.config import Settings

def test_settings_default_values():
    settings = Settings()
    assert settings.WHISPER_MODEL == "medium"
    assert settings.WHISPER_LANGUAGE is None
    assert settings.MAX_FILE_SIZE_MB == 500
    assert settings.PORT == 8000

def test_settings_env_override(monkeypatch):
    monkeypatch.setenv("WHISPER_MODEL", "large")
    monkeypatch.setenv("PORT", "9000")
    settings = Settings()
    assert settings.WHISPER_MODEL == "large"
    assert settings.PORT == 9000
