import json
from app.agents.member1_issue_analyst.prompt import ISSUE_ANALYST_PROMPT
from app.agents.member1_issue_analyst.tool_bug_report_parser import parse_bug_report
from app.shared.llm import get_worker_llm
from app.shared.logger import log_text, log_trace
from app.state import GraphState, AgentTraceEntry


def run_issue_analyst(state: GraphState) -> GraphState:
    log_text("Issue Analyst started")

    parsed = parse_bug_report(state.user_input)

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
            "expected_behavior": "The application should handle the user action without failing.",
            "next_investigation_focus": "Inspect the most relevant file and suspicious statement."
        }

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
        "agent": "Issue Analyst",
        "tool": "parse_bug_report",
        "input": state.user_input,
        "output_summary": "Issue summary created",
    })

    log_text("Issue Analyst completed")
    return state