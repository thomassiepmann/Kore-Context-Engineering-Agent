from pydantic import BaseModel
from typing import Optional, List

class ProjectContext(BaseModel):
    project_name: str
    system_context: str = ""
    task_context: str = ""
    knowledge_context: str = ""
    interaction_context: str = ""
    situation_context: str = ""
    updated_at: Optional[str] = None

class PromptRequest(BaseModel):
    project_name: str
    user_input: str
    user_role: Optional[str] = "thomas"

class PromptResponse(BaseModel):
    optimized_prompt: str
    project_name: str
    context_used: List[str]

class FeedbackRequest(BaseModel):
    prompt_id: str
    quality: int
    notes: Optional[str] = ""

class ContextUpdate(BaseModel):
    field: str
    value: str
