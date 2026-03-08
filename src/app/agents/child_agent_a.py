"""
ChildAgentA - Demonstrates the Tool Pattern using a simple datetime tool.

RESPONSIBILITY:
    This agent calls DatetimeTool to retrieve the current date/time.
    It shows how agents stay thin — they only call tools, not external services directly.

ARCHITECTURE FIT:
    Supervisor fan-out calls run_turn() on each child agent.
    Child agents call their tool, package the result, and return a ModelResponse.
    To replace this agent's capability, swap in a different tool.
"""
from .i_agent import IAgent
from ..models.supervisor_models import ModelResponse
from ..tools.datetime_tool import DatetimeTool


class ChildAgentA(IAgent):
    """
    A child agent that retrieves the current date and time via DatetimeTool.

    Demonstrates: Tool Pattern — agent delegates to a tool for its capability.
    """

    def __init__(self):
        """Initialize with a DatetimeTool instance."""
        self._name = "AgentAlpha"
        self._vendor = "Internal"
        self._model_name = "datetime-tool-v1"
        # The tool encapsulates the capability — the agent just calls it.
        self._tool = DatetimeTool()

    @property
    def name(self) -> str:
        """Return the agent's name used as its key in the Supervisor registry."""
        return self._name

    @property
    def model_name(self) -> str:
        """Return the underlying tool identifier."""
        return self._model_name

    @property
    def vendor(self) -> str:
        """Return the provider name."""
        return self._vendor

    async def respond(self, message: str) -> str:
        """Call the datetime tool and return its result."""
        return self._tool.run()

    async def run_turn(self, history: list[dict]) -> ModelResponse:
        """
        Execute one turn by calling the datetime tool.

        Args:
            history: Conversation history (not used by this tool-based agent).

        Returns:
            ModelResponse: Contains the current datetime string and status.
        """
        result = self._tool.run()
        return ModelResponse(text=result, status="complete")

    def create_af_agent(self) -> object:
        """Stub for Agent Framework integration — not required for tool-based agents."""
        return object()
