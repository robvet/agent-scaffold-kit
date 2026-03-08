"""
ChildAgentB - Demonstrates the LLM Tool Pattern using Azure OpenAI GPT.

RESPONSIBILITY:
    This agent calls LlmTool to generate a response from GPT.
    It shows that an LLM call is just another tool — the agent stays thin.

SWAP PROVIDER:
    To use a different LLM (Gemini, Anthropic, etc.):
    1. Create a new tool (e.g., GeminiTool) following the same pattern as LlmTool.
    2. Replace self._tool = LlmTool() with self._tool = GeminiTool().
    3. Fill in the provider's key in .env.
    The agent itself does not change.

ARCHITECTURE FIT:
    Supervisor fan-out calls run_turn() on each child agent.
    Child agents call their tool, package the result, and return a ModelResponse.
"""
from .i_agent import IAgent
from ..models.supervisor_models import ModelResponse
from ..tools.llm_tool import LlmTool


class ChildAgentB(IAgent):
    """
    A child agent that generates responses via LlmTool (Azure OpenAI GPT by default).

    Demonstrates: LLM Tool Pattern — the LLM call is encapsulated inside a tool.
    """

    def __init__(self):
        """Initialize with an LlmTool instance (defaults to GPT)."""
        self._name = "AgentBeta"
        self._vendor = "Azure OpenAI"
        self._model_name = "gpt"
        # Swap this tool to change the underlying LLM provider.
        self._tool = LlmTool()

    @property
    def name(self) -> str:
        """Return the agent's name used as its key in the Supervisor registry."""
        return self._name

    @property
    def model_name(self) -> str:
        """Return the underlying model identifier."""
        return self._model_name

    @property
    def vendor(self) -> str:
        """Return the provider name."""
        return self._vendor

    async def respond(self, message: str) -> str:
        """Call the LLM tool with the message and return its response."""
        return await self._tool.run(message)

    async def run_turn(self, history: list[dict]) -> ModelResponse:
        """
        Execute one turn by calling the LLM tool with the latest user message.

        Args:
            history: Conversation history. The most recent user message is sent to the LLM.

        Returns:
            ModelResponse: Contains the LLM response text and status.
        """
        # Extract the most recent user message from conversation history.
        prompt = ""
        for msg in reversed(history):
            if msg.get("role") == "user":
                prompt = msg.get("content", "")
                break

        if not prompt:
            return ModelResponse(text="", status="error", error_message="No user message found.")

        result = await self._tool.run(prompt)
        return ModelResponse(text=result, status="complete")

    def create_af_agent(self) -> object:
        """Stub for Agent Framework integration — not required for tool-based agents."""
        return object()
