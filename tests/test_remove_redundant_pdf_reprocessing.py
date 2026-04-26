from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import frontend.app as frontend_app
from src import demo_api
from src import run_baseline_policy_summary as policy_summary
from src.citation_linking import build_section_text_map


class FakeSectionSummary:
    def __init__(self, section_name: str) -> None:
        self.section_name = section_name

    def to_dict(self) -> dict:
        return {
            "section_name": self.section_name,
            "summary_overall": f"Summary for {self.section_name}",
            "key_coverages": [],
            "key_exclusions": [],
            "conditions_notable": [],
            "dispute_angles_possible": [],
        }


def _patch_policy_summary(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    sections: dict[str, str],
) -> tuple[Mock, Mock]:
    monkeypatch.setattr(policy_summary, "DATA_PROCESSED_DIR", tmp_path / "processed")
    monkeypatch.setattr(policy_summary, "SAFE_DATA_PROCESSED_DIR", tmp_path / "safe")
    monkeypatch.setattr(
        policy_summary,
        "get_settings",
        lambda: SimpleNamespace(persist_raw_text=False, safe_mode=False),
    )

    load_pdf_text = Mock(return_value="policy text")
    split_into_sections = Mock(return_value=sections)
    monkeypatch.setattr(policy_summary, "load_pdf_text", load_pdf_text)
    monkeypatch.setattr(policy_summary, "split_into_sections", split_into_sections)
    monkeypatch.setattr(
        policy_summary,
        "summarize_section",
        Mock(
            side_effect=lambda section_name, section_text: FakeSectionSummary(
                section_name
            )
        ),
    )
    return load_pdf_text, split_into_sections


