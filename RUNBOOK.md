# Runbook (policy-dispute-ai-assistant)

## Purpose

Local-first Streamlit app that analyzes an HO3 policy + denial letter to generate a structured dispute report (A–G) for adjusters/attorneys.

This is a drafting / decision-support tool — outputs require human review.

---

## Quick Start (Live Mode)

1. Activate venv
2. Install deps:
   - `pip install -r requirements.txt`
3. Create `.env` (or set env vars) with:
   - `OPENAI_API_KEY=...`
   - recommended: `SAFE_MODE=true`
4. Run:
   - `streamlit run frontend/app.py`

---

## Demo Mode (Offline / Conference Mode)

Goal: Run the full demo with **zero API calls**.

### Demo assets

Deterministic demo files live here:

- `data/processed/demo/demo.json`
- `data/processed/demo/demo.report.md`

### Steps

1. Run:
   - `streamlit run frontend/app.py`
2. Toggle **Demo Mode (offline)** ON
3. Confirm results render end-to-end (no key required)

### If demo assets are missing

Use one of the sample pairs in `data/processed/` and copy them into:

- `data/processed/demo/demo.json`
- `data/processed/demo/demo.report.md`

Primary recommended source:

- `HO3_ISO_1999_III_SAMPLE__1768603155` + `.report`

---

## Common Commands

- Run app:
  - `streamlit run frontend/app.py`

- CLI (optional):
  - `python -m src.run_baseline_policy_summary path/to/policy.pdf`
  - `python -m src.run_denial_summary data/processed/policy.json path/to/denial.txt`
  - `python -m src.report_builder data/processed/`

- Model comparison (requires `WANDB_ENABLED=true`):
  - `python -m scripts.model_compare`
  - `python -m scripts.model_compare --models gpt-4.1-mini,gpt-4.1`
  - `python -m scripts.model_compare --policy_text_fixture data/processed_safe/HO3_TRUE_FL_2021.json --denial_text_fixture data/raw_denials/HO3_TRUE_FL_2021_denial.txt --models gpt-4.1-mini,gpt-4.1,gpt-4o-mini`

---

## W&B Telemetry

### Overview

When `WANDB_ENABLED=true`, each claim analysis (Streamlit) or model comparison run creates a W&B run with:

- **Per-call metrics** (`llm/*`): `model`, `stage`, `latency_ms`, `prompt_tokens`, `completion_tokens`, `total_tokens`, `success`, `attempt`, `error_type`, `temperature`
- **Run rollups** (`run/*`): `total_tokens`, `total_prompt_tokens`, `total_completion_tokens`, `total_latency_ms`, `calls`, `errors`
- **Quality metrics** (`quality/*`): `ag_present_count` (0-7), `ag_order_ok` (bool)
- **Run config** (`run/*`): `claim_id`, `mode`, `git_commit`, `safe_mode`, `persist_raw_text`, `default_model`

**Privacy**: No raw policy/denial/report/prompt text is ever sent to W&B.

### Env vars

```bash
WANDB_ENABLED=true
WANDB_PROJECT=policy-dispute-ai
WANDB_ENTITY=itprodirect          # recommended; your W&B team/user
SAFE_MODE=true                    # recommended
OPENAI_API_KEY=sk-...
```

### Where to find run config in W&B

Open any run in the W&B dashboard, then: **Overview tab > Config section**.
The `run/*` fields are there.  Also available as `config.yaml` under the **Files** tab.

### Filtering runs

Filter by `run/mode` config value:
- `policy_only` -- policy analysis via Streamlit
- `dispute` -- full dispute report via Streamlit
- `model_compare` -- model comparison script

---

## Troubleshooting

### Streamlit boots but errors when demo mode is on

- Confirm both files exist:
  - `data/processed/demo/demo.json`
  - `data/processed/demo/demo.report.md`

### Live mode fails due to missing key

- Ensure `.env` exists and contains `OPENAI_API_KEY`
- Or set the environment variable in your shell/session

### "pytest not installed"

If you want tests as a status check:

- `pip install pytest`
- `python -m pytest -q`

### "wandb.init() called while a run is active"

W&B lifecycle is owned exclusively by `src/wandb_telemetry.py`.
If you see this error, another module is calling `wandb.init()` directly.
Fix: remove the competing `wandb.init()` call and use `start_wandb_run()` from `wandb_telemetry` instead.

### "You must call wandb.init() before wandb.log()"

All `wandb.log()` calls are guarded by `wandb.run is not None`.
This error means a run was not started via `start_wandb_run()` before logging.
Fix: ensure `demo_api.py` (or your script) calls `start_wandb_run()` before any LLM calls.

### "Using a boolean value for 'reinit' is deprecated"

Non-blocking warning from wandb >= 0.23.  The `reinit=True` kwarg in `start_wandb_run()` can be updated to `finish_previous=True` in a future cleanup.  Does not affect functionality.

---

## Safety defaults

Recommended for local dev and demos:

- `SAFE_MODE=true`
- `PERSIST_RAW_TEXT=false`
  Never commit real client documents or outputs containing PII.
