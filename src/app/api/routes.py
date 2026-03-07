"""
API routes for Model Fusion Playground.

This module defines the HTTP endpoints using FastAPI's APIRouter.
Similar to a Controller in ASP.NET or Spring.
"""
from fastapi import APIRouter, HTTPException

from ..agents.supervisor_agent import Supervisor
from ..models.supervisor_models import UserQueryRequest, SupervisorResponse


##########################################################################
# ApiRoutes - HTTP Endpoint Definitions
##########################################################################
# This class groups related API endpoints together using FastAPI's APIRouter.
#
# In C# terms:
#   - This is like an ASP.NET Controller
#   - APIRouter is like the route collection on a controller
#   - @self.router.get("/health") is like [HttpGet("health")] attribute
#
# Why a class?
#   - Allows constructor injection of dependencies (Supervisor)
#   - Keeps routes organized in one place
#   - Cleaner than putting all routes in main.py
#
# Usage in main.py:
#   api_routes = ApiRoutes(supervisor=supervisor)
#   app.include_router(api_routes.router)  # Registers all routes
##########################################################################
class ApiRoutes:
    """
    API routes with constructor injection.
    
    Groups all HTTP endpoints and receives dependencies via constructor.
    """

    def __init__(self, supervisor: Supervisor) -> None:
        """
        Initialize routes with injected dependencies.
        
        Args:
            supervisor: The Supervisor agent that handles queries
        """
        # Store the injected dependency
        self.supervisor = supervisor
        
        # Create a FastAPI router - this holds all our route definitions
        # Similar to creating a new controller in ASP.NET
        self.router = APIRouter()
        
        # Register all routes on the router
        self._register_routes()

    def _register_routes(self) -> None:
        """
        Define all HTTP endpoints.
        
        Uses decorator syntax to bind functions to HTTP methods/paths.
        The @self.router decorators are like [HttpGet] / [HttpPost] attributes.
        """
        
        # GET /health - Simple health check endpoint
        # Useful for load balancers and monitoring
        @self.router.get("/health")
        async def health() -> dict:
            return {"status": "ok", "service": "Model Fusion Playground"}

        # GET /health/af - Real AF connectivity check via Supervisor
        @self.router.get("/health/af")
        async def health_af() -> dict:
            """Return healthy only when a real AF-backed call succeeds."""
            try:
                probe_request = UserQueryRequest(
                    user_prompt="health probe",
                    enabled_agents=["gemini"],
                )
                result = await self.supervisor.post(probe_request)

                for agent_name in ["gemini"]:
                    model_result = result.responses.get(agent_name)
                    if model_result is None:
                        raise HTTPException(status_code=503, detail=f"AF health check failed: missing {agent_name} response")
                    if model_result.status != "complete":
                        raise HTTPException(
                            status_code=503,
                            detail=f"AF health check failed: {model_result.error_message or f'{agent_name} status not complete'}",
                        )
                    if not model_result.text.strip():
                        raise HTTPException(status_code=503, detail=f"AF health check failed: empty {agent_name} response")

                return {"status": "ok", "service": "Model Fusion Playground", "af": "ok"}
            except HTTPException:
                raise
            except Exception as ex:
                raise HTTPException(status_code=503, detail=f"AF health check failed: {str(ex) or 'Unknown error'}")

        # POST /post - Explicit post endpoint
        @self.router.post("/post", response_model=SupervisorResponse)
        async def post(req: UserQueryRequest):
            """Run post flow directly."""
            print(f"[DEBUG Route] Received post request: {req}")
            try:
                return await self.supervisor.post(req)
            except ValueError as ex:
                print(f"[DEBUG Route] Post validation failed: {ex}")
                raise HTTPException(status_code=400, detail=str(ex) or "Invalid request")
            except Exception as ex:
                print(f"[DEBUG Route] Post failed: {ex}")
                raise HTTPException(status_code=500, detail=str(ex) or "Unknown error")
