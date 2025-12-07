from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional


# --- Existing section-level summaries ----------------------------------------


@dataclass
class SectionSummary:
    section_name: str
    summary_overall: str
    key_coverages: List[str]
    key_exclusions: List[str]
    conditions_notable: List[str]
    dispute_angles_possible: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PolicySummary:
    policy_id: str
    sections: List[SectionSummary]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# --- New dispute-level summaries (policy + denial) ---------------------------


@dataclass
class Point:
    """
    Simple text point with an optional citation label
    (e.g. section name, page reference).
    """
    text: str
    citation: Optional[str] = None


@dataclass
class Angle:
    """
    High-level dispute angle with optional list of citations.
    """
    text: str
    citations: List[str] = field(default_factory=list)


@dataclass
class ConfidenceBlock:
    """
    Lightweight confidence / verification metadata.
    """
    score: Optional[float] = None  # 0–1, optional
    notes: str = ""
    verify_clauses: List[str] = field(default_factory=list)


@dataclass
class DisputeReport:
    """
    Canonical A–G style dispute report for a policy + denial pair.

    This is what UI, CLI, and (later) voice mode should consume.
    """
    # Optional metadata about the case
    policy_id: Optional[str] = None
    denial_id: Optional[str] = None

    # A–G sections
    plain_summary: str = ""  # A
    coverage_highlights: List[Point] = field(default_factory=list)        # B
    exclusions_limitations: List[Point] = field(default_factory=list)     # C
    denial_reasons: List[Point] = field(default_factory=list)             # D
    dispute_angles: List[Angle] = field(default_factory=list)             # E
    missing_info: List[str] = field(default_factory=list)                 # F
    confidence: ConfidenceBlock = field(default_factory=ConfidenceBlock)  # G

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
