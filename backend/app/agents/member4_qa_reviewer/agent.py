import json
from app.agents.member4_qa_reviewer.prompt import QA_REVIEWER_PROMPT
from app.agents.member4_qa_reviewer.tool_qa_checklist import generate_qa_checklist
from app.shared.llm import get_coordinator_llm
from app.shared.logger import (
    log_text,
    log_trace,
    log_agent_start,
    log_tool_call,
    log_agent_end,
)
from app.state import GraphState, AgentTraceEntry


def _default_qa_checklist():
    return [
        "Verify the original issue can be reproduced before the fix.",
        "Apply the proposed fix and verify the original issue no longer occurs.",
        "Test related user flow for regressions.",
    ]


def _default_regression_risks():
    return [
        "Invalid input cases may still fail if the fix is incomplete.",
        "Valid login flow may break if the return logic is changed incorrectly.",
    ]


def run_qa_reviewer(state: GraphState) -> GraphState:
    log_text("QA Reviewer started")
    log_agent_start(
        state.run_id,
        "QA Reviewer",
        {
            "issue_summary": state.issue_summary,
            "code_findings": state.code_findings,
            "fix_plan": state.fix_plan,
        },
    )

    checklist_seed = generate_qa_checklist(state.user_input)
    log_tool_call(
        state.run_id,
        "QA Reviewer",
        "generate_qa_checklist",
        {"issue_text": state.user_input},
        {"checklist_seed": checklist_seed},
    )

    llm = get_coordinator_llm()
    prompt = f"""
{QA_REVIEWER_PROMPT}

Issue summary:
{state.issue_summary}

Code findings:
{state.code_findings}

Fix plan:
{state.fix_plan}

Checklist seed:
{checklist_seed}
"""

    response = llm.invoke(prompt)
    content = response.content if hasattr(response, "content") else str(response)
    cleaned = content.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(cleaned)
    except Exception:
        parsed = {}

    qa_checklist = parsed.get("qa_checklist", []) if isinstance(parsed, dict) else []
    if len(qa_checklist) < 3:
        qa_checklist = _default_qa_checklist()

    acceptance_criteria = parsed.get("acceptance_criteria", []) if isinstance(parsed, dict) else []

    success_item = "Correct credentials should log in successfully."
    safe_failure_item = "Wrong credentials should return an error message without crashing."

    cleaned_acceptance = []
    for item in acceptance_criteria:
        text = str(item).strip()
        lowered = text.lower()

        if "crash" in lowered and "without crashing" not in lowered and "no longer occurs" not in lowered:
            continue

        cleaned_acceptance.append(text)

    has_success_path = any(
        "correct credentials" in str(item).lower() or "log in successfully" in str(item).lower()
        for item in cleaned_acceptance
    )
    has_safe_failure = any(
        "without crashing" in str(item).lower()
        for item in cleaned_acceptance
    )

    final_acceptance = []

    if has_success_path:
        for item in cleaned_acceptance:
            lowered = str(item).lower()
            if "correct credentials" in lowered or "log in successfully" in lowered:
                final_acceptance.append(item)
                break
    else:
        final_acceptance.append(success_item)

    if has_safe_failure:
        for item in cleaned_acceptance:
            if "without crashing" in str(item).lower():
                final_acceptance.append(item)
                break
    else:
        final_acceptance.append(safe_failure_item)

    regression_risks = parsed.get("regression_risks", []) if isinstance(parsed, dict) else []
    if len(regression_risks) < 2:
        regression_risks = _default_regression_risks()

    state.qa_report = {
        "qa_checklist": qa_checklist[:3],
        "acceptance_criteria": final_acceptance,
        "regression_risks": regression_risks[:2],
        "decision": "needs_changes",
    }

    state.trace.append(
        AgentTraceEntry(
            agent="QA Reviewer",
            step="QA review completed",
            tool_used="generate_qa_checklist",
            summary="Generated QA review and acceptance checks",
        )
    )

    log_trace({
        "run_id": state.run_id,
        "agent": "QA Reviewer",
        "tool": "generate_qa_checklist",
        "input": state.user_input,
        "output_summary": "QA review created",
    })

    log_agent_end(
        state.run_id,
        "QA Reviewer",
        {
            "qa_report": state.qa_report,
            "trace_count": len(state.trace),
        },
    )

    log_text("QA Reviewer completed")
    return state