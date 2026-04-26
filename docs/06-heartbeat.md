# Heartbeat

Last updated: 2026-04-25 22:32 ET

## Current Phase
- Phase 1 is complete: Phase 1A demo polish, Phase 1B technical closeout, and Phase 1C local/demo trust polish.
- Phase 2 baseline benchmarking is complete via #46 / PR #54.
- Phase 2 model/API/speed refactor has not started.

## Current Truth
- PR #44 wrapped Phase 1 and handed off to Phase 2 baseline benchmarking.
- PR #54 merged the repeatable Phase 2 before-state benchmark harness.
- The checked-in baseline is deterministic demo-bundle mode with no API calls.
- #21 Demo Mode citation/source accordions are complete via PR #41.
- Demo source-map loading hardening is complete via PR #42.
- #23 human-readable export context and human/AI export grouping are complete via PR #43.
- The repo remains a research prototype with AI-generated and not-legal-advice framing.

## Next Action
- Start #47 Responses API migration only. Do not bundle Structured Outputs, model swaps, prompt/schema changes, PDF processing changes, or speed refactors.

## Deferred
- #18 Streamlit deployment prep — deferred because hosted deployment is not needed yet and adds surface area.
- #20 walkthrough/video recipe — deferred until after Phase 2 model/API/speed upgrades stabilize.

## Watchouts
- #46 baseline benchmarking is complete; use it as the before-state reference for #47.
- Do not start Structured Outputs, model swaps, prompt changes, schema changes, PDF processing changes, or speed refactors in #47.
- Preserve research prototype / AI-generated / not legal advice framing.
