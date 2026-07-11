from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Keys
    openai_api_key: str = ""
    gemini_api_key: str = ""

    # GitLab
    gitlab_webhook_secret: str = ""

    # Google Calendar
    google_credentials_path: str = "./credentials.json"

    # Telegram
    telegram_bot_token: str = ""

    # Paths
    raw_logs_dir: Path = Path("./raw_logs")
    init_dir: Path = Path("./init")
    vault_dir: Path = Path("./vault")
    jobs_dir: Path = Path("./jobs")

    # Database & Vector DB
    qdrant_url: str = "http://localhost:6333"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pro_copilot"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
