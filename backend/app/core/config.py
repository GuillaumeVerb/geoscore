from __future__ import annotations

from urllib.parse import urlparse

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Dev-only default; must not be used when ENVIRONMENT is production (validated below).
_DEV_JWT_PLACEHOLDER = "geoscore-dev-jwt-secret-change-in-production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql://geoscore:geoscore@localhost:5432/geoscore"
    cors_origins: str = "http://localhost:3000"
    environment: str = "development"
    use_mock_workflow: bool = False

    # Minimal JWT session (MVP — set JWT_SECRET_KEY in production)
    jwt_secret_key: str = _DEV_JWT_PLACEHOLDER
    jwt_algorithm: str = "HS256"
    jwt_expire_days: int = 30

    # When false, skip ``alembic upgrade head`` in API lifespan (use a release / pre-deploy step instead).
    run_alembic_on_startup: bool = True

    # Optional headless render fallback (pipeline-analysis.md). Requires: pip install playwright && playwright install chromium
    playwright_enabled: bool = True
    playwright_timeout_ms: int = 25_000
    playwright_settle_ms: int = 1_200

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @staticmethod
    def _database_hostname(url: str) -> str | None:
        normalized = url.replace("postgresql+psycopg2://", "postgresql://", 1)
        try:
            return urlparse(normalized).hostname
        except ValueError:
            return None

    @model_validator(mode="after")
    def reject_placeholder_jwt_in_production(self) -> "Settings":
        if self.environment.lower() in ("production", "prod") and self.jwt_secret_key == _DEV_JWT_PLACEHOLDER:
            raise ValueError(
                "JWT_SECRET_KEY must be set to a strong random value when ENVIRONMENT is production "
                f"(do not use the dev placeholder)."
            )
        return self

    @model_validator(mode="after")
    def reject_localhost_database_in_production(self) -> "Settings":
        if self.environment.lower() not in ("production", "prod") or self.use_mock_workflow:
            return self
        host = self._database_hostname(self.database_url)
        if host in ("localhost", "127.0.0.1", "::1"):
            raise ValueError(
                "DATABASE_URL must point to your real Postgres host in production (not localhost). "
                "On Railway: add variable DATABASE_URL from the Postgres service (Variables → Reference → "
                "Postgres.DATABASE_URL or equivalent). Pre-deploy may not receive linked variables; "
                "migrations run at container start."
            )
        return self


settings = Settings()
