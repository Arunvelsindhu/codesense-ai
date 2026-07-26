from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    gemini_api_key: str
    # Optional: only needed as a fallback for private repos. Users can also
    # supply a token per-request instead of setting one server-side.
    github_token: Optional[str] = None
    chroma_persist_dir: str = "./chroma_db"
    sqlite_db_path: str = "./data/codesense.db"

    class Config:
        env_file = ".env"

settings = Settings()