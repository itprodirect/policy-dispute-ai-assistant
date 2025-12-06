import json
from pathlib import Path
from typing import Iterable, List, Dict

import argparse
from rich import print

from .pdf_loader import load_pdf_text
from .sectioning import split_into_sections
from .schemas import SectionSummary  # for type hints only


def classify_section_role(section_name: str, raw_text: str) -> str:
    """
    Heuristic tag for whether a section is substantive policy language
    vs meta/administrative stuff (sample disclaimers, regulator notices, etc.).
    """
    name_l = (section_name or "").lower()
    text_l = (raw_text or "").lower()

    # Strong signals this is NOT the actual operative policy language
    meta_text_markers = [
        "this is only a sample",
        "sample of a base policy",
        "sample policy",
        "not an actual policy",
        "not part of your policy",
        "for illustration only",
        "for informational purposes only",
    ]

    meta_regulatory_markers = [
        "office of insurance regulation",
        "florida office of insurance regulation",
        "texas department of insurance",
        "serff",
    ]

    meta_copyright_markers = [
        "copyright",
        "iso properties",
        "insurance services office",
    ]

    # 1) UNKNOWN + obvious meta language in the text (your USAA sample case)
    if "unknown" in name_l and (
        any(m in text_l for m in meta_text_markers)
        or any(m in text_l for m in meta_regulatory_markers)
        or any(m in text_l for m in meta_copyright_markers)
    ):
        return "meta"

    # 2) Explicitly meta-sounding section names
    if any(k in name_l for k in ["sample policy", "office of insurance regulation"]):
        return "meta"

    # 3) Form identifiers that look like headers, *when* the text is header-y
    #    (HO 00 03..., TRUE HO 03..., SGP HO 03..., HO-208TX, etc.)
    form_like = [
        "ho 00 03",
        "true ho 03",
        "sgp ho 03",
        "ho-",
        "ho ",
    ]
    if any(name_l.startswith(prefix) for prefix in form_like):
        if any(m in text_l for m in meta_copyright_markers) or any(
            m in text_l for m in meta_text_markers
        ):
            return "meta"

    # 4) Generic meta markers in the text
    if any(m in text_l for m in meta_text_markers + meta_regulatory_markers):
        return "meta"

    # Default assumption: this is substantive policy language
    return "substantive"


# --- Summarizer import with fallbacks ---------------------------------------
# Prefer a dedicated summarizer.py if you ever add one; otherwise use
# the current summarizer_frontier implementation.

try:
    # if you later add src/summarizer.py with summarize_section(), this will win
    from .summarizer import summarize_section  # type: ignore
except ImportError:
    try:
        # current project setup
        from .summarizer_frontier import summarize_section  # type: ignore
    except ImportError:
        # last-resort alias if you rename the function in summarizer_frontier
        from .summarizer_frontier import (  # type: ignore
            summarize_policy_section as summarize_section,
        )


DATA_PROCESSED_DIR = Path("data/processed")


def summarize_policy(pdf_path: Path) -> Path:
    """
    End-to-end pipeline for a single policy PDF:
    - load text
    - split into sections (dict: section_name -> section_text)
    - summarize each section via LLM
    - write JSON to data/processed/<stem>.json
    """
    print(f"\n[bold]Loading policy:[/bold] {pdf_path}")
    text = load_pdf_text(pdf_path)

    print("Splitting into sections...")
    sections: Dict[str, str] = split_into_sections(text)

    results: List[dict] = []
    for section_name, section_text in sections.items():
        print(f"Summarizing section: [cyan]{section_name}[/cyan]")

        section_summary: SectionSummary = summarize_section(
            section_name, section_text
        )

        section_dict = section_summary.to_dict()
        section_dict["raw_text"] = section_text
        section_dict["section_role"] = classify_section_role(
            section_name, section_text)
        results.append(section_dict)

    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_PROCESSED_DIR / f"{pdf_path.stem}.json"

    payload = {
        "policy_id": pdf_path.stem,
        "policy_path": str(pdf_path),
        "sections": results,
    }

    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Saved summary to: [green]{out_path}[/green]")

    return out_path


def iter_input_files(paths: Iterable[str], pattern: str = "*.pdf") -> Iterable[Path]:
    """
    Expand CLI inputs into actual PDF files.

    - If an argument is a file -> yield it.
    - If an argument is a directory -> yield all files matching pattern inside it.
    - If path doesn't exist -> warn and skip.
    """
    for raw in paths:
        p = Path(raw)
        if p.is_file():
            yield p
        elif p.is_dir():
            for pdf in sorted(p.glob(pattern)):
                if pdf.is_file():
                    yield pdf
        else:
            print(
                f"[yellow]Warning:[/yellow] path does not exist, skipping: {raw}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the baseline policy summarization pipeline over one or more "
            "policy PDFs (files and/or directories)."
        )
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="PDF files and/or directories containing PDFs.",
    )
    parser.add_argument(
        "--pattern",
        default="*.pdf",
        help="Glob pattern to use when a path is a directory (default: *.pdf).",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help=(
            "If set, skip any input where data/processed/<stem>.json already exists. "
            "Useful when re-running on a large folder."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    files = list(iter_input_files(args.paths, args.pattern))
    if not files:
        print("[red]No input PDFs found. Nothing to do.[/red]")
        return

    print(f"[bold]Found {len(files)} PDF(s) to process.[/bold]")

    processed_count = 0
    for pdf_path in files:
        out_path = DATA_PROCESSED_DIR / f"{pdf_path.stem}.json"
        if args.skip_existing and out_path.exists():
            print(
                f"[yellow]Skipping {pdf_path} because output already exists:[/yellow] {out_path}"
            )
            continue

        try:
            summarize_policy(pdf_path)
            processed_count += 1
        except Exception as e:
            # Don't crash the whole batch because of one bad file.
            print(f"[red]Error processing {pdf_path}:[/red] {e}")

    print(
        f"\n[bold]Done.[/bold] Successfully processed {processed_count} file(s).")


if __name__ == "__main__":
    main()
