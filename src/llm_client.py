# src/llm_client.py
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from openai import OpenAI
from .config import get_settings, ConfigError
from .wandb_telemetry import get_run_tracker

# Optional wandb import - gracefully handle if not installed
try:
    import wandb
    _WANDB_AVAILABLE = True
except ImportError:
    wandb = None
    _WANDB_AVAILABLE = False


@dataclass
class LLMCallError(RuntimeError):
    message: str
    last_response: Optional[str] = None


def _log_to_wandb(metrics: Dict[str, Any]) -> None:
    """
    Log metrics to wandb if a run is active.

    IMPORTANT: Only logs if wandb.run is not None.
    All wandb.init() calls must go through wandb_telemetry.start_wandb_run().
    """
    if not _WANDB_AVAILABLE:
        return
    if wandb.run is not None:
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
    stage: Optional[str] = None,
    response_schema: Optional[Dict[str, Any]] = None,
    schema_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Call the LLM expecting a JSON object.

    - Uses OpenAI Responses API.
    - Retries on transient errors and JSON decode failures.
    - Raises LLMCallError with the last raw response text on final failure.
    - Logs metrics to wandb if a run is active (via wandb_telemetry.start_wandb_run).
    """
    last_raw: Optional[str] = None
    model_name = model or _get_model_name()
    if response_schema is None:
        text_arg = {"format": {"type": "json_object"}}
    else:
        text_arg = {
            "format": {
                "type": "json_schema",
                "name": schema_name or stage or "structured_output",
                "schema": response_schema,
                "strict": True,
            }
        }

    for attempt in range(1, max_retries + 1):
        start_time = time.time()
        try:
            settings = get_settings()
            client = OpenAI(api_key=settings.openai_api_key, timeout=timeout)

            response = client.responses.create(
                model=model_name,
                instructions=system_prompt,
                input=user_prompt,
                text=text_arg,
                temperature=temperature,
                store=False,
            )

            latency_ms = (time.time() - start_time) * 1000
            raw = response.output_text
            last_raw = raw
            parsed = json.loads(raw)

            # Log successful call
            total_tokens = response.usage.total_tokens
            prompt_tokens = response.usage.input_tokens
            completion_tokens = response.usage.output_tokens
            _log_to_wandb({
                "llm/model": model_name,
                "llm/stage": stage or "unknown",
                "llm/latency_ms": latency_ms,
                "llm/prompt_tokens": prompt_tokens,
                "llm/completion_tokens": completion_tokens,
                "llm/total_tokens": total_tokens,
                "llm/temperature": temperature,
                "llm/attempt": attempt,
                "llm/success": True,
                "llm/error_type": None,
            })

            # Record to run tracker if active
            tracker = get_run_tracker()
            if tracker is not None:
                tracker.record_call(
                    stage,
                    latency_ms,
                    total_tokens,
                    success=True,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                )

            return parsed

        except json.JSONDecodeError:
            latency_ms = (time.time() - start_time) * 1000
            _log_to_wandb({
                "llm/model": model_name,
                "llm/stage": stage or "unknown",
                "llm/latency_ms": latency_ms,
                "llm/prompt_tokens": 0,
                "llm/completion_tokens": 0,
                "llm/total_tokens": 0,
                "llm/temperature": temperature,
                "llm/attempt": attempt,
                "llm/success": False,
                "llm/error_type": "json_decode_error",
            })
            # Record error to run tracker
            tracker = get_run_tracker()
            if tracker is not None:
                tracker.record_call(stage, latency_ms, 0, success=False)
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
                "llm/stage": stage or "unknown",
                "llm/latency_ms": latency_ms,
                "llm/prompt_tokens": 0,
                "llm/completion_tokens": 0,
                "llm/total_tokens": 0,
                "llm/temperature": temperature,
                "llm/attempt": attempt,
                "llm/success": False,
                "llm/error_type": type(e).__name__,
            })
            # Record error to run tracker
            tracker = get_run_tracker()
            if tracker is not None:
                tracker.record_call(stage, latency_ms, 0, success=False)
            if attempt == max_retries:
                raise LLMCallError(
                    message=f"LLM call failed after retries: {e}",
                    last_response=last_raw,
                )
            time.sleep(2**attempt)

    # Should never reach here
    raise LLMCallError("Unexpected error in call_llm_json",
                       last_response=last_raw)
