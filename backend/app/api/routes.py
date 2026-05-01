from fastapi import APIRouter, File, Form, UploadFile
from app.shared.models import RunRequest
from app.orchestrator.workflow import run_full_workflow
from app.shared.upload_utils import save_uploaded_codebase

router = APIRouter()


@router.get("/health")
def health_check():
    return {"ok": True, "message": "Backend is running", "orchestration_engine": "LangGraph"}


@router.post("/run")
def run_agents(payload: RunRequest):
    result = run_full_workflow(
        user_input=payload.user_input,
        project_path=payload.project_path or "",
    )

    return {
        "run_id": result.run_id,
        "orchestration_engine": "LangGraph",
        "issue_summary": result.issue_summary,
        "relevant_files": result.relevant_files,
        "code_findings": result.code_findings,
        "fix_plan": result.fix_plan,
        "qa_report": result.qa_report,
        "final_report": result.final_report,
        "trace": [entry.model_dump() for entry in result.trace],
    }


@router.post("/run-upload")
def run_agents_with_upload(
    user_input: str = Form(...),
    codebase_file: UploadFile = File(...),
):
    project_path, upload_kind = save_uploaded_codebase(codebase_file)

    result = run_full_workflow(
        user_input=user_input,
        project_path=project_path,
    )

    return {
        "run_id": result.run_id,
        "orchestration_engine": "LangGraph",
        "upload_kind": upload_kind,
        "project_path": project_path,
        "issue_summary": result.issue_summary,
        "relevant_files": result.relevant_files,
        "code_findings": result.code_findings,
        "fix_plan": result.fix_plan,
        "qa_report": result.qa_report,
        "final_report": result.final_report,
        "trace": [entry.model_dump() for entry in result.trace],
    }