from pathlib import Path
from app.agents.member2_codebase_investigator.tool_repo_search import search_repository
from app.agents.member2_codebase_investigator.tool_file_reader import read_file_excerpt
from app.agents.member2_codebase_investigator.tool_code_hints import extract_code_hints
from app.agents.member2_codebase_investigator.agent import run_codebase_investigator
from app.agents.member1_issue_analyst.agent import run_issue_analyst
from app.state import GraphState


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
    file.write_text('return result["message"]', encoding="utf-8")

    content = read_file_excerpt(str(file))
    assert 'result["message"]' in content


def test_extract_code_hints_detects_nameerror_pattern():
    code = 'def login_user():\n    return result["message"]\n'
    hints = extract_code_hints(code)
    assert any("result" in hint.lower() for hint in hints)


def test_codebase_investigator_finds_correct_file_and_statement():
    state = GraphState(
        user_input="Login fails and the app crashes after entering wrong credentials.",
        project_path=r"data\sample_projects\zip_demo_app",
    )

    state = run_issue_analyst(state)
    updated = run_codebase_investigator(state)

    assert len(updated.relevant_files) == 1
    assert updated.relevant_files[0].endswith("login_handler.py")

    findings = updated.code_findings
    assert isinstance(findings, dict)
    assert "probable_cause" in findings
    assert "suspicious_statement" in findings
    assert findings["suspicious_statement"] == 'return result["message"]'
    assert "result" in findings["probable_cause"].lower()