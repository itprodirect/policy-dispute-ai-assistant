# Heartbeat

Date: 2026-04-25

## Status

- Phase 1A demo polish is complete.
- Phase 1B technical closeout is complete with #19 GitHub Actions CI for pytest and #22 stale `frontend/data/` artifact cleanup.
- #20 walkthrough video and screenshot recipe remains open but is intentionally deferred to a future brand/content walkthrough session.
- Phase 1C hosted demo and trust polish has not started.
- Phase 2 model/speed refactor has not started.
- The next technical issue is #18: Streamlit Community Cloud deployment prep.

## Current Watchouts

- Keep phase boundaries clear. Phase 1C may begin with #18 Streamlit Community Cloud deployment prep.
- Do not start #20 during technical hardening; defer it to a future brand/content walkthrough session.
- Do not mix Phase 2 model/API refactor work into Phase 1B or Phase 1C PRs.
- Do not start model/API modernization before Phase 1B/1C completion or intentional deferral, inspection, and measurement.
- Do not change prompts or report schemas as part of docs, CI, or deployment work.
- Keep public-demo safety centered on deterministic Demo Mode and `DEMO_FORCE_ON`.
- Do not commit local runtime artifacts, real claim data, secrets, or screenshot candidates.
- Preserve the research prototype / not legal advice framing in README, UI, and generated reports.
