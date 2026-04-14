from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentTraceEntry(BaseModel):
    agent: str
    step: str
    tool_used: Optional[str] = None
    summary: str


class GraphState(BaseModel):
    user_input: str = ""
    project_path: str = ""
    issue_summary: Dict[str, Any] = Field(default_factory=dict)
    relevant_files: List[str] = Field(default_factory=list)
    code_findings: str = ""
    fix_plan: str = ""
    qa_report: str = ""
    final_report: str = ""
    trace: List[AgentTraceEntry] = Field(default_factory=list)