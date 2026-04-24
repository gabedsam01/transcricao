# Faster-Whisper Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate the transcription API from `openai-whisper` (PyTorch) to `faster-whisper` (CTranslate2) targeting CPU-only execution with low RAM usage and Docker Swarm deployment.

**Architecture:** Replace the model loading and inference logic to use `faster-whisper.WhisperModel`. Implement a Singleton pattern for the model that loads on startup and processes requests linearly. The web server stays FastAPI, and we use Loguru for structured logging.

**Tech Stack:** FastAPI, faster-whisper, python-multipart, Docker, Docker Swarm (Portainer), Traefik.

---

### Task 1: Update Configuration

**Files:**
- Modify: `app/config.py`

- [ ] **Step 1: Update variables in config**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PORT: int = 8000
    WHISPER_MODEL: str = "small"
    WHISPER_LANGUAGE: str = "pt"
    MAX_FILE_SIZE_MB: int = 500
    FW_DEVICE: str = "cpu"
    FW_COMPUTE_TYPE: str = "int8"
    FW_CPU_THREADS: int = 4
    
    class Config:
        env_file = ".env"

settings = Settings()
```

- [ ] **Step 2: Commit**
```bash
git add app/config.py
git commit -m "chore(config): add faster-whisper environment variables"
```

### Task 2: Refactor Transcribe Logic

**Files:**
- Modify: `app/transcribe.py`

- [ ] **Step 1: Replace implementation in transcribe.py**

```python
import threading
from faster_whisper import WhisperModel
from app.config import settings
from app.logger import logger

_model = None
_model_lock = threading.Lock()

def get_model():
    """
    Returns the Whisper model instance, loading it if necessary (Singleton).
    """
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                logger.info(f"Loading faster-whisper model: {settings.WHISPER_MODEL} on {settings.FW_DEVICE} with {settings.FW_COMPUTE_TYPE}")
                _model = WhisperModel(
                    settings.WHISPER_MODEL,
                    device=settings.FW_DEVICE,
                    compute_type=settings.FW_COMPUTE_TYPE,
                    cpu_threads=settings.FW_CPU_THREADS,
                    download_root="/root/.cache/whisper"
                )
                logger.info("Whisper model loaded successfully")
    return _model

def transcribe_file(file_path: str, language: str = None) -> dict:
    """
    Transcribes an audio file and returns a dictionary with text, language and segments.
    """
    model = get_model()
    logger.info(f"Transcribing file: {file_path}")
    
    # Determine the language to use
    lang_to_use = language if language and language != "auto" else settings.WHISPER_LANGUAGE
    # If "auto" is explicitly sent or if WHISPER_LANGUAGE is "auto", we pass None to the model
    if lang_to_use == "auto":
        lang_to_use = None
        
    segments, info = model.transcribe(file_path, language=lang_to_use, beam_size=5)
    
    text_content = ""
    segments_list = []
    
    for segment in segments:
        text_content += segment.text
        segments_list.append({
            "id": segment.id,
            "seek": segment.seek,
            "start": segment.start,
            "end": segment.end,
            "text": segment.text,
        })
        
    return {
        "text": text_content.strip(),
        "language": info.language,
        "segments": segments_list
    }
```

- [ ] **Step 2: Commit**
```bash
git add app/transcribe.py
git commit -m "feat(transcribe): implement faster-whisper logic"
```

### Task 3: Update API Endpoints

**Files:**
- Modify: `app/main.py`

- [ ] **Step 1: Update main.py endpoints**

```python
import time
import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, HTTPException, Form
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.logger import logger
from app.transcribe import transcribe_file, get_model

