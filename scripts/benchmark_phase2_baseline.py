from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.citation_linking import find_section_for_citation
from src.report_builder import render_dispute_markdown
from src.schemas import Angle, ConfidenceBlock, DisputeReport, Point


DEMO_JSON_PATH = ROOT / "assets" / "demo" / "demo.json"
DEMO_MD_PATH = ROOT / "assets" / "demo" / "demo.report.md"
DEMO_SECTION_TEXT_PATH = ROOT / "assets" / "demo" / "section_text.json"


def _round_seconds(seconds: float) -> float:
    return round(seconds, 4)


@contextmanager
def _timed(stage_name: str, timings: List[Dict[str, Any]]) -> Iterator[None]:
    start = time.perf_counter()
    try:
        yield
    finally:
        timings.append(
            {
                "stage": stage_name,
                "wall_clock_seconds": _round_seconds(time.perf_counter() - start),
            }
        )


def _read_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object at {path}")
    return payload


def _point_from_dict(raw: Any) -> Point:
    if isinstance(raw, dict):
        return Point(
            text=str(raw.get("text", "") or "").strip(),
            citation=(
                str(raw.get("citation", "") or "").strip()
                if raw.get("citation")
                else None
            ),
        )
    return Point(text=str(raw or "").strip())


def _angle_from_dict(raw: Any) -> Angle:
    if isinstance(raw, dict):
        citations = [
            str(citation).strip()
            for citation in raw.get("citations", []) or []
            if str(citation).strip()
        ]
        return Angle(text=str(raw.get("text", "") or "").strip(), citations=citations)
    return Angle(text=str(raw or "").strip())


def _to_dispute_report(payload: Dict[str, Any]) -> DisputeReport:
    confidence_raw = payload.get("confidence") or {}
    if not isinstance(confidence_raw, dict):
        confidence_raw = {}

    score = confidence_raw.get("score")
    confidence = ConfidenceBlock(
        score=float(score) if isinstance(score, (int, float)) else None,
        notes=str(confidence_raw.get("notes", "") or ""),
        verify_clauses=[
            str(clause).strip()
            for clause in confidence_raw.get("verify_clauses", []) or []
            if str(clause).strip()
        ],
    )

    return DisputeReport(
        policy_id=str(payload.get("policy_id", "") or ""),
        denial_id=str(payload.get("denial_id", "") or ""),
        plain_summary=str(payload.get("plain_summary", "") or ""),
        coverage_highlights=[
            _point_from_dict(item)
            for item in payload.get("coverage_highlights", []) or []
        ],
        exclusions_limitations=[
            _point_from_dict(item)
            for item in payload.get("exclusions_limitations", []) or []
        ],
        denial_reasons=[
            _point_from_dict(item) for item in payload.get("denial_reasons", []) or []
        ],
        dispute_angles=[
            _angle_from_dict(item) for item in payload.get("dispute_angles", []) or []
        ],
        missing_info=[
            str(item).strip()
            for item in payload.get("missing_info", []) or []
            if str(item).strip()
        ],
        confidence=confidence,
    )


def _iter_demo_citations(report: Dict[str, Any]) -> Iterable[str]:
    for field in ("coverage_highlights", "exclusions_limitations", "denial_reasons"):
        for item in report.get(field, []) or []:
            citation = str(item.get("citation", "") or "").strip()
            if citation:
                yield citation

    for angle in report.get("dispute_angles", []) or []:
        for citation in angle.get("citations", []) or []:
            citation = str(citation).strip()
            if citation:
                yield citation


def _environment() -> Dict[str, Any]:
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "working_directory": str(ROOT),
    }


