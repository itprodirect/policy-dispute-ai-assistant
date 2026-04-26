# Session Log

Purpose:
Track real working sessions so future AI/dev sessions can quickly understand what happened, what changed, and what to do next.

## Entry format

### YYYY-MM-DD HH:MM ET — Short session title

#### Goal
- What this session was trying to accomplish.

#### Completed
- What changed.
- PRs/issues touched.

#### Decisions
- Any decisions made.
- Link to `docs/05-decision-log.md` when relevant.

#### Validation
- Tests/checks/run results, if any.

#### Deferred
- Anything intentionally postponed.

#### Next session starter
- The exact next recommended action.

### 2026-04-25 21:07 ET — Phase 1C trust polish

#### Goal
- Complete local/demo trust polish after Phase 1A and Phase 1B.

#### Completed
- #21 Demo Mode citation/source accordions completed via PR #41.
- Demo source-map loading hardened via PR #42.
- #23 human-readable export context and human/AI export grouping completed via PR #43.

#### Decisions
- Keep hosted deployment prep separate from local/demo trust polish.
- See `docs/05-decision-log.md` for related Phase 1C and deferral decisions.

#### Validation
- PR-level validation completed in PR #41, PR #42, and PR #43.

#### Deferred
- #18 Streamlit Community Cloud deployment prep.
- #20 walkthrough video/screenshot recipe.

#### Next session starter
- Wrap Phase 1 in durable docs and make Phase 2 start with baseline benchmarking.

### 2026-04-25 21:42 ET — Phase 1 wrap and Phase 2 handoff

#### Goal
- Record Phase 1 completion, intentional deferrals, and the Phase 2 baseline gate.

#### Completed
- PR #44 updated durable docs to mark Phase 1 complete.
- Recorded #18 and #20 as intentional deferrals.
- Set Phase 2 order to begin with baseline benchmarking before model/API/speed work.

#### Decisions
- Phase 2 must start with baseline benchmarking.
- See `docs/05-decision-log.md` for the Phase 1C wrap decision.

#### Validation
- PR #44 validated docs-only scope and grep checks for stale Phase 1C/#18/Future CI wording.

#### Deferred
- #18 Streamlit Community Cloud deployment prep remains deferred until a hosted public demo is needed.
- #20 walkthrough video/screenshot recipe remains deferred until after Phase 2 stabilizes.

#### Next session starter
- Start Phase 2 baseline benchmarking and current-state measurement against the demo bundle.

### 2026-04-25 22:19 ET - Phase 2 baseline benchmark harness

#### Goal
- Start issue #46 only by adding a repeatable before-state benchmark before model/API/speed work.

#### Completed
- Added `scripts/benchmark_phase2_baseline.py`.
- Added `benchmarks/phase2-baseline.md`.
- Documented rerun commands in README and RUNBOOK.
- Updated heartbeat and memory for the baseline-only Phase 2 step.

#### Decisions
- Use deterministic demo-bundle mode as the checked-in baseline because it makes no API calls and uses tracked demo-safe inputs.
- Keep live current-pipeline benchmarking optional because it requires `OPENAI_API_KEY` and non-sensitive local inputs.

#### Validation
- `python scripts/benchmark_phase2_baseline.py --mode demo`
- `python scripts/benchmark_phase2_baseline.py --mode demo --output .tmp/phase2-baseline-demo.json`
- `python -m pytest -q` - 27 passed.

#### Deferred
- Live OpenAI/API benchmark run.
- #47 Responses API migration.
- Structured Outputs, model swaps, prompt/schema changes, and speed refactors.

#### Next session starter
- Use the merged #46 baseline before starting #47 Responses API migration.

### 2026-04-25 22:32 ET - Post-#54 hygiene truth sync

#### Goal
- Confirm #46 / PR #54 post-merge state and align project docs with #47 as the next intended issue.

#### Completed
- Confirmed PR #54 is merged and issue #46 is closed.
- Confirmed #47 is open.
- Updated current-state docs to mark #46 complete and #47 next.

#### Decisions
- No new technical decisions.

#### Validation
- Git/GitHub hygiene checks completed.
- Docs-only diff reviewed.

#### Deferred
- Local deletion of the fully merged #46 branch.
- Removal of ignored `.tmp/phase2-baseline-demo.json`.
- #47 Responses API migration.

#### Next session starter
- Start #47 only: Responses API migration, without Structured Outputs, model swaps, prompt/schema changes, PDF processing changes, or speed refactors.

### 2026-04-25 22:59 ET - Post-#56 hygiene truth sync

#### Goal
- Confirm #47 / PR #56 post-merge state and align durable docs with #48 as the next intended issue.

#### Completed
- Confirmed PR #56 is merged and issue #47 is closed.
- Confirmed #48 is open and next in the Phase 2 order.
- Updated durable docs to mark #47 complete and #48 next.

