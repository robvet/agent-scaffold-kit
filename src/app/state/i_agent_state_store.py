from abc import ABC, abstractmethod
from typing import Optional

from ..models.models import AgentState

##################################################
# IAgentStateStore
##################################################
# Represents the interface for agent state storage,
# is an abstract base class (ABC) in python that 
# cannot be instantiated directly.
#
# Instead, you instantiate a concrete implementation
# of this interface, such as InMemoryAgentStateStore,
# which provides the actual storage functionality.
#
# The concrete class then inherits the abstract methods
# defined in this interface to implement the storage logic.
#
# This the implementation for dependency injection in python.
# (Manual dependency injection)
##################################################


class IAgentStateStore(ABC):
    """
    Pluggable interface for agent state storage.
    """

    @abstractmethod
    async def get_state(self, conversation_id: str, agent_id: str) -> Optional[AgentState]:
        """Retrieve state for a specific conversation and agent."""

    @abstractmethod
    async def save_state(self, state: AgentState) -> None:
        """Persist state for a specific conversation and agent."""
