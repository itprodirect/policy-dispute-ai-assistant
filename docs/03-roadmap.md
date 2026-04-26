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

## Phase 2: Model and speed refactor - complete

True Phase 2 remains reserved for model/speed/API refactor work. Baseline measurement is complete via #46 / PR #54. The Responses API migration is complete via #47 / PR #56. Structured Outputs for final dispute report generation is complete via #48 / PR #58. Stage-specific model configuration is complete via #49 / PR #60. Section-summary latency reduction is complete via #50 / PR #62. Redundant live policy PDF reprocessing cleanup is complete via #51 / PR #64. Focused-analysis mode is complete via #52 / PR #66. Final benchmark comparison reporting is complete via #53.

Gating rule:

#50 added bounded concurrency for section-summary LLM calls only. Section-summary calls now use `ThreadPoolExecutor`; `SECTION_SUMMARY_MAX_WORKERS` defaults to 4, and `SECTION_SUMMARY_MAX_WORKERS=1` forces sequential behavior. #51 removed the second live policy PDF pass by reusing first-pass raw sections for the in-memory citation source map, and `section_text_map` is stripped before claim persistence to avoid raw policy text persistence. #52 added explicit opt-in focused-analysis mode while preserving full analysis as the default. Focused mode filters policy sections before section-summary LLM calls to the canonical core allowlist (`DEFINITIONS`, `EXCLUSIONS`, `CONDITIONS`, `COVERAGE A - DWELLING`, `COVERAGE B - OTHER STRUCTURES`, `COVERAGE C - PERSONAL PROPERTY`, `COVERAGE D - LOSS OF USE`) and skips obvious meta sections. It did not change prompts, report schemas/dataclasses, Structured Outputs behavior, model defaults, stage-specific model configuration, or section-summary concurrency behavior beyond filtering the input section list before `executor.map`. `section_text_map` still comes from full raw sections for citation/source accordions, and raw policy section text is still not persisted. Export context includes Mode, including Demo Mode plus Focused/Full combinations. #53 added `benchmarks/phase2-final.md` and a live-only focused benchmark flag for current full-vs-focused comparison without changing default benchmark or app behavior.

Order:

1. Baseline benchmarking and current-state measurement: complete via #46 / PR #54.
2. Replace the Chat Completions wrapper with the Responses API: complete via #47 / PR #56.
3. Add Structured Outputs for final dispute report generation: complete via #48 / PR #58.
   Section summaries intentionally remain on `json_object` mode.
4. Add stage-specific model configuration: complete via #49 / PR #60.
5. Parallelize per-section LLM calls: complete via #50 / PR #62.
6. Remove redundant PDF reprocessing in the live pipeline: complete via #51 / PR #64.
7. Add focused-analysis mode: complete via #52 / PR #66.
8. Final benchmark report comparing deterministic demo parity and current live full/focused behavior: complete via #53.

Phase 2 is now closed. Revisit #18 Streamlit Community Cloud deployment prep and #20 walkthrough/screenshot recipe as separate post-Phase-2 work only when needed.

## Out of scope across all phases

- Prompt rewrites that change A-G semantics.
- Report schema changes.
- Backend rebuild.
- Auth, users, billing, or server-side storage.
- New policy form support such as HO5, HO6, or commercial.
- Real client data, fake testimonials, or implied production outcomes.
