"""
Model Fusion Playground - Entry point.
"""
import logging

from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from .observability.telemetry_service import setup_telemetry
from .state.in_memory_agent_state_store import InMemoryAgentStateStore

# Import the new Static Child Agents
from .agents.child_agent_a import ChildAgentA
from .agents.child_agent_b import ChildAgentB

from .agents.supervisor_agent import Supervisor
from .config.config import settings
from .utils.lifespan_manager import LifespanManager
from .api.routes import ApiRoutes

# Setup root logging
logging.basicConfig(level=logging.INFO)

# Run dependency injection for telemetry facade
setup_telemetry()

# Lifespan manager handles startup/shutdown
lifespan_manager = LifespanManager(port=8010, open_browser=True, flush_telemetry=True)

# FastAPI Application Instance
app = FastAPI(title="Architectural Accelerator Framework", lifespan=lifespan_manager.lifespan)
FastAPIInstrumentor.instrument_app(app)

# ==========================================================================
# DEPENDENCY INJECTION ROOT
# ==========================================================================

# 1. State Store
state_store = InMemoryAgentStateStore()

# 2. Child Agents
agent_alpha = ChildAgentA()
agent_beta = ChildAgentB()
agents = {
    agent_alpha.name: agent_alpha,
    agent_beta.name: agent_beta
}

# 3. Orchestrator
supervisor = Supervisor(
    agents=agents,
    state_store=state_store
)

# 4. Routing
api_routes = ApiRoutes(supervisor=supervisor)
app.include_router(api_routes.router)
