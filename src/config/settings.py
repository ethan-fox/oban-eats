from pydantic_settings import BaseSettings
from functools import lru_cache
from enum import Enum

from src.config.app_mode import AppMode


class Environment(str, Enum):
    LOCAL = "LOCAL"
    PROD = "PROD"

class Settings(BaseSettings):
    environment: Environment = Environment.LOCAL
    database_url: str
    api_title: str = "Oban Eats API"
    mode: AppMode = AppMode.API

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
