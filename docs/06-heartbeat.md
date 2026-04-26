# Heartbeat

Last updated: 2026-04-26 00:27 ET

## Current Phase
- Phase 1 is complete: Phase 1A demo polish, Phase 1B technical closeout, and Phase 1C local/demo trust polish.
- Phase 2 baseline benchmarking is complete via #46 / PR #54.
- Phase 2 Responses API migration is complete via #47 / PR #56.
- Phase 2 Structured Outputs for final dispute report generation is complete via #48 / PR #58.
- Phase 2 stage-specific model configuration is complete via #49 / PR #60.
- Phase 2 section-summary latency reduction is complete via #50 / PR #62.
- Phase 2 redundant live policy PDF reprocessing cleanup is complete via #51 / PR #64.

## Current Truth
- PR #44 wrapped Phase 1 and handed off to Phase 2 baseline benchmarking.
- PR #54 merged the repeatable Phase 2 before-state benchmark harness.
- PR #56 migrated the single OpenAI wrapper to the Responses API without prompt, schema, model, retry, telemetry, PDF-processing, benchmark, or pipeline optimization changes.
- PR #58 added Responses API Structured Outputs strict JSON Schema mode only for final dispute report generation. Section summaries intentionally remain on default `json_object` mode.
- PR #60 added optional stage-specific model overrides through `OPENAI_MODEL_<STAGE_UPPER>`, while preserving default model behavior unless per-stage overrides are explicitly set.
- PR #62 added bounded concurrency for section-summary LLM calls using `ThreadPoolExecutor`. `SECTION_SUMMARY_MAX_WORKERS` defaults to 4, and `SECTION_SUMMARY_MAX_WORKERS=1` forces sequential behavior.
- PR #64 removed live policy PDF reprocessing by reusing first-pass raw sections for the in-memory citation source map.
- PR #64 strips `section_text_map` before claim persistence to avoid persisting raw policy text.
- The checked-in baseline is deterministic demo-bundle mode with no API calls.
- #21 Demo Mode citation/source accordions are complete via PR #41.
- Demo source-map loading hardening is complete via PR #42.
- #23 human-readable export context and human/AI export grouping are complete via PR #43.
- The repo remains a research prototype with AI-generated and not-legal-advice framing.

## Next Action
- Start #52 focused-analysis mode only. Do not bundle prompt rewrites, report schema changes, Structured Outputs changes, model configuration changes, section-summary concurrency changes, retry changes, telemetry semantics changes, benchmark changes, deployment/auth/storage work, PDF export work, or unrelated refactors.

## Deferred
- #18 Streamlit deployment prep — deferred because hosted deployment is not needed yet and adds surface area.
- #20 walkthrough/video recipe — deferred until after Phase 2 model/API/speed upgrades stabilize.

## Watchouts
- #46 baseline benchmarking is complete; use it as the before-state reference for remaining Phase 2 work.
- #47 Responses API migration is complete; do not re-open API migration work while starting #52.
- #48 Structured Outputs is complete for final dispute report generation only; do not expand it while starting #52.
- #49 stage-specific model configuration is complete; do not tune model choices by default while starting #52.
- #50 section-summary concurrency is complete; do not rework prompts, schemas, model configuration, retry behavior, telemetry, or benchmark code while starting #52.
- #51 redundant live policy PDF reprocessing cleanup is complete; do not re-open PDF processing while starting #52.
- Section summaries remain on `json_object` mode unless a later issue explicitly changes that.
- Section-summary calls use bounded `ThreadPoolExecutor` concurrency; keep `SECTION_SUMMARY_MAX_WORKERS=1` as the sequential kill-switch.
- The live citation source map reuses first-pass raw sections in memory; `section_text_map` is stripped before claim persistence.
- Preserve research prototype / AI-generated / not legal advice framing.
