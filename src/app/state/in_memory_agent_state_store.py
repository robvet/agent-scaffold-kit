from typing import Optional

from ..models.models import AgentState
from .i_agent_state_store import IAgentStateStore

####################################################
# Architectural Observation - In-Memory State Store
####################################################
# This class inherits the IAgentStateStore interface
# and implements the abstract methods defined in the
# interface.
#
# This is how we implement the dependency injection
# pattern in python.
####################################################
class InMemoryAgentStateStore(IAgentStateStore):
    """
    Simple in-memory implementation for local development.
    """

    def __init__(self) -> None:
        self._store: dict[tuple[str, str], AgentState] = {}

    async def get_state(self, conversation_id: str, agent_id: str) -> Optional[AgentState]:
        return self._store.get((conversation_id, agent_id))

    async def save_state(self, state: AgentState) -> None:
        self._store[(state.conversation_id, state.agent_id)] = state
