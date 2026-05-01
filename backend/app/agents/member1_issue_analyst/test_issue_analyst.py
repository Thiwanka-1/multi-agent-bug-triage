from app.agents.member1_issue_analyst.tool_bug_report_parser import parse_bug_report
from app.agents.member1_issue_analyst.agent import run_issue_analyst
from app.state import GraphState


def test_parse_bug_report_high_severity():
    result = parse_bug_report("The app crashes when saving profile data.")
    assert result["severity"] == "high"


def test_parse_bug_report_low_severity():
    result = parse_bug_report("Minor UI issue in dashboard alignment.")
    assert result["severity"] == "low"


def test_parse_bug_report_returns_original_text():
    text = "Login button does not respond."
    result = parse_bug_report(text)
    assert result["original_report"] == text


def test_issue_analyst_output_is_structured_and_safe():
    state = GraphState(
        user_input="Login fails and the app crashes after entering wrong credentials."
    )

    updated = run_issue_analyst(state)
    summary = updated.issue_summary["llm_summary"]

    assert isinstance(summary, dict)
    assert "title" in summary
    assert "severity" in summary
    assert "problem_description" in summary
    assert "expected_behavior" in summary
    assert summary["severity"] == "high"
    assert "wrong credentials" in summary["expected_behavior"].lower() or "without crashing" in summary["expected_behavior"].lower()