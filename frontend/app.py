from __future__ import annotations

import importlib
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import streamlit as st

# Ensure project root is on sys.path so we can import "src.*"
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

demo_api = importlib.import_module("src.demo_api")
config = importlib.import_module("src.config")
pdf_loader = importlib.import_module("src.pdf_loader")
summarizer_frontier = importlib.import_module("src.summarizer_frontier")
report_builder = importlib.import_module("src.report_builder")
schemas = importlib.import_module("src.schemas")
database = importlib.import_module("src.database")
sectioning = importlib.import_module("src.sectioning")
citation_linking = importlib.import_module("src.citation_linking")

is_demo_force_on = config.is_demo_force_on
run_policy_analysis = demo_api.run_policy_analysis
load_pdf_text = pdf_loader.load_pdf_text
build_denial_aware_report = summarizer_frontier.build_denial_aware_report
render_dispute_markdown = report_builder.render_dispute_markdown
render_dispute_docx = report_builder.render_dispute_docx
DisputeReport = schemas.DisputeReport
Point = schemas.Point
Angle = schemas.Angle
ConfidenceBlock = schemas.ConfidenceBlock
save_claim = database.save_claim
get_all_claims = database.get_all_claims
get_claim_by_id = database.get_claim_by_id
delete_claim = database.delete_claim
split_into_sections = sectioning.split_into_sections
build_section_text_map = citation_linking.build_section_text_map
get_citation_display_data = citation_linking.get_citation_display_data
get_angle_citation_display_data = citation_linking.get_angle_citation_display_data


UPLOAD_DIR = Path("data/uploads")
SESSION_KEY_POLICY = "policy_result"
SESSION_KEY_DISPUTE = "dispute_result"
SESSION_KEY_CLAIM_METADATA = "claim_metadata"
SESSION_KEY_SELECTED_CLAIM = "selected_claim_id"
SESSION_KEY_SECTION_MAP = "section_text_map"
SESSION_KEY_DEMO_MODE = "demo_mode"
SESSION_KEY_PAGE = "main_page"

DEMO_ASSET_DIR = ROOT / "assets" / "demo"
DEMO_JSON_PATH = DEMO_ASSET_DIR / "demo.json"
DEMO_MD_PATH = DEMO_ASSET_DIR / "demo.report.md"
DEMO_SECTION_TEXT_PATH = DEMO_ASSET_DIR / "section_text.json"


def _render_framing_badges() -> None:
    st.markdown(
        "**Research prototype** · **Not legal advice** · **AI-generated**"
    )


def _render_value_prop_intro() -> None:
    st.markdown("### Policy dispute review, structured for faster triage")
    st.caption(
        "Upload a homeowners policy and denial letter to produce a focused A-G "
        "review of coverage language, denial reasons, dispute angles, and missing information."
    )

    _render_framing_badges()

    col_what, col_who, col_not = st.columns(3)
    with col_what:
        st.markdown("**What it does**")
        st.write(
            "Turns policy summaries and denial text into a structured dispute brief "
            "with citations, next-step questions, and downloadable output."
        )
    with col_who:
        st.markdown("**Who it is for**")
        st.write(
            "Claim reviewers, adjusters, and legal teams evaluating homeowners "
            "coverage disputes and preparing for human review."
        )
    with col_not:
        st.markdown("**What it is not**")
        st.write(
            "Not a coverage decision, legal advice, attorney service, or guarantee "
            "of any claim outcome."
        )

    with st.expander("Important research framing", expanded=False):
        st.write(
            "This is an AI-generated analysis of policy language and a denial letter. "
            "It is a research prototype for educational and workflow exploration. "
            "It does not create coverage, rights, an attorney-client relationship, "
            "or a substitute for professional judgment against the actual policy and claim file."
        )


def _save_denial_pdf(uploaded_file, claim_nickname: str | None = None) -> Path:
    """
    Save the uploaded denial letter PDF under data/uploads/ with a timestamped name.
    """
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    stem = (claim_nickname or Path(uploaded_file.name).stem or "denial").strip()
    safe_stem = stem.replace(" ", "_")
    ts = int(time.time())
    filename = f"{safe_stem}__denial__{ts}.pdf"

    path = UPLOAD_DIR / filename
    path.write_bytes(uploaded_file.getvalue())
    return path


def _demo_asset_instructions() -> str:
    return (
        "Demo assets not found. Expected tracked demo files at:\n"
        f"1) {DEMO_JSON_PATH.relative_to(ROOT)}\n"
        f"2) {DEMO_MD_PATH.relative_to(ROOT)}\n"
        "Restore these files from the repository or see RUNBOOK.md for Demo Mode setup."
    )


def _load_demo_section_map() -> Dict[str, str]:
    if not DEMO_SECTION_TEXT_PATH.is_file():
        return {}

    section_text = json.loads(DEMO_SECTION_TEXT_PATH.read_text(encoding="utf-8"))
    if not isinstance(section_text, dict):
        raise RuntimeError(
            "Demo source text asset must be a JSON object mapping section names to text."
        )

    return {
        str(section_name).strip(): str(text).strip()
        for section_name, text in section_text.items()
        if str(section_name).strip() and str(text).strip()
    }


