# src/config.py
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv

# Load .env file into environment
load_dotenv()


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or invalid."""


def _get_env_var(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ConfigError(
            f"{name} is not set. "
            "Set it in your environment (e.g. .env or shell) before running this command."
        )
    return value


def _get_bool_env(name: str, default: bool) -> bool:
    """
    Parse a boolean-like environment variable.

    Accepted truthy values (case-insensitive):
      - 1, true, yes, on
    Accepted falsy values:
      - 0, false, no, off

    Empty / unset -> default.

    We raise ConfigError on invalid values because these flags
    control privacy / data hygiene and should not silently misbehave.
    """
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default

    value = raw.strip().lower()
    if value in ("1", "true", "yes", "on"):
        return True
    if value in ("0", "false", "no", "off"):
        return False

    raise ConfigError(
        f"{name} must be one of: 1,0,true,false,yes,no,on,off (case-insensitive). Got: {raw!r}"
    )


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_model: str

    # Data-handling / privacy flags
    persist_raw_text: bool
    safe_mode: bool

    # Weights & Biases logging
    wandb_enabled: bool
    wandb_project: str
    wandb_entity: Optional[str]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Lazily load settings on first use so importing this module never fails.

    SAFE_MODE, if true, forces persist_raw_text=False regardless
    of PERSIST_RAW_TEXT.
    """
    safe_mode = _get_bool_env("SAFE_MODE", False)
    persist_raw_text_default = _get_bool_env("PERSIST_RAW_TEXT", True)

    # In safe mode we always drop raw_text, even if PERSIST_RAW_TEXT was set.
    persist_raw_text = False if safe_mode else persist_raw_text_default

    # Weights & Biases config (all optional)
    wandb_enabled = _get_bool_env("WANDB_ENABLED", False)
    wandb_project = os.getenv("WANDB_PROJECT", "policy-dispute-ai")
    wandb_entity = os.getenv("WANDB_ENTITY") or None

    return Settings(
        openai_api_key=_get_env_var("OPENAI_API_KEY"),
        # OPENAI_MODEL is optional; default to a reasonable model if not set.
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        persist_raw_text=persist_raw_text,
        safe_mode=safe_mode,
        wandb_enabled=wandb_enabled,
        wandb_project=wandb_project,
        wandb_entity=wandb_entity,
    )
