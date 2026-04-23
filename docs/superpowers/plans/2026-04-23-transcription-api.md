# Transcription API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform a local Whisper script into a production-ready, stateless REST API optimized for ARM64 Oracle VPS using FastAPI and Docker.

**Architecture:** Use a singleton pattern to load the Whisper model on startup. Implement chunked streaming for file uploads to minimize memory usage on a VPS.

**Tech Stack:** FastAPI, openai-whisper, loguru, pydantic-settings, Docker, ffmpeg.

---

### Task 1: Environment Setup & Clean Requirements

**Files:**
- Create: `requirements.txt`

- [ ] **Step 1: Write clean requirements.txt**

```text
fastapi==0.110.0
uvicorn==0.27.1
python-multipart==0.0.9
openai-whisper==20231117
torch==2.2.1
loguru==0.7.2
pydantic-settings==2.2.1
```

- [ ] **Step 2: Commit**

```bash
git add requirements.txt
git commit -m "chore: setup requirements.txt"
```

### Task 2: Configuration Management

**Files:**
- Create: `app/config.py`

- [ ] **Step 1: Implement Settings with Pydantic**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    WHISPER_MODEL: str = "medium"
    WHISPER_LANGUAGE: str | None = None
    MAX_FILE_SIZE_MB: int = 500
    PORT: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()
```

- [ ] **Step 2: Commit**

```bash
mkdir -p app
git add app/config.py
git commit -m "feat: add configuration management"
```

### Task 3: Logger Configuration

**Files:**
- Create: `app/logger.py`

- [ ] **Step 1: Configure Loguru**

```python
import sys
from loguru import logger

def setup_logging():
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
    )

setup_logging()
```

- [ ] **Step 2: Commit**

```bash
git add app/logger.py
git commit -m "feat: setup loguru logging"
```

### Task 4: Transcription Logic (Pure Function)

**Files:**
- Create: `app/transcribe.py`

- [ ] **Step 1: Implement transcribe_audio function**

```python
import whisper
from app.config import settings
from app.logger import logger

_model = None

def get_model():
    global _model
    if _model is None:
        logger.info(f"Loading Whisper model: {settings.WHISPER_MODEL}")
        _model = whisper.load_model(settings.WHISPER_MODEL)
    return _model

def transcribe_file(file_path: str):
    model = get_model()
    options = {}
    if settings.WHISPER_LANGUAGE:
        options["language"] = settings.WHISPER_LANGUAGE
    
    logger.info(f"Starting transcription for {file_path}")
    result = model.transcribe(file_path, **options)
    return {
        "text": result["text"],
        "language": result.get("language"),
        "segments": result.get("segments")
    }
```

- [ ] **Step 2: Commit**

```bash
git add app/transcribe.py
git commit -m "feat: add transcription logic with singleton model"
```

### Task 5: FastAPI Application & Endpoints

**Files:**
- Create: `app/main.py`

- [ ] **Step 1: Implement FastAPI app with CORS and Endpoints**

```python
import time
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.logger import logger
from app.transcribe import transcribe_file, get_model

app = FastAPI(title="Transcription API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Warm up the model
    get_model()

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model": settings.WHISPER_MODEL,
        "device": "cpu"
    }

@app.post("/transcribe")
async def transcribe(file: UploadFile):
    if not file.content_type.startswith(("audio/", "video/")):
        raise HTTPException(status_code=400, detail="File must be audio or video")

    start_time = time.time()
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        try:
            # Chunked streaming to disk
            size = 0
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                size += len(chunk)
                if size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
                    raise HTTPException(status_code=413, detail="File too large")
                tmp.write(chunk)
            tmp.flush()
            
            result = transcribe_file(tmp.name)
            
            duration = time.time() - start_time
            logger.info(f"Transcription completed in {duration:.2f}s for {file.filename} ({size / 1024 / 1024:.2f} MB)")
            
            result["usage_example"] = "fetch('URL/transcribe', { method: 'POST', body: new FormData().append('file', file) })"
            return result
            
        except Exception as e:
            logger.error(f"Error processing {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            tmp.close()
            import os
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
```

- [ ] **Step 2: Commit**

```bash
git add app/main.py
git commit -m "feat: implement FastAPI app and endpoints"
```

### Task 6: Dockerization (ARM64 Optimized)

**Files:**
- Create: `Dockerfile`
- Create: `.dockerignore`

- [ ] **Step 1: Create .dockerignore**

```text
__pycache__
.git
.env
docs
```

- [ ] **Step 2: Create Dockerfile**

```dockerfile
FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

ENV WHISPER_MODEL=medium
ENV PORT=8000

VOLUME /root/.cache/whisper

HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["python", "-m", "app.main"]
```

- [ ] **Step 3: Create docker-compose.yml**

```yaml
version: '3.8'

services:
  whisper-api:
    build: .
    restart: unless-stopped
    ports:
      - "${PORT:-8000}:8000"
    environment:
      - WHISPER_MODEL=${WHISPER_MODEL:-medium}
      - WHISPER_LANGUAGE=${WHISPER_LANGUAGE}
      - MAX_FILE_SIZE_MB=${MAX_FILE_SIZE_MB:-500}
    volumes:
      - whisper-cache:/root/.cache/whisper
    deploy:
      resources:
        limits:
          memory: 12G

volumes:
  whisper-cache:
```

- [ ] **Step 4: Commit**

```bash
git add Dockerfile .dockerignore docker-compose.yml
git commit -m "chore: add docker configuration"
```

### Task 7: Documentation

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update README with deploy instructions**

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: update README with deployment instructions"
```
