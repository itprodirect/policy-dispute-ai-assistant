from __future__ import annotations

import re
from typing import Dict, List

from rich import print  # type: ignore[assignment]


UNKNOWN_SECTION_NAME = "UNKNOWN"


# --- Heading normalisation helpers -------------------------------------------------


def _collapse_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _canonical_key(raw: str) -> str:
    """
    Normalise a raw heading line into an uppercase key with simple punctuation
    normalisation so we can match aliases robustly.
    """
    text = _collapse_ws(raw)
    # normalise various dash types to a simple hyphen
    text = text.replace("–", "-").replace("—", "-")
    return text.upper()


HO3_HEADING_ALIASES: Dict[str, str] = {
    # Core global sections
    "DEFINITIONS": "DEFINITIONS",
    "DEFINITIONS USED IN THIS POLICY": "DEFINITIONS",
    "DEFINITIONS USED IN THIS POLICY SECTION I AND SECTION II": "DEFINITIONS",
    "SECTION I - EXCLUSIONS": "EXCLUSIONS",
    "SECTION I EXCLUSIONS": "EXCLUSIONS",
    "EXCLUSIONS": "EXCLUSIONS",
    "SECTION I - CONDITIONS": "CONDITIONS",
    "SECTION I CONDITIONS": "CONDITIONS",
    "CONDITIONS": "CONDITIONS",
    # Coverage blocks
    "COVERAGE A - DWELLING": "COVERAGE A - DWELLING",
    "COVERAGE B - OTHER STRUCTURES": "COVERAGE B - OTHER STRUCTURES",
    "COVERAGE C - PERSONAL PROPERTY": "COVERAGE C - PERSONAL PROPERTY",
    "COVERAGE D - LOSS OF USE": "COVERAGE D - LOSS OF USE",
}

SECTION_RE = re.compile(
    r"^SECTION\s+([IVX]+)\s*[-–—:]?\s*(.*)$",
    flags=re.IGNORECASE,
)

COVERAGE_RE = re.compile(
    r"^COVERAGE\s+([A-Z])\s*[-–—:]?\s*(.*)$",
    flags=re.IGNORECASE,
)

ALL_CAPS_HEADING_RE = re.compile(
    r"^[^a-z]*[A-Z][A-Z0-9\s,&()'/\-]*$"
)


def _normalize_heading(raw: str) -> str:
    """
    Convert the raw heading text from the PDF into a canonical section name
    suitable for our summaries (DEFINITIONS, EXCLUSIONS, COVERAGE A - DWELLING, etc.)
    """
    key = _canonical_key(raw)
    if not key:
        return UNKNOWN_SECTION_NAME

    # Exact alias match first
    if key in HO3_HEADING_ALIASES:
        return HO3_HEADING_ALIASES[key]

    # Pattern: SECTION I - EXCLUSIONS / CONDITIONS / PROPERTY COVERAGES, etc.
    m = SECTION_RE.match(key)
    if m:
        rest = _collapse_ws(m.group(2) or "").upper()
        if "EXCLUSIONS" in rest:
            return "EXCLUSIONS"
        if "CONDITIONS" in rest:
            return "CONDITIONS"
        if "PROPERTY COVERAGES" in rest:
            return "SECTION I - PROPERTY COVERAGES"
        # Fallback: keep the cleaned SECTION ... string
        return key

    # Pattern: COVERAGE A/B/C/D ...
    m = COVERAGE_RE.match(key)
    if m:
        letter = m.group(1).upper()
        rest = _collapse_ws(m.group(2) or "").upper()
        if rest:
            return f"COVERAGE {letter} - {rest}"
        return f"COVERAGE {letter}"

    # Fallback: just use the canonicalised uppercase text
    return key


def _looks_like_heading(line: str) -> bool:
    """
    Best-effort heuristic for HO3-style headings.

    We bias strongly toward known patterns (SECTION I, COVERAGE A, etc.)
    and short, all-caps lines without periods.
    """
    stripped = line.strip()
    if not stripped:
        return False

    # Explicit HO3 patterns first
    if SECTION_RE.match(stripped) or COVERAGE_RE.match(stripped):
        return True

    # Very short lines usually aren't headings
    if len(stripped) < 5:
        return False

    # Don't treat long paragraphs as headings
    if len(stripped) > 90:
        return False

    # If it contains lowercase letters, assume it's regular body text
    if re.search(r"[a-z]", stripped):
        return False

    # Avoid sentences / disclaimers which tend to have periods
    if "." in stripped:
        return False

    # Now demand an all-caps-ish pattern
    if not ALL_CAPS_HEADING_RE.match(stripped):
        return False

    # And keep word count modest (HEADINGS ARE LIKE THIS, not huge blocks)
    if len(stripped.split()) > 12:
        return False

    return True


# --- Main API ----------------------------------------------------------------------


def split_into_sections(text: str) -> Dict[str, str]:
    """
    Split a policy text blob into sections keyed by canonical section name.

    We keep anything before the first detected heading in an UNKNOWN section,
    and we always return UNKNOWN if it contains non-empty text.
    """
    lines = text.splitlines()

    sections: Dict[str, List[str]] = {}
    current_key = UNKNOWN_SECTION_NAME
    sections[current_key] = []

    for line in lines:
        if _looks_like_heading(line):
            heading = _normalize_heading(line)
            current_key = heading or UNKNOWN_SECTION_NAME
            if current_key not in sections:
                sections[current_key] = []
            # we don't keep the heading line itself in the body text;
            # it's already encoded as the key
            continue

        sections[current_key].append(line)

    # Convert list-of-lines to single strings, trimming empty ones
    merged: Dict[str, str] = {}
    for key, body_lines in sections.items():
        body = "\n".join(body_lines).strip()
        if body:
            merged[key] = body

    # UNKNOWN diagnostics
    total_len = sum(len(chunk) for chunk in merged.values())
    unknown_text = merged.get(UNKNOWN_SECTION_NAME, "")
    unknown_len = len(unknown_text)

    if total_len > 0:
        frac = unknown_len / total_len
        if frac >= 0.30:
            print(
                f"[yellow][sectioning] WARNING: UNKNOWN section contains "
                f"{frac:.0%} of policy text ({unknown_len} / {total_len} chars).[/yellow]"
            )
            preview = _collapse_ws(unknown_text[:400])
            if preview:
                print(
                    f"[yellow][sectioning] UNKNOWN preview: {preview}[/yellow]"
                )

    # Also log a quick summary of sections we detected
    section_names = ", ".join(sorted(merged.keys()))
    print(f"[green][sectioning] Detected sections:[/green] {section_names}")

    return merged