def _build_policy_result_from_summary(
    summary_data: Dict[str, Any],
    *,
    summary_path: Path,
    markdown_text: str,
) -> Dict[str, Any]:
    policy_report = report_builder.build_policy_report(summary_data)
    markdown = markdown_text or report_builder.render_markdown(policy_report)

    return {
        "policy_name": policy_report.policy_name,
        "source_path": policy_report.source_path,
        "stats": {
            "num_sections": policy_report.num_sections,
            "num_unknown_sections": policy_report.num_unknown_sections,
            "num_meta_sections": policy_report.num_meta_sections,
        },
        "sections_substantive": policy_report.sections_substantive,
        "sections_meta": policy_report.sections_meta,
        "artifacts": {
            "summary_json": str(summary_path),
            "markdown_report": str(DEMO_MD_PATH),
            "demo_mode": True,
        },
        "markdown": markdown,
    }


def _build_demo_dispute_report_from_policy(summary_data: Dict[str, Any]) -> Dict[str, Any]:
    sections = summary_data.get("sections", []) or []
    substantive = []
    for s in sections:
        role = (s.get("section_role") or "substantive").lower()
        if role != "meta":
            substantive.append(s)

    def collect_points(field: str, limit: int) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        for section in substantive:
            section_name = (section.get("section_name") or "UNKNOWN").strip()
            for item in section.get(field, []) or []:
                text = str(item).strip()
                if not text:
                    continue
                items.append({"text": text, "citation": section_name})
                if len(items) >= limit:
                    return items
        return items

    def collect_angles(limit: int) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        for section in substantive:
            section_name = (section.get("section_name") or "UNKNOWN").strip()
            for item in section.get("dispute_angles_possible", []) or []:
                text = str(item).strip()
                if not text:
                    continue
                items.append({"text": text, "citations": [section_name]})
                if len(items) >= limit:
                    return items
        return items

    policy_id = summary_data.get("policy_id") or "policy"

    return {
        "policy_id": policy_id,
        "denial_id": "demo_denial",
        "plain_summary": (
            "Demo Mode: This dispute summary is generated from the policy summary "
            "only. No denial letter was analyzed."
        ),
        "coverage_highlights": collect_points("key_coverages", 4),
        "exclusions_limitations": collect_points("key_exclusions", 4),
        "denial_reasons": [],
        "dispute_angles": collect_angles(6),
        "missing_info": [
            "Denial letter text (required for live analysis).",
            "Claim facts and loss timeline.",
            "Photos, estimates, and repair invoices.",
            "Policy declarations page for limits and deductible.",
        ],
        "confidence": {
            "score": 0.2,
            "notes": f"Demo Mode only. Generated from {policy_id} policy summaries.",
            "verify_clauses": [],
        },
    }


def _load_demo_assets() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if not DEMO_JSON_PATH.is_file() or not DEMO_MD_PATH.is_file():
        raise FileNotFoundError(_demo_asset_instructions())

    demo_payload = json.loads(DEMO_JSON_PATH.read_text(encoding="utf-8"))
    demo_markdown = DEMO_MD_PATH.read_text(encoding="utf-8")

    if (
        isinstance(demo_payload, dict)
        and "policy_result" in demo_payload
        and "dispute_result" in demo_payload
    ):
        policy_result = demo_payload.get("policy_result") or {}
        dispute_result = demo_payload.get("dispute_result") or {}
        if not dispute_result.get("markdown"):
            dispute_result["markdown"] = demo_markdown
        return policy_result, dispute_result

    if isinstance(demo_payload, dict) and "plain_summary" in demo_payload:
        dispute_report = demo_payload
        dispute_result = {
            "policy_id": dispute_report.get("policy_id") or "policy",
            "denial_id": dispute_report.get("denial_id") or "demo_denial",
            "dispute_report": dispute_report,
            "markdown": demo_markdown,
            "artifacts": {
                "demo_json": str(DEMO_JSON_PATH),
                "demo_markdown": str(DEMO_MD_PATH),
            },
        }
        policy_result = {
            "policy_name": dispute_result["policy_id"],
            "source_path": "",
            "stats": {"num_sections": 0, "num_unknown_sections": 0, "num_meta_sections": 0},
            "sections_substantive": [],
            "sections_meta": [],
            "artifacts": {
                "summary_json": str(DEMO_JSON_PATH),
                "markdown_report": str(DEMO_MD_PATH),
                "demo_mode": True,
            },
            "markdown": "",
        }
        return policy_result, dispute_result

    if isinstance(demo_payload, dict) and "sections" in demo_payload:
        policy_result = _build_policy_result_from_summary(
            demo_payload,
            summary_path=DEMO_JSON_PATH,
            markdown_text=demo_markdown,
        )
        dispute_report = _build_demo_dispute_report_from_policy(demo_payload)
        dispute_result = {
            "policy_id": demo_payload.get("policy_id") or "policy",
            "denial_id": "demo_denial",
            "dispute_report": dispute_report,
            "markdown": render_dispute_markdown(_dict_to_dispute_report(dispute_report)),
            "artifacts": {
                "demo_json": str(DEMO_JSON_PATH),
                "demo_markdown": str(DEMO_MD_PATH),
            },
        }
        return policy_result, dispute_result

    raise RuntimeError(
        "Demo assets loaded but demo.json format is unsupported. "
        "Expected a policy summary JSON, a dispute report JSON, or a bundle "
        "with policy_result + dispute_result."
    )


