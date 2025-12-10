import importlib
import sys
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st
from pypdf import PdfReader

# Ensure project root is on sys.path so we can import "src.*"
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import demo_api dynamically so import sorters don't reorder it
demo_api = importlib.import_module("src.demo_api")
run_policy_analysis = demo_api.run_policy_analysis
run_dispute_analysis = demo_api.run_dispute_analysis


def _render_bullet_list(items: List[str]) -> None:
    """Render a simple list of strings as markdown bullets."""
    if not items:
        st.caption("None noted.")
        return
    for item in items:
        st.markdown(f"- {item}")


def _render_section_summary(section: Dict[str, Any]) -> None:
    """Claim-facing view of a single policy section."""
    st.write(
        section.get("summary_overall", "").strip()
        or "_No plain-English summary available._"
    )

    st.markdown("**Key coverages**")
    _render_bullet_list(section.get("key_coverages", []))

    st.markdown("**Key exclusions / limitations**")
    _render_bullet_list(section.get("key_exclusions", []))

    st.markdown("**Notable conditions / duties**")
    _render_bullet_list(section.get("conditions_notable", []))

    st.markdown("**Potential dispute angles**")
    _render_bullet_list(section.get("potential_dispute_angles", []))


def _extract_denial_text(uploaded_file) -> str:
    """Convert an uploaded denial file (txt/pdf) into plain text."""
    if uploaded_file is None:
        raise ValueError("No denial file provided")

    name = uploaded_file.name or "denial"
    suffix = name.lower().rsplit(".", 1)[-1]

    raw = uploaded_file.getvalue()

    if suffix == "txt":
        return raw.decode("utf-8", errors="ignore")

    if suffix == "pdf":
        reader = PdfReader(BytesIO(raw))
        texts: List[str] = []
        for page in reader.pages:
            texts.append(page.extract_text() or "")
        return "\n\n".join(texts)

    raise ValueError(f"Unsupported denial file type: {suffix}")


