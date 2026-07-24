from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables or `.env`."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    kafka_bootstrap_servers: str = "localhost:19092"
    schema_registry_url: str = "http://localhost:8081"
    trade_topic: str = "trades.v1"
    trade_consumer_group: str = "trade-audit-v1"


@lru_cache
def get_settings() -> Settings:
    return Settings()
