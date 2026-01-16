"""
Tests for citation linking feature (Phase 1).

These tests verify that:
1. Section text map is created from policy sections and available for lookups
2. Citations in the A-G report can be matched to section text
3. UI helpers can retrieve and display section text for a citation
"""

from __future__ import annotations

import pytest
from typing import Any, Dict, List, Optional


# -----------------------------------------------------------------------------
# Test 1: Section text map creation and storage
# -----------------------------------------------------------------------------


class TestSectionTextMapCreation:
    """Test that section text map is created from policy analysis."""

    def test_build_section_text_map_returns_dict(self):
        """build_section_text_map() should return a dict mapping section names to text."""
        # This function doesn't exist yet - test should fail
        from src.citation_linking import build_section_text_map

        # Sample sections as they come from sectioning.py
        raw_sections = {
            "COVERAGE A - DWELLING": "We cover the dwelling on the residence premises...",
            "COVERAGE B - OTHER STRUCTURES": "We cover other structures on the residence premises...",
            "EXCLUSIONS": "We do not insure for loss caused directly or indirectly by...",
        }

        section_map = build_section_text_map(raw_sections)

        assert isinstance(section_map, dict)
        assert "COVERAGE A - DWELLING" in section_map
        assert section_map["COVERAGE A - DWELLING"] == raw_sections["COVERAGE A - DWELLING"]

    def test_build_section_text_map_normalizes_keys(self):
        """Section map keys should be normalized for fuzzy matching."""
        from src.citation_linking import build_section_text_map

        raw_sections = {
            "COVERAGE A - DWELLING": "Dwelling coverage text...",
            "SECTION I - EXCLUSIONS": "Exclusions text...",
        }

        section_map = build_section_text_map(raw_sections)

        # Should be able to lookup with slight variations
        assert "COVERAGE A - DWELLING" in section_map
        # Normalized lookup key should also work
        assert section_map.get("COVERAGE A - DWELLING") is not None

    def test_build_section_text_map_handles_empty_input(self):
        """Should return empty dict for empty input."""
        from src.citation_linking import build_section_text_map

        section_map = build_section_text_map({})
        assert section_map == {}

    def test_build_section_text_map_excludes_unknown_section(self):
        """UNKNOWN section should be excluded from the map by default."""
        from src.citation_linking import build_section_text_map

        raw_sections = {
            "UNKNOWN": "Some preamble text...",
            "COVERAGE A - DWELLING": "Dwelling coverage...",
        }

        section_map = build_section_text_map(raw_sections)

        assert "UNKNOWN" not in section_map
        assert "COVERAGE A - DWELLING" in section_map


# -----------------------------------------------------------------------------
# Test 2: Citation to section text matching
# -----------------------------------------------------------------------------


class TestCitationMatching:
    """Test that citations from the A-G report can be matched to section text."""

    def test_find_section_for_citation_exact_match(self):
        """Exact citation match should return the section text."""
        from src.citation_linking import find_section_for_citation

        section_map = {
            "COVERAGE A - DWELLING": "We cover the dwelling...",
            "EXCLUSIONS": "We do not insure for loss...",
        }

        result = find_section_for_citation("COVERAGE A - DWELLING", section_map)

        assert result is not None
        assert result["section_name"] == "COVERAGE A - DWELLING"
        assert result["section_text"] == "We cover the dwelling..."

    def test_find_section_for_citation_partial_match(self):
        """Partial/fuzzy citation match should still find the section."""
        from src.citation_linking import find_section_for_citation

        section_map = {
            "COVERAGE A - DWELLING": "We cover the dwelling...",
            "COVERAGE B - OTHER STRUCTURES": "We cover other structures...",
        }

        # Citation might just say "Coverage A" without full name
        result = find_section_for_citation("Coverage A", section_map)

        assert result is not None
        assert "COVERAGE A" in result["section_name"]

    def test_find_section_for_citation_case_insensitive(self):
        """Citation matching should be case-insensitive."""
        from src.citation_linking import find_section_for_citation

        section_map = {
            "EXCLUSIONS": "We do not insure for loss...",
        }

        result = find_section_for_citation("exclusions", section_map)

        assert result is not None
        assert result["section_name"] == "EXCLUSIONS"

    def test_find_section_for_citation_no_match_returns_none(self):
        """Non-matching citation should return None."""
        from src.citation_linking import find_section_for_citation

        section_map = {
            "COVERAGE A - DWELLING": "We cover the dwelling...",
        }

        result = find_section_for_citation("COVERAGE Z - NONEXISTENT", section_map)

        assert result is None

    def test_find_section_for_citation_handles_section_i_prefix(self):
        """Citations like 'Section I - Exclusions' should match 'EXCLUSIONS'."""
        from src.citation_linking import find_section_for_citation

        section_map = {
            "EXCLUSIONS": "We do not insure for loss...",
            "CONDITIONS": "Your duties after loss...",
        }

        result = find_section_for_citation("Section I - Exclusions", section_map)

        assert result is not None
        assert result["section_name"] == "EXCLUSIONS"


