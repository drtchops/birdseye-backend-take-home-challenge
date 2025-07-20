from functools import cache
from typing import ClassVar

from pydantic_settings import BaseSettings
from pydantic_settings.main import SettingsConfigDict


class Settings(BaseSettings):
    """The class that holds configuration fields loaded from the environment"""

    database_url: str = ""
    """The connection URL to be used for the database engine"""

    service_root: str = ""
    """The root URL for the active service"""

    sentry_dsn: str = ""
    """The DSN for Sentry integration"""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(env_file=".env")


@cache
def get_settings() -> Settings:
    """Returns a cached instance of the Settings object"""
    return Settings()
