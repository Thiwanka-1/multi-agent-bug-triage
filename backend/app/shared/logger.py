import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from typing import Any

from app.config import settings


TRACE_FILE = settings.log_dir / "run_trace.jsonl"
TEXT_LOG = settings.log_dir / "agent_steps.log"
RUNS_DIR = settings.log_dir / "runs"
RUNS_DIR.mkdir(parents=True, exist_ok=True)


def create_run_id() -> str:
    return uuid4().hex[:12]


def _now() -> str:
    return datetime.now().isoformat()


def _safe_data(value: Any) -> Any:
    """
    Convert values into JSON-safe compact representations for logs.
    """
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    if isinstance(value, list):
        return [_safe_data(item) for item in value]

    if isinstance(value, dict):
        return {str(k): _safe_data(v) for k, v in value.items()}

    if hasattr(value, "model_dump"):
        return _safe_data(value.model_dump())

    return str(value)


def _append_jsonl(path: Path, payload: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def log_text(message: str) -> None:
    with TEXT_LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{_now()}] {message}\n")


def log_trace(data: dict) -> None:
    payload = {
        "timestamp": _now(),
        **_safe_data(data),
    }
    _append_jsonl(TRACE_FILE, payload)


def log_run_event(run_id: str, event_type: str, data: dict) -> None:
    payload = {
        "timestamp": _now(),
        "run_id": run_id,
        "event_type": event_type,
        **_safe_data(data),
    }

    run_file = RUNS_DIR / f"{run_id}.jsonl"
    _append_jsonl(run_file, payload)
    _append_jsonl(TRACE_FILE, payload)


def log_agent_start(run_id: str, agent: str, input_data: dict) -> None:
    log_run_event(
        run_id,
        "agent_start",
        {
            "agent": agent,
            "input": input_data,
        },
    )


def log_tool_call(run_id: str, agent: str, tool_name: str, tool_input: dict, tool_output: Any) -> None:
    log_run_event(
        run_id,
        "tool_call",
        {
            "agent": agent,
            "tool_name": tool_name,
            "tool_input": tool_input,
            "tool_output": tool_output,
        },
    )


def log_agent_end(run_id: str, agent: str, output_data: dict) -> None:
    log_run_event(
        run_id,
        "agent_end",
        {
            "agent": agent,
            "output": output_data,
        },
    )


def log_workflow_summary(run_id: str, summary: dict) -> None:
    log_run_event(
        run_id,
        "workflow_summary",
        summary,
    )