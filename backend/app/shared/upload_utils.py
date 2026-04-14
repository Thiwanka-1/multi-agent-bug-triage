from __future__ import annotations

import shutil
import uuid
import zipfile
from pathlib import Path
from typing import Tuple

from fastapi import UploadFile

from app.config import settings


ALLOWED_SINGLE_FILE_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".json"}
ALLOWED_UPLOAD_EXTENSIONS = ALLOWED_SINGLE_FILE_EXTENSIONS | {".zip"}


def _safe_name(filename: str) -> str:
    return Path(filename).name.replace(" ", "_")


def save_uploaded_codebase(upload: UploadFile) -> Tuple[str, str]:
    """
    Save an uploaded codebase file into the uploads directory.

    Supports:
    - .zip archives
    - single code files (.py, .js, .jsx, .ts, .tsx, .json)

    Returns:
        tuple[str, str]:
            - project_path: extracted folder path or containing folder path
            - upload_kind: "zip" or "single_file"

    Raises:
        ValueError: if file type is not allowed or upload is invalid.
    """
    if not upload.filename:
        raise ValueError("No file name was provided.")

    original_name = _safe_name(upload.filename)
    suffix = Path(original_name).suffix.lower()

    if suffix not in ALLOWED_UPLOAD_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{suffix}'. Allowed: .zip, .py, .js, .jsx, .ts, .tsx, .json"
        )

    upload_id = uuid.uuid4().hex[:12]
    target_root = settings.upload_dir / upload_id
    target_root.mkdir(parents=True, exist_ok=True)

    saved_path = target_root / original_name

    with saved_path.open("wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)

    if suffix == ".zip":
        extract_dir = target_root / "extracted"
        extract_dir.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(saved_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)
        except zipfile.BadZipFile as exc:
            raise ValueError("Uploaded ZIP file is invalid or corrupted.") from exc

        return str(extract_dir), "zip"

    single_dir = target_root / "single_file_project"
    single_dir.mkdir(parents=True, exist_ok=True)

    moved_path = single_dir / original_name
    shutil.move(str(saved_path), str(moved_path))

    return str(single_dir), "single_file"