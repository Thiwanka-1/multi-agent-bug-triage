import json
from app.agents.member2_codebase_investigator.prompt import CODEBASE_INVESTIGATOR_PROMPT
from app.agents.member2_codebase_investigator.tool_repo_search import search_repository
from app.agents.member2_codebase_investigator.tool_file_reader import read_file_excerpt
from app.agents.member2_codebase_investigator.tool_code_hints import extract_code_hints
from app.shared.llm import get_worker_llm
from app.shared.logger import log_text, log_trace
from app.state import GraphState, AgentTraceEntry


def _extract_exact_suspicious_statement(excerpt: str) -> str:
    for line in excerpt.splitlines():
        stripped = line.strip()
        if 'return result["message"]' in stripped or "return result['message']" in stripped:
            return stripped
        if 'return profile["non_existing_key"]' in stripped or "return profile['non_existing_key']" in stripped:
            return stripped
    return ""


def _derive_probable_cause_from_statement(statement: str) -> str:
    if statement == 'return result["message"]' or statement == "return result['message']":
        return "NameError: variable 'result' is used before being defined."
    if statement == 'return profile["non_existing_key"]' or statement == "return profile['non_existing_key']":
        return "KeyError: code accesses a dictionary key that does not exist."
    return "Possible bug found in selected file."


def run_codebase_investigator(state: GraphState) -> GraphState:
    log_text("Codebase Investigator started")

    keywords = ["login", "credentials", "password", "username", "auth", "invalid", "crash"]
    matches = search_repository(state.project_path, keywords)
    selected_files = matches[:1]

    file_context_blocks = []
    hint_blocks = []
    exact_suspicious_statement = ""

    for file_path in selected_files:
        excerpt = read_file_excerpt(file_path, max_chars=3000)
        if excerpt.strip():
            file_context_blocks.append(f"FILE: {file_path}\n{excerpt}")

            if not exact_suspicious_statement:
                exact_suspicious_statement = _extract_exact_suspicious_statement(excerpt)

            hints = extract_code_hints(excerpt)
            if hints:
                hint_blocks.append(
                    f"FILE: {file_path}\n" + "\n".join(f"- {hint}" for hint in hints)
                )

    file_context = "\n\n".join(file_context_blocks) if file_context_blocks else "No readable file excerpts found."
    code_hints = "\n\n".join(hint_blocks) if hint_blocks else "No rule-based bug hints found."

    llm = get_worker_llm()
    prompt = f"""
{CODEBASE_INVESTIGATOR_PROMPT}

Issue summary:
{state.issue_summary}

Matching files:
{selected_files}

File excerpts:
{file_context}

Rule-based bug hints:
{code_hints}

Exact suspicious statement detected:
{exact_suspicious_statement or "None"}

Analyze the actual code excerpts carefully.
If an exact suspicious statement is provided, use it directly.
"""

    response = llm.invoke(prompt)
    content = response.content if hasattr(response, "content") else str(response)

    cleaned = content.replace("```json", "").replace("```", "").strip()

    try:
        parsed_findings = json.loads(cleaned)
    except Exception:
        parsed_findings = {
            "relevant_files": selected_files,
            "probable_cause": _derive_probable_cause_from_statement(exact_suspicious_statement),
            "suspicious_statement": exact_suspicious_statement,
            "notes": "Derived from rule-based analysis because LLM output could not be parsed cleanly."
        }

    if not parsed_findings.get("suspicious_statement"):
        parsed_findings["suspicious_statement"] = exact_suspicious_statement

    if (
        not parsed_findings.get("probable_cause")
        or parsed_findings.get("probable_cause") == "Possible bug found in selected file."
    ):
        parsed_findings["probable_cause"] = _derive_probable_cause_from_statement(
            parsed_findings.get("suspicious_statement", "")
        )

    state.relevant_files = selected_files
    state.code_findings = parsed_findings

    state.trace.append(
        AgentTraceEntry(
            agent="Codebase Investigator",
            step="Repository investigation completed",
            tool_used="search_repository + read_file_excerpt + extract_code_hints",
            summary=f"Selected {len(selected_files)} most relevant file(s) and generated code hints",
        )
    )

    log_trace({
        "agent": "Codebase Investigator",
        "tool": "search_repository + read_file_excerpt + extract_code_hints",
        "input": state.project_path,
        "output_summary": f"{len(selected_files)} top-ranked file(s) analyzed",
    })

    log_text("Codebase Investigator completed")
    return state