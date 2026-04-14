import json
from app.agents.member4_qa_reviewer.prompt import QA_REVIEWER_PROMPT
from app.agents.member4_qa_reviewer.tool_qa_checklist import generate_qa_checklist
from app.shared.llm import get_coordinator_llm
from app.shared.logger import log_text, log_trace
from app.state import GraphState, AgentTraceEntry


def run_qa_reviewer(state: GraphState) -> GraphState:
    log_text("QA Reviewer started")

    checklist = generate_qa_checklist(state.user_input)

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
{checklist}
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
        qa_checklist = [
            "Verify the original issue can be reproduced before the fix.",
            "Apply the proposed fix and verify the original issue no longer occurs.",
            "Test related user flow for regressions."
        ]

    acceptance_criteria = parsed.get("acceptance_criteria", []) if isinstance(parsed, dict) else []
    cleaned_acceptance = []
    for item in acceptance_criteria:
        text = str(item)
        if "crash" in text.lower() and "without crashing" not in text.lower() and "no longer occurs" not in text.lower():
            continue
        cleaned_acceptance.append(text)

    if len(cleaned_acceptance) < 2:
        cleaned_acceptance = [
            "Correct credentials should log in successfully.",
            "Wrong credentials should return an error message without crashing."
        ]

    regression_risks = parsed.get("regression_risks", []) if isinstance(parsed, dict) else []
    if len(regression_risks) < 2:
        regression_risks = [
            "Invalid input cases may still fail if the fix is incomplete.",
            "Valid login flow may break if the return logic is changed incorrectly."
        ]

    state.qa_report = {
        "qa_checklist": qa_checklist[:3],
        "acceptance_criteria": cleaned_acceptance[:2],
        "regression_risks": regression_risks[:2],
        "decision": "needs_changes"
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
        "agent": "QA Reviewer",
        "tool": "generate_qa_checklist",
        "input": state.user_input,
        "output_summary": "QA review created",
    })

    log_text("QA Reviewer completed")
    return state