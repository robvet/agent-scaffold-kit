"""
LlmTool - A tool that calls Azure OpenAI GPT to generate a response.

RESPONSIBILITY:
    Demonstrates wrapping an LLM call inside a Tool, so agents stay thin
    and all provider-specific logic is encapsulated here.

SWAP PROVIDERS:
    To switch from GPT to Gemini, Anthropic, or another provider, replace
    this tool with the corresponding implementation. The child agent that
    calls this tool does not change.

ARCHITECTURE FIT:
    Tools encapsulate a unit of capability. An LLM call is just another capability.
    By wrapping it here, we keep agents free of provider-specific import dependencies.
"""
import asyncio
import logging

import httpx
from openai import AsyncAzureOpenAI, APIConnectionError

from ..config.config import settings
from ..identity.azure_identity_provider import AzureIdentityProvider


class LlmTool:
    """
    Calls Azure OpenAI GPT and returns the response text.

    This is the DEFAULT provider. To swap to a different LLM, replace the
    body of run() with a different client call (e.g. Anthropic, Gemini).

    USAGE:
        tool = LlmTool()
        result = await tool.run("What is the capital of France?")
    """

    def __init__(self) -> None:
        """Initialize the tool."""
        self._client = None

    def _get_client(self) -> AsyncAzureOpenAI:
        """Create and return the AsyncAzureOpenAI client on the active event loop."""
        if self._client is None:
            # Timeout from settings so it is configurable via .env.
            timeout = httpx.Timeout(
                settings.get_agent_timeout("gpt"),
                connect=settings.agent_connect_timeout
            )

            if settings.azure_openai_api_key:
                # API key present — use it directly (local dev).
                self._client = AsyncAzureOpenAI(
                    azure_endpoint=settings.azure_openai_endpoint,
                    api_key=settings.azure_openai_api_key,
                    api_version="2024-02-15-preview",
                    http_client=httpx.AsyncClient(timeout=timeout),
                )
            else:
                # No API key — fall back to Azure AD (Managed Identity / az login).
                identity = AzureIdentityProvider.default()
                self._client = AsyncAzureOpenAI(
                    azure_endpoint=settings.azure_openai_endpoint,
                    azure_ad_token_provider=identity.token_provider,
                    api_version="2024-02-15-preview",
                    http_client=httpx.AsyncClient(timeout=timeout),
                )
        return self._client

    async def run(self, prompt: str) -> str:
        """
        Send a prompt to GPT and return the response text.

        Args:
            prompt: The user message to send to the LLM.

        Returns:
            str: The model's response text, or an error message on failure.
        """
        try:
            client = self._get_client()
            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model=settings.azure_openai_deployment_gpt,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                ),
                timeout=settings.get_agent_timeout("gpt")
            )
            if response.choices:
                return response.choices[0].message.content.strip()
            return ""
        except APIConnectionError:
            logging.exception("LlmTool: Connection or Auth endpoint timeout")
            return "Error: Unable to connect or authenticate. Did you run 'az login'?"
        except Exception as ex:
            logging.exception("LlmTool: GPT call failed")
            return f"Error: {str(ex)}"
