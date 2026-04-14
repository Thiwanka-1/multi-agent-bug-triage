from pathlib import Path
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "Multi-Agent Bug Triage")
    app_env: str = os.getenv("APP_ENV", "development")
    app_host: str = os.getenv("APP_HOST", "127.0.0.1")
    app_port: int = int(os.getenv("APP_PORT", "8000"))

    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    coordinator_model: str = os.getenv("COORDINATOR_MODEL", "llama3.1")
    worker_model: str = os.getenv("WORKER_MODEL", "phi3")

    log_dir: Path = Path(os.getenv("LOG_DIR", "logs"))
    upload_dir: Path = Path(os.getenv("UPLOAD_DIR", "data/uploads"))
    sample_projects_dir: Path = Path(os.getenv("SAMPLE_PROJECTS_DIR", "data/sample_projects"))
    max_file_read_chars: int = int(os.getenv("MAX_FILE_READ_CHARS", "12000"))


settings = Settings()

settings.log_dir.mkdir(parents=True, exist_ok=True)
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.sample_projects_dir.mkdir(parents=True, exist_ok=True)