# -----------------------------------------------------------------------------
# Test 3: UI retrieval of section text for citations
# -----------------------------------------------------------------------------


class TestUICitationRetrieval:
    """Test that UI can retrieve section text for display."""

    def test_get_citation_display_data_returns_structured_data(self):
        """get_citation_display_data() should return data for UI rendering."""
        from src.citation_linking import get_citation_display_data

        section_map = {
            "COVERAGE A - DWELLING": "We cover the dwelling on the residence premises shown in the Declarations against direct physical loss to property described in Coverage A.",
        }

        # A Point with a citation from the A-G report
        point = {
            "text": "Coverage A explicitly covers the dwelling structure",
            "citation": "COVERAGE A - DWELLING",
        }

        display_data = get_citation_display_data(point, section_map)

        assert display_data is not None
        assert display_data["has_linkable_citation"] is True
        assert display_data["section_name"] == "COVERAGE A - DWELLING"
        assert "We cover the dwelling" in display_data["section_text"]
        assert display_data["point_text"] == point["text"]

    def test_get_citation_display_data_no_citation(self):
        """Points without citations should return has_linkable_citation=False."""
        from src.citation_linking import get_citation_display_data

        section_map = {
            "COVERAGE A - DWELLING": "We cover the dwelling...",
        }

        point = {
            "text": "General observation about the policy",
            "citation": None,
        }

        display_data = get_citation_display_data(point, section_map)

        assert display_data["has_linkable_citation"] is False
        assert display_data["section_text"] is None

    def test_get_citation_display_data_unmatched_citation(self):
        """Points with unmatched citations should still be renderable."""
        from src.citation_linking import get_citation_display_data

        section_map = {
            "COVERAGE A - DWELLING": "We cover the dwelling...",
        }

        point = {
            "text": "Reference to some clause",
            "citation": "Page 47, Paragraph 3",  # Free-form citation, no section match
        }

        display_data = get_citation_display_data(point, section_map)

        assert display_data["has_linkable_citation"] is False
        assert display_data["citation_text"] == "Page 47, Paragraph 3"
        assert display_data["section_text"] is None

    def test_get_citation_display_data_for_angle_multiple_citations(self):
        """Angles with multiple citations should return data for each."""
        from src.citation_linking import get_angle_citation_display_data

        section_map = {
            "EXCLUSIONS": "We do not insure for loss caused by...",
            "CONDITIONS": "Your duties after loss include...",
        }

        angle = {
            "text": "Dispute the exclusion based on conditions",
            "citations": ["EXCLUSIONS", "CONDITIONS"],
        }

        display_data = get_angle_citation_display_data(angle, section_map)

        assert display_data is not None
        assert len(display_data["linked_citations"]) == 2
        assert display_data["linked_citations"][0]["section_name"] == "EXCLUSIONS"
        assert display_data["linked_citations"][1]["section_name"] == "CONDITIONS"


# -----------------------------------------------------------------------------
# Test 4: Integration - session state storage pattern
# -----------------------------------------------------------------------------


