# Phase 2 Baseline Benchmark

This is the before-state benchmark for Phase 2. It exists to record what the current Phase 1 app can measure before Responses API work, Structured Outputs, model swaps, prompt/schema changes, or speed refactors begin.

## Baseline run

- Date: 2026-04-25
- Command: `python scripts/benchmark_phase2_baseline.py --mode demo`
- Input: checked-in demo bundle:
  - `assets/demo/demo.json`
  - `assets/demo/demo.report.md`
  - `assets/demo/section_text.json`
- API calls made: no
- Environment assumptions: local Python environment with repo dependencies installed.

## What this measures

- Loading the deterministic demo bundle.
- Converting the checked-in demo dispute JSON into the existing `DisputeReport` dataclass.
- Rendering Markdown through the existing `render_dispute_markdown` path.
- Resolving demo citations through the existing citation-linking helper.
- Total wall-clock runtime and per-stage wall-clock timing for those steps.

## What this does not measure

- PDF extraction.
- Policy sectioning.
- OpenAI latency.
- Token usage.
- Cost per claim.
- Live denial-aware report generation.
- Streamlit browser rendering.

## Baseline result

Local run on 2026-04-25 using `python scripts/benchmark_phase2_baseline.py --mode demo`:

| Metric | Value |
| --- | ---: |
| Total wall-clock runtime | 0.0024 seconds |
| Demo citations | 23 |
| Linked demo citations | 23 |
| Rendered Markdown characters | 5,895 |

Stage timings from the same run:

| Stage | Wall-clock seconds |
| --- | ---: |
| `load_demo_assets` | 0.0011 |
| `build_dispute_report_object` | 0.0001 |
| `render_dispute_markdown` | 0.0001 |
| `link_demo_citations` | 0.0010 |

Run environment:

- Python: 3.12.3
- Platform: Windows-11-10.0.26200-SP0

## Live pipeline benchmark

The same harness can run the current live pipeline when non-sensitive local inputs and `OPENAI_API_KEY` are available:

```bash
python scripts/benchmark_phase2_baseline.py --mode live \
  --policy-pdf data/raw_policies/HO3_TRUE_FL_2021.pdf \
  --denial-text data/raw_denials/HO3_TRUE_FL_2021_denial.txt \
  --output .tmp/phase2-baseline-live.json
```

Live mode makes OpenAI API calls and writes the same local `data/processed` or `data/processed_safe` artifacts as the current pipeline. It is intentionally not the default because the repo should have a safe deterministic benchmark that can run without API access.

## Limitations

- The checked-in before-state number is the deterministic no-API benchmark, not a full model/API latency benchmark.
- Token usage and cost are not reported because the current pipeline does not expose them outside optional W&B telemetry.
- Future Phase 2 benchmark reports should compare against this offline baseline and, where API access is available, add a live-pipeline baseline run with the same script.
