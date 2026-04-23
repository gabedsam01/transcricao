import whisper
import threading
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
                logger.info(f"Loading Whisper model: {settings.WHISPER_MODEL}")
                _model = whisper.load_model(settings.WHISPER_MODEL)
                logger.info("Whisper model loaded successfully")
    return _model

def transcribe_file(file_path: str) -> dict:
    """
    Transcribes an audio file and returns a dictionary with text, language and segments.
    """
    model = get_model()
    logger.info(f"Transcribing file: {file_path}")
    
    # transcribe() parameters can be adjusted as needed (e.g., language, task)
    options = {}
    if settings.WHISPER_LANGUAGE:
        options["language"] = settings.WHISPER_LANGUAGE
        
    result = model.transcribe(file_path, **options)
    
    return {
        "text": result.get("text", ""),
        "language": result.get("language", ""),
        "segments": result.get("segments", [])
    }
