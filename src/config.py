from functools import cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = ""


@cache
def get_settings() -> Settings:
    return Settings()