def _load_demo_into_session() -> None:
    try:
        policy_result, dispute_result = _load_demo_assets()
        section_map = _load_demo_section_map()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()
    except Exception as exc:  # noqa: BLE001
        st.error(f"Failed to load demo assets: {exc}")
        st.stop()

    st.session_state[SESSION_KEY_POLICY] = policy_result
    st.session_state[SESSION_KEY_DISPUTE] = dispute_result
    st.session_state[SESSION_KEY_SECTION_MAP] = section_map
    st.session_state[SESSION_KEY_CLAIM_METADATA] = {
        "nickname": "Demo Mode",
        "state": "",
        "policy_filename": "demo.json",
        "denial_filename": "demo.report.md",
    }


def _render_points(
    points: List[Dict[str, Any]] | None,
    empty_message: str,
    section_map: Dict[str, str] | None = None,
    key_prefix: str = "pt",
) -> None:
    """Render points with clickable citation accordions."""
    points = points or []
    section_map = section_map or {}

    if not points:
        st.write(empty_message)
        return

    for idx, p in enumerate(points):
        if isinstance(p, dict):
            text = str(p.get("text", "")).strip()
            citation = str(p.get("citation", "") or "").strip()
        else:
            text = str(p).strip()
            citation = ""

        if not text:
            continue

        # Display the point text
        st.markdown(f"- {text}")

        # If there's a citation, try to make it clickable
        if citation and section_map:
            display_data = get_citation_display_data(p, section_map)

            if display_data["has_linkable_citation"]:
                # Clickable accordion with section text
                with st.expander(f"View source: {display_data['section_name']}", expanded=False):
                    section_text = display_data["section_text"] or ""
                    # Show first 2000 chars with option to expand
                    if len(section_text) > 2000:
                        st.text_area(
                            "Policy section text",
                            section_text,
                            height=300,
                            disabled=True,
                            key=f"{key_prefix}_cit_{idx}_{hash(text)}_{hash(citation)}",
                        )
                    else:
                        st.markdown(f"```\n{section_text}\n```")
            else:
                # Non-linkable citation, just show as text
                st.caption(f"_Citation: {citation}_")
        elif citation:
            # No section map available, show citation as plain text
            st.caption(f"_Citation: {citation}_")


def _render_dispute_angles(
    angles: List[Dict[str, Any]] | None,
    section_map: Dict[str, str] | None = None,
    key_prefix: str = "ang",
) -> None:
    """Render dispute angles with clickable citation accordions."""
    angles = angles or []
    section_map = section_map or {}

    if not angles:
        st.write("No dispute angles identified.")
        return

    for idx, a in enumerate(angles):
        if isinstance(a, dict):
            text = str(a.get("text", "")).strip()
            raw_cits = a.get("citations") or []
            cits: List[str] = []
            if isinstance(raw_cits, list):
                for c in raw_cits:
                    s = str(c).strip()
                    if s:
                        cits.append(s)
        else:
            text = str(a).strip()
            cits = []

        if not text:
            continue

        # Display the angle text
        st.markdown(f"- {text}")

        # If there are citations and we have a section map, make them clickable
        if cits and section_map:
            display_data = get_angle_citation_display_data(a, section_map)

            # Render linked citations as accordions
            for cit_idx, linked in enumerate(display_data.get("linked_citations", [])):
                section_name = linked.get("section_name", "")
                with st.expander(f"View source: {section_name}", expanded=False):
                    section_text = linked.get("section_text") or ""
                    if len(section_text) > 2000:
                        st.text_area(
                            "Policy section text",
                            section_text,
                            height=300,
                            disabled=True,
                            key=f"{key_prefix}_cit_{idx}_{cit_idx}_{hash(text)}_{hash(section_name)}",
                        )
                    else:
                        st.markdown(f"```\n{section_text}\n```")

            # Show unlinked citations as plain text
            unlinked = display_data.get("unlinked_citations", [])
            if unlinked:
                st.caption(f"_Other citations: {', '.join(unlinked)}_")
        elif cits:
            # No section map, show all as plain text
            joined = ", ".join(cits)
            st.caption(f"_Citations: {joined}_")


def _dict_to_dispute_report(d: Dict[str, Any]) -> DisputeReport:
    """Reconstruct a DisputeReport dataclass from a dict."""
    def parse_points(items: List[Any] | None) -> List[Point]:
        result = []
        for item in (items or []):
            if isinstance(item, dict):
                text = str(item.get("text", "")).strip()
                citation = item.get("citation")
                if text:
                    result.append(Point(text=text, citation=citation))
        return result

    def parse_angles(items: List[Any] | None) -> List[Angle]:
        result = []
        for item in (items or []):
            if isinstance(item, dict):
                text = str(item.get("text", "")).strip()
                citations = item.get("citations") or []
                if text:
                    result.append(Angle(text=text, citations=citations))
        return result

    conf_dict = d.get("confidence") or {}
    confidence = ConfidenceBlock(
        score=conf_dict.get("score"),
        notes=str(conf_dict.get("notes", "") or ""),
        verify_clauses=conf_dict.get("verify_clauses") or [],
    )

    return DisputeReport(
        policy_id=d.get("policy_id"),
        denial_id=d.get("denial_id"),
        plain_summary=str(d.get("plain_summary", "") or ""),
        coverage_highlights=parse_points(d.get("coverage_highlights")),
        exclusions_limitations=parse_points(d.get("exclusions_limitations")),
        denial_reasons=parse_points(d.get("denial_reasons")),
        dispute_angles=parse_angles(d.get("dispute_angles")),
        missing_info=d.get("missing_info") or [],
        confidence=confidence,
    )


