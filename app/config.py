from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PORT: int = 8000
    WHISPER_MODEL: str = "small"
    WHISPER_LANGUAGE: str = "pt"
    MAX_FILE_SIZE_MB: int = 500
    FW_DEVICE: str = "cpu"
    FW_COMPUTE_TYPE: str = "int8"
    FW_CPU_THREADS: int = 4
    WHISPER_CACHE_DIR: str | None = None
    
    class Config:
        env_file = ".env"

settings = Settings()
