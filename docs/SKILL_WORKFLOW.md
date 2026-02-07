# Skill Workflow (Policy Dispute AI Assistant)

This repo uses a lightweight “session logging” skill so work can resume fast and changes stay intentional.

## Why

- Restart in under 60 seconds
- Capture decisions (so you don’t re-decide)
- Keep momentum without writing essays

## Non-negotiables

- Create a new `logs/YYYY-MM-DD_<topic>.md` at the start of each session
- Capture: Goal, Decisions, Friction, Next — Immediate
- End with a Restart Test

(See `SESSION_LOGGER_RULES.md`.)

## How we work (per session)

1. Create the new session log from `logs/SESSION_TEMPLATE.md`
2. Define **one** goal (small enough to finish)
3. Use Claude Code / Codex to implement
4. Add a Restart Test (exact commands + first file to open)
5. Commit + push

## Repo quick commands

- Run app:
  - `streamlit run frontend/app.py`
- CLI (optional):
  - `python -m src.run_baseline_policy_summary path/to/policy.pdf`
  - `python -m src.run_denial_summary data/processed/policy.json path/to/denial.txt`
  - `python -m src.report_builder data/processed/`

## Safety defaults

- Prefer `SAFE_MODE=true`
- Prefer `PERSIST_RAW_TEXT=false`
- Do not commit real client data or outputs containing PII
