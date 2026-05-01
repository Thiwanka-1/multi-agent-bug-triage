from app.agents.member3_fix_planner.tool_task_plan_writer import build_fix_steps
from app.agents.member3_fix_planner.agent import run_fix_planner
from app.agents.member2_codebase_investigator.agent import run_codebase_investigator
from app.agents.member1_issue_analyst.agent import run_issue_analyst
from app.state import GraphState


def test_build_fix_steps_contains_reproduction():
    results = build_fix_steps(["a.py"])
    assert "Reproduce the issue locally" in results[0]


def test_build_fix_steps_contains_file_steps():
    results = build_fix_steps(["a.py", "b.py"])
    assert any("a.py" in step for step in results)
    assert any("b.py" in step for step in results)


def test_fix_planner_returns_precise_fix():
    state = GraphState(
        user_input="Login fails and the app crashes after entering wrong credentials.",
        project_path=r"data\sample_projects\zip_demo_app",
    )

    state = run_issue_analyst(state)
    state = run_codebase_investigator(state)
    updated = run_fix_planner(state)

    plan = updated.fix_plan
    assert isinstance(plan, dict)
    assert plan["priority"] == "high"
    assert "Invalid credentials" in plan["direct_fix"]
    assert len(plan["implementation_steps"]) >= 3
    assert len(plan["regression_checks"]) >= 3