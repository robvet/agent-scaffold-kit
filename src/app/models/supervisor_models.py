from typing import Dict, Optional

from pydantic import BaseModel


class UserQueryRequest(BaseModel):
    """
    External contract for the initial user query into the Supervisor.
    """
    user_prompt: str
    conversation_id: Optional[str] = None
    enabled_agents: Optional[list[str]] = None  # None = all agents


class ModelResponse(BaseModel):
    """
    Response from a single model.
    """
    text: str
    status: str  # "complete" or "error"
    error_message: Optional[str] = None


class SupervisorResponse(BaseModel):
    """
    Aggregated response from the Supervisor.
    """
    conversation_id: str
    original_prompt: str
    responses: Dict[str, ModelResponse]
    aggregated_response: str = ""
