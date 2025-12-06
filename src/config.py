# src/config.py
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_model: str


def _get_env_var(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ConfigError(
            f"{name} is not set. "
            "Set it in your environment (e.g. in .env or shell) before running this command."
        )
    return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Lazily load settings on first use so importing this module never fails.
    """
    return Settings(
        openai_api_key=_get_env_var("OPENAI_API_KEY"),
        # OPENAI_MODEL is optional; default to a reasonable model if not set.
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
    )
