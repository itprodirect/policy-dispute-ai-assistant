from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock, patch

from pytest import MonkeyPatch

from src.llm_client import call_llm_json


MODEL_ENV_VARS = (
    "OPENAI_MODEL",
    "OPENAI_MODEL_SECTION_SUMMARY",
    "OPENAI_MODEL_DISPUTE_REPORT",
    "OPENAI_MODEL_FOCUSED_ANALYSIS",
    "OPENAI_MODEL_QA_STAGE",
)


def _settings() -> SimpleNamespace:
    return SimpleNamespace(openai_api_key="test-key")


def _response() -> SimpleNamespace:
    return SimpleNamespace(
        output_text='{"ok": true}',
        usage=SimpleNamespace(
            input_tokens=11,
            output_tokens=7,
            total_tokens=18,
        ),
    )


def _clear_model_env(monkeypatch: MonkeyPatch) -> None:
    for name in MODEL_ENV_VARS:
        monkeypatch.delenv(name, raising=False)


def _model_used(*, stage: str | None = None, model: str | None = None) -> str:
    client = Mock()
    client.responses.create.return_value = _response()

    kwargs = {
        "system_prompt": "system JSON instruction",
        "user_prompt": "user JSON instruction",
        "max_retries": 1,
    }
    if stage is not None:
        kwargs["stage"] = stage
    if model is not None:
        kwargs["model"] = model

    with (
        patch("src.llm_client.get_settings", return_value=_settings()),
        patch("src.llm_client.OpenAI", return_value=client),
    ):
        call_llm_json(**kwargs)

    return client.responses.create.call_args.kwargs["model"]


def test_default_model_remains_gpt_4_1_mini_when_no_env_vars_are_set(
    monkeypatch: MonkeyPatch,
) -> None:
    _clear_model_env(monkeypatch)

    assert _model_used(stage="section_summary") == "gpt-4.1-mini"


def test_global_openai_model_still_works_for_known_stages(
    monkeypatch: MonkeyPatch,
) -> None:
    _clear_model_env(monkeypatch)
    monkeypatch.setenv("OPENAI_MODEL", "gpt-global")

    assert _model_used(stage="section_summary") == "gpt-global"


def test_section_summary_stage_model_wins_over_global(
    monkeypatch: MonkeyPatch,
) -> None:
    _clear_model_env(monkeypatch)
    monkeypatch.setenv("OPENAI_MODEL", "gpt-global")
    monkeypatch.setenv("OPENAI_MODEL_SECTION_SUMMARY", "gpt-section")

    assert _model_used(stage="section_summary") == "gpt-section"


def test_dispute_report_stage_model_wins_over_global(
    monkeypatch: MonkeyPatch,
) -> None:
    _clear_model_env(monkeypatch)
    monkeypatch.setenv("OPENAI_MODEL", "gpt-global")
    monkeypatch.setenv("OPENAI_MODEL_DISPUTE_REPORT", "gpt-dispute")

    assert _model_used(stage="dispute_report") == "gpt-dispute"


def test_explicit_model_argument_wins_over_all_env_vars(
    monkeypatch: MonkeyPatch,
) -> None:
    _clear_model_env(monkeypatch)
    monkeypatch.setenv("OPENAI_MODEL", "gpt-global")
    monkeypatch.setenv("OPENAI_MODEL_SECTION_SUMMARY", "gpt-section")

    assert _model_used(stage="section_summary", model="gpt-explicit") == "gpt-explicit"


def test_section_summary_override_does_not_affect_dispute_report_stage(
    monkeypatch: MonkeyPatch,
) -> None:
    _clear_model_env(monkeypatch)
    monkeypatch.setenv("OPENAI_MODEL", "gpt-global")
    monkeypatch.setenv("OPENAI_MODEL_SECTION_SUMMARY", "gpt-section")

    assert _model_used(stage="dispute_report") == "gpt-global"


def test_empty_string_stage_env_var_is_treated_as_unset(
    monkeypatch: MonkeyPatch,
) -> None:
    _clear_model_env(monkeypatch)
    monkeypatch.setenv("OPENAI_MODEL", "gpt-global")
    monkeypatch.setenv("OPENAI_MODEL_SECTION_SUMMARY", "")

    assert _model_used(stage="section_summary") == "gpt-global"


def test_unknown_stage_falls_back_to_global_model(
    monkeypatch: MonkeyPatch,
) -> None:
    _clear_model_env(monkeypatch)
    monkeypatch.setenv("OPENAI_MODEL", "gpt-global")

    assert _model_used(stage="unknown_stage") == "gpt-global"


def test_stage_none_falls_back_to_global_model(monkeypatch: MonkeyPatch) -> None:
    _clear_model_env(monkeypatch)
    monkeypatch.setenv("OPENAI_MODEL", "gpt-global")

    assert _model_used(stage=None) == "gpt-global"


def test_stage_lookup_is_mechanical_via_uppercasing(
    monkeypatch: MonkeyPatch,
) -> None:
    _clear_model_env(monkeypatch)
    monkeypatch.setenv("OPENAI_MODEL", "gpt-global")
    monkeypatch.setenv("OPENAI_MODEL_QA_STAGE", "gpt-qa")

    assert _model_used(stage="qa_stage") == "gpt-qa"


def test_future_stage_env_var_works(monkeypatch: MonkeyPatch) -> None:
    _clear_model_env(monkeypatch)
    monkeypatch.setenv("OPENAI_MODEL", "gpt-global")
    monkeypatch.setenv("OPENAI_MODEL_FOCUSED_ANALYSIS", "gpt-focused")

    assert _model_used(stage="focused_analysis") == "gpt-focused"