def main() -> None:
    st.set_page_config(
        page_title="Policy Dispute AI – Demo",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    st.title("Policy Dispute AI – v0 Frontend")
    st.write(
        "This internal demo ingests a homeowners policy PDF and produces a structured, dispute-focused summary."
    )
    st.caption(
        "Important: This is an AI-generated summary of policy language only. "
        "It is not legal advice and does not create coverage, rights, or an attorney–client relationship."
    )

    # Session state setup
    if "policy_result" not in st.session_state:
        st.session_state["policy_result"] = None
    if "policy_error" not in st.session_state:
        st.session_state["policy_error"] = None
    if "dispute_result" not in st.session_state:
        st.session_state["dispute_result"] = None
    if "dispute_error" not in st.session_state:
        st.session_state["dispute_error"] = None

    st.markdown("---")

    # --- Step 1: Policy upload + analysis ---
    st.subheader("Step 1 – Upload policy and run analysis")

    uploaded_policy = st.file_uploader(
        "Upload a policy PDF",
        type=["pdf"],
        help="HO3 policy PDF, up to ~200MB.",
    )

    if uploaded_policy is not None:
        st.info(f"Selected file: **{uploaded_policy.name}**")

    run_policy_col, _ = st.columns([1, 4])
    with run_policy_col:
        run_policy_clicked = st.button(
            "Run analysis",
            type="primary",
            disabled=uploaded_policy is None,
            key="run_policy",
        )

    if run_policy_clicked and uploaded_policy is not None:
        st.session_state["policy_error"] = None
        st.session_state["policy_result"] = None
        st.session_state["dispute_result"] = None  # reset downstream state

        with st.spinner("Analyzing policy… this can take a bit."):
            try:
                result = run_policy_analysis(
                    uploaded_policy.getvalue(), uploaded_policy.name
                )
            except Exception as exc:  # noqa: BLE001
                st.session_state["policy_error"] = str(exc)
            else:
                st.session_state["policy_result"] = result

    if st.session_state["policy_error"]:
        st.error(f"Policy analysis failed: {st.session_state['policy_error']}")

    result = st.session_state["policy_result"]

    if result:
        st.success("Analysis complete.")

        stats = result.get("stats", {})
        cols = st.columns(3)
        cols[0].metric("Total sections", stats.get("num_sections", 0))
        cols[1].metric("UNKNOWN sections", stats.get(
            "num_unknown_sections", 0))
        cols[2].metric("Meta sections", stats.get("num_meta_sections", 0))

        st.markdown("### Views")

        (
            tab_summary,
            tab_dev,
            tab_markdown,
            tab_artifacts,
            tab_dispute,
        ) = st.tabs(
            [
                "Summary (claim-facing)",
                "Sections (dev view)",
                "Markdown report",
                "Artifacts / debug",
                "Dispute report (policy + denial)",
            ]
        )

        # Claim-facing summary view
        with tab_summary:
            st.caption("Substantive sections only (no raw text).")

            for section in result.get("sections_substantive", []):
                name = section.get("section_name") or "Unnamed section"
                with st.expander(name, expanded=False):
                    _render_section_summary(section)

        # Developer view – raw section payloads
        with tab_dev:
            st.caption("Raw section payloads as returned from the backend.")
            st.json(
                {
                    "substantive": result.get("sections_substantive", []),
                    "meta": result.get("sections_meta", []),
                }
            )

        # Markdown report for policy-only analysis
        with tab_markdown:
            st.caption("Full Markdown report generated from PolicyReport.")
            st.code(result.get("markdown", ""), language="markdown")

        # Artifact paths and config flags
        with tab_artifacts:
            st.caption("Paths to artifacts on disk + privacy flags.")
            st.json(result.get("artifacts", {}))

        # --- Step 2: Dispute report (policy + denial) ---
        with tab_dispute:
            st.caption(
                "Combine the policy summary with a denial letter to generate an A–G style dispute report. "
                "Run Step 1 first, then upload a denial letter here."
            )

            denial_file = st.file_uploader(
                "Upload denial letter (.txt or .pdf)",
                type=["txt", "pdf"],
                key="denial_file",
                help="For v0, plain text or simple PDF denial letters work best.",
            )

            run_dispute_clicked = st.button(
                "Run dispute analysis",
                type="primary",
                disabled=denial_file is None,
                key="run_dispute",
            )

            if run_dispute_clicked and denial_file is not None:
                st.session_state["dispute_error"] = None
                st.session_state["dispute_result"] = None

                artifacts = result.get("artifacts", {})
                summary_json_path = artifacts.get("summary_json")

                if not summary_json_path:
                    st.session_state[
                        "dispute_error"
                    ] = "Missing summary_json path in artifacts – cannot run dispute analysis."
                else:
                    try:
                        denial_text = _extract_denial_text(denial_file)
                        dispute = run_dispute_analysis(
                            policy_summary_json_path=summary_json_path,
                            denial_text=denial_text,
                            denial_id=Path(denial_file.name).stem,
                        )
                    except Exception as exc:  # noqa: BLE001
                        st.session_state["dispute_error"] = str(exc)
                    else:
                        st.session_state["dispute_result"] = dispute

            if st.session_state["dispute_error"]:
                st.error(
                    f"Dispute analysis failed: {st.session_state['dispute_error']}")

            dispute_result = st.session_state["dispute_result"]
            if dispute_result:
                report = dispute_result.get("dispute_report", {}) or {}

                st.success("Dispute report generated.")

                st.markdown("#### A. Plain-English overview")
                st.write(
                    report.get("plain_summary", "").strip()
                    or "_No overview provided._"
                )

                st.markdown("#### B. Coverage highlights supporting the claim")
                highlights = report.get("coverage_highlights", [])
                if highlights:
                    for pt in highlights:
                        text = pt.get("text", "")
                        citation = pt.get("citation")
                        if citation:
                            st.markdown(f"- {text} _(source: {citation})_")
                        else:
                            st.markdown(f"- {text}")
                else:
                    st.caption("No specific coverage highlights identified.")

                st.markdown("#### C. Key exclusions / limitations")
                exclusions = report.get("exclusions_limitations", [])
                if exclusions:
                    for pt in exclusions:
                        text = pt.get("text", "")
                        citation = pt.get("citation")
                        if citation:
                            st.markdown(f"- {text} _(source: {citation})_")
                        else:
                            st.markdown(f"- {text}")
                else:
                    st.caption(
                        "No specific exclusions/limitations highlighted.")

                st.markdown("#### D. Stated reasons for denial")
                denial_reasons = report.get("denial_reasons", [])
                if denial_reasons:
                    for pt in denial_reasons:
                        text = pt.get("text", "")
                        citation = pt.get("citation")
                        if citation:
                            st.markdown(f"- {text} _(source: {citation})_")
                        else:
                            st.markdown(f"- {text}")
                else:
                    st.caption("No explicit denial reasons extracted.")

                st.markdown("#### E. Potential dispute angles")
                angles = report.get("dispute_angles", [])
                if angles:
                    for angle in angles:
                        text = angle.get("text", "")
                        cites = angle.get("citations", []) or []
                        if cites:
                            st.markdown(
                                f"- {text}  \n  _Citations:_ {', '.join(cites)}"
                            )
                        else:
                            st.markdown(f"- {text}")
                else:
                    st.caption("No specific dispute angles identified.")

                st.markdown(
                    "#### F. Missing information / suggested follow-up")
                missing = report.get("missing_info", [])
                _render_bullet_list(missing)

                st.markdown("#### G. Confidence / verification notes")
                conf = report.get("confidence", {}) or {}
                score = conf.get("score")
                notes = conf.get("notes", "").strip()
                verify_clauses = conf.get("verify_clauses", []) or []

                if score is not None:
                    st.write(
                        f"Estimated confidence score: **{score:.2f}** (0–1, heuristic only)."
                    )
                if notes:
                    st.write(notes)
                if verify_clauses:
                    st.markdown("**Clauses / documents to verify:**")
                    _render_bullet_list(verify_clauses)

                with st.expander("Raw dispute JSON (debug)"):
                    st.json(dispute_result.get("dispute_report", {}))

                with st.expander("Markdown dispute report (debug)"):
                    st.code(dispute_result.get(
                        "markdown", ""), language="markdown")


if __name__ == "__main__":
    main()
