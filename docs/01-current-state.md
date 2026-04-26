# Current State

Last updated: 2026-04-25

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

## Current Phase

Phase 1A demo polish is complete.

Phase 1B technical closeout is complete with #19 GitHub Actions CI for pytest and #22 stale `frontend/data/` artifact cleanup.

Phase 1C local/demo trust polish is complete with #21 Demo Mode citation/source accordions, Demo source-map loading hardening, and #23 export context polish.

#18 Streamlit Community Cloud deployment prep is intentionally deferred because hosted deployment is not needed yet and adds surface area.

#20 walkthrough video and screenshot recipe is intentionally deferred because walkthrough/video work should wait until after Phase 2 stabilizes.

Phase 2 baseline benchmarking is complete via #46 / PR #54. #47 Responses API migration is complete via PR #56. #48 Structured Outputs is complete via PR #58 for final dispute report generation only.

Section summaries intentionally remain on the default `json_object` mode. The next intended issue is #49 stage-specific model configuration. No model swaps, prompt changes, dataclass/schema refactors, parser changes, PDF processing changes, benchmark changes, or speed refactors have started.

## Local Cleanup

After PR #35 merged, local screenshot candidate files were moved outside the repo to:

`C:\Users\user\Desktop\policy-dispute-screenshot-candidates-archive\`

The repo working tree was clean after that cleanup.
