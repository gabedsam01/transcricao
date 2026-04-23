# Spec: Transcription API (FastAPI + Whisper + Docker ARM64)

**Date:** 2026-04-23
**Status:** Approved
**Description:** Transform a local Whisper script into a production-ready, stateless REST API optimized for ARM64 Oracle VPS.

## 1. Objectives
- Provide a high-performance API for audio/video transcription.
- Ensure memory efficiency for large files (up to 500MB).
- Support ARM64 architecture (Oracle Cloud Free Tier).
- Maintain singleton model loading for performance.

## 2. Technical Stack
- **Language:** Python 3.11
- **Framework:** FastAPI
- **Transcription:** openai-whisper
- **Logging:** loguru
- **Configuration:** pydantic-settings
- **Server:** Uvicorn
- **Containerization:** Docker + Docker Compose

## 3. Project Structure
```
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app, endpoints, CORS, Lifecycle
│   ├── config.py        # Settings via pydantic-settings
│   ├── transcribe.py    # Whisper logic (pure functions)
│   └── logger.py        # Loguru configuration
├── Dockerfile           # ARM64 optimized, includes ffmpeg
├── docker-compose.yml   # Portainer-ready
├── requirements.txt     # Clean dependency list
└── .dockerignore
```

## 4. API Endpoints

### `GET /health`
- **Purpose:** Healthcheck.
- **Response:** `{"status": "ok", "model": "medium", "device": "cpu"}`

### `POST /transcribe`
- **Purpose:** Upload and transcribe file.
- **Input:** `multipart/form-data` with field `file`.
- **Logic:**
    1. Validate file size and type.
    2. Stream upload to a temporary file.
    3. Transcribe using singleton Whisper model.
    4. Clean up temporary file.
- **Output:** JSON containing `text`, `language`, `segments`, and `usage_example`.

## 5. Configuration (Environment Variables)
- `WHISPER_MODEL`: (tiny/base/small/medium/large-v3) Default: `medium`.
- `WHISPER_LANGUAGE`: Language code (e.g., `pt`). Default: `None` (auto-detect).
- `MAX_FILE_SIZE_MB`: Max upload size. Default: `500`.
- `PORT`: API port. Default: `8000`.

## 6. Infrastructure & Docker
- **Image:** `python:3.11-slim-bookworm`
- **System Deps:** `ffmpeg`, `build-essential`, `curl`.
- **Volumes:** `/root/.cache/whisper` (persistent model storage).
- **RAM Limit:** 12GB via Docker Compose.
- **Platform:** `linux/arm64`.

## 7. Error Handling
- **413 Request Entity Too Large:** If file exceeds `MAX_FILE_SIZE_MB`.
- **400 Bad Request:** If file type is not audio/video.
- **500 Internal Server Error:** For Whisper or processing failures.

## 8. Lovable Integration
- The response will include a `usage_example` string containing a JavaScript snippet for `fetch`.
- CORS configured to allow all origins (`*`).
