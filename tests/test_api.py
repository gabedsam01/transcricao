import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model" in data
    assert "device" in data
    assert "compute_type" in data

def test_transcribe_endpoint():
    settings.WHISPER_MODEL = "small"
    
    sample_path = os.path.join(os.path.dirname(__file__), "sample_audio.wav")
    if not os.path.exists(sample_path):
        with open(sample_path, "wb") as f:
            f.write(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")
    
    with open(sample_path, "rb") as f:
        files = {"file": ("sample_audio.wav", f, "audio/wav")}
        data = {"language": "en"}
        response = client.post("/transcribe", files=files, data=data)
    
    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert "language" in data
    assert "duration" in data

def test_transcribe_invalid_type():
    files = {"file": ("test.txt", b"hello world", "text/plain")}
    response = client.post("/transcribe", files=files)
    assert response.status_code == 400
    assert "audio or video" in response.json()["detail"]

def test_file_size_limit():
    old_limit = settings.MAX_FILE_SIZE_MB
    settings.MAX_FILE_SIZE_MB = 0
    try:
        files = {"file": ("test.wav", b"a" * 1024 * 1024, "audio/wav")}
        response = client.post("/transcribe", files=files)
        assert response.status_code == 413
        assert "File exceeds limit" in response.json()["detail"]
    finally:
        settings.MAX_FILE_SIZE_MB = old_limit
