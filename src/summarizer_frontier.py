from __future__ import annotations

from .llm_client import call_llm_json, LLMCallError
from .schemas import SectionSummary


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