def test_summarize_policy_with_sections_returns_output_path_and_raw_sections(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    raw_sections = {"COVERAGE A": "Dwelling text", "CONDITIONS": "Duties text"}
    _patch_policy_summary(monkeypatch, tmp_path, raw_sections)

    out_path, returned_sections = policy_summary.summarize_policy_with_sections(
        tmp_path / "policy.pdf"
    )

    assert out_path == tmp_path / "processed" / "policy.json"
    assert returned_sections is raw_sections
    assert out_path.is_file()


def test_summarize_policy_remains_path_only_backward_compatible(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _patch_policy_summary(monkeypatch, tmp_path, {"COVERAGE A": "Dwelling text"})

    out_path = policy_summary.summarize_policy(tmp_path / "policy.pdf")

    assert isinstance(out_path, Path)
    assert out_path == tmp_path / "processed" / "policy.json"


def test_summarize_policy_with_sections_loads_and_splits_pdf_once(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    load_pdf_text, split_into_sections = _patch_policy_summary(
        monkeypatch,
        tmp_path,
        {"COVERAGE A": "Dwelling text"},
    )

    policy_summary.summarize_policy_with_sections(tmp_path / "policy.pdf")

    load_pdf_text.assert_called_once_with(tmp_path / "policy.pdf")
    split_into_sections.assert_called_once_with("policy text")


def test_run_policy_analysis_returns_in_memory_section_text_map(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    raw_sections = {
        "COVERAGE A": "Dwelling text",
        "CONDITIONS": "Duties text",
        "UNKNOWN": "Excluded unknown text",
    }
    summary_json_path = tmp_path / "processed" / "uploaded.json"
    summary_json_path.parent.mkdir()
    summary_json_path.write_text(
        json.dumps(
            {
                "policy_id": "uploaded",
                "policy_path": "uploaded.pdf",
                "sections": [
                    {
                        "section_name": "COVERAGE A",
                        "summary_overall": "Dwelling summary",
                        "key_coverages": [],
                        "key_exclusions": [],
                        "conditions_notable": [],
                        "dispute_angles_possible": [],
                        "raw_text": "Dwelling text",
                        "section_role": "substantive",
                    },
                    {
                        "section_name": "CONDITIONS",
                        "summary_overall": "Duties summary",
                        "key_coverages": [],
                        "key_exclusions": [],
                        "conditions_notable": [],
                        "dispute_angles_possible": [],
                        "raw_text": "Duties text",
                        "section_role": "substantive",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(demo_api, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(
        demo_api,
        "get_settings",
        lambda: SimpleNamespace(safe_mode=False, persist_raw_text=False),
    )
    monkeypatch.setattr(demo_api, "start_wandb_run", lambda **kwargs: None)
    monkeypatch.setattr(demo_api, "finish_wandb_run", lambda: None)
    monkeypatch.setattr(
        demo_api,
        "summarize_policy_with_sections",
        Mock(return_value=(summary_json_path, raw_sections)),
    )

    policy_result = demo_api.run_policy_analysis(b"%PDF", "uploaded.pdf")

    expected_map = build_section_text_map(raw_sections)
    assert policy_result["section_text_map"] == expected_map
    assert list(policy_result["section_text_map"]) == ["COVERAGE A", "CONDITIONS"]
    assert "section_text_map" not in policy_result["artifacts"]
    assert "raw_text" not in policy_result["sections_substantive"][0]


def test_run_policy_analysis_forwards_focused_and_keeps_full_section_map(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    raw_sections = {
        "DEFINITIONS": "Definitions text",
        "COVERAGE A - DWELLING": "Dwelling text",
        "LOSS SETTLEMENT": "Full raw section text still available for citations",
    }
    summary_json_path = tmp_path / "processed" / "uploaded.json"
    summary_json_path.parent.mkdir()
    summary_json_path.write_text(
        json.dumps(
            {
                "policy_id": "uploaded",
                "policy_path": "uploaded.pdf",
                "analysis_mode": "focused",
                "sections": [
                    {
                        "section_name": "DEFINITIONS",
                        "summary_overall": "Definitions summary",
                        "key_coverages": [],
                        "key_exclusions": [],
                        "conditions_notable": [],
                        "dispute_angles_possible": [],
                        "section_role": "substantive",
                    },
                    {
                        "section_name": "COVERAGE A - DWELLING",
                        "summary_overall": "Dwelling summary",
                        "key_coverages": [],
                        "key_exclusions": [],
                        "conditions_notable": [],
                        "dispute_angles_possible": [],
                        "section_role": "substantive",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    summarize_mock = Mock(return_value=(summary_json_path, raw_sections))

    monkeypatch.setattr(demo_api, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(
        demo_api,
        "get_settings",
        lambda: SimpleNamespace(safe_mode=False, persist_raw_text=False),
    )
    monkeypatch.setattr(demo_api, "start_wandb_run", lambda **kwargs: None)
    monkeypatch.setattr(demo_api, "finish_wandb_run", lambda: None)
    monkeypatch.setattr(
        demo_api,
        "summarize_policy_with_sections",
        summarize_mock,
    )

    policy_result = demo_api.run_policy_analysis(
        b"%PDF",
        "uploaded.pdf",
        focused=True,
    )

    assert summarize_mock.call_args.kwargs["focused"] is True
    assert policy_result["analysis_mode"] == "focused"
    assert policy_result["section_text_map"] == build_section_text_map(raw_sections)
    assert "LOSS SETTLEMENT" in policy_result["section_text_map"]
    assert "LOSS SETTLEMENT" not in [
        section["section_name"] for section in policy_result["sections_substantive"]
    ]


class _FakeStatus:
    def __init__(self) -> None:
        self.updates: list[dict] = []

    def __enter__(self) -> "_FakeStatus":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def update(self, **kwargs) -> None:
        self.updates.append(kwargs)


class _FakeProgress:
    def __init__(self) -> None:
        self.values: list[int] = []

    def progress(self, value: int) -> None:
        self.values.append(value)


class _FakeStreamlit:
    def __init__(self) -> None:
        self.session_state: dict[str, object] = {}

    def status(self, *args, **kwargs) -> _FakeStatus:
        return _FakeStatus()

    def progress(self, value: int) -> _FakeProgress:
        progress = _FakeProgress()
        progress.progress(value)
        return progress

    def write(self, *args, **kwargs) -> None:
        return None


class _FakeIntakeStreamlit:
    def __init__(self, policy_file, denial_file) -> None:
        self.session_state: dict[str, object] = {}
        self.policy_file = policy_file
        self.denial_file = denial_file
        self.successes: list[str] = []
        self.warnings: list[str] = []

    def __enter__(self) -> "_FakeIntakeStreamlit":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def header(self, *args, **kwargs) -> None:
        return None

    def info(self, *args, **kwargs) -> None:
        return None

    def caption(self, *args, **kwargs) -> None:
        return None

    def form(self, *args, **kwargs) -> "_FakeIntakeStreamlit":
        return self

    def columns(self, count: int):
        return [self for _ in range(count)]

    def text_input(self, label: str, **kwargs) -> str:
        if label.startswith("Claim nickname"):
            return "Kitchen"
        if label.startswith("State"):
            return "TX"
        return ""

    def file_uploader(self, label: str, **kwargs):
        if label == "Policy PDF":
            return self.policy_file
        if label == "Denial letter PDF":
            return self.denial_file
        return None

    def checkbox(self, *args, **kwargs) -> bool:
        return False

    def form_submit_button(self, *args, **kwargs) -> bool:
        return True

    def error(self, *args, **kwargs) -> None:
        return None

    def stop(self) -> None:
        raise RuntimeError("streamlit stop")

    def success(self, message: str) -> None:
        self.successes.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)


def test_frontend_live_path_uses_policy_result_section_map_without_reprocessing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    summary_json_path = tmp_path / "policy.json"
    summary_json_path.write_text(
        json.dumps({"policy_id": "policy", "sections": []}),
        encoding="utf-8",
    )
    policy_pdf_path = tmp_path / "uploaded_policy.pdf"
    policy_pdf_path.write_bytes(b"%PDF policy")
    denial_path = tmp_path / "denial.pdf"
    denial_path.write_bytes(b"%PDF denial")
    section_map = {"COVERAGE A": "Dwelling text"}
    fake_st = _FakeStreamlit()
    load_pdf_text = Mock(return_value="denial text")

    monkeypatch.setattr(frontend_app, "st", fake_st)
    monkeypatch.setattr(frontend_app, "is_demo_force_on", lambda: False)
    monkeypatch.setattr(
        frontend_app,
        "run_policy_analysis",
        Mock(
            return_value={
                "policy_name": "policy",
                "source_path": str(policy_pdf_path),
                "section_text_map": section_map,
                "artifacts": {
                    "summary_json": str(summary_json_path),
                    "uploaded_pdf": str(policy_pdf_path),
                },
            }
        ),
    )
    monkeypatch.setattr(frontend_app, "_save_denial_pdf", lambda uploaded, nickname: denial_path)
    monkeypatch.setattr(frontend_app, "load_pdf_text", load_pdf_text)
    monkeypatch.setattr(
        frontend_app,
        "build_denial_aware_report",
        lambda policy_summary_payload, denial_text: SimpleNamespace(
            policy_id=None,
            denial_id=None,
            to_dict=lambda: {"plain_summary": "done"},
        ),
    )
    monkeypatch.setattr(frontend_app, "render_dispute_markdown", lambda *args, **kwargs: "md")

    policy_file = SimpleNamespace(
        name="uploaded_policy.pdf",
        getvalue=lambda: b"%PDF policy",
    )
    denial_file = SimpleNamespace(name="denial.pdf")

    frontend_app._run_full_analysis(
        claim_nickname="Kitchen",
        state="TX",
        policy_file=policy_file,
        denial_file=denial_file,
    )

    assert fake_st.session_state[frontend_app.SESSION_KEY_SECTION_MAP] == section_map
    load_pdf_text.assert_called_once_with(denial_path)


def test_frontend_run_full_analysis_forwards_focused_true(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    summary_json_path = tmp_path / "policy.json"
    summary_json_path.write_text(
        json.dumps({"policy_id": "policy", "analysis_mode": "focused", "sections": []}),
        encoding="utf-8",
    )
    denial_path = tmp_path / "denial.pdf"
    denial_path.write_bytes(b"%PDF denial")
    fake_st = _FakeStreamlit()
    run_policy_analysis = Mock(
        return_value={
            "policy_name": "policy",
            "source_path": "",
            "analysis_mode": "focused",
            "section_text_map": {},
            "artifacts": {"summary_json": str(summary_json_path)},
        }
    )

    monkeypatch.setattr(frontend_app, "st", fake_st)
    monkeypatch.setattr(frontend_app, "is_demo_force_on", lambda: False)
    monkeypatch.setattr(frontend_app, "run_policy_analysis", run_policy_analysis)
    monkeypatch.setattr(frontend_app, "_save_denial_pdf", lambda uploaded, nickname: denial_path)
    monkeypatch.setattr(frontend_app, "load_pdf_text", Mock(return_value="denial text"))
    monkeypatch.setattr(
        frontend_app,
        "build_denial_aware_report",
        lambda policy_summary_payload, denial_text: SimpleNamespace(
            policy_id=None,
            denial_id=None,
            to_dict=lambda: {"plain_summary": "done"},
        ),
    )
    monkeypatch.setattr(frontend_app, "render_dispute_markdown", lambda *args, **kwargs: "md")

    frontend_app._run_full_analysis(
        claim_nickname="Kitchen",
        state="TX",
        policy_file=SimpleNamespace(name="policy.pdf", getvalue=lambda: b"%PDF"),
        denial_file=SimpleNamespace(name="denial.pdf"),
        focused=True,
    )

    assert run_policy_analysis.call_args.kwargs["focused"] is True


def test_frontend_live_path_empty_section_map_does_not_overwrite_session_map(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    summary_json_path = tmp_path / "policy.json"
    summary_json_path.write_text(
        json.dumps({"policy_id": "policy", "sections": []}),
        encoding="utf-8",
    )
    existing_map = {"EXISTING": "Keep me"}
    fake_st = _FakeStreamlit()
    fake_st.session_state[frontend_app.SESSION_KEY_SECTION_MAP] = existing_map

    monkeypatch.setattr(frontend_app, "st", fake_st)
    monkeypatch.setattr(frontend_app, "is_demo_force_on", lambda: False)
    monkeypatch.setattr(
        frontend_app,
        "run_policy_analysis",
        Mock(
            return_value={
                "policy_name": "policy",
                "source_path": "",
                "artifacts": {"summary_json": str(summary_json_path)},
            }
        ),
    )
    monkeypatch.setattr(frontend_app, "_save_denial_pdf", lambda uploaded, nickname: tmp_path / "denial.pdf")
    monkeypatch.setattr(frontend_app, "load_pdf_text", Mock(return_value="denial text"))
    monkeypatch.setattr(
        frontend_app,
        "build_denial_aware_report",
        lambda policy_summary_payload, denial_text: SimpleNamespace(
            policy_id=None,
            denial_id=None,
            to_dict=lambda: {"plain_summary": "done"},
        ),
    )
    monkeypatch.setattr(frontend_app, "render_dispute_markdown", lambda *args, **kwargs: "md")

    frontend_app._run_full_analysis(
        claim_nickname="Kitchen",
        state="TX",
        policy_file=SimpleNamespace(name="policy.pdf", getvalue=lambda: b"%PDF"),
        denial_file=SimpleNamespace(name="denial.pdf"),
    )

    assert fake_st.session_state[frontend_app.SESSION_KEY_SECTION_MAP] is existing_map


def test_intake_persistence_strips_section_text_map_without_changing_memory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    policy_file = SimpleNamespace(name="policy.pdf")
    denial_file = SimpleNamespace(name="denial.pdf")
    fake_st = _FakeIntakeStreamlit(policy_file, denial_file)
    raw_policy_text = "RAW POLICY TEXT THAT MUST NOT BE PERSISTED"
    policy_result = {
        "policy_name": "policy",
        "sections_substantive": [],
        "section_text_map": {"COVERAGE A": raw_policy_text},
        "artifacts": {"summary_json": "policy.json"},
    }
    dispute_result = {"dispute_report": {"plain_summary": "done"}}
    saved_payloads: list[dict] = []

    monkeypatch.setattr(frontend_app, "st", fake_st)
    monkeypatch.setattr(frontend_app, "is_demo_force_on", lambda: False)
    monkeypatch.setattr(
        frontend_app,
        "_run_full_analysis",
        lambda **kwargs: (policy_result, dispute_result),
    )

    def fake_save_claim(**kwargs) -> int:
        saved_payloads.append(kwargs)
        return 123

    monkeypatch.setattr(frontend_app, "save_claim", fake_save_claim)

    frontend_app._render_intake_form()

    assert fake_st.session_state[frontend_app.SESSION_KEY_POLICY] is policy_result
    assert policy_result["section_text_map"] == {"COVERAGE A": raw_policy_text}

    persisted_policy = saved_payloads[0]["report_json"]["policy_result"]
    assert "section_text_map" not in persisted_policy
    assert raw_policy_text not in json.dumps(saved_payloads[0]["report_json"])
