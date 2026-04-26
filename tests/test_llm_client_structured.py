from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict, Iterable
from unittest.mock import Mock, patch

from src.llm_client import call_llm_json
from src.schemas import DisputeReport
from src.summarizer_frontier import (
    DISPUTE_REPORT_SCHEMA,
    build_denial_aware_report,
    summarize_section,
)


def _settings() -> SimpleNamespace:
    return SimpleNamespace(openai_api_key="test-key")


def _response(output_text: str) -> SimpleNamespace:
    return SimpleNamespace(
        output_text=output_text,
        usage=SimpleNamespace(
            input_tokens=11,
            output_tokens=7,
            total_tokens=18,
        ),
    )


def _client_with_response(response: SimpleNamespace) -> Mock:
    client = Mock()
    client.responses.create.return_value = response
    return client


def _sample_response_schema() -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": {"ok": {"type": "boolean"}},
        "required": ["ok"],
        "additionalProperties": False,
    }


def _synthetic_dispute_payload() -> Dict[str, Any]:
    return {
        "plain_summary": "The insurer denied the claim based on stated policy terms.",
        "coverage_highlights": [
            {"text": "Coverage A may apply.", "citation": "COVERAGE A - DWELLING"}
        ],
        "exclusions_limitations": [
            {"text": "Wear and tear may be raised.", "citation": None}
        ],
        "denial_reasons": [
            {"text": "The insurer cited an exclusion.", "citation": "EXCLUSIONS"}
        ],
        "dispute_angles": [
            {"text": "Check whether the cited exclusion fits.", "citations": ["EXCLUSIONS"]}
        ],
        "missing_info": ["Adjuster photos"],
        "confidence": {
            "score": 0.72,
            "notes": "Based on summarized policy sections and denial text.",
            "verify_clauses": ["EXCLUSIONS"],
        },
    }


def test_call_llm_json_uses_json_object_when_no_schema_is_supplied() -> None:
    client = _client_with_response(_response('{"ok": true}'))

    with (
        patch("src.llm_client.get_settings", return_value=_settings()),
        patch("src.llm_client.OpenAI", return_value=client),
    ):
        result = call_llm_json(
            system_prompt="system JSON instruction",
            user_prompt="user JSON instruction",
            max_retries=1,
            model="gpt-test",
        )

    assert result == {"ok": True}
    client.responses.create.assert_called_once()
    assert client.responses.create.call_args.kwargs["text"] == {
        "format": {"type": "json_object"}
    }


def test_call_llm_json_uses_json_schema_when_schema_is_supplied() -> None:
    client = _client_with_response(_response('{"ok": true}'))
    schema = _sample_response_schema()

    with (
        patch("src.llm_client.get_settings", return_value=_settings()),
        patch("src.llm_client.OpenAI", return_value=client),
    ):
        result = call_llm_json(
            system_prompt="system JSON instruction",
            user_prompt="user JSON instruction",
            max_retries=1,
            model="gpt-test",
            response_schema=schema,
            schema_name="unit_test_schema",
        )

    assert result == {"ok": True}
    client.responses.create.assert_called_once()
    assert client.responses.create.call_args.kwargs["text"] == {
        "format": {
            "type": "json_schema",
            "name": "unit_test_schema",
            "schema": schema,
            "strict": True,
        }
    }


def test_call_llm_json_uses_stage_as_fallback_schema_name() -> None:
    client = _client_with_response(_response('{"ok": true}'))
    schema = _sample_response_schema()

    with (
        patch("src.llm_client.get_settings", return_value=_settings()),
        patch("src.llm_client.OpenAI", return_value=client),
    ):
        call_llm_json(
            system_prompt="system JSON instruction",
            user_prompt="user JSON instruction",
            max_retries=1,
            stage="structured_stage",
            response_schema=schema,
        )

    assert client.responses.create.call_args.kwargs["text"]["format"]["name"] == (
        "structured_stage"
    )


def _walk_schema_nodes(schema: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    yield schema

    properties = schema.get("properties")
    if isinstance(properties, dict):
        for child in properties.values():
            if isinstance(child, dict):
                yield from _walk_schema_nodes(child)

    items = schema.get("items")
    if isinstance(items, dict):
        yield from _walk_schema_nodes(items)


def test_dispute_report_schema_is_strict_mode_compatible() -> None:
    banned_keywords = {
        "format",
        "pattern",
        "default",
        "minimum",
        "maximum",
        "minLength",
        "maxLength",
        "patternProperties",
        "allOf",
        "not",
        "dependentRequired",
        "dependentSchemas",
        "if",
        "then",
        "else",
    }

    assert DISPUTE_REPORT_SCHEMA["type"] == "object"
    assert "policy_id" not in DISPUTE_REPORT_SCHEMA["properties"]
    assert "denial_id" not in DISPUTE_REPORT_SCHEMA["properties"]

    for node in _walk_schema_nodes(DISPUTE_REPORT_SCHEMA):
        assert banned_keywords.isdisjoint(node.keys())
        if node.get("type") == "object":
            properties = node.get("properties")
            assert isinstance(properties, dict)
            assert node.get("additionalProperties") is False
            assert set(node.get("required", [])) == set(properties.keys())


def test_build_denial_aware_report_passes_dispute_report_schema_and_parses_payload() -> None:
    with patch(
        "src.summarizer_frontier.call_llm_json",
        return_value=_synthetic_dispute_payload(),
    ) as call_mock:
        report = build_denial_aware_report({"sections": []}, "Denied.")

    call_mock.assert_called_once()
    kwargs = call_mock.call_args.kwargs
    assert kwargs["response_schema"] is DISPUTE_REPORT_SCHEMA
    assert kwargs["schema_name"] == "dispute_report"

    assert isinstance(report, DisputeReport)
    assert report.plain_summary.startswith("The insurer denied")
    assert report.coverage_highlights[0].citation == "COVERAGE A - DWELLING"
    assert report.exclusions_limitations[0].citation is None
    assert report.dispute_angles[0].citations == ["EXCLUSIONS"]
    assert report.confidence.score == 0.72


def test_summarize_section_does_not_pass_response_schema() -> None:
    with patch(
        "src.summarizer_frontier.call_llm_json",
        return_value={
            "summary_overall": "Coverage summary.",
            "key_coverages": ["Coverage A"],
            "key_exclusions": ["Wear and tear"],
            "conditions_notable": ["Prompt notice"],
            "dispute_angles_possible": ["Check ambiguity"],
        },
    ) as call_mock:
        summary = summarize_section("COVERAGE A", "Policy text.")

    call_mock.assert_called_once()
    assert "response_schema" not in call_mock.call_args.kwargs
    assert summary.section_name == "COVERAGE A"
