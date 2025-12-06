# src/report_builder.py
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class PolicyReport:
    policy_name: str
    source_path: str
    num_sections: int
    num_unknown_sections: int
    sections: List[Dict[str, Any]]


def build_policy_report(summary: Dict[str, Any]) -> PolicyReport:
    sections = summary.get("sections", []) or []
    num_sections = len(sections)

    def get_name(s: Dict[str, Any]) -> str:
        return (s.get("name") or s.get("section_name") or "").strip()

    num_unknown = sum(1 for s in sections if get_name(s).upper() == "UNKNOWN")

    policy_name = (
        summary.get("policy_name")
        or Path(summary.get("policy_path", "")).name
        or "Unknown policy"
    )

    return PolicyReport(
        policy_name=policy_name,
        source_path=summary.get("policy_path", ""),
        num_sections=num_sections,
        num_unknown_sections=num_unknown,
        sections=sections,
    )


def render_markdown(report: PolicyReport) -> str:
    lines: List[str] = []

    lines.append(f"# Policy report: {report.policy_name}")
    lines.append("")

    if report.source_path:
        lines.append(f"- Source file: `{report.source_path}`")
    lines.append(f"- Total sections: {report.num_sections}")
    lines.append(f"- Sections under UNKNOWN: {report.num_unknown_sections}")
    lines.append("")

    for section in report.sections:
        name = (
            section.get("name")
            or section.get("section_name")
            or "UNKNOWN"
        )
        summary = (
            section.get("summary_overall")
            or section.get("summary")
            or ""
        )

        lines.append(f"## {name}")
        lines.append("")
        if summary:
            lines.append(summary.strip())
        else:
            lines.append("_No summary for this section._")
        lines.append("")

        angles = section.get("dispute_angles_possible") or []
        if angles:
            lines.append("**Potential dispute angles:**")
            lines.append("")
            for a in angles:
                lines.append(f"- {a}")
            lines.append("")

    return "\n".join(lines)


def build_and_save_markdown(summary_json_path: Path) -> Path:
    """
    Given the path to a PolicySummary JSON file, build and save a Markdown report
    next to it (same name with `.report.md` suffix).
    """
    data = json.loads(summary_json_path.read_text(encoding="utf-8"))
    report = build_policy_report(data)
    markdown = render_markdown(report)

    md_path = summary_json_path.with_suffix(".report.md")
    md_path.write_text(markdown, encoding="utf-8")

    if report.num_sections and report.num_unknown_sections / report.num_sections > 0.3:
        print(
            f"[WARN] {report.num_unknown_sections}/{report.num_sections} sections "
            "are UNKNOWN. Section detection may need tuning."
        )

    return md_path
