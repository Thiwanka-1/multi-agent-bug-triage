from pathlib import Path
from typing import List, Tuple


def search_repository(project_path: str, keywords: List[str]) -> List[str]:
    """
    Search a local repository for files containing the given keywords and rank them by relevance.

    Args:
        project_path: Path to the project folder.
        keywords: Keywords to search for.

    Returns:
        A ranked list of matching file paths.
    """
    root = Path(project_path) if project_path else Path.cwd()
    if not root.exists() or not root.is_dir():
        return []

    allowed_suffixes = {".py", ".js", ".jsx", ".ts", ".tsx", ".json"}
    ignored_dirs = {
        "venv",
        ".venv",
        "__pycache__",
        "node_modules",
        ".git",
        "dist",
        "build",
        ".pytest_cache",
    }

    scored_matches: List[Tuple[str, int]] = []

    for file_path in root.rglob("*"):
        if any(part in ignored_dirs for part in file_path.parts):
            continue

        if file_path.is_file() and file_path.suffix.lower() in allowed_suffixes:
            try:
                text = file_path.read_text(encoding="utf-8", errors="ignore").lower()
                score = 0
                filename = file_path.name.lower()

                for keyword in keywords:
                    kw = keyword.lower()
                    score += text.count(kw)
                    if kw in filename:
                        score += 10

                if score > 0:
                    scored_matches.append((str(file_path), score))
            except Exception:
                continue

    scored_matches.sort(key=lambda item: item[1], reverse=True)
    return [path for path, _ in scored_matches[:2]]