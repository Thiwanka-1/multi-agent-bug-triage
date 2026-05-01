from app.agents.member4_qa_reviewer.tool_qa_checklist import generate_qa_checklist
from app.agents.member4_qa_reviewer.agent import run_qa_reviewer
from app.agents.member3_fix_planner.agent import run_fix_planner
from app.agents.member2_codebase_investigator.agent import run_codebase_investigator
from app.agents.member1_issue_analyst.agent import run_issue_analyst
from app.state import GraphState


def test_generate_qa_checklist_has_multiple_items():
    result = generate_qa_checklist("Dashboard crashes on save")
    assert len(result) >= 4


def test_generate_qa_checklist_mentions_context():
    result = generate_qa_checklist("Login fails after password reset")
    assert any("Login fails" in item for item in result)


def test_qa_reviewer_returns_safe_decision_and_checks():
    state = GraphState(
        user_input="Login fails and the app crashes after entering wrong credentials.",
        project_path=r"data\sample_projects\zip_demo_app",
    )

    state = run_issue_analyst(state)
    state = run_codebase_investigator(state)
    state = run_fix_planner(state)
    updated = run_qa_reviewer(state)

    report = updated.qa_report
    assert isinstance(report, dict)
    assert report["decision"] == "needs_changes"
    assert len(report["qa_checklist"]) >= 3
    assert any("without crashing" in item.lower() for item in report["acceptance_criteria"])