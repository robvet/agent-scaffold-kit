import json
import logging
import os
from pathlib import Path

from .i_agent import IAgent
from ..models.supervisor_models import ModelResponse


class ChildAgentA(IAgent):
    """
    A simple agent that returns a static response loaded from the data layer.
    """
    def __init__(self):
        self._name = "AgentAlpha"
        self._vendor = "Internal"
        self._model_name = "static-model-v1"
        self._response_file = Path(__file__).parent.parent / "data" / "agent_responses.json"

    @property
    def name(self) -> str:
        return self._name

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def vendor(self) -> str:
        return self._vendor

    def _load_static_response(self) -> str:
        try:
            with open(self._response_file, "r") as f:
                data = json.load(f)
                return data.get(self._name, "Response not found.")
        except Exception as e:
            logging.error(f"Failed to load static response for {self._name}: {e}")
            return "Error loading static data."

    async def respond(self, message: str) -> str:
        # Simulate processing time
        return self._load_static_response()

    async def run_turn(self, history: list[dict]) -> ModelResponse:
        response_text = self._load_static_response()
        return ModelResponse(
            text=response_text,
            status="complete"
        )

    def create_af_agent(self) -> object:
        # Stub for future framework integration if needed
        return object()
