import re
from typing import Dict

SECTION_LABELS = [
    "DECLARATIONS",
    "COVERAGE A",
    "COVERAGE B",
    "COVERAGE C",
    "COVERAGE D",
    "EXCLUSIONS",
    "CONDITIONS",
    "DEFINITIONS",
    "ENDORSEMENTS",
    "DENIAL REASONS",
]


def split_into_sections(text: str) -> Dict[str, str]:
    """
    Very rough heuristic: look for headings in all caps.
    You will absolutely refine this later with better rules per carrier/form.
    """
    # Normalize line breaks
    lines = [l.strip() for l in text.splitlines()]
    # Join back for regex slicing
    joined = "\n".join(lines)

    # Build pattern to capture sections
    # Example: "\nDECLARATIONS\n" as anchors
    pattern = "(" + "|".join([re.escape(label)
                              for label in SECTION_LABELS]) + ")"
    # Split but keep the delimiters
    parts = re.split(pattern, joined)

    sections: Dict[str, str] = {}
    current_label = "UNKNOWN"
    buffer: list[str] = []

    def flush():
        nonlocal buffer, current_label
        if buffer:
            sections[current_label] = "\n".join(buffer).strip()
            buffer = []

    for part in parts:
        if part in SECTION_LABELS:
            flush()
            current_label = part
        else:
            buffer.append(part)

    flush()
    return sections