def _render_hero(
    dispute_report: Dict[str, Any],
    dispute_markdown: str,
    policy_label: str,
    denial_label: str,
    policy_filename: str | None = None,
    denial_filename: str | None = None,
) -> None:
    st.subheader("Dispute overview")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        plain_summary = str(dispute_report.get(
            "plain_summary", "") or "").strip()
        if plain_summary:
            st.markdown("##### A. Plain-language summary")
            st.write(plain_summary)
        else:
            st.write("No plain-language summary available from the model.")

        # try to pull 2–3 "key takeaways" from B/E
        takeaways: List[str] = []
        for pt in dispute_report.get("coverage_highlights", []) or []:
            text = ""
            if isinstance(pt, dict):
                text = str(pt.get("text", "")).strip()
            else:
                text = str(pt).strip()
            if text:
                takeaways.append(text)
            if len(takeaways) >= 3:
                break

        if len(takeaways) < 3:
            for angle in dispute_report.get("dispute_angles", []) or []:
                text = ""
                if isinstance(angle, dict):
                    text = str(angle.get("text", "")).strip()
                else:
                    text = str(angle).strip()
                if text:
                    takeaways.append(text)
                if len(takeaways) >= 3:
                    break

        if takeaways:
            st.markdown("##### Key takeaways")
            for t in takeaways[:3]:
                st.markdown(f"- {t}")

    with col_right:
        confidence = dispute_report.get("confidence") or {}
        score = confidence.get("score")

        st.markdown("##### Review context")
        st.write(f"**Policy file:** {policy_filename or policy_label}")
        st.write(f"**Denial file:** {denial_filename or denial_label}")
        if score is not None:
            try:
                st.metric("Confidence", f"{float(score):.2f}")
            except (TypeError, ValueError):
                st.write(f"**Confidence:** {score}")

        st.markdown("##### Actions")
        st.caption("Download the full A–G dispute write-up.")
        st.download_button(
            "Download as Word (.docx)",
            data=render_dispute_docx(_dict_to_dispute_report(dispute_report)),
            file_name=f"{policy_label}__{denial_label}.dispute.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        st.download_button(
            "Download as Markdown",
            data=dispute_markdown,
            file_name=f"{policy_label}__{denial_label}.dispute.md",
            mime="text/markdown",
        )
        st.caption(
            "Always compare against the actual policy & denial."
        )


def _render_confidence_content(dispute_report: Dict[str, Any]) -> None:
    """Render confidence metadata without exposing raw report JSON."""
    conf = dispute_report.get("confidence") or {}
    score = conf.get("score")
    notes = str(conf.get("notes", "") or "").strip()
    verify_clauses = conf.get("verify_clauses") or []

    st.markdown("### Confidence")

    if score is not None:
        try:
            st.metric("Confidence score", f"{float(score):.2f}")
        except (TypeError, ValueError):
            st.write(f"**Confidence score:** {score}")

    if notes:
        st.markdown("#### Notes")
        st.write(notes)

    if verify_clauses:
        st.markdown("#### Clauses / sections to double-check")
        for clause in verify_clauses:
            s = str(clause).strip()
            if s:
                st.markdown(f"- {s}")

    if score is None and not notes and not verify_clauses:
        st.info("No explicit confidence metadata provided by the model.")


def _render_confidence_debug(
    dispute_report: Dict[str, Any],
    *,
    policy_artifacts: Dict[str, Any] | None = None,
    dispute_artifacts: Dict[str, Any] | None = None,
) -> None:
    with st.expander("Developer: raw A-G JSON", expanded=False):
        st.json(dispute_report)

    with st.expander("Developer: artifacts / advanced debug", expanded=False):
        st.json(
            {
                "policy_artifacts": policy_artifacts or {},
                "dispute_artifacts": dispute_artifacts or {},
            }
        )


