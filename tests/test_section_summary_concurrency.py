from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src import run_baseline_policy_summary as policy_summary


class FakeSectionSummary:
    def __init__(self, section_name: str) -> None:
        self.section_name = section_name

    def to_dict(self) -> dict:
        return {"section_name": self.section_name}


def _run_summarize_policy(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    sections: dict[str, str],
    *,
    focused: bool = False,
    persist_raw_text: bool = False,
    summarize_section: Mock | None = None,
) -> dict:
    output_dir = tmp_path / "processed"
    monkeypatch.setattr(policy_summary, "DATA_PROCESSED_DIR", output_dir)
    monkeypatch.setattr(policy_summary, "SAFE_DATA_PROCESSED_DIR", tmp_path / "safe")
    monkeypatch.setattr(
        policy_summary,
        "get_settings",
        lambda: SimpleNamespace(persist_raw_text=persist_raw_text, safe_mode=False),
    )
    monkeypatch.setattr(policy_summary, "load_pdf_text", lambda pdf_path: "policy text")
    monkeypatch.setattr(policy_summary, "split_into_sections", lambda text: sections)

    if summarize_section is None:
        summarize_section = Mock(
            side_effect=lambda section_name, section_text: FakeSectionSummary(
                section_name
            )
        )
    monkeypatch.setattr(policy_summary, "summarize_section", summarize_section)

    out_path = policy_summary.summarize_policy(
        tmp_path / "policy.pdf",
        focused=focused,
    )

    return json.loads(out_path.read_text(encoding="utf-8"))