def benchmark_demo_bundle() -> Dict[str, Any]:
    timings: List[Dict[str, Any]] = []
    start = time.perf_counter()

    with _timed("load_demo_assets", timings):
        demo_report = _read_json(DEMO_JSON_PATH)
        demo_markdown = DEMO_MD_PATH.read_text(encoding="utf-8")
        section_map = _read_json(DEMO_SECTION_TEXT_PATH)

    with _timed("build_dispute_report_object", timings):
        dispute_report = _to_dispute_report(demo_report)

    with _timed("render_dispute_markdown", timings):
        rendered_markdown = render_dispute_markdown(dispute_report)

    with _timed("link_demo_citations", timings):
        citations = list(_iter_demo_citations(demo_report))
        linked_count = sum(
            1
            for citation in citations
            if find_section_for_citation(citation, section_map) is not None
        )

    total_wall_clock_seconds = _round_seconds(time.perf_counter() - start)

    return {
        "benchmark": "phase2_baseline",
        "mode": "demo_bundle_offline",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "api_calls_made": False,
        "inputs": {
            "demo_json": str(DEMO_JSON_PATH.relative_to(ROOT)),
            "demo_markdown": str(DEMO_MD_PATH.relative_to(ROOT)),
            "demo_section_text": str(DEMO_SECTION_TEXT_PATH.relative_to(ROOT)),
        },
        "environment": _environment(),
        "total_wall_clock_seconds": total_wall_clock_seconds,
        "stage_timings": timings,
        "counts": {
            "coverage_highlights": len(dispute_report.coverage_highlights),
            "exclusions_limitations": len(dispute_report.exclusions_limitations),
            "denial_reasons": len(dispute_report.denial_reasons),
            "dispute_angles": len(dispute_report.dispute_angles),
            "missing_info": len(dispute_report.missing_info),
            "citations": len(citations),
            "linked_citations": linked_count,
            "demo_markdown_chars": len(demo_markdown),
            "rendered_markdown_chars": len(rendered_markdown),
            "section_text_entries": len(section_map),
        },
        "token_usage": None,
        "cost_estimate": None,
        "limitations": [
            "Offline demo-bundle mode does not run PDF extraction, sectioning, OpenAI calls, or live dispute generation.",
            "Token usage and cost are not collected because the current local pipeline does not expose them outside optional W&B telemetry.",
        ],
    }


def benchmark_live_pipeline(policy_pdf: Path, denial_text_path: Path) -> Dict[str, Any]:
    from src.demo_api import run_dispute_analysis
    from src.run_baseline_policy_summary import summarize_policy

    timings: List[Dict[str, Any]] = []
    start = time.perf_counter()

    if not policy_pdf.is_file():
        raise FileNotFoundError(f"Policy PDF not found: {policy_pdf}")
    if not denial_text_path.is_file():
        raise FileNotFoundError(f"Denial text file not found: {denial_text_path}")

    with _timed("policy_summary_pipeline", timings):
        summary_json_path = summarize_policy(policy_pdf)

    with _timed("load_denial_text", timings):
        denial_text = denial_text_path.read_text(encoding="utf-8", errors="ignore")

    with _timed("dispute_analysis_pipeline", timings):
        dispute_result = run_dispute_analysis(
            summary_json_path,
            denial_text,
            denial_id=denial_text_path.stem,
        )

    total_wall_clock_seconds = _round_seconds(time.perf_counter() - start)

    return {
        "benchmark": "phase2_baseline",
        "mode": "live_pipeline",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "api_calls_made": True,
        "inputs": {
            "policy_pdf": str(policy_pdf),
            "denial_text": str(denial_text_path),
        },
        "environment": _environment(),
        "total_wall_clock_seconds": total_wall_clock_seconds,
        "stage_timings": timings,
        "artifacts": {
            "policy_summary_json": str(summary_json_path),
            **(dispute_result.get("artifacts") or {}),
        },
        "token_usage": None,
        "cost_estimate": None,
        "limitations": [
            "Live mode measures current end-to-end policy summary and dispute analysis calls, but does not change pipeline behavior.",
            "Token usage and cost are not collected because the current local pipeline does not expose them outside optional W&B telemetry.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Phase 2 before-state benchmark harness."
    )
    parser.add_argument(
        "--mode",
        choices=("demo", "live"),
        default="demo",
        help="Benchmark mode. 'demo' is deterministic and makes no API calls.",
    )
    parser.add_argument(
        "--policy-pdf",
        type=Path,
        help="Policy PDF for --mode live. Requires OPENAI_API_KEY.",
    )
    parser.add_argument(
        "--denial-text",
        type=Path,
        help="Denial letter .txt file for --mode live. Requires OPENAI_API_KEY.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write benchmark metrics JSON.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.mode == "demo":
        result = benchmark_demo_bundle()
    else:
        if args.policy_pdf is None or args.denial_text is None:
            raise SystemExit("--mode live requires --policy-pdf and --denial-text")
        result = benchmark_live_pipeline(args.policy_pdf, args.denial_text)

    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    print(rendered)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