def _render_dispute_tabs(
    dispute_report: Dict[str, Any],
    section_map: Dict[str, str] | None = None,
    *,
    policy_artifacts: Dict[str, Any] | None = None,
    dispute_artifacts: Dict[str, Any] | None = None,
) -> None:
    """Render the dispute report tabs with optional citation linking."""
    section_map = section_map or {}

    tab_ag, tab_policy_view, tab_denial_view, tab_debug = st.tabs(
        [
            "Dispute summary (A–G)",
            "Policy highlights",
            "Denial reasons",
            "Confidence",
        ]
    )

    # A–G
    with tab_ag:
        st.markdown("### A–G dispute structure")

        if section_map:
            st.caption("Click 'View source' below citations to see the original policy text.")

        with st.expander("A – Plain-language overview", expanded=True):
            plain_summary = str(dispute_report.get(
                "plain_summary", "") or "").strip()
            if plain_summary:
                st.write(plain_summary)
            else:
                st.write("No overview available.")

        with st.expander("B – Coverage highlights that may support the insured"):
            _render_points(
                dispute_report.get("coverage_highlights"),
                "No coverage highlights identified.",
                section_map,
                key_prefix="ag_b",
            )

        with st.expander("C – Key exclusions / limitations that may hurt the insured"):
            _render_points(
                dispute_report.get("exclusions_limitations"),
                "No exclusions / limitations identified.",
                section_map,
                key_prefix="ag_c",
            )

        with st.expander("D – Denial reasons & cited clauses"):
            _render_points(
                dispute_report.get("denial_reasons"),
                "No denial reasons extracted from the letter.",
                section_map,
                key_prefix="ag_d",
            )

        with st.expander("E – Possible dispute angles to explore"):
            _render_dispute_angles(dispute_report.get("dispute_angles"), section_map, key_prefix="ag_e")

        with st.expander("F – Missing information / suggested next steps"):
            missing = dispute_report.get("missing_info") or []
            if not missing:
                st.write("No specific missing information identified.")
            else:
                for item in missing:
                    s = str(item).strip()
                    if s:
                        st.markdown(f"- {s}")

        with st.expander("G – Confidence & clauses to double-check"):
            conf = dispute_report.get("confidence") or {}
            score = conf.get("score")
            notes = str(conf.get("notes", "") or "").strip()
            verify_clauses = conf.get("verify_clauses") or []

            if score is not None:
                st.write(f"**Confidence score (0–1):** {float(score):.2f}")
            if notes:
                st.write(f"**Notes:** {notes}")
            if verify_clauses:
                st.markdown("**Clauses / sections to double-check:**")
                for c in verify_clauses:
                    s = str(c).strip()
                    if s:
                        st.markdown(f"- {s}")
            if (
                score is None
                and not notes
                and not (verify_clauses or [])
            ):
                st.write("No explicit confidence metadata provided by the model.")

    # Policy slice
    with tab_policy_view:
        st.markdown("### Policy highlights from A–G report")
        st.caption(
            "These are pulled from the dispute report (not the full policy). "
            "Use them as a quick checklist, then confirm against the actual wording."
        )

        st.markdown("#### Coverage highlights (B)")
        _render_points(
            dispute_report.get("coverage_highlights"),
            "No coverage highlights identified.",
            section_map,
            key_prefix="pol_b",
        )

        st.markdown("#### Exclusions / limitations (C)")
        _render_points(
            dispute_report.get("exclusions_limitations"),
            "No exclusions / limitations identified.",
            section_map,
            key_prefix="pol_c",
        )

    # Denial slice
    with tab_denial_view:
        st.markdown("### Denial reasons & angles")

        st.markdown("#### Denial reasons (D)")
        _render_points(
            dispute_report.get("denial_reasons"),
            "No denial reasons extracted from the letter.",
            section_map,
            key_prefix="den_d",
        )

        st.markdown("#### Dispute angles (E)")
        _render_dispute_angles(dispute_report.get("dispute_angles"), section_map, key_prefix="den_e")

    # Confidence and collapsed developer details
    with tab_debug:
        _render_confidence_content(dispute_report)
        _render_confidence_debug(
            dispute_report,
            policy_artifacts=policy_artifacts,
            dispute_artifacts=dispute_artifacts,
        )


def _render_policy_breakdown(policy_result: Dict[str, Any]) -> None:
    st.markdown("### Policy breakdown (section summaries)")
    stats = policy_result.get("stats", {}) or {}

    c1, c2, c3 = st.columns(3)
    c1.metric("Total sections", stats.get("num_sections", 0))
    c2.metric("UNKNOWN sections", stats.get("num_unknown_sections", 0))
    c3.metric("Meta sections", stats.get("num_meta_sections", 0))

    st.caption("Substantive sections only (no raw policy text).")

    for s in policy_result.get("sections_substantive", []) or []:
        section_title = s.get("section_name", "Section")
        with st.expander(section_title, expanded=False):
            summary = s.get("summary_overall", "")
            if summary:
                st.write(summary)

            st.markdown("**Key coverages**")
            st.write(s.get("key_coverages", []))

            st.markdown("**Key exclusions / limitations**")
            st.write(s.get("key_exclusions", []))

            st.markdown("**Notable conditions / duties**")
            st.write(s.get("conditions_notable", []))

            st.markdown("**Potential dispute angles**")
            st.write(s.get("dispute_angles_possible", []))

    meta_sections = policy_result.get("sections_meta", []) or []
    if meta_sections:
        with st.expander("Meta / regulatory sections", expanded=False):
            st.caption(
                "Likely non-operative material (disclaimers, OIR filings, etc.).")
            st.write(meta_sections)


