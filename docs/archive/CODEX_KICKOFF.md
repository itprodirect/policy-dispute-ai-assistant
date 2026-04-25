Archived note: This document is preserved for project history. It may contain stale issue status or paths. See docs/01-current-state.md and docs/03-roadmap.md for current status.

# Codex Kickoff — Demo Mode (Offline)

## Goal

Implement Demo Mode (offline) so Streamlit can render a full report with **zero API calls**.

## Deterministic demo assets

- `data/processed/demo/demo.json`
- `data/processed/demo/demo.report.md`

If missing, copy from:

- `data/processed/HO3_ISO_1999_III_SAMPLE__1768603155` and `.report`

## Requirements

- Add UI toggle in `frontend/app.py`: Demo Mode vs Live Mode
- When Demo Mode is ON:
  - Do not call any OpenAI client functions
  - Load and render results from the deterministic demo files
- When Demo Mode is OFF:
  - Existing behavior unchanged

## Deliverables

- Working Demo Mode toggle
- Update RUNBOOK with Demo Mode steps
- Minimal code change surface area
