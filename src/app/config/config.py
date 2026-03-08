from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application configuration managed by Pydantic.
    Loads from environment variables or a .env file.
    """
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    app_name: str = "Model Fusion Playground"
    environment: str = Field("dev", env=["APP_ENVIRONMENT", "app_environment"])

    # --- LLM Configurations ---
    azure_openai_endpoint: str = Field(default="", env="AZURE_OPENAI_ENDPOINT")
    azure_openai_deployment_gpt: str = Field(default="", env="AZURE_OPENAI_DEPLOYMENT_GPT")
    azure_openai_deployment_grok: str = Field(default="", env="AZURE_OPENAI_DEPLOYMENT_GROK")
    azure_openai_deployment_deepseek: str = Field(default="", env="AZURE_OPENAI_DEPLOYMENT_DEEPSEEK")
    azure_openai_api_key: str | None = Field(default=None, env="azure_openai_api_key")

    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    gemini_model: str = Field("gemini-3-pro-preview", env="GEMINI_MODEL")

    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field("claude-3-5-sonnet-20241022", env="ANTHROPIC_MODEL")

    # --- Timeouts ---
    agent_timeout: float = Field(120.0, env="AGENT_TIMEOUT")
    agent_connect_timeout: float = Field(30.0, env="AGENT_CONNECT_TIMEOUT")
    
    agent_timeout_gpt: float | None = Field(default=None, env="AGENT_TIMEOUT_GPT")
    agent_timeout_grok: float | None = Field(default=None, env="AGENT_TIMEOUT_GROK")
    agent_timeout_deepseek: float | None = Field(default=None, env="AGENT_TIMEOUT_DEEPSEEK")
    agent_timeout_gemini: float | None = Field(default=None, env="AGENT_TIMEOUT_GEMINI")
    agent_timeout_anthropic: float | None = Field(default=None, env="AGENT_TIMEOUT_ANTHROPIC")

    # --- Telemetry ---
    otel_service_name: str = "model-fusion-playground"
    otel_log_level: str = "INFO"
    APPLICATIONINSIGHTS_CONNECTION_STRING: str = ""

    def get_agent_timeout(self, agent_name: str) -> float:
        """Return per-model timeout if set, otherwise the shared agent_timeout."""
        per_model = getattr(self, f"agent_timeout_{agent_name}", None)
        return per_model if per_model is not None else self.agent_timeout


# Instantiate a global settings object to be imported across the app.
settings = Settings()
