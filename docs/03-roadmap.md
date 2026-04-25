# Roadmap

## Phase 1A: Demo polish - completed

- #12 `DEMO_FORCE_ON` hosted demo safety.
- #13 Hero/value proposition.
- #14 Confidence tab cleanup.
- #15 README screenshots and repo first-impression polish.
- #16 Progress UI and step labels.
- #17 Recent claims card.

## Phase 1B: Operational closeout - technical closeout complete

Completed:

- #19 GitHub Actions CI for pytest.
- #22 Clean up stale `frontend/data/` artifacts.

Note:
#20 walkthrough video and screenshot recipe remains open, but it is intentionally deferred to a future brand/content walkthrough session. Do not mix it into technical hardening sessions.

## Phase 1C: Hosted demo and trust polish - next

Work one issue per PR, in this order:

1. #18 Streamlit Community Cloud deployment prep.
2. #21 Citation/source accordions in Demo Mode.
3. #23 Human-readable context in dispute report exports.

Note:
Deployment prep may come before citation accordions, but the hosted demo should not be publicly promoted as a final portfolio demo until the Demo Mode citation/source accordion work is complete.

## Phase 2: Model and speed refactor - not started

True Phase 2 remains reserved for model/speed/API refactor work. Begin only after Phase 1A, 1B, and 1C are complete or intentionally deferred, and only after focused inspection or measurement.

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
