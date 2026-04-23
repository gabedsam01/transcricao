import os
import pytest
from app.config import settings
from app.transcribe import get_model, transcribe_file

def test_get_model_singleton():
    # Force tiny model for tests
    settings.WHISPER_MODEL = "tiny"
    
    model1 = get_model()
    model2 = get_model()
    
    assert model1 is model2
    assert model1 is not None

def test_transcribe_sample_file():
    # Force tiny model for tests
    settings.WHISPER_MODEL = "tiny"
    
    sample_path = os.path.join(os.path.dirname(__file__), "sample_audio.wav")
    assert os.path.exists(sample_path)
    
    result = transcribe_file(sample_path)
    
    assert isinstance(result, dict)
    assert "text" in result
    assert "language" in result
    assert "segments" in result
    # Since it's a sine wave, it might not have clear text, but it should return something (likely empty or [Music])
    assert isinstance(result["text"], str)
