from app.orchestrator.graph import compiled_bug_triage_graph
from app.orchestrator.workflow import run_full_workflow


def test_langgraph_compiles_as_real_graph():
    assert type(compiled_bug_triage_graph).__name__ == "CompiledStateGraph"


def test_langgraph_workflow_runs_end_to_end():
    result = run_full_workflow(
        user_input="Login fails and the app crashes after entering wrong credentials.",
        project_path=r"data\sample_projects\zip_demo_app",
    )

    assert type(result).__name__ == "GraphState"
    assert len(result.trace) == 4
    assert len(result.relevant_files) == 1
    assert result.relevant_files[0].endswith("login_handler.py")
    assert result.code_findings["suspicious_statement"] == 'return result["message"]'
    assert "issue_summary" in result.final_report
    assert "code_findings" in result.final_report
    assert "fix_plan" in result.final_report
    assert "qa_report" in result.final_report