import importlib
import sys
from pathlib import Path

import streamlit as st

# Ensure project root is on sys.path so we can import "src.*"
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import demo_api dynamically so import sorters don't reorder it
demo_api = importlib.import_module("src.demo_api")
run_policy_analysis = demo_api.run_policy_analysis


st.set_page_config(
    page_title="Policy Dispute AI – Demo",
    layout="wide",
)

st.title("Policy Dispute AI – v0 Frontend")

st.markdown(
    """
This internal demo ingests a homeowners policy PDF and produces a structured, dispute-focused summary.

> **Important:** This is an AI-generated summary of policy language only.  
> It is **not** legal advice and does not create coverage, rights, or an attorney–client relationship.
"""
)

st.divider()

uploaded_file = st.file_uploader("Upload a policy PDF", type=["pdf"])

if uploaded_file is not None:
    st.info(f"Selected file: `{uploaded_file.name}`")

run_clicked = st.button(
    "Run analysis",
    type="primary",
    disabled=uploaded_file is None,
)

if run_clicked and uploaded_file is not None:
    with st.spinner("Analyzing policy… this can take a bit."):
        try:
            result = run_policy_analysis(
                uploaded_file.getvalue(),
                uploaded_file.name,
            )
        except Exception as e:
            st.error(f"Analysis failed: {e}")
        else:
            st.success("Analysis complete.")

            stats = result.get("stats", {})

            # High-level stats
            c1, c2, c3 = st.columns(3)
            c1.metric("Total sections", stats.get("num_sections", 0))
            c2.metric("UNKNOWN sections", stats.get("num_unknown_sections", 0))
            c3.metric("Meta sections", stats.get("num_meta_sections", 0))

            st.subheader("Views")

            tab_summary, tab_sections, tab_markdown, tab_artifacts = st.tabs(
                [
                    "Summary (claim-facing)",
                    "Sections (dev view)",
                    "Markdown report",
                    "Artifacts / debug",
                ]
            )

            # Summary: substantive sections in a claim-facing view
            with tab_summary:
                st.caption("Substantive sections only (no raw text).")
                for s in result.get("sections_substantive", []):
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

            # Dev-ish view: show raw section dicts (minus raw_text)
            with tab_sections:
                st.caption(
                    "Substantive + meta sections as JSON (for debugging).")
                st.json(
                    {
                        "substantive": result.get("sections_substantive", []),
                        "meta": result.get("sections_meta", []),
                    }
                )

            # Markdown report
            with tab_markdown:
                st.caption("Full Markdown report generated from PolicyReport.")
                st.code(result.get("markdown", ""), language="markdown")

            # Artifact paths and config flags
            with tab_artifacts:
                st.caption("Paths to artifacts on disk + privacy flags.")
                st.json(result.get("artifacts", {}))
