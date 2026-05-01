from app.orchestrator.graph import compiled_bug_triage_graph
from app.orchestrator.workflow import run_full_workflow

print("=== LANGGRAPH VERIFICATION ===")

# 1. Check compiled graph type
graph_type = type(compiled_bug_triage_graph).__name__
print("Graph object type:", graph_type)
assert graph_type == "CompiledStateGraph", f"Expected CompiledStateGraph, got {graph_type}"

# 2. Check graph topology
mermaid = compiled_bug_triage_graph.get_graph().draw_mermaid()
print("\n--- Graph Mermaid ---")
print(mermaid)

required_nodes = [
    "issue_analyst",
    "codebase_investigator",
    "fix_planner",
    "qa_reviewer",
    "finalize_report",
]

for node in required_nodes:
    assert node in mermaid, f"Missing node in graph: {node}"

required_edges = [
    "__start__ --> issue_analyst;",
    "issue_analyst --> codebase_investigator;",
    "codebase_investigator --> fix_planner;",
    "fix_planner --> qa_reviewer;",
    "qa_reviewer --> finalize_report;",
    "finalize_report --> __end__;",
]

for edge in required_edges:
    assert edge in mermaid, f"Missing edge in graph: {edge}"

# 3. Check actual invocation through workflow
result = run_full_workflow(
    user_input="Login fails and the app crashes after entering wrong credentials.",
    project_path=r"data\sample_projects\zip_demo_app",
)

print("\n--- Workflow Result ---")
print("Result object type:", type(result).__name__)
print("Relevant files:", result.relevant_files)
print("Trace length:", len(result.trace))
print("Final report keys:", list(result.final_report.keys()))

assert type(result).__name__ == "GraphState"
assert len(result.trace) == 4, f"Expected 4 trace entries, got {len(result.trace)}"
assert "issue_summary" in result.final_report
assert "code_findings" in result.final_report
assert "fix_plan" in result.final_report
assert "qa_report" in result.final_report

print("\nLANGGRAPH CHECK PASSED")