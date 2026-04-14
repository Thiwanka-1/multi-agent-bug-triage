from pathlib import Path


def read_file_excerpt(file_path: str, max_chars: int = 4000) -> str:
    """
    Read a safe excerpt from a text file.

    Args:
        file_path: Path to the file.
        max_chars: Maximum number of characters to read.

    Returns:
        File content excerpt as a string. Returns an empty string if unreadable.
    """
    path = Path(file_path)

    if not path.exists() or not path.is_file():
        return ""

    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return text[:max_chars]
    except Exception:
        return ""