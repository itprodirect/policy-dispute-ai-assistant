# Current State

Last updated: 2026-04-26

Phase 1 is complete. The app remains a Streamlit research prototype with deterministic Demo Mode, a live API-backed local workflow, README screenshots, and explicit AI-generated / not-legal-advice framing.

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

## Current Phase

Phase 1A demo polish is complete.

Phase 1B technical closeout is complete with #19 GitHub Actions CI for pytest and #22 stale `frontend/data/` artifact cleanup.

Phase 1C local/demo trust polish is complete with #21 Demo Mode citation/source accordions, Demo source-map loading hardening, and #23 export context polish.

#18 Streamlit Community Cloud deployment prep is intentionally deferred because hosted deployment is not needed yet and adds surface area.

#20 walkthrough video and screenshot recipe is intentionally deferred because walkthrough/video work should wait until after Phase 2 stabilizes.

Phase 2 baseline benchmarking is complete via #46 / PR #54. #47 Responses API migration is complete via PR #56. #48 Structured Outputs is complete via PR #58 for final dispute report generation only. #49 stage-specific model configuration is complete via PR #60. #50 section-summary latency reduction is complete via PR #62. #51 redundant live policy PDF reprocessing cleanup is complete via PR #64.

Stage-specific model overrides are available through `OPENAI_MODEL_<STAGE_UPPER>`, such as `OPENAI_MODEL_SECTION_SUMMARY` and `OPENAI_MODEL_DISPUTE_REPORT`. Default model behavior is unchanged unless a per-stage override is explicitly set.

Section summaries intentionally remain on the default `json_object` mode. Section-summary calls now use bounded concurrency via `ThreadPoolExecutor`; `SECTION_SUMMARY_MAX_WORKERS` defaults to 4, and `SECTION_SUMMARY_MAX_WORKERS=1` forces sequential behavior.

PR #64 removed live policy PDF reprocessing by reusing the first-pass raw sections for the in-memory citation source map. `section_text_map` is stripped before claim persistence to avoid persisting raw policy text with saved claims.

The next intended issue is #52 focused-analysis mode. Do not start #52 as part of post-#64 hygiene; no focused-analysis mode, prompt changes, dataclass/schema refactors, Structured Outputs changes, model configuration changes, section-summary concurrency changes, retry changes, telemetry semantics changes, benchmark changes, deployment/auth/storage work, or PDF export work have started.

## Local Cleanup

After PR #35 merged, local screenshot candidate files were moved outside the repo to:

`C:\Users\user\Desktop\policy-dispute-screenshot-candidates-archive\`

The repo working tree was clean after that cleanup.
