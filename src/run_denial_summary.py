from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich import print

from .summarizer_frontier import build_denial_aware_report
from .schemas import DisputeReport
from .report_builder import render_dispute_markdown

DATA_PROCESSED_DIR = Path("data/processed")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a dispute-focused A–G report from a policy summary JSON "
            "and a denial letter text file."
        )
    )
    parser.add_argument(
        "policy_summary",
        help="Path to policy summary JSON (output of run_baseline_policy_summary.py).",
    )
    parser.add_argument(
        "denial_text",
        help="Path to denial letter .txt file (v0 uses plain text, not PDF).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    policy_path = Path(args.policy_summary)
    denial_path = Path(args.denial_text)

    if not policy_path.is_file():
        print(f"[red]Policy summary JSON not found:[/red] {policy_path}")
        return

    if not denial_path.is_file():
        print(f"[red]Denial text file not found:[/red] {denial_path}")
        return

    print(f"[bold]Loading policy summary:[/bold] {policy_path}")
    policy_payload = json.loads(policy_path.read_text(encoding="utf-8"))

    print(f"[bold]Loading denial letter text:[/bold] {denial_path}")
    denial_text = denial_path.read_text(encoding="utf-8", errors="ignore")

    print("[bold]Calling LLM to build denial-aware dispute report...[/bold]")
    dispute_report: DisputeReport = build_denial_aware_report(
        policy_payload, denial_text
    )

    # Attach simple metadata
    policy_id = policy_payload.get("policy_id") or policy_path.stem
    denial_id = denial_path.stem
    dispute_report.policy_id = policy_id
    dispute_report.denial_id = denial_id

    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    base_name = f"{policy_id}__{denial_id}.dispute"

    json_out = DATA_PROCESSED_DIR / f"{base_name}.json"
    md_out = DATA_PROCESSED_DIR / f"{base_name}.md"

    json_out.write_text(
        json.dumps(dispute_report.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"[green]Wrote dispute JSON:[/green] {json_out}")

    md_text = render_dispute_markdown(dispute_report)
    md_out.write_text(md_text, encoding="utf-8")
    print(f"[green]Wrote dispute Markdown:[/green] {md_out}")

    print("[bold]Done.[/bold]")


if __name__ == "__main__":
    main()
