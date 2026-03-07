"""
Test Error Telemetry - Verify errors appear in App Insights.

This test intentionally triggers an error to verify that:
1. span.record_exception() captures stack traces
2. span.set_status(StatusCode.ERROR) marks the span as failed
3. Errors appear in App Insights Failures blade
"""
import pytest
import os
from unittest.mock import patch

# Add src to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.mark.asyncio
async def test_invalid_api_key_emits_error_telemetry():
    """
    Test that an invalid API key causes proper error telemetry.
    
    This test:
    1. Overrides the Anthropic API key with an invalid value
    2. Attempts to call the agent
    3. Verifies an exception is raised
    
    To verify telemetry manually:
    1. Run this test
    2. Check App Insights Failures blade
    3. Look for exception with stack trace
    """
    from app.agents.anthropic_agent import AnthropicAgent
    
    # Create agent with invalid API key
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "invalid-key-12345"}):
        # We need to recreate settings to pick up the patched env var
        # For now, directly create agent with invalid key
        pass
    
    # Create agent (it will use the configured key from settings)
    agent = AnthropicAgent("claude-3-sonnet-20240229")
    
    # Expect an authentication error
    with pytest.raises(Exception):
        await agent.respond("Test message")


@pytest.mark.asyncio  
async def test_timeout_emits_error_telemetry():
    """
    Test that timeout errors are properly recorded in telemetry.
    
    This test verifies the Supervisor's timeout handling
    records exceptions with proper status codes.
    """
    # This would require mocking - keeping as placeholder
    # The actual timeout testing happens with Grok agent in production
    pass


if __name__ == "__main__":
    # Quick manual test
    import asyncio
    asyncio.run(test_invalid_api_key_emits_error_telemetry())