app = FastAPI(title="Transcription API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """
    Load the model on startup to avoid delay on the first request.
    """
    logger.info("Initializing application startup...")
    get_model()
    logger.info("Application startup complete.")

@app.get("/health")
async def health():
    """
    Health check endpoint.
    """
    return {
        "status": "ok",
        "model": settings.WHISPER_MODEL,
        "device": settings.FW_DEVICE,
        "compute_type": settings.FW_COMPUTE_TYPE
    }

@app.post("/transcribe")
async def transcribe(file: UploadFile, language: Optional[str] = Form(None)):
    """
    Transcribe an uploaded audio/video file.
    """
    # 1. Validate file type
    if not file.content_type.startswith(("audio/", "video/")):
        logger.warning(f"Invalid content type: {file.content_type}")
        raise HTTPException(status_code=400, detail="File must be audio or video")

    start_time = time.time()
    
    # 2. Use a temporary file to store the upload
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = tmp.name
        try:
            # 3. Stream the upload to disk to save memory
            size = 0
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                size += len(chunk)
                if size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
                    logger.error(f"File too large: {size} bytes")
                    raise HTTPException(status_code=413, detail=f"File exceeds limit of {settings.MAX_FILE_SIZE_MB}MB")
                tmp.write(chunk)
            tmp.flush()
            tmp.close()  # Close the file before transcribing to ensure it's written
            
            # 4. Perform transcription
            result = transcribe_file(tmp_path, language=language)
            
            duration = time.time() - start_time
            logger.info(f"Transcription completed in {duration:.2f}s for {file.filename} ({size / 1024 / 1024:.2f} MB)")
            
            result["duration"] = duration
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error processing {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            # 5. Cleanup
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
```

- [ ] **Step 2: Commit**
```bash
git add app/main.py
git commit -m "feat(api): support optional language field and update health output"
```

### Task 4: Fix Tests

**Files:**
- Modify: `tests/test_api.py`
- Modify: `tests/test_transcribe.py`

- [ ] **Step 1: Update `tests/test_api.py`**
Remove `usage_example` check since we removed it from `main.py` response. Update health tests. Use `replace`.

- [ ] **Step 2: Write implementation**
```python
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
    settings.WHISPER_MODEL = "tiny"
    
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
```

- [ ] **Step 3: Update `tests/test_transcribe.py`**
```python
import os
import pytest
from app.config import settings
from app.transcribe import get_model, transcribe_file

def test_get_model_singleton():
    settings.WHISPER_MODEL = "tiny"
    model1 = get_model()
    model2 = get_model()
    assert model1 is model2
    assert model1 is not None

def test_transcribe_sample_file():
    settings.WHISPER_MODEL = "tiny"
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
```

- [ ] **Step 4: Commit**
```bash
git add tests/test_api.py tests/test_transcribe.py
git commit -m "test: update tests for faster-whisper endpoints"
```

### Task 5: Requirements

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Write clean requirements**
```txt
fastapi==0.110.0
uvicorn==0.27.1
python-multipart==0.0.9
faster-whisper==1.0.1
loguru==0.7.2
pydantic-settings==2.2.1
pytest==8.0.0
httpx==0.27.0
```

- [ ] **Step 2: Commit**
```bash
git add requirements.txt
git commit -m "build: update requirements for faster-whisper"
```

### Task 6: Dockerfile

**Files:**
- Modify: `Dockerfile`

- [ ] **Step 1: Write Dockerfile**
```dockerfile
FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

ENV PORT=8000
ENV WHISPER_MODEL=small
ENV WHISPER_LANGUAGE=pt
ENV MAX_FILE_SIZE_MB=500
ENV FW_DEVICE=cpu
ENV FW_COMPUTE_TYPE=int8
ENV FW_CPU_THREADS=4

VOLUME /root/.cache/whisper

HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

EXPOSE ${PORT}

CMD ["python", "-m", "app.main"]
```

- [ ] **Step 2: Commit**
```bash
git add Dockerfile
git commit -m "build: optimize Dockerfile for faster-whisper cpu"
```

### Task 7: Docker Compose (Swarm/Portainer)

**Files:**
- Modify: `docker-compose.yml`

- [ ] **Step 1: Write Compose**
```yaml
version: '3.8'

services:
  whisper-api:
    image: gabedsam01/whisper-fast-api:latest
    environment:
      - PORT=8000
      - WHISPER_MODEL=${WHISPER_MODEL:-small}
      - WHISPER_LANGUAGE=${WHISPER_LANGUAGE:-pt}
      - MAX_FILE_SIZE_MB=${MAX_FILE_SIZE_MB:-500}
      - FW_DEVICE=${FW_DEVICE:-cpu}
      - FW_COMPUTE_TYPE=${FW_COMPUTE_TYPE:-int8}
      - FW_CPU_THREADS=${FW_CPU_THREADS:-4}
    volumes:
      - whisper-cache:/root/.cache/whisper
    networks:
      - FioriniNet
    deploy:
      restart_policy:
        condition: any
        delay: 5s
        max_attempts: 3
        window: 120s
      resources:
        limits:
          memory: 4G
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.whisper-api.rule=Host(`${DOMAIN}`)"
        - "traefik.http.routers.whisper-api.entrypoints=websecure"
        - "traefik.http.routers.whisper-api.tls.certresolver=letsencryptresolver"
        - "traefik.http.services.whisper-api.loadbalancer.server.port=8000"

volumes:
  whisper-cache:

networks:
  FioriniNet:
    external: true
```

- [ ] **Step 2: Commit**
```bash
git add docker-compose.yml
git commit -m "chore: update docker-compose for swarm deployment"
```

### Task 8: GitHub Actions

**Files:**
- Modify: `.github/workflows/build-multiarch.yml`
- Delete: `.github/workflows/docker-image.yml` (if it conflicts)

- [ ] **Step 1: Update action**
```yaml
name: Build and Push Multi-Arch Docker Image

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile
          platforms: linux/amd64
          push: true
          tags: gabedsam01/whisper-fast-api:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

- [ ] **Step 2: Commit**
```bash
git add .github/workflows/build-multiarch.yml
git commit -m "ci: update github actions for faster-whisper image"
```

### Task 9: Real-world Benchmark Script

**Files:**
- Create: `scripts/test_real_world.sh`

- [ ] **Step 1: Create script**
```bash
#!/bin/bash
set -e

mkdir -p output-tests
API_URL="http://localhost:8000"

echo "Checking API Health..."
curl -s $API_URL/health | jq .

echo ""
echo "Testing SHORT VIDEO..."
yt-dlp -f "bestaudio" -x --audio-format mp3 -o "output-tests/short.mp3" "https://youtube.com/shorts/GPLg0FZQSmk"
curl -s -X POST -F "file=@output-tests/short.mp3" $API_URL/transcribe > output-tests/short_result.json
echo "Short video transcribed! Results at output-tests/short_result.json"
cat output-tests/short_result.json | jq '{text: .text[0:100], duration: .duration}'

echo ""
echo "Testing LONG VIDEO..."
yt-dlp -f "bestaudio" -x --audio-format mp3 -o "output-tests/long.mp3" "https://youtu.be/lT2Ze4LT6Ls"
curl -s -X POST -F "file=@output-tests/long.mp3" $API_URL/transcribe > output-tests/long_result.json
echo "Long video transcribed! Results at output-tests/long_result.json"
cat output-tests/long_result.json | jq '{text: .text[0:100], duration: .duration}'
```

- [ ] **Step 2: Make executable and commit**
```bash
chmod +x scripts/test_real_world.sh
git add scripts/test_real_world.sh
git commit -m "test: add real-world yt-dlp test script"
```

### Task 10: README update

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Write README**
```markdown
# Transcription API (Faster-Whisper)

A fast, lightweight, and robust API for audio/video transcription using `faster-whisper`.
Designed specifically for CPU-only environments (e.g., cheap VPS) running under Docker Swarm/Portainer.

## Stack
- **Framework:** FastAPI
- **Transcription Engine:** `faster-whisper` (CTranslate2)
- **Deployment:** Docker, Docker Compose (Swarm-ready with Traefik labels)

## Environment Variables
- `PORT` (default: 8000)
- `WHISPER_MODEL` (default: "small")
- `WHISPER_LANGUAGE` (default: "pt")
- `MAX_FILE_SIZE_MB` (default: 500)
- `FW_DEVICE` (default: "cpu")
- `FW_COMPUTE_TYPE` (default: "int8")
- `FW_CPU_THREADS` (default: 4)

*Note: For low RAM CPU instances, `small` model with `int8` compute type offers the best trade-off between speed and accuracy.*

## Running Locally

1. Create a virtual environment and install dependencies:
```bash
pip install -r requirements.txt
```
2. Run the application:
```bash
python -m app.main
```

## Running with Docker

```bash
docker-compose up -d
```

## API Endpoints

### 1. Health Check
```bash
curl http://localhost:8000/health
```
Response:
```json
{
  "status": "ok",
  "model": "small",
  "device": "cpu",
  "compute_type": "int8"
}
```

### 2. Transcribe
```bash
curl -X POST -F "file=@audio.mp3" -F "language=pt" http://localhost:8000/transcribe
```

## Performance & Limitations
This API relies on `faster-whisper`, performing up to 4x faster than the original `openai-whisper` on CPUs.
The model is loaded once on application startup (Singleton) preventing delays in individual requests. High concurrency on single-core/low-RAM nodes might throttle performance; adjusting `FW_CPU_THREADS` properly is highly recommended.
```

- [ ] **Step 2: Commit**
```bash
git add README.md
git commit -m "docs: update README for faster-whisper migration"
```
