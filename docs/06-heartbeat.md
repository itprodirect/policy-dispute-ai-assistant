# Heartbeat

Date: 2026-04-25

## Status

- Phase 1A demo polish: complete.
- Phase 1B technical closeout: complete.
- Phase 1C local/demo trust polish: complete via PR #41, PR #42, and PR #43.
- #18 deployment prep: intentionally deferred.
- #20 walkthrough/video recipe: intentionally deferred until after Phase 2 stabilizes.
- Phase 2 model/speed refactor: not started.
- Next step: baseline benchmarking.

## Current Watchouts

- Keep phase boundaries clear. #18 and #20 are intentionally deferred, not missing from the roadmap.
- Do not start Responses API, Structured Outputs, model swaps, or speed refactors before baseline benchmarking exists.
- Do not mix Phase 2 implementation work into docs-only wrap PRs.
- Do not change prompts or report schemas as part of docs, CI, or deployment work.
- Keep public-demo safety centered on deterministic Demo Mode and `DEMO_FORCE_ON`.
- Do not commit local runtime artifacts, real claim data, secrets, or screenshot candidates.
- Preserve the research prototype / not legal advice framing in README, UI, and generated reports.
