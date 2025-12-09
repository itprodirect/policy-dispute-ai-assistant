from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

from .run_baseline_policy_summary import summarize_policy
from .report_builder import build_policy_report, render_markdown
from .config import get_settings


UPLOAD_DIR = Path("data/uploads")


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
