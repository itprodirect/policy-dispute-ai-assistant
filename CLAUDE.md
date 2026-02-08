# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI assistant that analyzes homeowners insurance policies (HO3 forms) and denial letters to generate structured A-G dispute reports for public adjusters and attorneys. This is an internal prototype, not a legal product.

## Commands

### Run the Streamlit app
```bash
streamlit run frontend/app.py
```

### CLI: Summarize a policy PDF
```bash
python -m src.run_baseline_policy_summary path/to/policy.pdf
```

### CLI: Build dispute report from policy summary + denial text
```bash
python -m src.run_denial_summary data/processed/policy.json path/to/denial.txt
```

### Build Markdown reports from existing JSON summaries
```bash
python -m src.report_builder data/processed/
```

### Model comparison (W&B telemetry)
```bash
python -m scripts.model_compare
python -m scripts.model_compare --models gpt-4.1-mini,gpt-4.1
```

## Environment Setup

Copy `.env.example` to `.env` and set:
- `OPENAI_API_KEY` (required)
- `OPENAI_MODEL` (defaults to `gpt-4.1-mini`)
- `SAFE_MODE=true` prevents raw policy text from being persisted
- `PERSIST_RAW_TEXT=false` to strip raw text from outputs
- `WANDB_ENABLED=true` for optional run-level W&B telemetry
- `WANDB_PROJECT=policy-dispute-ai` (default)
- `WANDB_ENTITY=itprodirect` (recommended; your W&B team/user)

## Architecture

### Data Flow
1. **PDF Ingestion**: `pdf_loader.load_pdf_text()` extracts text via pypdf
2. **Sectioning**: `sectioning.split_into_sections()` splits policy text into canonical sections (DEFINITIONS, EXCLUSIONS, COVERAGE A-D, etc.) using HO3-specific heading detection
3. **Section Summarization**: `summarizer_frontier.summarize_section()` calls OpenAI to extract key coverages, exclusions, conditions, and dispute angles per section
4. **Dispute Report**: `summarizer_frontier.build_denial_aware_report()` combines policy summaries with denial letter text to produce the A-G report structure
5. **Rendering**: `report_builder.render_dispute_markdown()` and `render_dispute_docx()` convert DisputeReport to Markdown or Word (.docx)

### Key Modules
- `src/config.py`: Settings singleton via `get_settings()`, enforces SAFE_MODE/PERSIST_RAW_TEXT flags
- `src/llm_client.py`: `call_llm_json()` wrapper with retry logic, JSON response parsing, per-call W&B metrics (`stage` param labels each call)
- `src/wandb_telemetry.py`: **Sole owner** of W&B lifecycle (`start_wandb_run()`, `finish_wandb_run()`); run rollups; A-G quality evaluator. No other module may call `wandb.init()`.
- `src/schemas.py`: Pydantic-style dataclasses for `SectionSummary`, `DisputeReport`, `Point`, `Angle`, `ConfidenceBlock`
- `src/demo_api.py`: High-level service layer used by Streamlit frontend (`run_policy_analysis()`, `run_dispute_analysis()`); sets W&B run boundaries per claim via try-finally
- `src/database.py`: SQLite-based claim history storage (`save_claim()`, `get_all_claims()`, `get_claim_by_id()`)
- `scripts/model_compare.py`: CLI tool to run the same fixture through multiple models with separate W&B runs for comparison

### A-G Report Structure
- A: Plain-language overview
- B: Coverage highlights supporting the insured
- C: Exclusions/limitations hurting the insured
- D: Denial reasons with policy citations
- E: Dispute angles to explore
- F: Missing information / next steps
- G: Confidence score and clauses to verify

### File Outputs
- `data/uploads/`: Temporary uploaded PDFs (gitignored)
- `data/processed/`: JSON summaries + Markdown reports (normal mode)
- `data/processed_safe/`: Outputs when SAFE_MODE=true
- `data/claims.db`: SQLite database for claim history (gitignored)

## Code Patterns

- All LLM calls go through `call_llm_json()` which expects JSON responses via OpenAI's `response_format={"type": "json_object"}`
- Each `call_llm_json()` call accepts a `stage` param (e.g. `"section_summary"`, `"dispute_report"`) that is logged to W&B as `llm/stage`
- W&B lifecycle is deterministic: only `src/wandb_telemetry.py` calls `wandb.init()`/`wandb.finish()`; `llm_client.py` guards `wandb.log()` behind `wandb.run is not None`
- No raw policy, denial, report, or prompt text is ever sent to W&B (privacy-safe); only hashes, counts, timings, and flags
- Section detection uses regex patterns in `sectioning.py` for HO3 headings (SECTION I/II, COVERAGE A-D)
- `classify_section_role()` in `run_baseline_policy_summary.py` separates substantive policy sections from meta/boilerplate
- Streamlit app uses `st.session_state` to persist analysis results between rerenders
