from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

from .run_baseline_policy_summary import summarize_policy
from .report_builder import (
    build_policy_report,
    render_markdown,
    render_dispute_markdown,
)
from .summarizer_frontier import build_denial_aware_report
from .config import get_settings


UPLOAD_DIR = Path("data/uploads")

# Where dispute reports (JSON + Markdown) are written.
# Mirrors run_denial_summary.py
DEFAULT_DATA_PROCESSED_DIR = Path("data/processed")
SAFE_DATA_PROCESSED_DIR = Path("data/processed_safe")


def _save_uploaded_policy(file_bytes: bytes, original_name: str) -> Path:
    """
    Save the uploaded policy PDF into data/uploads with a timestamped name.
    """
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    stem = Path(original_name).stem or "uploaded_policy"
    ts = int(time.time())
    filename = f"{stem}__{ts}.pdf"
    path = UPLOAD_DIR / filename
    path.write_bytes(file_bytes)
    return path


def _strip_raw_text(sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove any raw_text field from section dicts before returning to the UI.
    We still respect on-disk persistence controlled via env config.
    """
    cleaned: List[Dict[str, Any]] = []
    for s in sections:
        s_copy = dict(s)
        s_copy.pop("raw_text", None)
        cleaned.append(s_copy)
    return cleaned


def _resolve_dispute_output_dir() -> Path:
    """
    Decide where to write dispute outputs (JSON + Markdown).

    - Normal mode: data/processed/
    - SAFE_MODE=true: data/processed_safe/
    """
    settings = get_settings()
    return SAFE_DATA_PROCESSED_DIR if settings.safe_mode else DEFAULT_DATA_PROCESSED_DIR


def run_policy_analysis(
    policy_file_bytes: bytes,
    policy_filename: str,
) -> Dict[str, Any]:
    """
    High-level service for the v0 frontend.

    Workflow:
      - Save uploaded PDF under data/uploads/
      - Run existing policy summarization pipeline
      - Build PolicyReport (stats + sections)
      - Build Markdown report
      - Return a JSON-serializable dict safe for UI (no raw policy text)
    """
    # Load settings early so misconfig errors surface here (OPENAI_API_KEY, SAFE_MODE, etc.).
    settings = get_settings()

    pdf_path = _save_uploaded_policy(policy_file_bytes, policy_filename)

    # This runs your existing end-to-end pipeline (PDF -> sections -> LLM summaries -> JSON).
    summary_json_path = summarize_policy(pdf_path)

    # Normalise into PolicyReport
    summary_data = json.loads(summary_json_path.read_text(encoding="utf-8"))
    policy_report = build_policy_report(summary_data)

    sections_substantive = _strip_raw_text(policy_report.sections_substantive)
    sections_meta = _strip_raw_text(policy_report.sections_meta)

    # Build Markdown in-memory and also write it out next to the JSON summary.
    markdown_text = render_markdown(policy_report)
    md_path = summary_json_path.with_suffix(".report.md")
    md_path.write_text(markdown_text, encoding="utf-8")

    return {
        "policy_name": policy_report.policy_name,
        "source_path": policy_report.source_path,
        "stats": {
            "num_sections": policy_report.num_sections,
            "num_unknown_sections": policy_report.num_unknown_sections,
            "num_meta_sections": policy_report.num_meta_sections,
        },
        "sections_substantive": sections_substantive,
        "sections_meta": sections_meta,
        "artifacts": {
            "summary_json": str(summary_json_path),
            "markdown_report": str(md_path),
            "uploaded_pdf": str(pdf_path),
            "safe_mode": settings.safe_mode,
            "persist_raw_text": settings.persist_raw_text,
        },
        "markdown": markdown_text,
    }


def run_dispute_analysis(
    policy_summary_json_path: str | Path,
    denial_text: str,
    *,
    denial_id: str | None = None,
) -> Dict[str, Any]:
    """
    Build a denial-aware A–G dispute report from an existing policy summary JSON
    and a denial letter text blob.

    This is the programmatic equivalent of run_denial_summary.py for the frontend.

    Args:
        policy_summary_json_path:
            Path to the policy summary JSON (output of run_baseline_policy_summary.py
            / summarize_policy()).
        denial_text:
            Plain-text content of the denial letter (v0: already extracted text).
        denial_id:
            Optional identifier for the denial (e.g. claim number or filename stem).
            If omitted, a timestamp-based ID is generated.

    Returns:
        JSON-serializable dict including:
          - policy_id, denial_id
          - dispute_report (nested A–G structure as dict)
          - markdown (rendered dispute report)
          - artifacts (paths to saved JSON/Markdown, plus safe_mode flag)
    """
    settings = get_settings()

    policy_path = Path(policy_summary_json_path)
    if not policy_path.is_file():
        raise FileNotFoundError(
            f"Policy summary JSON not found: {policy_path}")

    policy_payload = json.loads(policy_path.read_text(encoding="utf-8"))

    # Call LLM-based builder (policy summary + denial text -> DisputeReport dataclass)
    dispute_report = build_denial_aware_report(policy_payload, denial_text)

    # Attach simple metadata (same pattern as run_denial_summary.py)
    policy_id = policy_payload.get("policy_id") or policy_path.stem
    if denial_id is None:
        # Fallback: timestamped ID if UI doesn’t supply something better
        denial_id = f"denial_{int(time.time())}"

    dispute_report.policy_id = policy_id
    dispute_report.denial_id = denial_id

    # Decide where to write outputs
    output_dir = _resolve_dispute_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    base_name = f"{policy_id}__{denial_id}.dispute"

    json_out = output_dir / f"{base_name}.json"
    md_out = output_dir / f"{base_name}.md"

    # Persist JSON version of the dispute report
    dispute_dict = dispute_report.to_dict()
    json_out.write_text(
        json.dumps(dispute_dict, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Render and persist Markdown
    md_text = render_dispute_markdown(dispute_report)
    md_out.write_text(md_text, encoding="utf-8")

    return {
        "policy_id": policy_id,
        "denial_id": denial_id,
        "dispute_report": dispute_dict,
        "markdown": md_text,
        "artifacts": {
            "dispute_json": str(json_out),
            "dispute_markdown": str(md_out),
            "policy_summary_json": str(policy_path),
            "safe_mode": settings.safe_mode,
        },
    }
