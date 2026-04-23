from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    WHISPER_MODEL: str = "medium"
    WHISPER_LANGUAGE: str | None = None
    MAX_FILE_SIZE_MB: int = 500
    PORT: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()
