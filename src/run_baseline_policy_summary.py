import json
from pathlib import Path

from rich import print

from .pdf_loader import load_pdf_text
from .sectioning import split_into_sections
from .summarizer_frontier import summarize_section
from .schemas import PolicySummary
from .report_builder import build_and_save_markdown


def summarize_policy(pdf_path: str, policy_id: str | None = None) -> PolicySummary:
    pdf_path = Path(pdf_path)
    if policy_id is None:
        policy_id = pdf_path.stem

    print(f"[bold cyan]Loading policy:[/bold cyan] {pdf_path}")
    text = load_pdf_text(pdf_path)

    print("[bold cyan]Splitting into sections...[/bold cyan]")
    sections = split_into_sections(text)

    section_summaries = []
    for name, content in sections.items():
        if not content.strip():
            continue
        print(f"[bold yellow]Summarizing section:[/bold yellow] {name}")
        summary = summarize_section(name, content)
        section_summaries.append(summary)

    return PolicySummary(policy_id=policy_id, sections=section_summaries)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Baseline policy summarizer")
    parser.add_argument("pdf", type=str, help="Path to the policy PDF")
    parser.add_argument(
        "--out",
        type=str,
        default=None,
        help="Output JSON file (default: data/processed/<policy_id>.json)",
    )

    args = parser.parse_args()
    policy_path = args.pdf

    summary = summarize_policy(policy_path)

    out_path = args.out
    if out_path is None:
        out_path = Path("data/processed") / f"{summary.policy_id}.json"
    else:
        out_path = Path(out_path)

    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary.to_dict(), f, indent=2, ensure_ascii=False)

    print(f"[bold green]Saved summary to:[/bold green] {out_path}")

    # NEW: build Markdown report next to the JSON
    md_path = build_and_save_markdown(out_path)
    print(f"[bold green]Saved Markdown report to:[/bold green] {md_path}")


if __name__ == "__main__":
    main()
