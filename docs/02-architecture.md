# Architecture

This is the current high-level architecture. It describes what exists now; it does not propose a redesign.

## Frontend

- `frontend/app.py` is the current Streamlit v1 UX.
- `frontend/app_v0_minimul.py` is legacy reference UI.
- The app has a New Claim page, Claim History page, Demo Mode controls, upload flow, progress status, results tabs, and report download actions.

## Modes

- Demo Mode loads tracked deterministic artifacts from `assets/demo/demo.json` and `assets/demo/demo.report.md`.
- `DEMO_FORCE_ON=true` locks hosted demos into deterministic Demo Mode, disables uploads and live analysis, and allows booting without `OPENAI_API_KEY`.
- Normal local mode uses uploaded policy and denial PDFs, extracts text, calls OpenAI through the existing client, and renders the resulting dispute report.

## Backend Pipeline

- `src/pdf_loader.py` extracts text from PDFs.
- `src/sectioning.py` splits policy text into logical HO3-oriented sections.
- `src/summarizer_frontier.py` summarizes policy sections and builds denial-aware A-G dispute reports.
- `src/schemas.py` defines the report data structures.
- `src/demo_api.py` provides service-style helpers used by the Streamlit frontend.
- `src/report_builder.py` renders Markdown and Word exports.
- `src/llm_client.py` is the current OpenAI wrapper.

## Reports and Exports

The report structure follows A-G:

- A: Plain-language overview.
- B: Coverage highlights supporting the insured.
- C: Exclusions or limitations.
- D: Denial reasons and cited clauses.
- E: Possible dispute angles.
- F: Missing information and next steps.
- G: Confidence notes and clauses to verify.

The UI renders this structure in tabs and offers Markdown and Word downloads. All output remains AI-generated and must be checked against the actual policy and denial.

## Local Artifacts

- `data/uploads/` holds local upload cache files.
- `data/processed/` and `data/processed_safe/` hold local generated outputs.
- `data/claims.db` stores local claim history.
- Runtime artifacts and real client data should not be committed.
