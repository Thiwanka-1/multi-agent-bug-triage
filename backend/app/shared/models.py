from pydantic import BaseModel, Field
from typing import Optional


class RunRequest(BaseModel):
    user_input: str = Field(..., min_length=5)
    project_path: Optional[str] = ""