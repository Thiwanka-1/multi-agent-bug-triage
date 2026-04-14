from app.agents.member1_issue_analyst.agent import run_issue_analyst
from app.agents.member2_codebase_investigator.agent import run_codebase_investigator
from app.agents.member3_fix_planner.agent import run_fix_planner
from app.agents.member4_qa_reviewer.agent import run_qa_reviewer
from app.state import GraphState


def run_full_workflow(user_input: str, project_path: str = "") -> GraphState:
    state = GraphState(
        user_input=user_input,
        project_path=project_path,
    )

    state = run_issue_analyst(state)
    state = run_codebase_investigator(state)
    state = run_fix_planner(state)
    state = run_qa_reviewer(state)

    state.final_report = {
        "issue_summary": state.issue_summary,
        "relevant_files": state.relevant_files,
        "code_findings": state.code_findings,
        "fix_plan": state.fix_plan,
        "qa_report": state.qa_report,
    }

    return state