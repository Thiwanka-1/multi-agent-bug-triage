from app.orchestrator.graph import compiled_bug_triage_graph
from app.shared.logger import create_run_id, log_workflow_summary
from app.state import GraphState


def run_full_workflow(user_input: str, project_path: str = "") -> GraphState:
    run_id = create_run_id()

    initial_state = {
        "run_id": run_id,
        "user_input": user_input,
        "project_path": project_path,
        "issue_summary": {},
        "relevant_files": [],
        "code_findings": {},
        "fix_plan": {},
        "qa_report": {},
        "final_report": {},
        "trace": [],
    }

    result = compiled_bug_triage_graph.invoke(initial_state)
    final_state = GraphState(**result)

    log_workflow_summary(
        run_id,
        {
            "relevant_files": final_state.relevant_files,
            "trace_count": len(final_state.trace),
            "final_report_keys": list(final_state.final_report.keys()),
        },
    )

    return final_state