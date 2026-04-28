# Current State

Last updated: 2026-04-28

Phase 1 is complete. The app remains a Streamlit research prototype with deterministic Demo Mode, a live API-backed local workflow, README screenshots, and explicit AI-generated / not-legal-advice framing.

## Sales-Proof Positioning

As of 2026-04-28, `docs/10-sales-proof.md` records the portfolio and sales-proof readout. The repo is credible as a private sales demo, website case-study source, and technical proof of AI-assisted insurance document workflow capability.

Do not position it as production-ready, legally accurate, client-proven, or a hosted secure SaaS product. The safest current positioning is: internal research prototype and human-review workflow accelerator for homeowners policy and denial-letter triage.

## Completed Phase 1A Issues

- #12 `DEMO_FORCE_ON` hosted demo safety.
- #13 Hero/value proposition and research framing.
- #14 Confidence tab cleanup.
- #15 README screenshots and repo first-impression polish.
- #16 Progress UI and step labels.
- #17 Recent claims card.

## Recent PRs

- PR #34: docs wrap for Phase 1 status and boundaries.
- PR #35: README screenshot polish with five committed demo-safe screenshots.
- PR #38: GitHub Actions CI for pytest.
- PR #39: stale `frontend/data/` artifact cleanup and runtime artifact docs.
- PR #41: Demo Mode citation/source accordions.
- PR #42: Demo source-map loading hardening.
- PR #43: human-readable export context and human/AI export grouping.
- PR #54: Phase 2 baseline benchmark harness and checked-in no-API baseline report.
- PR #56: #47 Responses API migration for the single OpenAI wrapper.
- PR #58: #48 Structured Outputs for final dispute report generation only.
- PR #60: #49 stage-specific model configuration via `OPENAI_MODEL_<STAGE_UPPER>`.
- PR #62: #50 bounded concurrency for section-summary LLM calls.
- PR #64: #51 redundant live policy PDF reprocessing cleanup.
- PR #66: #52 focused-analysis mode.
- #53: final Phase 2 benchmark comparison report.

## Current Phase

Phase 1A demo polish is complete.

Phase 1B technical closeout is complete with #19 GitHub Actions CI for pytest and #22 stale `frontend/data/` artifact cleanup.

Phase 1C local/demo trust polish is complete with #21 Demo Mode citation/source accordions, Demo source-map loading hardening, and #23 export context polish.

#18 Streamlit Community Cloud deployment prep is intentionally deferred because hosted deployment is not needed yet and adds surface area.

#20 walkthrough video and screenshot recipe is intentionally deferred because walkthrough/video work should wait until after Phase 2 stabilizes.

Phase 2 baseline benchmarking is complete via #46 / PR #54. #47 Responses API migration is complete via PR #56. #48 Structured Outputs is complete via PR #58 for final dispute report generation only. #49 stage-specific model configuration is complete via PR #60. #50 section-summary latency reduction is complete via PR #62. #51 redundant live policy PDF reprocessing cleanup is complete via PR #64. #52 focused-analysis mode is complete via PR #66. #53 final Phase 2 benchmark comparison reporting is complete.

Stage-specific model overrides are available through `OPENAI_MODEL_<STAGE_UPPER>`, such as `OPENAI_MODEL_SECTION_SUMMARY` and `OPENAI_MODEL_DISPUTE_REPORT`. Default model behavior is unchanged unless a per-stage override is explicitly set.

Section summaries intentionally remain on the default `json_object` mode. Section-summary calls now use bounded concurrency via `ThreadPoolExecutor`; `SECTION_SUMMARY_MAX_WORKERS` defaults to 4, and `SECTION_SUMMARY_MAX_WORKERS=1` forces sequential behavior.

PR #64 removed live policy PDF reprocessing by reusing the first-pass raw sections for the in-memory citation source map. `section_text_map` is stripped before claim persistence to avoid persisting raw policy text with saved claims.

PR #66 added explicit opt-in focused-analysis mode. Full analysis remains the default. Focused mode filters policy sections before section-summary LLM calls to a canonical core-section allowlist: `DEFINITIONS`, `EXCLUSIONS`, `CONDITIONS`, `COVERAGE A - DWELLING`, `COVERAGE B - OTHER STRUCTURES`, `COVERAGE C - PERSONAL PROPERTY`, and `COVERAGE D - LOSS OF USE`. Focused mode skips obvious meta sections. It did not change prompts, report schemas/dataclasses, Structured Outputs behavior, model defaults, or stage-specific model config. Section-summary concurrency behavior is unchanged except that focused mode filters the input section list before `executor.map`.

Focused mode preserves citation/source accordion behavior: `section_text_map` still comes from full raw sections, while raw policy section text is still stripped before claim persistence. Export context now includes a Mode row, including Demo Mode plus Focused/Full combinations. PR #66 validation: `python -m pytest -q` passed with 85 tests.

The final Phase 2 benchmark comparison report is `benchmarks/phase2-final.md`. It keeps `benchmarks/phase2-baseline.md` as the historical before-state, records deterministic demo parity, current live full/focused measurements for the HO3 TRUE FL fixture, and documents limitations around live baselines, token/cost telemetry, and quality scoring.

Phase 2 is complete through #53. #18 Streamlit Community Cloud deployment prep and #20 walkthrough/video recipe remain deferred post-Phase-2 work.

## Local Cleanup

After PR #35 merged, local screenshot candidate files were moved outside the repo to:

`C:\Users\user\Desktop\policy-dispute-screenshot-candidates-archive\`

The repo working tree was clean after that cleanup.
