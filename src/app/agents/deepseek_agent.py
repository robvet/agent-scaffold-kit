"""DeepSeek Agent - DeepSeek model via Azure OpenAI Service."""

import asyncio
import logging
import traceback

import httpx
from agent_framework import Agent
from agent_framework.azure import AzureOpenAIChatClient
from openai import AsyncAzureOpenAI
from opentelemetry import trace
from opentelemetry.trace import StatusCode

from ..config.config import settings
from ..config.model_config import ModelConfig
from ..identity.azure_identity_provider import AzureIdentityProvider
from ..models.supervisor_models import ModelResponse
from ..utils import prompt_loader
from .i_agent import IAgent

# OpenTelemetry tracer for distributed tracing
tracer = trace.get_tracer(__name__)


class DeepSeekAgent(IAgent):
    """
    DeepSeek model identity agent (DeepSeek via Azure).
    
    Connects to Azure OpenAI Service using Azure Entra authentication.
    Timeout values are configurable via AGENT_TIMEOUT and AGENT_CONNECT_TIMEOUT env vars.
    """

    def __init__(self, deployment_name: str, config: ModelConfig) -> None:
        """Initialize the DeepSeek agent with Azure OpenAI client."""
        self._deployment = deployment_name
        self._config = config
        
        # Shared singleton — one credential chain, one token provider across all Azure agents.
        identity = AzureIdentityProvider.default()

        # HTTP transport — timeout config stays with the agent (SRP).
        timeout = httpx.Timeout(settings.get_agent_timeout("deepseek"), connect=settings.agent_connect_timeout)
        http_client = httpx.AsyncClient(timeout=timeout)

        # Azure OpenAI async client
        self._client = AsyncAzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            azure_ad_token_provider=identity.token_provider,
            api_version="2024-02-15-preview",
            http_client=http_client,
        )

    @property
    def name(self) -> str:
        return "DeepSeek"

    @property
    def model_name(self) -> str:
        return self._deployment

    @property
    def vendor(self) -> str:
        return "DeepSeek"

    async def respond(self, message: str) -> str:
        """Generate response from DeepSeek via Azure OpenAI."""
        print(f"[DEBUG {self.name}] respond called with message length: {len(message)}")
        
        with tracer.start_as_current_span(f"agent.{self.name.lower()}.respond") as span:
            span.set_attribute("agent.name", self.name)
            span.set_attribute("agent.model", self._deployment)
            span.set_attribute("agent.vendor", self.vendor)

            try:
                params = {
                    "model": self._deployment,
                    "messages": [{"role": "user", "content": message}],
                    "temperature": self._config.temperature,
                    "stream": self._config.stream,
                }
                
                if self._config.max_tokens is not None:
                    params["max_tokens"] = self._config.max_tokens
                
                params.update(self._config.extra_params)
                
                print(f"[DEBUG {self.name}] Calling API: model={self._deployment}")
                
                # Call Azure OpenAI with configurable timeout
                response = await asyncio.wait_for(
                    self._client.chat.completions.create(**params),
                    timeout=settings.get_agent_timeout("deepseek")
                )
                
                print(f"[DEBUG {self.name}] API call completed")
                
                if response.choices and len(response.choices) > 0:
                    content = response.choices[0].message.content
                    if content:
                        span.set_attribute("response.length", len(content))
                        return content.strip()
                
                return ""
                
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
        """Create Agent Framework runtime agent for DeepSeek."""
        client = AzureOpenAIChatClient(
            async_client=self._client,
            deployment_name=self._deployment,
        )
        return Agent(
            name="deepseek",
            instructions=prompt_loader.render("system-prompt.jinja2", model_name="deepseek"),
            client=client,
        )

    async def run_turn(self, history: list[dict]) -> ModelResponse:
        """Run one history-backed turn through AF and return a normalized response."""
        with tracer.start_as_current_span("agent.deepseek.run_turn") as span:
            span.set_attribute("agent.name", self.name)
            try:
                prompt = prompt_loader.render("conversation.jinja2", history=history)
                af_agent = self.create_af_agent()
                raw_response = await asyncio.wait_for(af_agent.run(prompt), timeout=settings.get_agent_timeout("deepseek"))
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
