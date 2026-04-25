# Roadmap

## Phase 1A: Demo polish — completed

- #12 `DEMO_FORCE_ON` hosted demo safety.
- #13 Hero/value proposition.
- #14 Confidence tab cleanup.
- #15 README screenshots and repo first-impression polish.
- #16 Progress UI and step labels.
- #17 Recent claims card.

## Phase 1B: Operational closeout — next

Work one issue per PR, in this order:

1. #19 GitHub Actions CI for pytest.
2. #22 Clean up stale `frontend/data/` artifacts.
3. #20 Walkthrough video and screenshot recipe.

Note:
The walkthrough/video recipe can be deferred from the current coding session if needed, but it remains part of Phase 1B closeout.

## Phase 1C: Hosted demo and trust polish

Work one issue per PR, in this order:

1. #18 Streamlit Community Cloud deployment prep.
2. #21 Citation/source accordions in Demo Mode.
3. #23 Human-readable context in dispute report exports.

Note:
Deployment prep may come before citation accordions, but the hosted demo should not be publicly promoted as a final portfolio demo until the Demo Mode citation/source accordion work is complete.

## Phase 2: Model and speed refactor — not started

Begin only after Phase 1A, 1B, and 1C are complete or intentionally deferred, and only after focused inspection or measurement.

Scope:

- Replace the Chat Completions wrapper with the Responses API.
- Add Structured Outputs schemas for sectioning and dispute report generation.
- Add stage-specific model configuration.
- Parallelize or reduce per-section LLM calls.
- Add a focused-analysis mode that targets the most material sections.
- Remove redundant PDF reprocessing in the live pipeline.
- Add a benchmark report comparing latency, cost, and report quality before and after.

## Out of scope across all phases

- Prompt rewrites that change A-G semantics.
- Report schema changes.
- Backend rebuild.
- Auth, users, billing, or server-side storage.
- New policy form support such as HO5, HO6, or commercial.
- Real client data, fake testimonials, or implied production outcomes.