def _run_full_analysis(
    *,
    claim_nickname: str,
    state: str,
    policy_file,
    denial_file,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    End-to-end:
      - run policy analysis (existing demo_api helper)
      - save + OCR denial PDF to text
      - call build_denial_aware_report
      - render Markdown dispute report
    """
    if is_demo_force_on():
        raise RuntimeError(
            "Live analysis is disabled while DEMO_FORCE_ON=true. "
            "Run locally with DEMO_FORCE_ON=false to use file uploads."
        )

    with st.status("Starting live analysis", expanded=True) as analysis_status:
        progress_bar = st.progress(0)

        # Step 1: policy
        step_label = "Step 1/4: Analyzing policy"
        analysis_status.update(label=step_label, state="running", expanded=True)
        st.write(step_label)
        progress_bar.progress(20)

        policy_result = run_policy_analysis(
            policy_file.getvalue(),
            policy_file.name,
        )

        # Step 1b: Extract raw sections for citation linking (in-memory only)
        uploaded_pdf_path = Path(policy_result.get("artifacts", {}).get("uploaded_pdf", ""))
        if uploaded_pdf_path.is_file():
            policy_text = load_pdf_text(uploaded_pdf_path)
            raw_sections = split_into_sections(policy_text)
            section_map = build_section_text_map(raw_sections)
            st.session_state[SESSION_KEY_SECTION_MAP] = section_map

        # Step 2: denial text
        step_label = "Step 2/4: Reading denial letter"
        analysis_status.update(label=step_label, state="running", expanded=True)
        st.write(step_label)
        progress_bar.progress(45)

        denial_path = _save_denial_pdf(denial_file, claim_nickname or None)
        denial_text = load_pdf_text(denial_path)

        # Step 3: A-G dispute report
        step_label = "Step 3/4: Building dispute analysis"
        analysis_status.update(label=step_label, state="running", expanded=True)
        st.write(step_label)
        progress_bar.progress(75)

        summary_json_path = Path(policy_result.get(
            "artifacts", {}).get("summary_json", ""))
        if not summary_json_path.is_file():
            raise RuntimeError(
                f"Policy summary JSON not found at {summary_json_path!s}")

        policy_summary_payload = json.loads(
            summary_json_path.read_text(encoding="utf-8"))

        dispute_obj: DisputeReport = build_denial_aware_report(
            policy_summary_payload,
            denial_text,
        )

        # Step 4: output preparation
        step_label = "Step 4/4: Preparing outputs"
        analysis_status.update(label=step_label, state="running", expanded=True)
        st.write(step_label)
        progress_bar.progress(90)

        # attach IDs for nicer Markdown & UI labels
        dispute_obj.policy_id = (
            policy_result.get("policy_name")
            or Path(policy_result.get("source_path") or "").stem
            or "policy"
        )
        dispute_obj.denial_id = Path(denial_path).stem or "denial"

        markdown = render_dispute_markdown(dispute_obj)
        dispute_report_dict = dispute_obj.to_dict()

        dispute_result: Dict[str, Any] = {
            "policy_id": dispute_obj.policy_id,
            "denial_id": dispute_obj.denial_id,
            "dispute_report": dispute_report_dict,
            "markdown": markdown,
            "artifacts": {
                "summary_json": str(summary_json_path),
                "denial_pdf": str(denial_path),
            },
        }

        progress_bar.progress(100)
        analysis_status.update(
            label="Analysis complete",
            state="complete",
            expanded=False,
        )

    return policy_result, dispute_result


def _render_intake_form() -> None:
    st.header("New claim")

    if is_demo_force_on():
        st.info(
            "This hosted demo runs in deterministic Demo Mode. "
            "Live analysis and file uploads are disabled here; run the project "
            "locally with DEMO_FORCE_ON=false for the full workflow."
        )
        return

    st.caption(
        "Upload a homeowners policy and denial letter as PDFs. "
        "We’ll generate a dispute-focused A–G summary for quick triage. "
        "Nothing here is legal advice."
    )

    with st.form("claim_intake"):
        col1, col2 = st.columns(2)
        with col1:
            claim_nickname = st.text_input(
                "Claim nickname (optional)",
                help="Short label like 'Smith wind loss' to help you remember the case.",
            )
        with col2:
            state = st.text_input(
                "State (optional)",
                help="Two-letter state code like FL or TX. Used only for context today.",
                max_chars=10,
            )

        policy_file = st.file_uploader(
            "Policy PDF",
            type=["pdf"],
            key="policy_pdf",
            help="The full HO3 (or similar) policy as a single PDF.",
        )
        denial_file = st.file_uploader(
            "Denial letter PDF",
            type=["pdf"],
            key="denial_pdf",
            help="The carrier's denial letter as a PDF.",
        )

        submitted = st.form_submit_button("Analyze claim", type="primary")

    if not submitted:
        return

    errors: List[str] = []
    if policy_file is None:
        errors.append("Policy PDF is required.")
    if denial_file is None:
        errors.append("Denial letter PDF is required.")

    if errors:
        for err in errors:
            st.error(err)
        st.stop()

    try:
        policy_result, dispute_result = _run_full_analysis(
            claim_nickname=claim_nickname.strip(),
            state=state.strip(),
            policy_file=policy_file,
            denial_file=denial_file,
        )
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        st.stop()

    st.session_state[SESSION_KEY_POLICY] = policy_result
    st.session_state[SESSION_KEY_DISPUTE] = dispute_result
    st.session_state[SESSION_KEY_CLAIM_METADATA] = {
        "nickname": claim_nickname.strip(),
        "state": state.strip(),
        "policy_filename": policy_file.name,
        "denial_filename": denial_file.name,
    }

    # Save to database
    try:
        claim_id = save_claim(
            nickname=claim_nickname.strip(),
            state=state.strip(),
            policy_filename=policy_file.name,
            denial_filename=denial_file.name,
            report_json={
                "policy_result": policy_result,
                "dispute_result": dispute_result,
            },
        )
        st.success(f"Analysis complete. Saved as claim #{claim_id}.")
    except Exception as e:
        st.warning(f"Analysis complete, but failed to save to history: {e}")


def _render_results_section() -> None:
    if SESSION_KEY_DISPUTE not in st.session_state:
        st.info(
            "Upload a policy PDF and denial letter above to generate a dispute report.")
        return

    policy_result: Dict[str, Any] = st.session_state[SESSION_KEY_POLICY]
    dispute_result: Dict[str, Any] = st.session_state[SESSION_KEY_DISPUTE]
    dispute_report = dispute_result.get("dispute_report", {}) or {}

    st.divider()
    st.header("Results")

    policy_label = str(dispute_result.get("policy_id") or "policy")
    denial_label = str(dispute_result.get("denial_id") or "denial")
    claim_metadata = st.session_state.get(SESSION_KEY_CLAIM_METADATA, {}) or {}

    _render_hero(
        dispute_report,
        dispute_result.get("markdown", "") or "",
        policy_label,
        denial_label,
        policy_filename=claim_metadata.get("policy_filename"),
        denial_filename=claim_metadata.get("denial_filename"),
    )

    st.markdown("### Detailed dispute views")
    # Get section map from session state for citation linking
    section_map = st.session_state.get(SESSION_KEY_SECTION_MAP, {})
    _render_dispute_tabs(
        dispute_report,
        section_map,
        policy_artifacts=policy_result.get("artifacts", {}),
        dispute_artifacts=dispute_result.get("artifacts", {}),
    )

    st.markdown("### Full policy breakdown (optional)")
    _render_policy_breakdown(policy_result)


def _open_claim_history_detail(claim_id: int) -> None:
    st.session_state[SESSION_KEY_SELECTED_CLAIM] = claim_id
    st.session_state[SESSION_KEY_PAGE] = "Claim History"


def _render_recent_claims_card() -> None:
    if is_demo_force_on():
        return

    claims = get_all_claims()
    recent_claims = claims[:2]
    if not recent_claims:
        return

    st.markdown("### Recent claims")

    columns = st.columns(len(recent_claims))
    for col, claim in zip(columns, recent_claims):
        with col:
            with st.container(border=True):
                title = claim.nickname or f"Claim #{claim.id}"
                st.markdown(f"**{title}**")
                if claim.state:
                    st.caption(f"State: {claim.state}")
                st.caption(f"Created: {claim.created_at.strftime('%Y-%m-%d %H:%M')}")
                st.button(
                    "View",
                    key=f"recent_view_{claim.id}",
                    on_click=_open_claim_history_detail,
                    args=(claim.id,),
                )


def _render_claim_history_page() -> None:
    """Render the Claim History page."""
    st.header("Claim History")
    st.caption("View and reload previous claim analyses.")

    claims = get_all_claims()

    if not claims:
        st.info("No claims saved yet. Analyze a claim to see it here.")
        return

    # Check if we're viewing a specific claim
    if SESSION_KEY_SELECTED_CLAIM in st.session_state and st.session_state[SESSION_KEY_SELECTED_CLAIM]:
        claim_id = st.session_state[SESSION_KEY_SELECTED_CLAIM]
        claim = get_claim_by_id(claim_id)

        if claim:
            if st.button("← Back to claim list"):
                st.session_state[SESSION_KEY_SELECTED_CLAIM] = None
                st.rerun()

            st.subheader(f"Claim #{claim.id}: {claim.nickname or 'Untitled'}")

            col1, col2, col3 = st.columns(3)
            col1.metric("State", claim.state or "N/A")
            col2.metric("Policy", claim.policy_filename)
            col3.metric("Created", claim.created_at.strftime("%Y-%m-%d %H:%M"))

            st.caption(f"Denial file: {claim.denial_filename}")

            # Load the saved results
            policy_result = claim.report_json.get("policy_result", {})
            dispute_result = claim.report_json.get("dispute_result", {})
            dispute_report = dispute_result.get("dispute_report", {}) or {}

            policy_label = str(dispute_result.get("policy_id") or "policy")
            denial_label = str(dispute_result.get("denial_id") or "denial")

            st.divider()

            _render_hero(
                dispute_report,
                dispute_result.get("markdown", "") or "",
                policy_label,
                denial_label,
                policy_filename=claim.policy_filename,
                denial_filename=claim.denial_filename,
            )

            st.markdown("### Detailed dispute views")
            # Note: Section map not available for historical claims (in-memory only)
            _render_dispute_tabs(
                dispute_report,
                section_map=None,
                policy_artifacts=policy_result.get("artifacts", {}),
                dispute_artifacts=dispute_result.get("artifacts", {}),
            )

            if policy_result:
                st.markdown("### Full policy breakdown (optional)")
                _render_policy_breakdown(policy_result)

            return

    # Search box
    search_query = st.text_input(
        "Search claims",
        placeholder="Filter by nickname or policy filename...",
        label_visibility="collapsed",
    )

    # Filter claims based on search query
    if search_query:
        query_lower = search_query.lower()
        filtered_claims = [
            c for c in claims
            if query_lower in (c.nickname or "").lower()
            or query_lower in (c.policy_filename or "").lower()
        ]
    else:
        filtered_claims = claims

    # Show claim count
    if search_query:
        st.markdown(f"**{len(filtered_claims)} of {len(claims)} claim(s) match**")
    else:
        st.markdown(f"**{len(claims)} claim(s)**")

    if not filtered_claims:
        st.info("No claims match your search.")
        return

    for claim in filtered_claims:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])

            with col1:
                nickname = claim.nickname or "Untitled claim"
                st.markdown(f"**#{claim.id}** – {nickname}")
                st.caption(f"Policy: {claim.policy_filename}")

            with col2:
                st.write(f"State: {claim.state or 'N/A'}")

            with col3:
                st.write(claim.created_at.strftime("%Y-%m-%d %H:%M"))

            with col4:
                if st.button("View", key=f"view_{claim.id}"):
                    st.session_state[SESSION_KEY_SELECTED_CLAIM] = claim.id
                    st.rerun()

            with col5:
                if st.button("Delete", key=f"delete_{claim.id}", type="secondary"):
                    st.session_state[f"confirm_delete_{claim.id}"] = True
                    st.rerun()

            # Delete confirmation
            if st.session_state.get(f"confirm_delete_{claim.id}"):
                st.warning(f"Delete claim #{claim.id} ({nickname})? This cannot be undone.")
                conf_col1, conf_col2, _ = st.columns([1, 1, 4])
                with conf_col1:
                    if st.button("Yes, delete", key=f"confirm_yes_{claim.id}", type="primary"):
                        delete_claim(claim.id)
                        st.session_state[f"confirm_delete_{claim.id}"] = False
                        st.rerun()
                with conf_col2:
                    if st.button("Cancel", key=f"confirm_no_{claim.id}"):
                        st.session_state[f"confirm_delete_{claim.id}"] = False
                        st.rerun()

            st.divider()


def _render_new_claim_page() -> None:
    """Render the New Claim page."""
    _render_value_prop_intro()

    demo_force_on = is_demo_force_on()
    if st.session_state.get(SESSION_KEY_DEMO_MODE):
        if demo_force_on:
            st.warning(
                "Public demo safety mode is enabled. This hosted demo runs in "
                "deterministic Demo Mode, so live analysis and file uploads are "
                "disabled. For the full upload workflow, run the project locally "
                "with DEMO_FORCE_ON=false."
            )
        else:
            st.info(
                "Demo Mode is ON. Loading deterministic demo assets with zero API calls."
            )
        _load_demo_into_session()
        _render_results_section()
        return

    _render_intake_form()
    _render_recent_claims_card()
    _render_results_section()


def main() -> None:
    st.set_page_config(
        page_title="Policy Dispute AI",
        layout="wide",
    )

    st.title("Policy Dispute AI")

    # Sidebar navigation
    st.sidebar.title("Navigation")
    demo_force_on = is_demo_force_on()
    current_demo = st.session_state.get(SESSION_KEY_DEMO_MODE, False)

    if demo_force_on:
        demo_mode = True
        if not current_demo:
            for key in [
                SESSION_KEY_POLICY,
                SESSION_KEY_DISPUTE,
                SESSION_KEY_SECTION_MAP,
                SESSION_KEY_CLAIM_METADATA,
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state[SESSION_KEY_SELECTED_CLAIM] = None
        st.session_state[SESSION_KEY_DEMO_MODE] = True
        st.sidebar.info(
            "Public demo safety mode is locked on. Uploads and live analysis "
            "are disabled; run locally with DEMO_FORCE_ON=false for the full workflow."
        )
    else:
        demo_mode = st.sidebar.toggle(
            "Demo Mode (offline)",
            value=current_demo,
            help="Load deterministic demo assets with zero API calls.",
        )

    if demo_mode != current_demo:
        st.session_state[SESSION_KEY_DEMO_MODE] = demo_mode
        for key in [
            SESSION_KEY_POLICY,
            SESSION_KEY_DISPUTE,
            SESSION_KEY_SECTION_MAP,
            SESSION_KEY_CLAIM_METADATA,
        ]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state[SESSION_KEY_SELECTED_CLAIM] = None
        st.rerun()

    if demo_mode:
        st.sidebar.caption("Demo Mode enabled \u2013 uploads and API calls are disabled.")
    page = st.sidebar.radio(
        "Go to",
        ["New Claim", "Claim History"],
        label_visibility="collapsed",
        key=SESSION_KEY_PAGE,
    )

    if page == "New Claim":
        _render_new_claim_page()
    else:
        _render_claim_history_page()


if __name__ == "__main__":
    main()
