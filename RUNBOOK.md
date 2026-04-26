# Runbook (policy-dispute-ai-assistant)

## Purpose

Local-first Streamlit app that analyzes an HO3 policy + denial letter to generate a structured dispute report (A–G) for adjusters/attorneys.

This is a drafting / decision-support tool — outputs require human review.

---

## Quick Start (Live Mode)

1. Activate venv
2. Install deps:
   - `pip install -r requirements.txt`
3. Create `.env` (or set env vars) with:
   - `OPENAI_API_KEY=...`
   - recommended: `SAFE_MODE=true`
4. Run:
   - `streamlit run frontend/app.py`

---

## Demo Mode (Offline / Conference Mode)

Goal: Run the full demo with **zero API calls**.

### Demo assets

Deterministic demo files live here:

- `assets/demo/demo.json`
- `assets/demo/demo.report.md`
- `assets/demo/section_text.json`

### Steps

1. Run:
   - `streamlit run frontend/app.py`
2. Toggle **Demo Mode (offline)** ON
3. Confirm results render end-to-end (no key required)

### If demo assets are missing

The demo assets are tracked in the repository. Restore these files from git:

- `assets/demo/demo.json`
- `assets/demo/demo.report.md`
- `assets/demo/section_text.json`

Do not rebuild this bundle from real client claim data.

---

## Common Commands

- Run app:
  - `streamlit run frontend/app.py`

- CLI (optional):
  - `python -m src.run_baseline_policy_summary path/to/policy.pdf`
  - `python -m src.run_denial_summary data/processed/policy.json path/to/denial.txt`
  - `python -m src.report_builder data/processed/`

---

## Local Runtime Artifacts

The canonical local artifact location is the repository-root `data/` directory:

- `data/uploads/` for Streamlit upload cache files
- `data/processed/` for normal generated summaries and reports
- `data/processed_safe/` for `SAFE_MODE=true` generated outputs
- `data/claims.db` for local claim history

`frontend/data/` is a stale artifact path from earlier local runs. It is not read by the current app or backend and can be removed if it appears.

---

## Troubleshooting

### Streamlit boots but errors when demo mode is on

- Confirm both files exist:
  - `assets/demo/demo.json`
  - `assets/demo/demo.report.md`

### Live mode fails due to missing key

- Ensure `.env` exists and contains `OPENAI_API_KEY`
- Or set the environment variable in your shell/session

### “pytest not installed”

If you want tests as a status check:

- `pip install pytest`
- `python -m pytest -q`

---

## Safety defaults

Recommended for local dev and demos:

- `SAFE_MODE=true`
- `PERSIST_RAW_TEXT=false`
  Never commit real client documents or outputs containing PII.
