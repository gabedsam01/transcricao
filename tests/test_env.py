import fastapi
import uvicorn
import whisper
import torch
from loguru import logger
import pydantic_settings
import pytest
import httpx

def test_imports():
    assert fastapi.__version__ == "0.110.0"
    assert uvicorn.__version__ == "0.27.1"
    # whisper doesn't always have a __version__ that matches the pip version string
    assert torch.__version__ is not None
    assert pydantic_settings.__version__ == "2.2.1"
    assert pytest.__version__ == "8.0.0"
    assert httpx.__version__ == "0.27.0"
    logger.info("All imports successful")

if __name__ == "__main__":
    test_imports()
    print("DONE")
