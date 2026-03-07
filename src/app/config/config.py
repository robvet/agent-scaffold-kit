from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application configuration managed by Pydantic.
    Loads from environment variables or a .env file.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # General OpenTelemetry configuration
    otel_service_name: str = "model-fusion-playground"
    otel_log_level: str = "INFO"

    # Azure Monitor integration (optional, if empty string telemetry is printed to console)
    APPLICATIONINSIGHTS_CONNECTION_STRING: str = ""


# Instantiate a global settings object to be imported across the app.
settings = Settings()
