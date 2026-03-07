from abc import ABC, abstractmethod


class IAgent(ABC):
    """
    Abstract interface for a model identity agent.
    Designed for future framework integration (AutoGen, CrewAI, etc.)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent display name (e.g., 'GPT', 'Claude')."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Underlying model name (e.g., 'gpt-5.1', 'claude-3-opus')."""

    @property
    @abstractmethod
    def vendor(self) -> str:
        """Model vendor (e.g., 'OpenAI', 'Anthropic', 'Google')."""

    @abstractmethod
    async def respond(self, message: str) -> str:
        """
        Generate a response to the given message.
        Framework-compatible interface for agent response.
        """

    @abstractmethod
    async def run_turn(self, history: list[dict]) -> "ModelResponse":
        """
        Execute one conversation turn using the provided history.
        """

    @abstractmethod
    def create_af_agent(self) -> object:
        """
        Build and return a Microsoft Agent Framework Agent for this model.
        """
