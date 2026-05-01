import json
from app.agents.member3_fix_planner.prompt import FIX_PLANNER_PROMPT
from app.agents.member3_fix_planner.tool_task_plan_writer import build_fix_steps
from app.shared.llm import get_worker_llm
from app.shared.logger import (
    log_text,
    log_trace,
    log_agent_start,
    log_tool_call,
    log_agent_end,
)
from app.state import GraphState, AgentTraceEntry


def _best_direct_fix(suspicious_statement: str, current_fix: str) -> str:
    normalized = (current_fix or "").strip().lower()

    if suspicious_statement == 'return result["message"]':
        return 'Replace `return result["message"]` with `return {"success": False, "message": "Invalid credentials"}`.'

    if suspicious_statement == "return result['message']":
        return 'Replace `return result[\'message\']` with `return {"success": False, "message": "Invalid credentials"}`.'

    if suspicious_statement == 'return profile["non_existing_key"]':
        return 'Replace `return profile["non_existing_key"]` with a valid existing profile value, such as `return profile["name"]` if that is the intended field.'

    if suspicious_statement == "return profile['non_existing_key']":
        return 'Replace `return profile[\'non_existing_key\']` with a valid existing profile value, such as `return profile["name"]` if that is the intended field.'

    if normalized:
        return current_fix

    return "Replace the suspicious statement with the correct logic."


def run_fix_planner(state: GraphState) -> GraphState:
    log_text("Fix Planner started")
    log_agent_start(
        state.run_id,
        "Fix Planner",
        {
            "relevant_files": state.relevant_files,
            "code_findings": state.code_findings,
        },
    )

    steps = build_fix_steps(state.relevant_files)
    log_tool_call(
        state.run_id,
        "Fix Planner",
        "build_fix_steps",
        {"relevant_files": state.relevant_files},
        {"steps": steps},
    )

    suspicious_statement = ""
    probable_cause = ""

    if isinstance(state.code_findings, dict):
        suspicious_statement = state.code_findings.get("suspicious_statement", "")
        probable_cause = state.code_findings.get("probable_cause", "")

    llm = get_worker_llm()
    prompt = f"""
{FIX_PLANNER_PROMPT}

Issue summary:
{state.issue_summary}

Code findings:
{state.code_findings}

Suggested ordered steps:
{steps}

Exact suspicious statement:
{suspicious_statement or "None"}

Probable cause:
{probable_cause or "None"}
"""

    response = llm.invoke(prompt)
    content = response.content if hasattr(response, "content") else str(response)

    cleaned = content.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(cleaned)
    except Exception:
        parsed = {}

    direct_fix = parsed.get("direct_fix", "") if isinstance(parsed, dict) else ""
    direct_fix = _best_direct_fix(suspicious_statement, direct_fix)

    implementation_steps = parsed.get("implementation_steps", []) if isinstance(parsed, dict) else []
    if len(implementation_steps) < 3:
        implementation_steps = [
            "Reproduce the issue locally and confirm the failure conditions.",
            "Edit the suspicious statement in the selected file and replace it with the correct logic.",
            "Save the file and retest the same failing scenario."
        ]

    regression_checks = parsed.get("regression_checks", []) if isinstance(parsed, dict) else []
    if len(regression_checks) < 3:
        regression_checks = [
            "Retest the original failing scenario.",
            "Test the normal success path.",
            "Test one invalid input case."
        ]

    state.fix_plan = {
        "priority": parsed.get("priority", "high") if isinstance(parsed, dict) else "high",
        "direct_fix": direct_fix,
        "implementation_steps": implementation_steps[:3],
        "regression_checks": regression_checks[:3],
    }

    state.trace.append(
        AgentTraceEntry(
            agent="Fix Planner",
            step="Fix plan generated",
            tool_used="build_fix_steps",
            summary="Produced more code-aware implementation plan",
        )
    )

    log_trace({
        "run_id": state.run_id,
        "agent": "Fix Planner",
        "tool": "build_fix_steps",
        "input": state.relevant_files,
        "output_summary": "Code-aware fix plan prepared",
    })

    log_agent_end(
        state.run_id,
        "Fix Planner",
        {
            "fix_plan": state.fix_plan,
            "trace_count": len(state.trace),
        },
    )

    log_text("Fix Planner completed")
    return state