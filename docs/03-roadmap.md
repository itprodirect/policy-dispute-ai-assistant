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
#20 walkthrough video and screenshot recipe is intentionally deferred until after Phase 2 stabilizes. Do not mix it into technical hardening sessions.

## Phase 1C: Local/demo trust polish - completed

Completed:

- #21 Demo Mode citation/source accordions via PR #41.
- Demo source-map loading hardening via PR #42.
- #23 human-readable export context and human/AI export grouping via PR #43.

Intentionally deferred:

- #18 Streamlit Community Cloud deployment prep - revisit only when a hosted public demo is needed.
- #20 walkthrough video/screenshot recipe - revisit after Phase 2 stabilizes.

## Phase 2: Model and speed refactor - PDF reprocessing cleanup complete

True Phase 2 remains reserved for model/speed/API refactor work. Baseline measurement is complete via #46 / PR #54. The Responses API migration is complete via #47 / PR #56. Structured Outputs for final dispute report generation is complete via #48 / PR #58. Stage-specific model configuration is complete via #49 / PR #60. Section-summary latency reduction is complete via #50 / PR #62. Redundant live policy PDF reprocessing cleanup is complete via #51 / PR #64. The next intended issue is #52 focused-analysis mode.

Gating rule:

#50 added bounded concurrency for section-summary LLM calls only. Section-summary calls now use `ThreadPoolExecutor`; `SECTION_SUMMARY_MAX_WORKERS` defaults to 4, and `SECTION_SUMMARY_MAX_WORKERS=1` forces sequential behavior. #51 removed the second live policy PDF pass by reusing first-pass raw sections for the in-memory citation source map, and `section_text_map` is stripped before claim persistence to avoid raw policy text persistence. Do not bundle prompt rewrites, report schema changes, benchmark changes, model swaps, or unrelated refactors into #52.

Order:

1. Baseline benchmarking and current-state measurement: complete via #46 / PR #54.
2. Replace the Chat Completions wrapper with the Responses API: complete via #47 / PR #56.
3. Add Structured Outputs for final dispute report generation: complete via #48 / PR #58.
   Section summaries intentionally remain on `json_object` mode.
4. Add stage-specific model configuration: complete via #49 / PR #60.
5. Parallelize per-section LLM calls: complete via #50 / PR #62.
6. Remove redundant PDF reprocessing in the live pipeline: complete via #51 / PR #64.
7. Add focused-analysis mode: next via #52.
8. Final benchmark report comparing latency, cost, and report quality against the Phase 2 baseline.

## Out of scope across all phases

- Prompt rewrites that change A-G semantics.
- Report schema changes.
- Backend rebuild.
- Auth, users, billing, or server-side storage.
- New policy form support such as HO5, HO6, or commercial.
- Real client data, fake testimonials, or implied production outcomes.
