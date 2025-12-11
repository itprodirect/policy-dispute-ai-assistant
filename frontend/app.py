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
pdf_loader = importlib.import_module("src.pdf_loader")
summarizer_frontier = importlib.import_module("src.summarizer_frontier")
report_builder = importlib.import_module("src.report_builder")
schemas = importlib.import_module("src.schemas")

run_policy_analysis = demo_api.run_policy_analysis
load_pdf_text = pdf_loader.load_pdf_text
build_denial_aware_report = summarizer_frontier.build_denial_aware_report
render_dispute_markdown = report_builder.render_dispute_markdown
DisputeReport = schemas.DisputeReport


UPLOAD_DIR = Path("data/uploads")
SESSION_KEY_POLICY = "policy_result"
SESSION_KEY_DISPUTE = "dispute_result"


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


def _render_points(points: List[Dict[str, Any]] | None, empty_message: str) -> None:
    points = points or []
    if not points:
        st.write(empty_message)
        return

    for p in points:
        if isinstance(p, dict):
            text = str(p.get("text", "")).strip()
            citation = str(p.get("citation", "") or "").strip()
        else:
            text = str(p).strip()
            citation = ""

        if not text:
            continue

        if citation:
            st.markdown(f"- {text}  \n  _Citation: {citation}_")
        else:
            st.markdown(f"- {text}")


def _render_dispute_angles(angles: List[Dict[str, Any]] | None) -> None:
    angles = angles or []
    if not angles:
        st.write("No dispute angles identified.")
        return

    for a in angles:
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

        if cits:
            joined = ", ".join(cits)
            st.markdown(f"- {text}  \n  _Citations: {joined}_")
        else:
            st.markdown(f"- {text}")


def _render_hero(
    dispute_report: Dict[str, Any],
    dispute_markdown: str,
    policy_label: str,
    denial_label: str,
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

        # try to pull 2–3 “key takeaways” from B/E
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
        st.markdown("##### Actions")
        st.caption("Download or copy the full A–G dispute write-up.")
        st.download_button(
            "Download dispute report (Markdown)",
            data=dispute_markdown,
            file_name=f"{policy_label}__{denial_label}.dispute.md",
            mime="text/markdown",
        )
        st.caption(
            "Paste into Word/Docs as a starting draft. "
            "Always compare against the actual policy & denial."
        )


def _render_dispute_tabs(dispute_report: Dict[str, Any]) -> None:
    tab_ag, tab_policy_view, tab_denial_view, tab_debug = st.tabs(
        [
            "Dispute summary (A–G)",
            "Policy highlights",
            "Denial reasons",
            "Confidence / debug",
        ]
    )

    # A–G
    with tab_ag:
        st.markdown("### A–G dispute structure")

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
            )

        with st.expander("C – Key exclusions / limitations that may hurt the insured"):
            _render_points(
                dispute_report.get("exclusions_limitations"),
                "No exclusions / limitations identified.",
            )

        with st.expander("D – Denial reasons & cited clauses"):
            _render_points(
                dispute_report.get("denial_reasons"),
                "No denial reasons extracted from the letter.",
            )

        with st.expander("E – Possible dispute angles to explore"):
            _render_dispute_angles(dispute_report.get("dispute_angles"))

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
        )

        st.markdown("#### Exclusions / limitations (C)")
        _render_points(
            dispute_report.get("exclusions_limitations"),
            "No exclusions / limitations identified.",
        )

    # Denial slice
    with tab_denial_view:
        st.markdown("### Denial reasons & angles")

        st.markdown("#### Denial reasons (D)")
        _render_points(
            dispute_report.get("denial_reasons"),
            "No denial reasons extracted from the letter.",
        )

        st.markdown("#### Dispute angles (E)")
        _render_dispute_angles(dispute_report.get("dispute_angles"))

    # Minimal JSON view
    with tab_debug:
        st.markdown("### Raw A–G JSON (debug view)")
        st.json(dispute_report)


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
    progress_bar = st.progress(0)
    status = st.empty()

    # Step 1: policy
    status.write("Step 1/4 – Analyzing policy PDF…")
    progress_bar.progress(20)

    policy_result = run_policy_analysis(
        policy_file.getvalue(),
        policy_file.name,
    )

    # Step 2: denial text
    status.write("Step 2/4 – Saving and reading denial letter PDF…")
    progress_bar.progress(45)

    denial_path = _save_denial_pdf(denial_file, claim_nickname or None)
    denial_text = load_pdf_text(denial_path)

    # Step 3: A–G dispute report
    status.write(
        "Step 3/4 – Building A–G dispute report from policy + denial…")
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

    # attach IDs for nicer Markdown & UI labels
    dispute_obj.policy_id = (
        policy_result.get("policy_name")
        or Path(policy_result.get("source_path") or "").stem
        or "policy"
    )
    dispute_obj.denial_id = Path(denial_path).stem or "denial"

    markdown = render_dispute_markdown(dispute_obj)
    dispute_report_dict = dispute_obj.to_dict()

    progress_bar.progress(100)
    status.write("Step 4/4 – Done.")

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

    return policy_result, dispute_result


def _render_intake_form() -> None:
    st.header("New claim")

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

    st.success("Analysis complete.")


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

    _render_hero(
        dispute_report,
        dispute_result.get("markdown", "") or "",
        policy_label,
        denial_label,
    )

    st.markdown("### Detailed dispute views")
    _render_dispute_tabs(dispute_report)

    st.markdown("### Full policy breakdown (optional)")
    _render_policy_breakdown(policy_result)

    with st.expander("Artifacts / advanced debug", expanded=False):
        st.json(
            {
                "policy_artifacts": policy_result.get("artifacts", {}),
                "dispute_artifacts": dispute_result.get("artifacts", {}),
            }
        )


def main() -> None:
    st.set_page_config(
        page_title="Policy Dispute AI – Claim A–G Demo",
        layout="wide",
    )

    st.title("Policy Dispute AI – Claim A–G Demo")

    st.markdown(
        """
This internal demo ingests a homeowners policy PDF **and** a denial letter PDF and
produces a structured A–G dispute summary.

> **Important:** This is an AI-generated analysis of policy language and a denial letter.  
> It is **not** legal advice and does not create coverage, rights, or an attorney–client relationship.
"""
    )

    _render_intake_form()
    _render_results_section()


if __name__ == "__main__":
    main()
