from app.agents.member1_issue_analyst.tool_bug_report_parser import parse_bug_report


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