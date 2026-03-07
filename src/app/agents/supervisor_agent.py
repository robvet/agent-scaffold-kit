"""Supervisor: explicit post/debate entry points with shared internals."""
import asyncio
import logging
import traceback
import uuid
from typing import Dict

from opentelemetry import trace
from opentelemetry.trace import StatusCode

from .i_agent import IAgent
from ..models.models import AgentState
from ..models.supervisor_models import ModelResponse, SupervisorResponse, UserQueryRequest
from ..state.i_agent_state_store import IAgentStateStore

# =============================================================================
# TRACER: Entry point for creating spans
# =============================================================================
tracer = trace.get_tracer(__name__)

# Registration of explicit child agent keys
AGENT_NAMES = ["AgentAlpha", "AgentBeta"]


class Supervisor:
    """
    Orchestrates agent fan-out and aggregates static responses.
    """

    def __init__(
        self,
        agents: Dict[str, IAgent],
        state_store: IAgentStateStore,
    ) -> None:
        """
        Initialize Supervisor dependencies.

        Args:
            agents: Logical model agents keyed by model name.
            state_store: Persistence for per-conversation, per-model state.
        """
        self._agents = agents
        self._state_store = state_store

    async def post(self, req: UserQueryRequest) -> SupervisorResponse:
        """
        Execute post flow end-to-end.
        """
        conversation_id = req.conversation_id or str(uuid.uuid4())

        with tracer.start_as_current_span("Supervisor.post") as span:
            span.set_attribute("conversation_id", conversation_id)
            span.set_attribute("prompt_length", len(req.user_prompt))

            states = await self._load_states(conversation_id, req.user_prompt)
            agents_to_use = self._resolve_agents(req.enabled_agents)

            responses = await self._execute_agents(agents_to_use, states)
            await self._save_states(states)
            
            # Simple string concatenation instead of an LLM aggregation
            aggregated = "\\n\\n".join([f"**{name}**: {resp.text}" for name, resp in responses.items() if resp.status == "complete"])

            return SupervisorResponse(
                conversation_id=conversation_id,
                original_prompt=req.user_prompt,
                responses=responses,
                aggregated_response=aggregated,
            )


    async def debate(self, req: UserQueryRequest) -> SupervisorResponse:
        """
        Execute debate flow.
        """
        with tracer.start_as_current_span("Supervisor.debate") as span:
             return SupervisorResponse(
                conversation_id=req.conversation_id or str(uuid.uuid4()),
                original_prompt=req.user_prompt,
                responses={},
                aggregated_response="Debate mode is not strictly implemented in this template.",
            )

    async def _execute_agents(
        self,
        agents_to_use: Dict[str, IAgent],
        states: Dict[str, AgentState],
    ) -> Dict[str, ModelResponse]:
        """
        Execute fan-out to child agents.
        """
        with tracer.start_as_current_span("Supervisor.post.fan_out"):
            results = await asyncio.gather(
                *[
                    agents_to_use[name].run_turn(states[name].conversation_history)
                    for name in agents_to_use
                ],
                return_exceptions=True,
            )

            responses: Dict[str, ModelResponse] = {}

            for i, name in enumerate(agents_to_use.keys()):
                result = results[i]
                if isinstance(result, Exception):
                    logging.exception(f"Agent {name} failed", exc_info=result)
                    responses[name] = ModelResponse(
                        text="",
                        status="error",
                        error_message=str(result) or "Unknown error",
                    )
                    continue

                responses[name] = result
                if result.status == "complete" and result.text:
                    states[name].conversation_history.append({"role": "assistant", "content": result.text})

            return responses

    async def _load_states(self, conversation_id: str, user_prompt: str) -> Dict[str, AgentState]:
        states: Dict[str, AgentState] = {}
        for name in AGENT_NAMES:
            state = await self._state_store.get_state(conversation_id, name)
            if state is None:
                state = AgentState(conversation_id=conversation_id, agent_id=name)
            state.conversation_history.append({"role": "user", "content": user_prompt})
            states[name] = state
        return states

    def _resolve_agents(self, enabled_agents: list[str] | None) -> Dict[str, IAgent]:
        if not enabled_agents or enabled_agents == ["string"]:
            return self._agents

        unknown = [name for name in enabled_agents if name not in self._agents]
        if unknown:
            raise ValueError(f"Unknown enabled_agents: {', '.join(sorted(set(unknown)))}")

        return {name: self._agents[name] for name in enabled_agents}

    async def _save_states(self, states: Dict[str, AgentState]) -> None:
        for name in AGENT_NAMES:
            if name in states:
                await self._state_store.save_state(states[name])
