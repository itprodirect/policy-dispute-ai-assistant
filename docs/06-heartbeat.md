# Heartbeat

Last updated: 2026-04-28 sales-proof docs closeout

## Current Phase
- Phase 1 is complete: Phase 1A demo polish, Phase 1B technical closeout, and Phase 1C local/demo trust polish.
- Phase 2 baseline benchmarking is complete via #46 / PR #54.
- Phase 2 Responses API migration is complete via #47 / PR #56.
- Phase 2 Structured Outputs for final dispute report generation is complete via #48 / PR #58.
- Phase 2 stage-specific model configuration is complete via #49 / PR #60.
- Phase 2 section-summary latency reduction is complete via #50 / PR #62.
- Phase 2 redundant live policy PDF reprocessing cleanup is complete via #51 / PR #64.
- Phase 2 focused-analysis mode is complete via #52 / PR #66.
- Phase 2 final benchmark comparison reporting is complete via #53.

## Current Truth
- PR #44 wrapped Phase 1 and handed off to Phase 2 baseline benchmarking.
- PR #54 merged the repeatable Phase 2 before-state benchmark harness.
- PR #56 migrated the single OpenAI wrapper to the Responses API without prompt, schema, model, retry, telemetry, PDF-processing, benchmark, or pipeline optimization changes.
- PR #58 added Responses API Structured Outputs strict JSON Schema mode only for final dispute report generation. Section summaries intentionally remain on default `json_object` mode.
- PR #60 added optional stage-specific model overrides through `OPENAI_MODEL_<STAGE_UPPER>`, while preserving default model behavior unless per-stage overrides are explicitly set.
- PR #62 added bounded concurrency for section-summary LLM calls using `ThreadPoolExecutor`. `SECTION_SUMMARY_MAX_WORKERS` defaults to 4, and `SECTION_SUMMARY_MAX_WORKERS=1` forces sequential behavior.
- PR #64 removed live policy PDF reprocessing by reusing first-pass raw sections for the in-memory citation source map.
- PR #64 strips `section_text_map` before claim persistence to avoid persisting raw policy text.
- PR #66 added explicit opt-in focused-analysis mode. Full analysis remains the default.
- Focused mode filters policy sections before section-summary LLM calls to the canonical core allowlist: `DEFINITIONS`, `EXCLUSIONS`, `CONDITIONS`, `COVERAGE A - DWELLING`, `COVERAGE B - OTHER STRUCTURES`, `COVERAGE C - PERSONAL PROPERTY`, and `COVERAGE D - LOSS OF USE`.
- Focused mode skips obvious meta sections.
- PR #66 did not change prompts, report schemas/dataclasses, Structured Outputs behavior, model defaults, or stage-specific model config.
- Section-summary concurrency behavior remains unchanged except that focused mode filters the input section list before `executor.map`.
- `section_text_map` still comes from full raw sections, preserving citation/source accordion behavior, and raw policy section text is still not persisted.
- Export context now includes Mode, including Demo Mode plus Focused/Full combinations.
- PR #66 validation: `python -m pytest -q` passed with 85 tests.
- The checked-in baseline is deterministic demo-bundle mode with no API calls.
- The final Phase 2 comparison is `benchmarks/phase2-final.md`; it preserves `benchmarks/phase2-baseline.md` as the historical before-state and records current demo parity plus full/focused live measurements for the HO3 TRUE FL fixture.
- #21 Demo Mode citation/source accordions are complete via PR #41.
- Demo source-map loading hardening is complete via PR #42.
- #23 human-readable export context and human/AI export grouping are complete via PR #43.
- The repo remains a research prototype with AI-generated and not-legal-advice framing.
- `docs/10-sales-proof.md` records the sales-proof and website/case-study positioning.
- Current portfolio decision: credible private sales demo and case-study material, not public production proof.
- Safe claims are limited to internal prototype, human-review workflow, homeowners policy and denial-letter triage, A-G dispute summaries, deterministic Demo Mode, Markdown/Word exports, tests, CI, and demo-safe screenshots.
- Avoid claims of production readiness, legal accuracy, coverage determination, client-proven outcomes, secure hosted SaaS, or broad policy-form support.

## Next Action
- Phase 2 is closed after #53. If public promotion is next, start with artifact safety review and a Demo Mode walkthrough package before hosted deployment.

## Deferred
- Public promotion remains deferred until demo assets, tracked generated artifacts, screenshots, and limitation language are reviewed.
- #18 Streamlit deployment prep — deferred because hosted deployment is not needed yet and adds surface area.
- #20 walkthrough/video recipe — deferred until after Phase 2 model/API/speed upgrades stabilize.

## Watchouts
- #46 baseline benchmarking is complete; keep `benchmarks/phase2-baseline.md` as the before-state reference.
- #47 Responses API migration is complete; do not re-open API migration work while starting #53.
- #48 Structured Outputs is complete for final dispute report generation only; do not expand it while starting #53.
- #49 stage-specific model configuration is complete; do not tune model choices by default while starting #53.
- #50 section-summary concurrency is complete; do not rework prompts, schemas, model configuration, retry behavior, telemetry, or benchmark code while starting #53.
- #51 redundant live policy PDF reprocessing cleanup is complete; do not re-open PDF processing while starting #53.
- #52 focused-analysis mode is complete; do not re-open filtering, prompt, schema, model, or citation/source accordion behavior after #53.
- #53 final reporting is complete; do not add token/cost telemetry or a quality scoring harness unless a later issue explicitly asks for it.
- Section summaries remain on `json_object` mode unless a later issue explicitly changes that.
- Section-summary calls use bounded `ThreadPoolExecutor` concurrency; keep `SECTION_SUMMARY_MAX_WORKERS=1` as the sequential kill-switch.
- The live citation source map reuses first-pass raw sections in memory; `section_text_map` is stripped before claim persistence.
- Preserve research prototype / AI-generated / not legal advice framing.
- Do not turn sales copy into production, legal, or client-outcome claims.
