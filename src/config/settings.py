from pydantic_settings import BaseSettings
from functools import lru_cache
from enum import Enum


class Environment(str, Enum):
    LOCAL = "LOCAL"
    PROD = "PROD"

class Settings(BaseSettings):
    environment: Environment = Environment.LOCAL
    database_url: str
    api_title: str = "Oban Eats API"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
