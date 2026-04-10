from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql://geoscore:geoscore@localhost:5432/geoscore"
    cors_origins: str = "http://localhost:3000"
    environment: str = "development"
    use_mock_workflow: bool = False

    # Optional headless render fallback (pipeline-analysis.md). Requires: pip install playwright && playwright install chromium
    playwright_enabled: bool = True
    playwright_timeout_ms: int = 25_000
    playwright_settle_ms: int = 1_200

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
