import os
from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "InferenceOps Gateway"
    app_env: str = "local"
    debug: bool = True

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "inferenceops"
    postgres_user: str = "inferenceops"
    postgres_password: str = "inferenceops"

    redis_host: str = "localhost"
    redis_port: int = 6379

    default_user_key: str = "andrew"
    default_daily_budget_usd: float = 0.10
    default_requests_per_minute: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @cached_property
    def database_url(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @cached_property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"


settings = Settings(_env_file=os.getenv("ENV_FILE", ".env"))
