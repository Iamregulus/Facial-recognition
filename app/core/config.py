from pydantic_settings import BaseSettings # type: ignore
from pathlib import Path

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Face Verification API"
    
    # Directory settings
    UPLOAD_DIR: Path = Path("static/uploads")
    
    # Face verification settings
    FACE_MATCH_TOLERANCE: float = 0.3

    class Config:
        case_sensitive = True

settings = Settings()

# Ensure upload directory exists
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True) 