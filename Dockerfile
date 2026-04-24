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
