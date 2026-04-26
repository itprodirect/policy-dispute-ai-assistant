# Heartbeat

Last updated: 2026-04-25 23:38 ET

## Current Phase
- Phase 1 is complete: Phase 1A demo polish, Phase 1B technical closeout, and Phase 1C local/demo trust polish.
- Phase 2 baseline benchmarking is complete via #46 / PR #54.
- Phase 2 Responses API migration is complete via #47 / PR #56.
- Phase 2 Structured Outputs for final dispute report generation is complete via #48 / PR #58.
- Phase 2 stage-specific model configuration is complete via #49 / PR #60.

## Current Truth
- PR #44 wrapped Phase 1 and handed off to Phase 2 baseline benchmarking.
- PR #54 merged the repeatable Phase 2 before-state benchmark harness.
- PR #56 migrated the single OpenAI wrapper to the Responses API without prompt, schema, model, retry, telemetry, PDF-processing, benchmark, or pipeline optimization changes.
- PR #58 added Responses API Structured Outputs strict JSON Schema mode only for final dispute report generation. Section summaries intentionally remain on default `json_object` mode.
- PR #60 added optional stage-specific model overrides through `OPENAI_MODEL_<STAGE_UPPER>`, while preserving default model behavior unless per-stage overrides are explicitly set.
- The checked-in baseline is deterministic demo-bundle mode with no API calls.
- #21 Demo Mode citation/source accordions are complete via PR #41.
- Demo source-map loading hardening is complete via PR #42.
- #23 human-readable export context and human/AI export grouping are complete via PR #43.
- The repo remains a research prototype with AI-generated and not-legal-advice framing.

## Next Action
- Start #50 latency reduction in the section summary pipeline only. Do not bundle prompt rewrites, report schema changes, PDF processing changes, benchmark changes, model swaps, or unrelated refactors.

## Deferred
- #18 Streamlit deployment prep — deferred because hosted deployment is not needed yet and adds surface area.
- #20 walkthrough/video recipe — deferred until after Phase 2 model/API/speed upgrades stabilize.

## Watchouts
- #46 baseline benchmarking is complete; use it as the before-state reference for remaining Phase 2 work.
- #47 Responses API migration is complete; do not re-open API migration work while starting #50.
- #48 Structured Outputs is complete for final dispute report generation only; do not expand it while starting #50.
- #49 stage-specific model configuration is complete; do not tune model choices by default while starting #50.
- Section summaries remain on `json_object` mode unless a later issue explicitly changes that.
- Preserve research prototype / AI-generated / not legal advice framing.