#### Decisions
- No new technical decisions.

#### Validation
- Git/GitHub hygiene checks completed.
- Docs-only diff reviewed.

#### Deferred
- #48 Structured Outputs implementation.
- Model swaps, prompt rewrites, report schema changes, PDF processing changes, benchmark changes, and speed refactors.

#### Next session starter
- Start #48 only: Structured Outputs, without model swaps, prompt rewrites, report schema changes, PDF processing changes, benchmark changes, or speed refactors.

### 2026-04-25 23:19 ET - Post-#58 hygiene truth sync

#### Goal
- Confirm #48 / PR #58 post-merge state and align durable docs with #49 as the next intended issue.

#### Completed
- Confirmed PR #58 is merged and issue #48 is closed.
- Confirmed #49 is open and next in the Phase 2 order.
- Updated durable docs to mark #48 complete and #49 next.
- Recorded that Structured Outputs were applied only to final dispute report generation.
- Recorded that section summaries intentionally remain on default `json_object` mode.

#### Decisions
- No new technical decisions.

#### Validation
- Git/GitHub hygiene checks completed.
- Docs-only diff reviewed.

#### Deferred
- #49 stage-specific model configuration.
- Prompt cleanup, section-summary Structured Outputs, benchmark comparison, PDF processing changes, and speed refactors.

#### Next session starter
- Start #49 only: stage-specific model configuration, without prompt rewrites, report schema changes, PDF processing changes, benchmark changes, or speed refactors.

### 2026-04-25 23:38 ET - Post-#60 hygiene truth sync

#### Goal
- Confirm #49 / PR #60 post-merge state and align durable docs with #50 as the next intended issue.

#### Completed
- Confirmed PR #60 is merged and issue #49 is closed.
- Confirmed #50 is open and next in the Phase 2 order.
- Updated durable docs to mark #49 complete and #50 next.
- Recorded that stage-specific model overrides use `OPENAI_MODEL_<STAGE_UPPER>`.
- Recorded that default model behavior is unchanged unless a per-stage override is explicitly set.

#### Decisions
- No new technical decisions.

#### Validation
- Git/GitHub hygiene checks completed.
- Docs-only diff reviewed.

#### Deferred
- #50 latency reduction in the section summary pipeline.
- Prompt rewrites, report schema changes, PDF processing changes, benchmark changes, model tuning, and unrelated refactors.

#### Next session starter
- Start #50 only: latency reduction in the section summary pipeline, without prompt rewrites, report schema changes, PDF processing changes, benchmark changes, model swaps, or unrelated refactors.

### 2026-04-25 23:59 ET - Post-#62 hygiene truth sync

#### Goal
- Confirm #50 / PR #62 post-merge state and align durable docs with #51 as the next intended issue.

#### Completed
- Confirmed PR #62 is merged and issue #50 is closed.
- Confirmed #51 is open and next in the Phase 2 order.
- Updated durable docs to mark #50 complete and #51 next.
- Recorded that section-summary calls now use bounded concurrency via `ThreadPoolExecutor`.
- Recorded that `SECTION_SUMMARY_MAX_WORKERS` defaults to 4 and `SECTION_SUMMARY_MAX_WORKERS=1` forces sequential behavior.

#### Decisions
- No new technical decisions.

#### Validation
- Git/GitHub hygiene checks completed.
- Docs-only diff reviewed.

#### Deferred
- #51 redundant PDF reprocessing cleanup remains deferred to the next issue.
- Prompt rewrites, report schema changes, Structured Outputs changes, model configuration changes, retry changes, telemetry changes, benchmark changes, frontend behavior changes, and deployment/auth/storage/PDF export work remain out of scope.

#### Next session starter
- Start #51 only: remove redundant PDF reprocessing from the live pipeline, without prompt rewrites, report schema changes, Structured Outputs changes, model configuration changes, retry changes, telemetry changes, benchmark changes, frontend behavior changes, or unrelated refactors.

### 2026-04-26 00:27 ET - Post-#64 hygiene truth sync

#### Goal
- Confirm #51 / PR #64 post-merge state and align durable docs with #52 as the next intended issue.

#### Completed
- Confirmed PR #64 is merged and issue #51 is closed.
- Confirmed #52 is open and next in the Phase 2 order.
- Updated durable docs to mark #51 complete and #52 next.
- Recorded that live policy PDF reprocessing was removed by reusing first-pass raw sections for the in-memory citation source map.
- Recorded that `section_text_map` is stripped before claim persistence to avoid raw policy text persistence.

#### Decisions
- No new technical decisions.

#### Validation
- Git/GitHub hygiene checks completed.
- Docs-only diff reviewed.
- `git diff --check` passed.

