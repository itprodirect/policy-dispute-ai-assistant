# Heartbeat

Last updated: 2026-04-25 22:19 ET

## Current Phase
- Phase 1 is complete: Phase 1A demo polish, Phase 1B technical closeout, and Phase 1C local/demo trust polish.
- Phase 2 baseline benchmarking has started with issue #46.
- Phase 2 model/API/speed refactor has not started.

## Current Truth
- PR #44 wrapped Phase 1 and handed off to Phase 2 baseline benchmarking.
- Issue #46 adds a repeatable Phase 2 before-state benchmark harness.
- The checked-in baseline is deterministic demo-bundle mode with no API calls.
- #21 Demo Mode citation/source accordions are complete via PR #41.
- Demo source-map loading hardening is complete via PR #42.
- #23 human-readable export context and human/AI export grouping are complete via PR #43.
- The repo remains a research prototype with AI-generated and not-legal-advice framing.

## Next Action
- Review and merge the #46 baseline benchmark harness before starting #47 or other Phase 2 implementation work.

## Deferred
- #18 Streamlit deployment prep — deferred because hosted deployment is not needed yet and adds surface area.
- #20 walkthrough/video recipe — deferred until after Phase 2 model/API/speed upgrades stabilize.

## Watchouts
- Phase 2 must start with baseline benchmarking; issue #46 is the baseline-only step.
- Do not start Responses API, Structured Outputs, model swaps, prompt changes, schema changes, or speed refactors before the baseline exists.
- Preserve research prototype / AI-generated / not legal advice framing.
