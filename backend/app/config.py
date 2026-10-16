from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration, read from environment variables (and a local .env for dev)."""

    app_name: str = "FleetPulse API"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://fleetpulse:fleetpulse@localhost:5432/fleetpulse"
    cors_origins: str = "*"
    service_due_soon_km: int = 500

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
