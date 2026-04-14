import json
from datetime import datetime
from pathlib import Path
from app.config import settings


TRACE_FILE = settings.log_dir / "run_trace.jsonl"
TEXT_LOG = settings.log_dir / "agent_steps.log"


def log_text(message: str) -> None:
    timestamp = datetime.now().isoformat()
    with TEXT_LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def log_trace(data: dict) -> None:
    payload = {
        "timestamp": datetime.now().isoformat(),
        **data,
    }
    with TRACE_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")