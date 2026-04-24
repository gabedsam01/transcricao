import time
import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, HTTPException, Form
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.logger import logger
from app.transcribe import transcribe_file, get_model

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load the model on startup to avoid delay on the first request.
    """
    logger.info("Initializing application startup...")
    get_model()
    logger.info("Application startup complete.")
    yield

app = FastAPI(title="Transcription API", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
