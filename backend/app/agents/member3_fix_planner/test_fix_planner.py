from app.agents.member3_fix_planner.tool_task_plan_writer import build_fix_steps


def test_build_fix_steps_contains_reproduction():
    results = build_fix_steps(["a.py"])
    assert "Reproduce the issue locally" in results[0]


def test_build_fix_steps_contains_file_steps():
    results = build_fix_steps(["a.py", "b.py"])
    assert any("a.py" in step for step in results)
    assert any("b.py" in step for step in results)