def test_summarize_policy_preserves_section_order_with_default_concurrency(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("SECTION_SUMMARY_MAX_WORKERS", raising=False)
    sections = {
        "FIRST": "first text",
        "SECOND": "second text",
        "THIRD": "third text",
    }
    delays = {"FIRST": 0.03, "SECOND": 0.02, "THIRD": 0.01}

    def summarize(section_name: str, section_text: str) -> FakeSectionSummary:
        time.sleep(delays[section_name])
        return FakeSectionSummary(section_name)

    payload = _run_summarize_policy(
        monkeypatch,
        tmp_path,
        sections,
        summarize_section=Mock(side_effect=summarize),
    )

    assert [section["section_name"] for section in payload["sections"]] == [
        "FIRST",
        "SECOND",
        "THIRD",
    ]


def test_summarize_policy_preserves_section_order_with_env_concurrency(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("SECTION_SUMMARY_MAX_WORKERS", "8")
    sections = {
        "SECTION 0": "text 0",
        "SECTION 1": "text 1",
        "SECTION 2": "text 2",
        "SECTION 3": "text 3",
    }
    delays = {
        section_name: (len(sections) - index) * 0.01
        for index, section_name in enumerate(sections)
    }

    def summarize(section_name: str, section_text: str) -> FakeSectionSummary:
        time.sleep(delays[section_name])
        return FakeSectionSummary(section_name)

    payload = _run_summarize_policy(
        monkeypatch,
        tmp_path,
        sections,
        summarize_section=Mock(side_effect=summarize),
    )

    assert [section["section_name"] for section in payload["sections"]] == list(
        sections
    )


def test_section_summary_max_workers_one_runs_sequentially(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("SECTION_SUMMARY_MAX_WORKERS", "1")
    sections = {
        "FIRST": "first text",
        "SECOND": "second text",
        "THIRD": "third text",
    }
    lock = threading.Lock()
    in_flight = 0
    peak_in_flight = 0

    def summarize(section_name: str, section_text: str) -> FakeSectionSummary:
        nonlocal in_flight, peak_in_flight
        with lock:
            in_flight += 1
            peak_in_flight = max(peak_in_flight, in_flight)
        time.sleep(0.01)
        with lock:
            in_flight -= 1
        return FakeSectionSummary(section_name)

    _run_summarize_policy(
        monkeypatch,
        tmp_path,
        sections,
        summarize_section=Mock(side_effect=summarize),
    )

    assert peak_in_flight <= 1


def test_summarize_section_is_invoked_once_per_section(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("SECTION_SUMMARY_MAX_WORKERS", raising=False)
    sections = {"A": "a text", "B": "b text", "C": "c text"}
    summarize_section = Mock(
        side_effect=lambda section_name, section_text: FakeSectionSummary(section_name)
    )

    _run_summarize_policy(
        monkeypatch,
        tmp_path,
        sections,
        summarize_section=summarize_section,
    )

    assert summarize_section.call_count == len(sections)


def test_full_analysis_summarizes_every_section_by_default(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("SECTION_SUMMARY_MAX_WORKERS", raising=False)
    sections = {
        "DEFINITIONS": "definition text",
        "COVERAGE A - DWELLING": "dwelling text",
        "UNRELATED ENDORSEMENT": "endorsement text",
    }
    summarize_section = Mock(
        side_effect=lambda section_name, section_text: FakeSectionSummary(section_name)
    )

    payload = _run_summarize_policy(
        monkeypatch,
        tmp_path,
        sections,
        summarize_section=summarize_section,
    )

    assert payload["analysis_mode"] == "full"
    assert summarize_section.call_count == len(sections)
    assert [section["section_name"] for section in payload["sections"]] == list(
        sections
    )


def test_focused_false_preserves_full_analysis_behavior(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    sections = {
        "DEFINITIONS": "definition text",
        "COVERAGE A - DWELLING": "dwelling text",
        "UNRELATED ENDORSEMENT": "endorsement text",
    }
    summarize_section = Mock(
        side_effect=lambda section_name, section_text: FakeSectionSummary(section_name)
    )

    payload = _run_summarize_policy(
        monkeypatch,
        tmp_path,
        sections,
        focused=False,
        summarize_section=summarize_section,
    )

    assert payload["analysis_mode"] == "full"
    assert summarize_section.call_count == len(sections)


def test_focused_analysis_filters_to_canonical_sections_only(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    sections = {
        "DEFINITIONS": "definition text",
        "COVERAGE A - DWELLING": "dwelling text",
        "UNRELATED ENDORSEMENT": "endorsement text",
        "EXCLUSIONS": "exclusion text",
    }
    summarize_section = Mock(
        side_effect=lambda section_name, section_text: FakeSectionSummary(section_name)
    )

    payload = _run_summarize_policy(
        monkeypatch,
        tmp_path,
        sections,
        focused=True,
        summarize_section=summarize_section,
    )

    assert payload["analysis_mode"] == "focused"
    assert [section["section_name"] for section in payload["sections"]] == [
        "DEFINITIONS",
        "COVERAGE A - DWELLING",
        "EXCLUSIONS",
    ]
    assert [call.args[0] for call in summarize_section.call_args_list] == [
        "DEFINITIONS",
        "COVERAGE A - DWELLING",
        "EXCLUSIONS",
    ]


def test_focused_analysis_skips_meta_sections(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    sections = {
        "DEFINITIONS": "This is only a sample policy and not an actual policy.",
        "EXCLUSIONS": "We do not insure for loss caused by wear and tear.",
    }

    payload = _run_summarize_policy(
        monkeypatch,
        tmp_path,
        sections,
        focused=True,
    )

    assert [section["section_name"] for section in payload["sections"]] == [
        "EXCLUSIONS"
    ]


def test_focused_selection_preserves_original_section_order() -> None:
    sections = {
        "COVERAGE D - LOSS OF USE": "loss of use text",
        "UNRELATED": "unrelated text",
        "DEFINITIONS": "definition text",
        "COVERAGE A - DWELLING": "dwelling text",
        "CONDITIONS": "conditions text",
    }

    focused_sections = policy_summary._select_focused_sections(sections)

    assert list(focused_sections) == [
        "COVERAGE D - LOSS OF USE",
        "DEFINITIONS",
        "COVERAGE A - DWELLING",
        "CONDITIONS",
    ]


def test_section_summary_exception_propagates_and_writes_no_json(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("SECTION_SUMMARY_MAX_WORKERS", raising=False)
    sections = {"A": "a text", "B": "b text"}
    output_dir = tmp_path / "processed"

    def summarize(section_name: str, section_text: str) -> FakeSectionSummary:
        if section_name == "B":
            raise RuntimeError("section failed")
        return FakeSectionSummary(section_name)

    with pytest.raises(RuntimeError, match="section failed"):
        _run_summarize_policy(
            monkeypatch,
            tmp_path,
            sections,
            summarize_section=Mock(side_effect=summarize),
        )

    assert not (output_dir / "policy.json").exists()


def test_section_role_classification_is_preserved(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    sections = {
        "UNKNOWN": "This is only a sample policy and not an actual policy.",
        "COVERAGE A": "We cover the dwelling on the residence premises.",
    }

    payload = _run_summarize_policy(monkeypatch, tmp_path, sections)

    assert [section["section_role"] for section in payload["sections"]] == [
        "meta",
        "substantive",
    ]


def test_persist_raw_text_true_includes_raw_text(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    sections = {"COVERAGE A": "covered dwelling text"}

    payload = _run_summarize_policy(
        monkeypatch,
        tmp_path,
        sections,
        persist_raw_text=True,
    )

    assert payload["sections"][0]["raw_text"] == "covered dwelling text"


def test_persist_raw_text_false_omits_raw_text(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    sections = {"COVERAGE A": "covered dwelling text"}

    payload = _run_summarize_policy(
        monkeypatch,
        tmp_path,
        sections,
        persist_raw_text=False,
    )

    assert "raw_text" not in payload["sections"][0]


def test_resolve_section_summary_workers_defaults_to_four_when_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("SECTION_SUMMARY_MAX_WORKERS", raising=False)

    assert policy_summary._resolve_section_summary_workers() == 4


def test_resolve_section_summary_workers_uses_positive_env_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SECTION_SUMMARY_MAX_WORKERS", "8")

    assert policy_summary._resolve_section_summary_workers() == 8


@pytest.mark.parametrize("value", ["not-an-int", "4.5"])
def test_resolve_section_summary_workers_invalid_value_falls_back_to_four(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    monkeypatch.setenv("SECTION_SUMMARY_MAX_WORKERS", value)

    assert policy_summary._resolve_section_summary_workers() == 4


@pytest.mark.parametrize("value", ["0", "-1"])
def test_resolve_section_summary_workers_zero_or_negative_falls_back_to_four(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    monkeypatch.setenv("SECTION_SUMMARY_MAX_WORKERS", value)

    assert policy_summary._resolve_section_summary_workers() == 4


def test_resolve_section_summary_workers_empty_string_falls_back_to_four(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SECTION_SUMMARY_MAX_WORKERS", "")

    assert policy_summary._resolve_section_summary_workers() == 4


def test_empty_sections_produce_empty_sections_list(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    payload = _run_summarize_policy(monkeypatch, tmp_path, {})

    assert payload["sections"] == []


def test_single_section_still_works(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    payload = _run_summarize_policy(
        monkeypatch,
        tmp_path,
        {"COVERAGE A": "covered dwelling text"},
    )

    assert [section["section_name"] for section in payload["sections"]] == [
        "COVERAGE A"
    ]
