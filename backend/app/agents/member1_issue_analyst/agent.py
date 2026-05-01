import json
from app.agents.member1_issue_analyst.prompt import ISSUE_ANALYST_PROMPT
from app.agents.member1_issue_analyst.tool_bug_report_parser import parse_bug_report
from app.shared.llm import get_worker_llm
from app.shared.logger import (
    log_text,
    log_trace,
    log_agent_start,
    log_tool_call,
    log_agent_end,
)
from app.state import GraphState, AgentTraceEntry


def _coerce_expected_behavior_to_string(expected_behavior) -> str:
    if isinstance(expected_behavior, str):
        return expected_behavior.strip()

    if isinstance(expected_behavior, dict):
        successful = str(expected_behavior.get("successful_flow", "")).strip()
        safe_failure = str(expected_behavior.get("failure_safe_flow", "")).strip()

        parts = [part for part in [successful, safe_failure] if part]
        if parts:
            return " ".join(parts)

    return ""


def _normalize_expected_behavior(user_input: str, llm_summary: dict) -> dict:
    text = user_input.lower()

    expected = _coerce_expected_behavior_to_string(llm_summary.get("expected_behavior", ""))
    llm_summary["expected_behavior"] = expected

    if "login" in text and "credential" in text:
        llm_summary["expected_behavior"] = (
            "Correct credentials should log in successfully, and wrong credentials "
            "should return an error message without crashing."
        )
        if not llm_summary.get("suspected_module") or llm_summary.get("suspected_module") == "unknown":
            llm_summary["suspected_module"] = "authentication system"
        if not llm_summary.get("next_investigation_focus"):
            llm_summary["next_investigation_focus"] = "Authentication module validation logic"
        return llm_summary

    if not llm_summary["expected_behavior"]:
        llm_summary["expected_behavior"] = (
            "The operation should succeed when valid input is provided, and invalid input "
            "should be handled safely without crashing."
        )

    return llm_summary


def run_issue_analyst(state: GraphState) -> GraphState:
    log_text("Issue Analyst started")
    log_agent_start(
        state.run_id,
        "Issue Analyst",
        {
            "user_input": state.user_input,
        },
    )

    parsed = parse_bug_report(state.user_input)
    log_tool_call(
        state.run_id,
        "Issue Analyst",
        "parse_bug_report",
        {"report_text": state.user_input},
        parsed,
    )

    llm = get_worker_llm()
    prompt = f"""
{ISSUE_ANALYST_PROMPT}

Bug report:
{state.user_input}

Parsed helper data:
{parsed}
"""

    response = llm.invoke(prompt)
    content = response.content if hasattr(response, "content") else str(response)

    try:
        llm_summary = json.loads(content)
    except Exception:
        llm_summary = {
            "title": "Bug Report Analysis",
            "severity": parsed.get("severity", "medium"),
            "suspected_module": parsed.get("suspected_module", "unknown"),
            "problem_description": parsed.get("original_report", ""),
            "expected_behavior": (
                "The operation should succeed when valid input is provided, and invalid input "
                "should be handled safely without crashing."
            ),
            "next_investigation_focus": "Inspect the most relevant file and suspicious statement.",
        }

    llm_summary = _normalize_expected_behavior(state.user_input, llm_summary)

    state.issue_summary = {
        "parsed": parsed,
        "llm_summary": llm_summary,
    }

    state.trace.append(
        AgentTraceEntry(
            agent="Issue Analyst",
            step="Structured bug analysis completed",
            tool_used="parse_bug_report",
            summary="Extracted severity and generated issue summary",
        )
    )

    log_trace({
        "run_id": state.run_id,
        "agent": "Issue Analyst",
        "tool": "parse_bug_report",
        "input": state.user_input,
        "output_summary": "Issue summary created",
    })

    log_agent_end(
        state.run_id,
        "Issue Analyst",
        {
            "issue_summary": state.issue_summary,
            "trace_count": len(state.trace),
        },
    )

    log_text("Issue Analyst completed")
    return state