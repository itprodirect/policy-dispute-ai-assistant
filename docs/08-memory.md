# Memory

Durable project timeline for future Codex and Claude sessions.

## Current Baseline

- Repo: `policy-dispute-ai-assistant`.
- Current branch baseline: `main`.
- Phase 1 is complete.
- #18 Streamlit Community Cloud deployment prep and #20 walkthrough video/screenshot recipe are intentionally deferred.
- Phase 2 baseline benchmarking is complete via #46 / PR #54.
- Phase 2 Responses API migration is complete via #47 / PR #56.
- Phase 2 Structured Outputs for final dispute report generation is complete via #48 / PR #58.
- Phase 2 stage-specific model configuration is complete via #49 / PR #60.
- Phase 2 section-summary latency reduction is complete via #50 / PR #62.
- Phase 2 redundant live policy PDF reprocessing cleanup is complete via #51 / PR #64.
- Phase 2 focused-analysis mode is complete via #52 / PR #66.
- Phase 2 final benchmark comparison reporting is complete via #53.
- Stage-specific model overrides use `OPENAI_MODEL_<STAGE_UPPER>` and default model behavior is unchanged unless a per-stage override is explicitly set.
- Section summaries intentionally remain on default `json_object` mode.
- Section-summary calls now use bounded concurrency via `ThreadPoolExecutor`. `SECTION_SUMMARY_MAX_WORKERS` defaults to 4, and `SECTION_SUMMARY_MAX_WORKERS=1` forces sequential behavior.
- #51 removed live policy PDF reprocessing by reusing first-pass raw sections for the in-memory citation source map.
- `section_text_map` is stripped before claim persistence to avoid raw policy text persistence.
- #52 added explicit opt-in focused-analysis mode. Full analysis remains the default. Focused mode filters policy sections before section-summary LLM calls to a canonical core-section allowlist (`DEFINITIONS`, `EXCLUSIONS`, `CONDITIONS`, `COVERAGE A - DWELLING`, `COVERAGE B - OTHER STRUCTURES`, `COVERAGE C - PERSONAL PROPERTY`, `COVERAGE D - LOSS OF USE`) and skips obvious meta sections.
- #52 did not change prompts, report schemas/dataclasses, Structured Outputs behavior, model defaults, stage-specific model config, or section-summary concurrency behavior beyond filtering the input section list before `executor.map`.
- #52 preserves citation/source accordions because `section_text_map` still comes from full raw sections. Raw policy section text is still not persisted. Export context now includes Mode, including Demo Mode plus Focused/Full combinations.
- `benchmarks/phase2-final.md` is the final Phase 2 comparison report. It preserves `benchmarks/phase2-baseline.md` as historical before-state, records deterministic demo parity, and records current live full/focused measurements for the HO3 TRUE FL fixture.
- Phase 2 is closed after #53. Do not bundle prompt rewrites, report schema changes, Structured Outputs changes, model configuration changes, section-summary concurrency changes, retry changes, telemetry semantics changes, deployment/auth/storage work, PDF export work, token/cost telemetry, quality scoring harnesses, or unrelated refactors into Phase 2 closeout docs.

## Timeline

| Date/Time ET | Event | Issue/PR | Why it matters |
| --- | --- | --- | --- |
| 2026-04-25 17:37 ET | Phase 1A demo polish wrapped | PR #34 | Established the demo-hardening baseline and research/not-legal-advice framing. |
| 2026-04-25 19:24 ET | CI basics added | #19 / PR #38 | Made `python -m pytest -q` the automated merge gate. |
| 2026-04-25 19:30 ET | Stale artifact cleanup documented | #22 / PR #39 | Clarified runtime artifact paths and removed stale `frontend/data/` confusion. |
| 2026-04-25 20:36 ET | Demo citation/source accordions completed | #21 / PR #41 | Made bundled demo citations inspectable without live API calls. |
| 2026-04-25 20:45 ET | Demo source-map loading hardened | PR #42 | Reduced fragility in deterministic demo source lookup. |
| 2026-04-25 21:07 ET | Export context polish completed | #23 / PR #43 | Added human-readable export context and human/AI grouping. |
| 2026-04-25 21:42 ET | Phase 1 wrapped and Phase 2 handoff recorded | PR #44 | Marked Phase 1 complete, deferred #18/#20, and required Phase 2 to start with baseline benchmarking. |
| 2026-04-25 22:25 ET | Phase 2 baseline benchmark harness merged | #46 / PR #54 | Created the before-state benchmark before any model/API/speed refactor work. |
| 2026-04-25 22:57 ET | Responses API migration merged | #47 / PR #56 | Replaced the wrapper API surface while preserving prompts, schemas, model choices, retry behavior, telemetry names, PDF processing, benchmark harness, and pipeline behavior. |
| 2026-04-25 23:19 ET | Structured Outputs for dispute reports merged | #48 / PR #58 | Added strict JSON Schema mode only to final dispute report generation; section summaries remain on `json_object` mode. |
| 2026-04-25 23:37 ET | Stage-specific model configuration merged | #49 / PR #60 | Added optional `OPENAI_MODEL_<STAGE_UPPER>` overrides while preserving default model behavior unless explicitly configured. |
| 2026-04-25 23:58 ET | Section-summary concurrency merged | #50 / PR #62 | Added bounded `ThreadPoolExecutor` concurrency for section-summary LLM calls; `SECTION_SUMMARY_MAX_WORKERS=1` remains the sequential kill-switch. |
| 2026-04-26 00:25 ET | Redundant live policy PDF reprocessing cleanup merged | #51 / PR #64 | Reuses first-pass raw sections for the in-memory citation source map and strips `section_text_map` before claim persistence to avoid raw policy text persistence. |
| 2026-04-26 | Focused-analysis mode merged | #52 / PR #66 | Added explicit opt-in focused mode for canonical core policy sections while preserving full analysis as the default and keeping citation/source accordions backed by full raw sections. |
| 2026-04-26 | Final Phase 2 benchmark comparison added | #53 | Added `benchmarks/phase2-final.md`, kept the historical baseline immutable, and closed Phase 2 with current demo parity plus full/focused live benchmark measurements. |

## Standing Guardrails

- Preserve research prototype, AI-generated, not-legal-advice, and demo-safe framing.
- Keep work one issue per PR.
- Do not commit secrets, real client data, real claim names, claim numbers, or fake client proof.
- Keep routine logs, archived docs, and screenshots unchanged unless an issue explicitly requires them.
