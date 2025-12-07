from __future__ import annotations

from typing import Any, Dict, List

from .llm_client import call_llm_json, LLMCallError
from .schemas import (
    SectionSummary,
    DisputeReport,
    Point,
    Angle,
    ConfidenceBlock,
)


# --- Existing section-level summarization ------------------------------------

SYSTEM_PROMPT = """You are an assistant that summarizes property insurance policy sections and denial letters for attorneys and public adjusters.
- Use plain English.
- Do NOT give legal advice.
- Do NOT invent coverage that is not clearly present in the text.
- Be conservative and factual.
Return concise bullet points where applicable.
"""


def build_user_prompt(section_name: str, section_text: str) -> str:
    return f"""
You are analyzing the following section of a property insurance policy or denial letter.

SECTION NAME: {section_name}

TEXT:
\"\"\"{section_text}\"\"\"


Task:

1. Give a 2–4 sentence plain-English summary of what this section does.
2. List the most important coverage grants (if any).
3. List the most important exclusions or limitations (if any).
4. List any notable conditions, requirements, or duties on the insured or insurer.
5. List any high-level "dispute angles" that an attorney or public adjuster might want to explore.
   - These are NOT legal conclusions, just "areas to check" (e.g., ambiguity, conflicts, missing definitions).

Return your answer as strict JSON with this structure:

{{
  "summary_overall": "string",
  "key_coverages": ["string", ...],
  "key_exclusions": ["string", ...],
  "conditions_notable": ["string", ...],
  "dispute_angles_possible": ["string", ...]
}}
""".strip()


def summarize_section(section_name: str, section_text: str) -> SectionSummary:
    user_prompt = build_user_prompt(section_name, section_text)

    data = call_llm_json(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.2,
        max_retries=3,
        timeout=30.0,
    )

    return SectionSummary(
        section_name=section_name,
        summary_overall=data.get("summary_overall", "").strip(),
        key_coverages=data.get("key_coverages", []) or [],
        key_exclusions=data.get("key_exclusions", []) or [],
        conditions_notable=data.get("conditions_notable", []) or [],
        dispute_angles_possible=data.get("dispute_angles_possible", []) or [],
    )


# --- New denial-aware dispute report builder ---------------------------------

DENIAL_SYSTEM_PROMPT = """You are an assistant that analyzes property insurance coverage disputes.
You work with:
- A pre-summarized policy (by section).
- A claim denial letter.

Rules:
- Use plain English.
- Do NOT give legal advice or coverage determinations.
- Do NOT invent terms or rights not clearly supported by the text.
- Be conservative and factual.
"""


def _build_policy_overview_block(policy_summary_payload: Dict[str, Any]) -> str:
    """
    Compress the policy summary into a compact, LLM-friendly view:
    section name + overall summary + dispute angles (if any).
    """
    sections = policy_summary_payload.get("sections", []) or []
    lines: List[str] = []

    for s in sections:
        name = (s.get("section_name") or "UNKNOWN").strip()
        summary = (s.get("summary_overall") or "").strip()
        angles = s.get("dispute_angles_possible") or []

        if not summary and not angles:
            continue

        lines.append(f"SECTION: {name}")
        if summary:
            lines.append(f"  SUMMARY: {summary}")
        if angles:
            joined = "; ".join(str(a) for a in angles if str(a).strip())
            if joined:
                lines.append(f"  DISPUTE_ANGLES: {joined}")
        lines.append("")  # blank line between sections

    if not lines:
        return "[No usable policy summaries available.]"

    return "\n".join(lines)


