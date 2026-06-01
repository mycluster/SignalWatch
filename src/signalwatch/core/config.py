from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SignalWatch"
    app_env: str = "local"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql://signalwatch:signalwatch@localhost:5432/signalwatch"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