class TestSessionStatePattern:
    """Test the pattern for storing section map in session state."""

    def test_create_session_section_map_from_policy_result(self):
        """Policy result should be convertible to a session-storable section map."""
        from src.citation_linking import create_session_section_map

        # Simulated policy_result structure (from demo_api.run_policy_analysis)
        policy_result = {
            "sections_substantive": [
                {
                    "section_name": "COVERAGE A - DWELLING",
                    "summary_overall": "Covers the dwelling structure...",
                    "key_coverages": ["Dwelling reconstruction"],
                },
                {
                    "section_name": "EXCLUSIONS",
                    "summary_overall": "Lists what is not covered...",
                    "key_exclusions": ["Earth movement", "Water damage"],
                },
            ],
            "sections_meta": [
                {
                    "section_name": "DECLARATIONS",
                    "summary_overall": "Policy declarations page...",
                },
            ],
        }

        # This needs raw section text - we'll need to pass it separately
        # or reconstruct it from the JSON with raw_text field
        raw_sections = {
            "COVERAGE A - DWELLING": "Full text of Coverage A section...",
            "EXCLUSIONS": "Full text of Exclusions section...",
            "DECLARATIONS": "Full text of declarations...",
        }

        session_map = create_session_section_map(policy_result, raw_sections)

        # Should include substantive sections
        assert "COVERAGE A - DWELLING" in session_map
        assert "EXCLUSIONS" in session_map
        # Meta sections can optionally be included
        assert isinstance(session_map, dict)

    def test_session_section_map_is_json_serializable(self):
        """Section map should be JSON-serializable for session state."""
        import json
        from src.citation_linking import build_section_text_map

        raw_sections = {
            "COVERAGE A - DWELLING": "We cover the dwelling...",
        }

        section_map = build_section_text_map(raw_sections)

        # Should not raise
        serialized = json.dumps(section_map)
        deserialized = json.loads(serialized)

        assert deserialized == section_map


# -----------------------------------------------------------------------------
# Test 5: Edge cases and robustness
# -----------------------------------------------------------------------------


class TestEdgeCases:
    """Test edge cases and robustness of citation linking."""

    def test_citation_with_extra_whitespace(self):
        """Citations with extra whitespace should still match."""
        from src.citation_linking import find_section_for_citation

        section_map = {
            "COVERAGE A - DWELLING": "We cover the dwelling...",
        }

        result = find_section_for_citation("  COVERAGE A - DWELLING  ", section_map)

        assert result is not None
        assert result["section_name"] == "COVERAGE A - DWELLING"

    def test_citation_with_different_dash_types(self):
        """Different dash types (-, –, —) should all match."""
        from src.citation_linking import find_section_for_citation

        section_map = {
            "COVERAGE A - DWELLING": "We cover the dwelling...",
        }

        # En-dash
        result1 = find_section_for_citation("COVERAGE A – DWELLING", section_map)
        # Em-dash
        result2 = find_section_for_citation("COVERAGE A — DWELLING", section_map)

        assert result1 is not None
        assert result2 is not None

    def test_very_long_section_text_is_preserved(self):
        """Long section text should be fully preserved in the map."""
        from src.citation_linking import build_section_text_map

        long_text = "A" * 10000  # 10k characters
        raw_sections = {
            "COVERAGE A - DWELLING": long_text,
        }

        section_map = build_section_text_map(raw_sections)

        assert len(section_map["COVERAGE A - DWELLING"]) == 10000

    def test_empty_citation_string(self):
        """Empty citation string should return None."""
        from src.citation_linking import find_section_for_citation

        section_map = {
            "COVERAGE A - DWELLING": "We cover the dwelling...",
        }

        result = find_section_for_citation("", section_map)

        assert result is None

    def test_none_citation(self):
        """None citation should be handled gracefully."""
        from src.citation_linking import find_section_for_citation

        section_map = {
            "COVERAGE A - DWELLING": "We cover the dwelling...",
        }

        result = find_section_for_citation(None, section_map)

        assert result is None
