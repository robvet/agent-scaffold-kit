"""Smoke tests for Supervisor orchestration behavior."""

import importlib
import os
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest


class TestSupervisorSmoke:
    """HTTP-independent smoke checks for Supervisor core flow."""

    @staticmethod
    def _load_supervisor_module():
        """Load supervisor module from src using real installed dependencies."""
        src_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")
        src_path = os.path.abspath(src_path)
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        if "app.agents.supervisor_agent" in sys.modules:
            del sys.modules["app.agents.supervisor_agent"]

        return importlib.import_module("app.agents.supervisor_agent")

    @pytest.mark.asyncio
    async def test_query_routes_to_search(self):
        """query() should delegate to search() when mode is search."""
        module = self._load_supervisor_module()
        models_module = importlib.import_module("app.models.supervisor_models")

        Supervisor = module.Supervisor
        ModelResponse = models_module.ModelResponse
        SupervisorResponse = models_module.SupervisorResponse
        UserQueryRequest = models_module.UserQueryRequest

        supervisor = Supervisor(
            agents={"gpt": object()},
            state_store=SimpleNamespace(get_state=AsyncMock(), save_state=AsyncMock()),
            aggregation_tool=SimpleNamespace(aggregate=AsyncMock()),
        )

        expected = SupervisorResponse(
            conversation_id="cid-1",
            original_prompt="hello",
            responses={"gpt": ModelResponse(text="ok", status="complete")},
            aggregated_response="agg",
        )
        supervisor.search = AsyncMock(return_value=expected)

        req = UserQueryRequest(user_prompt="hello", mode="search")
        result = await supervisor.query(req)

        assert result == expected
        supervisor.search.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_search_happy_path(self):
        """search() should return responses and aggregated output."""
        module = self._load_supervisor_module()
        models_module = importlib.import_module("app.models.supervisor_models")

        Supervisor = module.Supervisor
        ModelResponse = models_module.ModelResponse
        UserQueryRequest = models_module.UserQueryRequest

        store = {}

        async def get_state(conversation_id, agent_id):
            return store.get((conversation_id, agent_id))

        async def save_state(state):
            store[(state.conversation_id, state.agent_id)] = state

        state_store = SimpleNamespace(
            get_state=AsyncMock(side_effect=get_state),
            save_state=AsyncMock(side_effect=save_state),
        )
        aggregation_tool = SimpleNamespace(aggregate=AsyncMock(return_value="combined"))

        supervisor = Supervisor(
            agents={"gpt": object(), "gemini": object()},
            state_store=state_store,
            aggregation_tool=aggregation_tool,
        )

        supervisor._run_agent_framework_search = AsyncMock(
            return_value={
                "gpt": ModelResponse(text="gpt answer", status="complete"),
                "gemini": ModelResponse(text="gemini answer", status="complete"),
            }
        )

        req = UserQueryRequest(
            user_prompt="What is RAG?",
            mode="search",
            enabled_agents=["gpt", "gemini"],
        )
        result = await supervisor.search(req)

        assert result.conversation_id
        assert result.aggregated_response == "combined"
        assert set(result.responses.keys()) == {"gpt", "gemini"}
        assert state_store.save_state.await_count == 5

    @pytest.mark.asyncio
    async def test_debate_hook_routes_to_search(self):
        """debate() should currently route through search with a marker prefix."""
        module = self._load_supervisor_module()
        models_module = importlib.import_module("app.models.supervisor_models")

        Supervisor = module.Supervisor
        ModelResponse = models_module.ModelResponse
        SupervisorResponse = models_module.SupervisorResponse
        UserQueryRequest = models_module.UserQueryRequest

        supervisor = Supervisor(
            agents={"gpt": object()},
            state_store=SimpleNamespace(get_state=AsyncMock(), save_state=AsyncMock()),
            aggregation_tool=SimpleNamespace(aggregate=AsyncMock()),
        )

        supervisor.search = AsyncMock(
            return_value=SupervisorResponse(
                conversation_id="cid-2",
                original_prompt="prompt",
                responses={"gpt": ModelResponse(text="ok", status="complete")},
                aggregated_response="base aggregate",
            )
        )

        req = UserQueryRequest(user_prompt="prompt", mode="debate", debate_rounds=2)
        result = await supervisor.debate(req)

        assert result.aggregated_response.startswith(
            "Debate mode is temporarily routed through search mode"
        )
        supervisor.search.assert_awaited_once()

    def test_resolve_agents_filter_and_fallback(self):
        """_resolve_agents should filter known agents and fallback for invalid input."""
        module = self._load_supervisor_module()
        Supervisor = module.Supervisor

        supervisor = Supervisor(
            agents={"gpt": object(), "gemini": object(), "anthropic": object()},
            state_store=SimpleNamespace(get_state=AsyncMock(), save_state=AsyncMock()),
            aggregation_tool=SimpleNamespace(aggregate=AsyncMock()),
        )

        filtered = supervisor._resolve_agents(["gpt"])
        fallback = supervisor._resolve_agents(["missing"])
        swagger_default = supervisor._resolve_agents(["string"])

        assert set(filtered.keys()) == {"gpt"}
        assert set(fallback.keys()) == {"gpt", "gemini", "anthropic"}
        assert set(swagger_default.keys()) == {"gpt", "gemini", "anthropic"}

    @pytest.mark.asyncio
    async def test_conversation_id_continuity_updates_history(self):
        """Repeated calls with same conversation_id should grow stored history."""
        module = self._load_supervisor_module()
        models_module = importlib.import_module("app.models.supervisor_models")

        Supervisor = module.Supervisor
        ModelResponse = models_module.ModelResponse
        UserQueryRequest = models_module.UserQueryRequest

        store = {}

        async def get_state(conversation_id, agent_id):
            return store.get((conversation_id, agent_id))

        async def save_state(state):
            store[(state.conversation_id, state.agent_id)] = state

        state_store = SimpleNamespace(
            get_state=AsyncMock(side_effect=get_state),
            save_state=AsyncMock(side_effect=save_state),
        )
        aggregation_tool = SimpleNamespace(aggregate=AsyncMock(return_value="combined"))

        supervisor = Supervisor(
            agents={"gpt": object()},
            state_store=state_store,
            aggregation_tool=aggregation_tool,
        )

        async def fake_run_agent_framework_search(_agents_to_use, states):
            states["gpt"].conversation_history.append(
                {"role": "assistant", "content": "assistant reply"}
            )
            return {"gpt": ModelResponse(text="assistant reply", status="complete")}

        supervisor._run_agent_framework_search = AsyncMock(
            side_effect=fake_run_agent_framework_search
        )

        first = await supervisor.search(UserQueryRequest(user_prompt="turn 1", mode="search"))
        second = await supervisor.search(
            UserQueryRequest(
                user_prompt="turn 2",
                mode="search",
                conversation_id=first.conversation_id,
            )
        )

        gpt_state = store[(second.conversation_id, "gpt")]
        assert len(gpt_state.conversation_history) >= 4
