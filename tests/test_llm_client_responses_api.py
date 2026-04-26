from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from src.config import ConfigError
from src.llm_client import LLMCallError, call_llm_json
from src.wandb_telemetry import WandbRunTracker


def _settings() -> SimpleNamespace:
    return SimpleNamespace(openai_api_key="test-key")


def _response(
    output_text: str,
    *,
    input_tokens: int = 11,
    output_tokens: int = 7,
    total_tokens: int = 18,
) -> SimpleNamespace:
    return SimpleNamespace(
        output_text=output_text,
        usage=SimpleNamespace(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
        ),
    )


def _client_with_response(response: SimpleNamespace) -> Mock:
    client = Mock()
    client.responses.create.return_value = response
    return client


def _assert_chat_create_not_called(client: Mock) -> None:
    getattr(getattr(client, "chat"), "completions").create.assert_not_called()


def test_call_llm_json_uses_responses_api_and_returns_parsed_json() -> None:
    client = _client_with_response(_response('{"ok": true}'))

    with (
        patch("src.llm_client.get_settings", return_value=_settings()),
        patch("src.llm_client.OpenAI", return_value=client),
    ):
        result = call_llm_json(
            system_prompt="system JSON instruction",
            user_prompt="user JSON instruction",
            temperature=0.3,
            max_retries=1,
            timeout=12.0,
            model="gpt-test",
        )

    assert result == {"ok": True}
    client.responses.create.assert_called_once_with(
        model="gpt-test",
        instructions="system JSON instruction",
        input="user JSON instruction",
        text={"format": {"type": "json_object"}},
        temperature=0.3,
        store=False,
    )
    _assert_chat_create_not_called(client)


def test_call_llm_json_maps_response_usage_to_existing_tracker_fields() -> None:
    tracker = WandbRunTracker()
    client = _client_with_response(
        _response(
            '{"ok": true}',
            input_tokens=101,
            output_tokens=37,
            total_tokens=138,
        )
    )

    with (
        patch("src.llm_client.get_settings", return_value=_settings()),
        patch("src.llm_client.OpenAI", return_value=client),
        patch("src.llm_client.get_run_tracker", return_value=tracker),
    ):
        call_llm_json(
            system_prompt="system JSON instruction",
            user_prompt="user JSON instruction",
            max_retries=1,
            stage="section_summary",
        )

    assert tracker.total_prompt_tokens == 101
    assert tracker.total_completion_tokens == 37
    assert tracker.total_tokens == 138
    assert tracker.call_count == 1
    assert tracker.error_count == 0


def test_call_llm_json_retries_invalid_json_and_eventually_succeeds() -> None:
    client = Mock()
    client.responses.create.side_effect = [
        _response("not json"),
        _response('{"ok": true}'),
    ]

    with (
        patch("src.llm_client.get_settings", return_value=_settings()),
        patch("src.llm_client.OpenAI", return_value=client),
        patch("src.llm_client.time.sleep"),
    ):
        result = call_llm_json(
            system_prompt="system JSON instruction",
            user_prompt="user JSON instruction",
            max_retries=2,
        )

    assert result == {"ok": True}
    assert client.responses.create.call_count == 2
    _assert_chat_create_not_called(client)


def test_call_llm_json_raises_after_invalid_json_retries_with_last_response() -> None:
    client = Mock()
    client.responses.create.side_effect = [
        _response("not json"),
        _response("still not json"),
    ]

    with (
        patch("src.llm_client.get_settings", return_value=_settings()),
        patch("src.llm_client.OpenAI", return_value=client),
        patch("src.llm_client.time.sleep"),
    ):
        with pytest.raises(LLMCallError) as exc_info:
            call_llm_json(
                system_prompt="system JSON instruction",
                user_prompt="user JSON instruction",
                max_retries=2,
            )

    assert exc_info.value.last_response == "still not json"
    assert client.responses.create.call_count == 2
    _assert_chat_create_not_called(client)


def test_call_llm_json_propagates_config_error_without_retry() -> None:
    with (
        patch("src.llm_client.get_settings", side_effect=ConfigError("missing key")),
        patch("src.llm_client.OpenAI") as openai_mock,
        patch("src.llm_client.time.sleep") as sleep_mock,
    ):
        with pytest.raises(ConfigError):
            call_llm_json(
                system_prompt="system JSON instruction",
                user_prompt="user JSON instruction",
                max_retries=3,
            )

    openai_mock.assert_not_called()
    sleep_mock.assert_not_called()


def test_call_llm_json_retries_generic_exception_and_eventually_succeeds() -> None:
    client = Mock()
    client.responses.create.side_effect = [
        RuntimeError("temporary failure"),
        _response('{"ok": true}'),
    ]

    with (
        patch("src.llm_client.get_settings", return_value=_settings()),
        patch("src.llm_client.OpenAI", return_value=client),
        patch("src.llm_client.time.sleep"),
    ):
        result = call_llm_json(
            system_prompt="system JSON instruction",
            user_prompt="user JSON instruction",
            max_retries=2,
        )

    assert result == {"ok": True}
    assert client.responses.create.call_count == 2
    _assert_chat_create_not_called(client)
