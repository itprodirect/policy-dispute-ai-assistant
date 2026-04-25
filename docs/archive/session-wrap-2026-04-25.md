Archived note: This document is preserved for project history. It may contain stale issue status or paths. See docs/01-current-state.md and docs/03-roadmap.md for current status.

# Session Wrap - 2026-04-25

## Completed foundation work

- PR [#25](https://github.com/itprodirect/policy-dispute-ai-assistant/pull/25) completed issue [#10](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/10): Demo Mode now loads tracked assets from `assets/demo/demo.json` and `assets/demo/demo.report.md`.
- PR [#26](https://github.com/itprodirect/policy-dispute-ai-assistant/pull/26) added shared repo agent guidance and the v1.5 demo polish audit/issue plan.
- PR [#27](https://github.com/itprodirect/policy-dispute-ai-assistant/pull/27) completed issue [#24](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/24): `.env.example` is safe by default and `requirements.txt` pins direct runtime dependencies.

## Completed Phase 1 demo-hardening work

- Issue [#12](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/12): `DEMO_FORCE_ON` hosted demo safety. Hosted demos can be locked to deterministic Demo Mode, uploads/live analysis are disabled, and the app can boot without `OPENAI_API_KEY`.
- Issue [#13](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/13): New Claim value proposition and research / not-legal-advice framing.
- Issue [#14](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/14): Confidence tab cleanup. Raw A-G JSON and artifact/debug details are hidden by default behind collapsed developer expanders.
- Issue [#16](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/16): Live-analysis progress UI now uses a cleaner `st.status`-style step flow.
- Issue [#17](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/17): New Claim page shows up to two Recent claims when local history exists and reuses the existing Claim History detail view.

## Current repo state

- Demo Mode works from tracked demo-safe assets and no longer depends on gitignored `data/processed/demo/`.
- `DEMO_FORCE_ON=true` is the public-demo safety mode: deterministic results render, uploads/live analysis are unavailable, and no OpenAI key is required to boot.
- `DEMO_FORCE_ON=false` remains the normal local mode with full policy/denial upload workflow and LLM-backed analysis.
- Results are more screenshot-ready: the hero/value-prop framing is clearer, confidence has its own tab, and raw debug JSON is hidden by default.
- Claim History behavior remains intact, with a small Recent claims entry point on the New Claim page for existing local runs.
- `.env.example` defaults to `SAFE_MODE=true` and `PERSIST_RAW_TEXT=false`.
- `requirements.txt` pins the direct runtime dependencies used by the current working environment.
- Validation from PR #27:
  - `python -m pytest -q` -> 20 passed.
  - Clean venv install from `requirements.txt` succeeded.
  - Import checks passed for `streamlit`, `openai`, `pypdf`, `docx`, and `dotenv`.

## Boundaries preserved

- No LLM prompt changes.
- No report schema changes.
- No model/API modernization.
- No auth, billing, user-management, or backend rebuild.
- This phase was demo hardening, not a product rebuild.

## Follow-up risk

- `wandb==0.24.0` is pinned to the known working local version, but pip warned that this candidate is yanked upstream. Leave it unchanged in demo/UI work; handle it in a focused dependency cleanup issue or PR.

## Remaining Phase 1 / portfolio follow-ups

- Issue [#15](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/15) remains open for README screenshots and repo first-impression polish. Do not close it from docs-wrap work.
- Curate the saved screenshots later; add `docs/screenshots/` only if selected screenshots are committed.
- Capture a real Confidence tab screenshot if one is missing.
- Before release/demo recording, run one live API-backed analysis with valid PDFs to visually confirm the progress UI.
- Consider issue [#11](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/11) later if a true live sample-input path is still desired.
