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
