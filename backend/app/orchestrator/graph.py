from typing import Any, Dict, List, TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.member1_issue_analyst.agent import run_issue_analyst
from app.agents.member2_codebase_investigator.agent import run_codebase_investigator
from app.agents.member3_fix_planner.agent import run_fix_planner
from app.agents.member4_qa_reviewer.agent import run_qa_reviewer
from app.state import GraphState


class GraphPayload(TypedDict, total=False):
    user_input: str
    project_path: str
    issue_summary: Dict[str, Any]
    relevant_files: List[str]
    code_findings: Dict[str, Any]
    fix_plan: Dict[str, Any]
    qa_report: Dict[str, Any]
    final_report: Dict[str, Any]
    trace: List[Dict[str, Any]]


def issue_analyst_node(state: GraphPayload) -> GraphPayload:
    graph_state = GraphState(**state)
    updated_state = run_issue_analyst(graph_state)
    return updated_state.model_dump()


def codebase_investigator_node(state: GraphPayload) -> GraphPayload:
    graph_state = GraphState(**state)
    updated_state = run_codebase_investigator(graph_state)
    return updated_state.model_dump()


def fix_planner_node(state: GraphPayload) -> GraphPayload:
    graph_state = GraphState(**state)
    updated_state = run_fix_planner(graph_state)
    return updated_state.model_dump()


def qa_reviewer_node(state: GraphPayload) -> GraphPayload:
    graph_state = GraphState(**state)
    updated_state = run_qa_reviewer(graph_state)
    return updated_state.model_dump()


def finalize_report_node(state: GraphPayload) -> GraphPayload:
    graph_state = GraphState(**state)

    graph_state.final_report = {
        "issue_summary": graph_state.issue_summary,
        "relevant_files": graph_state.relevant_files,
        "code_findings": graph_state.code_findings,
        "fix_plan": graph_state.fix_plan,
        "qa_report": graph_state.qa_report,
    }

    return graph_state.model_dump()


builder = StateGraph(GraphPayload)

builder.add_node("issue_analyst", issue_analyst_node)
builder.add_node("codebase_investigator", codebase_investigator_node)
builder.add_node("fix_planner", fix_planner_node)
builder.add_node("qa_reviewer", qa_reviewer_node)
builder.add_node("finalize_report", finalize_report_node)

builder.add_edge(START, "issue_analyst")
builder.add_edge("issue_analyst", "codebase_investigator")
builder.add_edge("codebase_investigator", "fix_planner")
builder.add_edge("fix_planner", "qa_reviewer")
builder.add_edge("qa_reviewer", "finalize_report")
builder.add_edge("finalize_report", END)

compiled_bug_triage_graph = builder.compile()