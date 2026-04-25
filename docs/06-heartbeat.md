# Heartbeat

Date: 2026-04-25

## Status

- Phase 1 demo hardening is complete.
- PR #34 and PR #35 are merged.
- Issue #15 is closed.
- Phase 2 has not started yet.
- The next issue is #19: add GitHub Actions CI for pytest.

## Current Watchouts

- Keep Phase 2 ordered. Start with CI, then deployment prep.
- Do not start model/API modernization before inspection and measurement.
- Do not change prompts or report schemas as part of docs, CI, or deployment work.
- Keep public-demo safety centered on deterministic Demo Mode and `DEMO_FORCE_ON`.
- Do not commit local runtime artifacts, real claim data, secrets, or screenshot candidates.
- Preserve the research prototype / not legal advice framing in README, UI, and generated reports.
