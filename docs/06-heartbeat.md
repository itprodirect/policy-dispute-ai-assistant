# Heartbeat

Date: 2026-04-25

## Status

- Phase 1A demo polish is complete.
- PR #34 and PR #35 are merged.
- Issue #15 is closed.
- Phase 1B operational closeout has not started.
- Phase 1C hosted demo and trust polish has not started.
- Phase 2 model/speed refactor has not started.
- The next build issue is #19: add GitHub Actions CI for pytest.

## Current Watchouts

- Keep phase boundaries clear. Start Phase 1B with CI, then stale artifact cleanup and walkthrough recipe work.
- Do not mix Phase 2 model/API refactor work into Phase 1B or Phase 1C PRs.
- Do not start model/API modernization before Phase 1B/1C completion or intentional deferral, inspection, and measurement.
- Do not change prompts or report schemas as part of docs, CI, or deployment work.
- Keep public-demo safety centered on deterministic Demo Mode and `DEMO_FORCE_ON`.
- Do not commit local runtime artifacts, real claim data, secrets, or screenshot candidates.
- Preserve the research prototype / not legal advice framing in README, UI, and generated reports.