def _build_denial_user_prompt(
    policy_summary_payload: Dict[str, Any],
    denial_text: str,
) -> str:
    policy_block = _build_policy_overview_block(policy_summary_payload)

    return f"""
You are analyzing a property insurance coverage dispute involving:

1) A homeowners policy that has already been summarized by section.
2) A claim denial letter.

POLICY SUMMARY (BY SECTION)
---------------------------
{policy_block}

DENIAL LETTER
-------------
\"\"\"{denial_text}\"\"\"


Task:

1. Provide a short 2–4 sentence plain-English overview of the dispute.
2. Extract 3–7 key denial reasons from the denial letter.
   - Each reason should be concise and refer to the insurer's stated position.
3. For each denial reason, reference the most relevant policy section(s) by section name
   (e.g. "EXCLUSIONS", "COVERAGE A - DWELLING", "DEFINITIONS").
4. Identify the most important coverage grants that could potentially support the insured.
5. Identify the most important exclusions or limitations that may hurt the insured.
6. Suggest 3–8 high-level dispute angles a public adjuster or attorney might want to explore.
   - These are NOT legal conclusions. They are simply "areas to check" or questions to ask.
7. List any missing information, documents, or facts that would be useful to clarify the dispute.
8. Provide a simple confidence block:
   - A numeric score between 0 and 1 (0 = very low confidence, 1 = very high confidence).
   - A short note explaining why.
   - A list of specific clauses/sections that should always be double-checked.

Return STRICT JSON with this structure:

{{
  "plain_summary": "string",
  "coverage_highlights": [{{"text": "string", "citation": "string"}}],
  "exclusions_limitations": [{{"text": "string", "citation": "string"}}],
  "denial_reasons": [{{"text": "string", "citation": "string"}}],
  "dispute_angles": [{{"text": "string", "citations": ["string", ...]}}],
  "missing_info": ["string", ...],
  "confidence": {{
      "score": 0.0,
      "notes": "string",
      "verify_clauses": ["string", ...]
  }}
}}
""".strip()


def _parse_points(raw_points: Any) -> List[Point]:
    points: List[Point] = []
    if not isinstance(raw_points, list):
        return points

    for item in raw_points:
        if isinstance(item, str):
            text = item.strip()
            if text:
                points.append(Point(text=text))
        elif isinstance(item, dict):
            text = str(item.get("text", "")).strip()
            if not text:
                continue
            citation = item.get("citation")
            if citation is not None:
                citation = str(citation).strip() or None
            points.append(Point(text=text, citation=citation))
    return points


def _parse_angles(raw_angles: Any) -> List[Angle]:
    angles: List[Angle] = []
    if not isinstance(raw_angles, list):
        return angles

    for item in raw_angles:
        if isinstance(item, str):
            text = item.strip()
            if text:
                angles.append(Angle(text=text))
        elif isinstance(item, dict):
            text = str(item.get("text", "")).strip()
            if not text:
                continue
            raw_cits = item.get("citations") or []
            citations: List[str] = []
            if isinstance(raw_cits, list):
                for c in raw_cits:
                    s = str(c).strip()
                    if s:
                        citations.append(s)
            angles.append(Angle(text=text, citations=citations))
    return angles


def _parse_confidence(raw_conf: Any) -> ConfidenceBlock:
    if not isinstance(raw_conf, dict):
        return ConfidenceBlock()

    score_raw = raw_conf.get("score")
    score: float | None
    if isinstance(score_raw, (int, float)):
        score = float(score_raw)
    else:
        score = None

    notes = str(raw_conf.get("notes", "") or "")
    raw_verify = raw_conf.get("verify_clauses") or []
    verify_clauses: List[str] = []
    if isinstance(raw_verify, list):
        for v in raw_verify:
            s = str(v).strip()
            if s:
                verify_clauses.append(s)

    return ConfidenceBlock(score=score, notes=notes, verify_clauses=verify_clauses)


def build_denial_aware_report(
    policy_summary_payload: Dict[str, Any],
    denial_text: str,
) -> DisputeReport:
    """
    High-level dispute report builder: policy summary JSON + denial text -> DisputeReport.
    """
    user_prompt = _build_denial_user_prompt(
        policy_summary_payload, denial_text)

    data = call_llm_json(
        system_prompt=DENIAL_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.2,
        max_retries=3,
        timeout=60.0,
    )

    plain_summary = str(data.get("plain_summary", "") or "").strip()
    coverage_highlights = _parse_points(data.get("coverage_highlights"))
    exclusions_limitations = _parse_points(data.get("exclusions_limitations"))
    denial_reasons = _parse_points(data.get("denial_reasons"))
    dispute_angles = _parse_angles(data.get("dispute_angles"))
    raw_missing = data.get("missing_info") or []
    missing_info: List[str] = []
    if isinstance(raw_missing, list):
        for m in raw_missing:
            s = str(m).strip()
            if s:
                missing_info.append(s)

    confidence = _parse_confidence(data.get("confidence"))

    return DisputeReport(
        plain_summary=plain_summary,
        coverage_highlights=coverage_highlights,
        exclusions_limitations=exclusions_limitations,
        denial_reasons=denial_reasons,
        dispute_angles=dispute_angles,
        missing_info=missing_info,
        confidence=confidence,
    )
