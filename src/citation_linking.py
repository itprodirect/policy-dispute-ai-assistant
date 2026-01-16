"""
Citation linking module for Phase 1 in-memory citation linking.

Provides functions to:
- Build a section text map from raw policy sections
- Match citations from A-G reports to section text
- Retrieve display data for UI rendering of clickable citations
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


# Section name to exclude from the map by default
EXCLUDED_SECTIONS = {"UNKNOWN"}


def _normalize_key(text: str) -> str:
    """
    Normalize a section name or citation for matching.

    - Strips whitespace
    - Converts to uppercase
    - Normalizes dash types (en-dash, em-dash) to hyphen
    - Collapses multiple spaces
    """
    if not text:
        return ""

    # Normalize dash types
    normalized = text.replace("–", "-").replace("—", "-")
    # Collapse whitespace and strip
    normalized = re.sub(r"\s+", " ", normalized).strip()
    # Uppercase for comparison
    return normalized.upper()


def build_section_text_map(raw_sections: Dict[str, str]) -> Dict[str, str]:
    """
    Build a section text map from raw policy sections.

    Args:
        raw_sections: Dict mapping section names to their full text content
                     (as returned by sectioning.split_into_sections())

    Returns:
        Dict mapping section names to text, excluding UNKNOWN sections
    """
    if not raw_sections:
        return {}

    section_map: Dict[str, str] = {}

    for section_name, section_text in raw_sections.items():
        # Skip excluded sections
        if section_name in EXCLUDED_SECTIONS:
            continue

        # Preserve the original section name as key, with full text
        section_map[section_name] = section_text

    return section_map


def find_section_for_citation(
    citation: Optional[str],
    section_map: Dict[str, str],
) -> Optional[Dict[str, Any]]:
    """
    Find the section that matches a citation string.

    Supports:
    - Exact matches (case-insensitive)
    - Partial matches (e.g., "Coverage A" matches "COVERAGE A - DWELLING")
    - "Section I - Exclusions" style citations matching "EXCLUSIONS"

    Args:
        citation: The citation string from an A-G report point
        section_map: Dict mapping section names to text

    Returns:
        Dict with section_name and section_text if found, None otherwise
    """
    if not citation or not section_map:
        return None

    normalized_citation = _normalize_key(citation)
    if not normalized_citation:
        return None

    # Build a lookup dict with normalized keys
    normalized_map: Dict[str, str] = {}
    for section_name in section_map:
        normalized_map[_normalize_key(section_name)] = section_name

    # 1. Try exact match first
    if normalized_citation in normalized_map:
        original_name = normalized_map[normalized_citation]
        return {
            "section_name": original_name,
            "section_text": section_map[original_name],
        }

    # 2. Try partial match - citation is prefix of section name
    for norm_key, original_name in normalized_map.items():
        if norm_key.startswith(normalized_citation):
            return {
                "section_name": original_name,
                "section_text": section_map[original_name],
            }

    # 3. Try partial match - section name contains citation
    for norm_key, original_name in normalized_map.items():
        if normalized_citation in norm_key:
            return {
                "section_name": original_name,
                "section_text": section_map[original_name],
            }

    # 4. Handle "Section I - X" style citations
    # Extract the meaningful part after "SECTION I/II - "
    section_pattern = re.match(
        r"^SECTION\s+[IVX]+\s*[-–—]?\s*(.+)$",
        normalized_citation,
        re.IGNORECASE,
    )
    if section_pattern:
        extracted = section_pattern.group(1).strip().upper()
        if extracted:
            # Try to find a section that matches the extracted part
            for norm_key, original_name in normalized_map.items():
                if extracted in norm_key or norm_key == extracted:
                    return {
                        "section_name": original_name,
                        "section_text": section_map[original_name],
                    }

    # No match found
    return None


def get_citation_display_data(
    point: Dict[str, Any],
    section_map: Dict[str, str],
) -> Dict[str, Any]:
    """
    Get display data for a Point's citation for UI rendering.

    Args:
        point: A Point dict with 'text' and optional 'citation' fields
        section_map: Dict mapping section names to text

    Returns:
        Dict with:
        - point_text: The point's text
        - citation_text: The raw citation string (if any)
        - has_linkable_citation: True if citation matches a section
        - section_name: Matched section name (if linkable)
        - section_text: Full section text (if linkable)
    """
    point_text = str(point.get("text", "")).strip()
    citation = point.get("citation")
    citation_text = str(citation).strip() if citation else None

    result: Dict[str, Any] = {
        "point_text": point_text,
        "citation_text": citation_text,
        "has_linkable_citation": False,
        "section_name": None,
        "section_text": None,
    }

    if not citation_text:
        return result

    # Try to find matching section
    match = find_section_for_citation(citation_text, section_map)

    if match:
        result["has_linkable_citation"] = True
        result["section_name"] = match["section_name"]
        result["section_text"] = match["section_text"]

    return result


def get_angle_citation_display_data(
    angle: Dict[str, Any],
    section_map: Dict[str, str],
) -> Dict[str, Any]:
    """
    Get display data for an Angle's citations (multiple) for UI rendering.

    Args:
        angle: An Angle dict with 'text' and 'citations' (list) fields
        section_map: Dict mapping section names to text

    Returns:
        Dict with:
        - angle_text: The angle's text
        - linked_citations: List of matched citation data
        - unlinked_citations: List of citation strings that didn't match
    """
    angle_text = str(angle.get("text", "")).strip()
    citations = angle.get("citations") or []

    linked_citations: List[Dict[str, Any]] = []
    unlinked_citations: List[str] = []

    for citation in citations:
        citation_str = str(citation).strip() if citation else ""
        if not citation_str:
            continue

        match = find_section_for_citation(citation_str, section_map)

        if match:
            linked_citations.append({
                "citation_text": citation_str,
                "section_name": match["section_name"],
                "section_text": match["section_text"],
            })
        else:
            unlinked_citations.append(citation_str)

    return {
        "angle_text": angle_text,
        "linked_citations": linked_citations,
        "unlinked_citations": unlinked_citations,
    }


def create_session_section_map(
    policy_result: Dict[str, Any],
    raw_sections: Dict[str, str],
) -> Dict[str, str]:
    """
    Create a section map suitable for storing in session state.

    This combines information from the policy_result (which has summaries)
    with the raw_sections (which has full text) to create a map that
    can be used for citation linking.

    Args:
        policy_result: The result from run_policy_analysis() with
                      sections_substantive and sections_meta lists
        raw_sections: Dict mapping section names to full text

    Returns:
        Dict mapping section names to full text, filtered to sections
        that appear in the policy_result
    """
    # Get section names from policy_result
    section_names: set[str] = set()

    for section in policy_result.get("sections_substantive", []) or []:
        name = section.get("section_name")
        if name:
            section_names.add(name)

    for section in policy_result.get("sections_meta", []) or []:
        name = section.get("section_name")
        if name:
            section_names.add(name)

    # Build map using raw_sections text for matching section names
    session_map: Dict[str, str] = {}

    for section_name in section_names:
        if section_name in raw_sections:
            session_map[section_name] = raw_sections[section_name]
        else:
            # Try normalized matching
            normalized_target = _normalize_key(section_name)
            for raw_name, raw_text in raw_sections.items():
                if _normalize_key(raw_name) == normalized_target:
                    session_map[section_name] = raw_text
                    break

    return session_map
