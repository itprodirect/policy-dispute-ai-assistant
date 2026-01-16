# src/llm_client.py
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from openai import OpenAI
from .config import get_settings, ConfigError

# Optional wandb import - gracefully handle if not installed
try:
    import wandb
    _WANDB_AVAILABLE = True
except ImportError:
    wandb = None
    _WANDB_AVAILABLE = False

# Module-level wandb run state
_wandb_run = None


@dataclass
class LLMCallError(RuntimeError):
    message: str
    last_response: Optional[str] = None


def _init_wandb() -> None:
    """Initialize wandb run if enabled and not already initialized."""
    global _wandb_run
    if _wandb_run is not None:
        return
    if not _WANDB_AVAILABLE:
        return
    settings = get_settings()
    if not settings.wandb_enabled:
        return
    _wandb_run = wandb.init(
        project=settings.wandb_project,
        entity=settings.wandb_entity,
        config={"model": settings.openai_model},
    )


def _log_to_wandb(metrics: Dict[str, Any]) -> None:
    """Log metrics to wandb if initialized."""
    if _wandb_run is not None:
        wandb.log(metrics)


def _get_model_name() -> str:
    """
    Resolve the model name, allowing an OPENAI_MODEL override.
    """
    return os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


def call_llm_json(
    *,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
    max_retries: int = 3,
    timeout: float = 30.0,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Call the LLM expecting a JSON object.

    - Uses OpenAI chat.completions API.
    - Retries on transient errors and JSON decode failures.
    - Raises LLMCallError with the last raw response text on final failure.
    - Logs metrics to wandb if enabled.
    """
    _init_wandb()

    last_raw: Optional[str] = None
    model_name = model or _get_model_name()

    for attempt in range(1, max_retries + 1):
        start_time = time.time()
        try:
            settings = get_settings()
            client = OpenAI(api_key=settings.openai_api_key, timeout=timeout)

            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=temperature,
            )

            latency_ms = (time.time() - start_time) * 1000
            raw = response.choices[0].message.content
            last_raw = raw
            parsed = json.loads(raw)

            # Log successful call
            _log_to_wandb({
                "llm/model": model_name,
                "llm/latency_ms": latency_ms,
                "llm/prompt_tokens": response.usage.prompt_tokens,
                "llm/completion_tokens": response.usage.completion_tokens,
                "llm/total_tokens": response.usage.total_tokens,
                "llm/temperature": temperature,
                "llm/attempt": attempt,
                "llm/success": True,
                "llm/error_type": None,
            })

            return parsed

        except json.JSONDecodeError:
            latency_ms = (time.time() - start_time) * 1000
            _log_to_wandb({
                "llm/model": model_name,
                "llm/latency_ms": latency_ms,
                "llm/temperature": temperature,
                "llm/attempt": attempt,
                "llm/success": False,
                "llm/error_type": "json_decode_error",
            })
            # Model returned non-JSON; retry unless we're out of attempts.
            if attempt == max_retries:
                raise LLMCallError(
                    message="Failed to decode JSON from LLM after retries.",
                    last_response=last_raw,
                )
            time.sleep(2**attempt)

        except ConfigError:
            # Config problems are not transient; re-raise immediately.
            raise

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            _log_to_wandb({
                "llm/model": model_name,
                "llm/latency_ms": latency_ms,
                "llm/temperature": temperature,
                "llm/attempt": attempt,
                "llm/success": False,
                "llm/error_type": type(e).__name__,
            })
            if attempt == max_retries:
                raise LLMCallError(
                    message=f"LLM call failed after retries: {e}",
                    last_response=last_raw,
                )
            time.sleep(2**attempt)

    # Should never reach here
    raise LLMCallError("Unexpected error in call_llm_json",
                       last_response=last_raw)