#### Deferred
- #52 focused-analysis mode remains deferred to the next issue.
- Prompt rewrites, schema/dataclass changes, Structured Outputs changes, model configuration changes, section-summary concurrency changes, retry changes, telemetry semantics changes, benchmark changes, deployment/auth/storage work, and PDF export work remain out of scope.

#### Next session starter
- Start #52 only: focused-analysis mode, without prompt rewrites, schema/dataclass changes, Structured Outputs changes, model configuration changes, section-summary concurrency changes, retry changes, telemetry semantics changes, benchmark changes, deployment/auth/storage work, PDF export work, or unrelated refactors.

### 2026-04-26 - Post-#66 hygiene truth sync

#### Goal
- Confirm #52 / PR #66 post-merge state and align durable docs with #53 as the next intended issue.

#### Completed
- Confirmed PR #66 is merged and #52 focused-analysis mode is complete.
- Updated durable docs to mark Phase 2 complete through #52.
- Recorded that focused-analysis mode is explicit opt-in and full analysis remains the default.
- Recorded that focused mode filters policy sections before section-summary LLM calls to the canonical core-section allowlist: `DEFINITIONS`, `EXCLUSIONS`, `CONDITIONS`, `COVERAGE A - DWELLING`, `COVERAGE B - OTHER STRUCTURES`, `COVERAGE C - PERSONAL PROPERTY`, and `COVERAGE D - LOSS OF USE`.
- Recorded that focused mode skips obvious meta sections.
- Recorded that PR #66 did not change prompts, report schemas/dataclasses, Structured Outputs behavior, model defaults, or stage-specific model config.
- Recorded that section-summary concurrency behavior remains unchanged except focused mode filters the input section list before `executor.map`.
- Recorded that `section_text_map` still comes from full raw sections for citation/source accordions and raw policy section text is still not persisted.
- Recorded that export context includes Mode, including Demo Mode plus Focused/Full combinations.

#### Decisions
- No new technical decisions.
- No decision-log update because there is no existing Phase 2 decision-log pattern for this kind of post-merge truth sync.

#### Validation
- PR #66 validation: `python -m pytest -q` passed with 85 tests.
- This PR is docs-only; tests were not run for the docs sync.

#### Deferred
- #53 P2-7 Add final Phase 2 benchmark comparison report remains deferred to the next issue.
- Prompt rewrites, schema/dataclass changes, Structured Outputs changes, model configuration changes, section-summary concurrency changes, retry changes, telemetry semantics changes, deployment/auth/storage work, PDF export work, and unrelated refactors remain out of scope.

#### Next session starter
- Start #53 only: final Phase 2 benchmark comparison report, without prompt rewrites, schema/dataclass changes, Structured Outputs changes, model configuration changes, section-summary concurrency changes, retry changes, telemetry semantics changes, deployment/auth/storage work, PDF export work, or unrelated refactors.

### 2026-04-26 - Final Phase 2 benchmark comparison

#### Goal
- Complete #53 as the final Phase 2 issue with a narrow benchmark comparison report.

#### Completed
- Added a live-mode-only `--focused` option to `scripts/benchmark_phase2_baseline.py`.
- Added `benchmarks/phase2-final.md`.
- Preserved `benchmarks/phase2-baseline.md` as the historical before-state report.
- Recorded deterministic demo parity against the baseline.
- Recorded current live full and focused measurements for `data/raw_policies/HO3_TRUE_FL_2021.pdf` with `data/raw_denials/HO3_TRUE_FL_2021_denial.txt`.
- Updated durable docs to mark Phase 2 complete through #53.

#### Decisions
- Keep the final comparison report separate from the historical baseline report.
- Close Phase 2 after #53; revisit #18 deployment prep and #20 walkthrough/screenshot recipe separately later.

#### Validation
- `python -m pytest -q` passed with 85 tests.
- `python scripts/benchmark_phase2_baseline.py --mode demo --output .tmp/phase2-final-demo.json`
- `python scripts/benchmark_phase2_baseline.py --mode live --policy-pdf data/raw_policies/HO3_TRUE_FL_2021.pdf --denial-text data/raw_denials/HO3_TRUE_FL_2021_denial.txt --output .tmp/phase2-final-live-full.json`
- `python scripts/benchmark_phase2_baseline.py --mode live --focused --policy-pdf data/raw_policies/HO3_TRUE_FL_2021.pdf --denial-text data/raw_denials/HO3_TRUE_FL_2021_denial.txt --output .tmp/phase2-final-live-focused.json`

#### Deferred
- Token/cost telemetry in checked-in benchmark artifacts.
- A-G quality scoring or evaluation harnesses.
- Deployment/auth/storage/PDF export work.
- Public demo work.

#### Next session starter
- Phase 2 is closed. Pick the next issue explicitly; likely post-Phase-2 candidates are #18 Streamlit deployment prep or #20 walkthrough/screenshot recipe if they are still needed.
