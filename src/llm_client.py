# src/llm_client.py
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from openai import OpenAI
from .config import get_settings, ConfigError


@dataclass
class LLMCallError(RuntimeError):
    message: str
    last_response: Optional[str] = None


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
    """
    last_raw: Optional[str] = None
    model_name = model or _get_model_name()

    for attempt in range(1, max_retries + 1):
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

            raw = response.choices[0].message.content
            last_raw = raw
            return json.loads(raw)

        except json.JSONDecodeError:
            # Model returned non-JSON; retry unless we’re out of attempts.
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
            if attempt == max_retries:
                raise LLMCallError(
                    message=f"LLM call failed after retries: {e}",
                    last_response=last_raw,
                )
            time.sleep(2**attempt)

    # Should never reach here
    raise LLMCallError("Unexpected error in call_llm_json",
                       last_response=last_raw)
