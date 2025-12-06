from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Iterable

from rich import print


@dataclass
class PolicyReport:
    policy_name: str
    source_path: str
    num_sections: int
    num_unknown_sections: int
    num_meta_sections: int
    sections_substantive: List[Dict[str, Any]]
    sections_meta: List[Dict[str, Any]]


def build_policy_report(summary_data: Dict[str, Any]) -> PolicyReport:
    """Normalize raw JSON from the summarizer into a PolicyReport object."""
    policy_name = summary_data.get("policy_id") or "<unknown_policy>"
    source_path = summary_data.get("policy_path") or ""

    sections: List[Dict[str, Any]] = summary_data.get("sections", [])
    num_sections = len(sections)

    num_unknown_sections = 0
    sections_meta: List[Dict[str, Any]] = []
    sections_substantive: List[Dict[str, Any]] = []

    for s in sections:
        name = (s.get("section_name") or "").strip()
        role = (s.get("section_role") or "substantive").lower()

        if name.upper().startswith("UNKNOWN"):
            num_unknown_sections += 1

        if role == "meta":
            sections_meta.append(s)
        else:
            sections_substantive.append(s)

    num_meta_sections = len(sections_meta)

    return PolicyReport(
        policy_name=policy_name,
        source_path=source_path,
        num_sections=num_sections,
        num_unknown_sections=num_unknown_sections,
        num_meta_sections=num_meta_sections,
        sections_substantive=sections_substantive,
        sections_meta=sections_meta,
    )


def _render_list_block(title: str, items: List[str]) -> str:
    if not items:
        return ""
    lines = [f"**{title}**"]
    for item in items:
        lines.append(f"- {item}")
    lines.append("")  # blank line after block
    return "\n".join(lines)


def render_section_markdown(section: Dict[str, Any]) -> str:
    """Render a single section (already filtered to substantive) to Markdown."""
    name = section.get("section_name") or "UNKNOWN SECTION"
    summary = section.get("summary_overall") or ""

    key_cov = section.get("key_coverages") or []
    key_exc = section.get("key_exclusions") or []
    conds = section.get("conditions_notable") or []
    disputes = section.get("dispute_angles_possible") or []

    parts: List[str] = []
    parts.append(f"### {name}")
    parts.append("")
    if summary:
        parts.append(summary.strip())
        parts.append("")

    parts.append(_render_list_block("Key coverages", key_cov))
    parts.append(_render_list_block("Key exclusions", key_exc))
    parts.append(_render_list_block("Notable conditions / duties", conds))
    parts.append(_render_list_block("Potential dispute angles", disputes))

    # Remove any empty chunks
    parts = [p for p in parts if p.strip() != ""]
    parts.append("")  # trailing blank line for spacing
    return "\n".join(parts)


def render_markdown(report: PolicyReport) -> str:
    """Render the whole policy report to Markdown."""
    header_lines = [
        f"# Policy summary – {report.policy_name}",
        "",
        f"- Source file: `{report.source_path}`" if report.source_path else "",
        f"- Total sections: {report.num_sections}",
        f"- UNKNOWN sections: {report.num_unknown_sections}",
        f"- Meta / non-substantive sections: {report.num_meta_sections}",
        "",
        "> **Framing:** This is an AI-generated summary of policy language only.",
        "> It is *not* legal advice and does not create coverage or rights.",
        "",
    ]

    header_lines = [l for l in header_lines if l != ""]

    body_lines: List[str] = []
    body_lines.extend(header_lines)

    # Substantive / claim-facing sections
    body_lines.append("## Substantive sections (claim-facing)")
    body_lines.append("")
    if not report.sections_substantive:
        body_lines.append("_No substantive sections detected._")
        body_lines.append("")
    else:
        for s in report.sections_substantive:
            body_lines.append(render_section_markdown(s))

    # Meta sections appendix
    if report.sections_meta:
        body_lines.append(
            "## Meta / regulatory / boilerplate sections (not analyzed for coverage)"
        )
        body_lines.append("")
        for s in report.sections_meta:
            name = s.get("section_name") or "UNKNOWN"
            body_lines.append(f"- {name}")
        body_lines.append("")

    return "\n".join(body_lines)


def generate_report_for_summary(summary_json_path: Path) -> Path:
    """Load a single <policy>.json and emit a <policy>.report.md file next to it."""
    print(f"[bold]Building report from:[/bold] {summary_json_path}")
    data = json.loads(summary_json_path.read_text(encoding="utf-8"))
    report = build_policy_report(data)
    markdown = render_markdown(report)

    md_path = summary_json_path.with_suffix(".report.md")
    md_path.write_text(markdown, encoding="utf-8")
    print(f"[green]Wrote report:[/green] {md_path}")

    if report.num_sections and report.num_unknown_sections / report.num_sections > 0.3:
        print(
            f"[yellow][WARN][/yellow] {report.num_unknown_sections}/{report.num_sections} sections "
            "are UNKNOWN. Section detection may need tuning."
        )

    return md_path


def iter_input_files(paths: Iterable[str], pattern: str = "*.json") -> Iterable[Path]:
    """
    Expand CLI inputs into actual JSON files.

    - File path -> yield as-is
    - Directory  -> glob for pattern (default *.json)
    - Nonexistent path -> warn and skip
    """
    for raw in paths:
        p = Path(raw)
        if p.is_file():
            if p.suffix.lower() == ".json":
                yield p
        elif p.is_dir():
            for json_path in sorted(p.glob(pattern)):
                if json_path.is_file() and json_path.suffix.lower() == ".json":
                    yield json_path
        else:
            print(
                f"[yellow]Warning:[/yellow] path does not exist, skipping: {raw}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build claim-facing Markdown reports from policy summary JSON files."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="One or more summary JSON files and/or directories containing JSON files.",
    )
    parser.add_argument(
        "--pattern",
        default="*.json",
        help="Glob pattern when expanding directories (default: *.json).",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip any JSON where the corresponding .report.md already exists.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    files = list(iter_input_files(args.paths, args.pattern))

    if not files:
        print("[red]No summary JSON files found. Nothing to do.[/red]")
        return

    print(f"[bold]Found {len(files)} summary JSON file(s) to process.[/bold]")

    count = 0
    for json_path in files:
        out_path = json_path.with_suffix(".report.md")
        if args.skip_existing and out_path.exists():
            print(
                f"[yellow]Skipping (report already exists):[/yellow] {json_path}")
            continue
        try:
            generate_report_for_summary(json_path)
            count += 1
        except Exception as e:
            print(f"[red]Error building report for {json_path}:[/red] {e}")

    print(f"[bold]Done.[/bold] Built {count} report file(s).")


if __name__ == "__main__":
    main()
