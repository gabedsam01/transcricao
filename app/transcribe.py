import os
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
                    download_root=settings.WHISPER_CACHE_DIR or os.path.join(os.path.expanduser("~"), ".cache", "whisper")
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
        
    segments, info = model.transcribe(file_path, language=lang_to_use, beam_size=2)
    
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
