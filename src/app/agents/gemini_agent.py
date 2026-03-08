"""Gemini Agent - Google Gemini model via Google GenAI API."""

import asyncio
import logging
import traceback

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from google import genai
from openai import AsyncOpenAI
from opentelemetry import trace
from opentelemetry.trace import StatusCode

from ..config.config import settings
from ..models.supervisor_models import ModelResponse
from ..utils import prompt_loader
from .i_agent import IAgent

# OpenTelemetry tracer for distributed tracing
tracer = trace.get_tracer(__name__)


class GeminiAgent(IAgent):
    """
    Gemini model identity agent (Google).
    
    Connects to Google GenAI API using API key authentication.
    Timeout values are configurable via AGENT_TIMEOUT env var.
    """

    def __init__(self, model_name: str) -> None:
        """Initialize the Gemini agent with Google GenAI client."""
        self._model = model_name
        self._client = genai.Client(api_key=settings.gemini_api_key)

    @property
    def name(self) -> str:
        return "Gemini"

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def vendor(self) -> str:
        return "Google"

    async def respond(self, message: str) -> str:
        """Generate response from Gemini via Google GenAI API."""
        print(f"[DEBUG {self.name}] respond called with message length: {len(message)}")
        
        with tracer.start_as_current_span(f"agent.{self.name.lower()}.respond") as span:
            span.set_attribute("agent.name", self.name)
            span.set_attribute("agent.model", self._model)
            span.set_attribute("agent.vendor", self.vendor)

            try:
                print(f"[DEBUG {self.name}] Calling API: model={self._model}")
                
                # Synchronous Google GenAI call wrapped in thread pool
                def call_gemini():
                    """Execute synchronous Gemini API call."""
                    response = self._client.models.generate_content(
                        model=self._model,
                        contents=message,
                    )
                    return response.text if response.text else ""
                
                # Run with configurable timeout from .env
                text = await asyncio.wait_for(
                    asyncio.to_thread(call_gemini),
                    timeout=settings.get_agent_timeout("gemini")
                )
                print(f"[DEBUG {self.name}] API call completed, response length: {len(text)}")
                
                span.set_attribute("response.length", len(text))
                return text.strip()
                
            except Exception as ex:
                logging.exception(f"{self.name} agent call failed")
                tb = traceback.format_exc()
                span.record_exception(ex)
                span.set_attribute("error.type", type(ex).__name__)
                span.set_attribute("error.message", str(ex))
                span.set_attribute("error.traceback", tb)
                span.set_status(StatusCode.ERROR, str(ex))
                raise

    def create_af_agent(self) -> object:
        """Create Agent Framework runtime agent for Gemini."""
        gemini_base = AsyncOpenAI(
            api_key=settings.gemini_api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            max_retries=0,
        )
        client = OpenAIChatClient(
            async_client=gemini_base,
            model_id=self._model,
        )
        return Agent(
            name="gemini",
            instructions=prompt_loader.render("system-prompt.jinja2", model_name="gemini"),
            client=client,
        )

    async def run_turn(self, history: list[dict]) -> ModelResponse:
        """Run one history-backed turn through AF and return a normalized response."""
        with tracer.start_as_current_span("agent.gemini.run_turn") as span:
            span.set_attribute("agent.name", self.name)
            try:
                prompt = prompt_loader.render("conversation.jinja2", history=history)
                af_agent = self.create_af_agent()
                raw_response = await asyncio.wait_for(af_agent.run(prompt), timeout=settings.get_agent_timeout("gemini"))
                text = self._extract_af_text(raw_response)
                span.set_attribute("status", "complete")
                span.set_attribute("response.length", len(text))
                return ModelResponse(text=text, status="complete")
            except asyncio.TimeoutError:
                logging.warning(f"[{self.name}] run_turn timed out")
                span.set_attribute("status", "error")
                return ModelResponse(text="", status="error", error_message="Timeout")
            except Exception as ex:
                logging.exception(f"[{self.name}] run_turn failed")
                span.record_exception(ex)
                span.set_attribute("status", "error")
                return ModelResponse(text="", status="error", error_message=str(ex))

    def _extract_af_text(self, raw_response: object) -> str:
        """Extract text from AF responses across provider-specific response shapes."""
        if isinstance(raw_response, str):
            return raw_response.strip()

        value = getattr(raw_response, "text", None)
        if isinstance(value, str) and value:
            return value.strip()

        value = getattr(raw_response, "content", None)
        if isinstance(value, str) and value:
            return value.strip()

        contents = getattr(raw_response, "contents", None)
        if isinstance(contents, list):
            parts = []
            for part in contents:
                part_text = getattr(part, "text", getattr(part, "content", None))
                if isinstance(part_text, str) and part_text:
                    parts.append(part_text)
            if parts:
                return "\n".join(parts).strip()

        return str(raw_response).strip()
