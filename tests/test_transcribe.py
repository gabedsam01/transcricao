import os
import pytest
from app.config import settings
from app.transcribe import get_model, transcribe_file

def test_get_model_singleton():
    settings.WHISPER_MODEL = "small"
    model1 = get_model()
    model2 = get_model()
    assert model1 is model2
    assert model1 is not None

def test_transcribe_sample_file():
    settings.WHISPER_MODEL = "small"
    sample_path = os.path.join(os.path.dirname(__file__), "sample_audio.wav")
    if not os.path.exists(sample_path):
        with open(sample_path, "wb") as f:
            f.write(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")
    
    result = transcribe_file(sample_path)
    assert isinstance(result, dict)
    assert "text" in result
    assert "language" in result
    assert "segments" in result
    assert isinstance(result["text"], str)
