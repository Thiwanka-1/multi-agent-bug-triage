from app.agents.member4_qa_reviewer.tool_qa_checklist import generate_qa_checklist


def test_generate_qa_checklist_has_multiple_items():
    result = generate_qa_checklist("Dashboard crashes on save")
    assert len(result) >= 4


def test_generate_qa_checklist_mentions_context():
    result = generate_qa_checklist("Login fails after password reset")
    assert any("Login fails" in item for item in result)