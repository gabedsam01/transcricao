FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install -r /app/requirements.txt \
    && python -c "import requests; import faster_whisper; print('dependency-imports-ok')"

COPY app/ /app/app/

ENV PORT=8000
ENV WHISPER_MODEL=small
ENV WHISPER_LANGUAGE=pt
ENV MAX_FILE_SIZE_MB=500
ENV FW_DEVICE=cpu
ENV FW_COMPUTE_TYPE=int8
ENV FW_CPU_THREADS=4

VOLUME /root/.cache/whisper

HEALTHCHECK --interval=30s --timeout=10s --start-period=300s --retries=5 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

EXPOSE ${PORT}

CMD ["python", "-m", "app.main"]
