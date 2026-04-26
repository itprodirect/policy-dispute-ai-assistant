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
- Stage-specific model overrides use `OPENAI_MODEL_<STAGE_UPPER>` and default model behavior is unchanged unless a per-stage override is explicitly set.
- Section summaries intentionally remain on default `json_object` mode.
- Section-summary calls now use bounded concurrency via `ThreadPoolExecutor`. `SECTION_SUMMARY_MAX_WORKERS` defaults to 4, and `SECTION_SUMMARY_MAX_WORKERS=1` forces sequential behavior.
- Next: start #51 redundant PDF reprocessing cleanup in the live pipeline only. PDF reprocessing cleanup remains deferred to #51. Do not bundle prompt rewrites, report schema changes, benchmark changes, model swaps, telemetry changes, frontend behavior changes, or unrelated refactors in the #51 PR.

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

## Standing Guardrails

- Preserve research prototype, AI-generated, not-legal-advice, and demo-safe framing.
- Keep work one issue per PR.
- Do not commit secrets, real client data, real claim names, claim numbers, or fake client proof.
- Keep routine logs, archived docs, and screenshots unchanged unless an issue explicitly requires them.
