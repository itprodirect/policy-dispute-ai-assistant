# Repository Guidelines

## Project Structure & Module Organization
- `src/` contains the core Python pipelines: PDF ingestion, sectioning, LLM calls, dispute report building, telemetry, and config.
- `frontend/app.py` is the main Streamlit app; `frontend/app_v0_minimul.py` is legacy reference UI.
- `tests/` holds `pytest` tests (currently focused on citation-linking behavior).
- `data/` stores local runtime artifacts: `raw_policies/`, `raw_denials/`, `uploads/`, `processed/`, `processed_safe/`, and `claims.db`.
- `docs/`, `README.md`, and `RUNBOOK.md` document workflow and operational notes.

## Build, Test, and Development Commands
- `python -m venv .venv` then `.\.venv\Scripts\Activate.ps1`: create and activate the local environment (Windows).
- `pip install -r requirements.txt`: install runtime and dev dependencies.
- `streamlit run frontend/app.py`: run the local UI at `http://localhost:8501`.
- `python -m pytest -q`: run the automated test suite.
- `python -m src.run_baseline_policy_summary data/raw_policies/HO3_TRUE_FL_2021.pdf`: summarize a policy PDF.
- `python -m src.run_denial_summary data/processed/HO3_TRUE_FL_2021.json data/raw_denials/HO3_TRUE_FL_2021_denial.txt`: generate an A-G dispute report from policy summary + denial text.
- `python -m src.report_builder data/processed`: render Markdown reports from summary JSON files.

## Coding Style & Naming Conventions
- Target Python 3.10+ with 4-space indentation, type hints, and small, composable functions.
- Follow existing naming: `snake_case` for modules/functions/variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- Keep domain logic in `src/`; keep UI-only logic in `frontend/`.
- Match current import grouping and docstring style; no separate formatter config is checked in.

## Testing Guidelines
- Framework: `pytest`; tests follow `tests/test_*.py`, `Test*` classes, and `test_*` functions.
- Add tests for new parsing/matching logic and for regressions found in Streamlit flows.
- Run `python -m pytest -q` before opening a PR; include failing-case coverage when fixing bugs.

## Commit & Pull Request Guidelines
- Use concise, imperative commit subjects. Existing history uses both plain subjects and prefixes like `feat:`, `fix:`, and `chore:`.
- Keep each commit focused (single concern where possible).
- PRs should include: purpose, key file/module changes, test evidence (command + result), and screenshots for UI changes.

## Security & Configuration Tips
- Start from `.env.example`; set `OPENAI_API_KEY` locally.
- Prefer `SAFE_MODE=true` and `PERSIST_RAW_TEXT=false` for local privacy.
- Never commit real client documents or outputs containing PII.
