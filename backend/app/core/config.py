"""Application configuration loaded from environment variables."""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "Document Intelligence API"
    APP_VERSION: str = "1.0.0"
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str = "sqlite:///./documents.db"

    MAX_PAGES: int = 3
    MAX_FILE_SIZE_MB: int = 20
    UPLOAD_DIR: str = "./uploads"

    LLM_PROVIDER: str = "gemini"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gemini-1.5-flash"

    OCR_PROVIDER: str = "tesseract"
    OCR_SPACE_API_KEY: str = ""
    POPPLER_PATH: str = ""


    SUPPORTED_MIME_TYPES: list[str] = [
        "application/pdf",
        "image/jpeg",
        "image/jpg",
        "image/png",
    ]
    SUPPORTED_DOCUMENT_TYPES: list[str] = [
        "invoice",
        "balance_sheet",
        "profit_and_loss",
        "cash_flow_statement",
    ]

    VALIDATION_TOLERANCE: float = 0.01

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
