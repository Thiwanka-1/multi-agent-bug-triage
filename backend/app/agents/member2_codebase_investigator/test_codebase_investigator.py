from pathlib import Path
from app.agents.member2_codebase_investigator.tool_repo_search import search_repository
from app.agents.member2_codebase_investigator.tool_file_reader import read_file_excerpt


def test_search_repository_finds_matching_file(tmp_path: Path):
    file = tmp_path / "sample.py"
    file.write_text("This function throws a login error", encoding="utf-8")

    results = search_repository(str(tmp_path), ["login"])
    assert len(results) == 1
    assert "sample.py" in results[0]


def test_search_repository_returns_empty_for_no_matches(tmp_path: Path):
    file = tmp_path / "sample.py"
    file.write_text("Everything is fine", encoding="utf-8")

    results = search_repository(str(tmp_path), ["dashboard"])
    assert results == []


def test_read_file_excerpt_returns_content(tmp_path: Path):
    file = tmp_path / "sample.py"
    file.write_text("return profile['non_existing_key']", encoding="utf-8")

    content = read_file_excerpt(str(file))
    assert "non_existing_key" in content