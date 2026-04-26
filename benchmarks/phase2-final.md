# Phase 2 Final Benchmark Comparison

Date: 2026-04-26

This is the final Phase 2 comparison report for #53. It preserves the historical before-state report at `benchmarks/phase2-baseline.md` and records current measurements after the Phase 2 model/API/speed sprint.

## Scope

Phase 2 completed:

- #46 / PR #54: baseline benchmark harness and checked-in no-API baseline report.
- #47 / PR #56: Responses API migration.
- #48 / PR #58: Structured Outputs for final dispute report generation only.
- #49 / PR #60: stage-specific model configuration.
- #50 / PR #62: bounded section-summary concurrency.
- #51 / PR #64: redundant live policy PDF reprocessing removed.
- #52 / PR #66: focused-analysis mode.

No prompts, report schemas/dataclasses, model defaults, stage-specific model defaults, focused-analysis behavior, section-summary concurrency behavior, citation/source accordion behavior, token/cost telemetry, quality scoring harnesses, deployment, auth, storage, or PDF export behavior were changed for this final report.

## Historical Baseline Reference

The Phase 2 before-state report remains `benchmarks/phase2-baseline.md`.

That baseline was intentionally deterministic and offline:

- Command: `python scripts/benchmark_phase2_baseline.py --mode demo`
- API calls made: no
- Input: checked-in demo bundle under `assets/demo/`
- Total wall-clock runtime: 0.0024 seconds
- Demo citations: 23
- Linked demo citations: 23
- Rendered Markdown characters: 5,895

The baseline did not measure PDF extraction, policy sectioning, OpenAI latency, token usage, cost, live denial-aware report generation, or Streamlit browser rendering.

## Current Demo-Bundle Parity

Current run:

```bash
python scripts/benchmark_phase2_baseline.py --mode demo --output .tmp/phase2-final-demo.json
```

Result on 2026-04-26:

| Metric | Historical baseline | Current rerun |
| --- | ---: | ---: |
| API calls made | no | no |
| Total wall-clock runtime | 0.0024 seconds | 0.0437 seconds |
| Demo citations | 23 | 23 |
| Linked demo citations | 23 | 23 |
| Rendered Markdown characters | 5,895 | 5,895 |
| Demo source-map entries | 13 | 13 |

Current stage timings:

| Stage | Wall-clock seconds |
| --- | ---: |
| `load_demo_assets` | 0.0417 |
| `build_dispute_report_object` | 0.0001 |
| `render_dispute_markdown` | 0.0002 |
| `link_demo_citations` | 0.0016 |

Interpretation: the deterministic demo output shape is preserved. Citation totals, linked citation totals, rendered Markdown length, and stage coverage match the before-state expectations. The wall-clock number is local filesystem/runtime noise and is not a live model latency measurement.

## Current Live Full Analysis

Current run:

```bash
python scripts/benchmark_phase2_baseline.py --mode live \
  --policy-pdf data/raw_policies/HO3_TRUE_FL_2021.pdf \
  --denial-text data/raw_denials/HO3_TRUE_FL_2021_denial.txt \
  --output .tmp/phase2-final-live-full.json
```

Result on 2026-04-26:

| Metric | Value |
| --- | ---: |
| API calls made | yes |
| Analysis mode | full |
| Total wall-clock runtime | 83.3361 seconds |
| Policy summary pipeline | 48.5842 seconds |
| Denial/dispute pipeline | 34.6988 seconds |
| Summarized policy sections | 25 |

Token usage and cost remain `null` in the checked-in benchmark payload because the benchmark harness does not add token/cost telemetry.

## Current Live Focused Analysis

Current run:

```bash
python scripts/benchmark_phase2_baseline.py --mode live --focused \
  --policy-pdf data/raw_policies/HO3_TRUE_FL_2021.pdf \
  --denial-text data/raw_denials/HO3_TRUE_FL_2021_denial.txt \
  --output .tmp/phase2-final-live-focused.json
```

Result on 2026-04-26:

| Metric | Value |
| --- | ---: |
| API calls made | yes |
| Analysis mode | focused |
| Total wall-clock runtime | 32.0213 seconds |
| Policy summary pipeline | 12.4485 seconds |
| Denial/dispute pipeline | 19.5184 seconds |
| Summarized policy sections | 4 |

The focused run summarized these current fixture sections:

- `DEFINITIONS`
- `CONDITIONS`
- `COVERAGE C - PERSONAL PROPERTY`
- `EXCLUSIONS`

## Current Full vs Focused Comparison

| Metric | Full | Focused | Change |
| --- | ---: | ---: | ---: |
| Summarized policy sections | 25 | 4 | 84.0% fewer |
| Total wall-clock runtime | 83.3361s | 32.0213s | 61.6% lower |
| Policy summary pipeline | 48.5842s | 12.4485s | 74.4% lower |
| Denial/dispute pipeline | 34.6988s | 19.5184s | 43.7% lower |

Interpretation: focused mode materially reduces section-summary work for this fixture by filtering the policy summary input before LLM section-summary calls. The dispute stage also ran faster in this single live comparison because it received a smaller policy-summary payload.

## Limitations

- No pre-Phase-2 live baseline was captured. The historical baseline is a deterministic no-API demo benchmark, not a live model/API benchmark.
- Token usage and cost are not captured in checked-in benchmark artifacts.
- The live full/focused results are a single-fixture local measurement and should not be generalized as a production latency guarantee.
- No A-G quality scoring or evaluation harness was added.
- The live benchmark writes local runtime artifacts under `data/processed`; those outputs are not part of this report and should not be committed.
- W&B may record telemetry if enabled in the local environment, but W&B output is not used as a checked-in benchmark source here.

## Final Recommendation

Phase 2 achieved the intended modernization and performance work without changing prompts, schemas, product scope, or deployment posture. The app now uses the Responses API, strict Structured Outputs for final dispute reports, optional stage-specific model overrides, bounded section-summary concurrency, one-pass live PDF section reuse for citation/source support, and explicit opt-in focused analysis.

Stop Phase 2 after #53. Consider #18 Streamlit deployment prep and #20 walkthrough/screenshot recipe later as separate, post-Phase-2 work.
