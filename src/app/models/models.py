from pydantic import BaseModel, Field


class AgentState(BaseModel):
    """
    Per-agent, per-conversation state for multi-turn memory.
    """
    conversation_id: str
    agent_id: str
    conversation_history: list[dict] = Field(default_factory=list)
