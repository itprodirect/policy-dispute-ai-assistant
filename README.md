# Policy Dispute AI Assistant

AI assistant for turning homeowners policies and denial letters into dispute‑focused summaries (A–G structure) for public adjusters and attorneys.

> **Status:** Internal prototype / demo
>
> **Frontend:** Streamlit v1 UX (`frontend/app.py`)
>
> **Backend:** Python pipelines in `src/` for policy + denial analysis using OpenAI models

This repo is **not** a legal product. It is an educational / research tool for exploring how LLMs can help with property‑claim disputes.

---

## What the app does

Given:

- A homeowners policy PDF (currently optimized for HO3 forms), and
- A denial letter PDF for a specific claim,

…the app:

1. **Extracts and sections the policy** into definitions, coverages, exclusions, conditions, etc.
2. **Summarizes each section** with a custom prompt tuned for HO3‑style language.
3. **Analyzes the denial letter** and maps denial reasons back to relevant policy concepts.
4. **Builds an A–G dispute report** that mirrors how public adjusters and coverage attorneys think about a file:

   - A – Plain‑language overview
   - B – Coverage highlights that may help the insured
   - C – Key exclusions / limitations
   - D – Denial reasons & cited clauses
   - E – Possible dispute angles
   - F – Missing info / suggested next steps
   - G – Confidence notes & clauses to double‑check

5. **Renders the results in a Streamlit UI** with:

   - A “New claim” upload flow and progress bar (steps 1–4)
   - A **Results** screen with:

     - Hero summary (plain‑language story + key takeaways)
     - Downloadable Markdown report
     - Tabs for Dispute summary (A–G), Policy highlights, Denial reasons & angles, and Confidence / debug.

The goal is to give a **fast triage view** for busy professionals, not to replace full policy / case review.

---

## Screenshots (v1 UX)

The repo’s GitHub PR and issues contain screenshots of:

- **New claim flow** – upload policy + denial PDFs, optional nickname and state, step 1–4 progress bar.
- **Results view** – A–G dispute summary, policy highlight checklist, denial reasons & angles, download button.

---

## Repo structure

```text
policy-dispute-ai-assistant/
├─ src/
│  ├─ config.py              # Env + safety flags (SAFE_MODE, PERSIST_RAW_TEXT, etc.)
│  ├─ llm_client.py          # Thin wrapper around OpenAI Responses API
│  ├─ pdf_loader.py          # PDF -> text extraction helpers
│  ├─ sectioning.py          # Split policy into logical sections
│  ├─ summarizer_frontier.py # Build denial-aware A–G report from summaries
│  ├─ report_builder.py      # Turn DisputeReport into Markdown
│  ├─ schemas.py             # Pydantic models for sections and DisputeReport
│  ├─ demo_api.py            # Simple API-style helpers used by the frontend
│  ├─ wandb_telemetry.py     # W&B run lifecycle, rollups, A-G quality evaluator
│  ├─ run_baseline_policy_summary.py   # CLI: summarize policy only
│  └─ run_denial_summary.py            # CLI: summarize denial letters only
│
├─ scripts/
│  └─ model_compare.py       # Run same fixture through multiple models with W&B telemetry
│
├─ frontend/
│  ├─ app.py                 # Streamlit v1 UX (current demo)
│  └─ app_v0_minimul.py      # Original single-page prototype (kept for reference)
│
├─ data/
│  ├─ processed/             # Sample JSON + Markdown outputs (checked in)
│  └─ uploads/               # Local upload cache (gitignored)
│
├─ notebooks/                # Experimental notebooks / scratchpads
├─ .env.example              # Sample env vars
├─ requirements.txt          # Python dependencies
└─ README.md                 # You are here
```

---

## Prerequisites

- Python **3.10+**
- An OpenAI API key with access to `gpt-4.1-mini` (or compatible model)

---

## Setup

Clone the repo and create a virtual environment:

```bash
git clone https://github.com/itprodirect/policy-dispute-ai-assistant.git
cd policy-dispute-ai-assistant

python -m venv .venv
# Windows
source .venv/Scripts/activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

### Environment variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env  # on Windows: copy .env.example .env
```

Then edit `.env` and set at least:

```bash
OPENAI_API_KEY="sk-..."

# Optional – override default model (defaults to gpt-4.1-mini)
OPENAI_MODEL="gpt-4.1-mini"

# Data-handling flags
SAFE_MODE=true          # when true, raw text is not persisted to disk
PERSIST_RAW_TEXT=false  # only set true if you explicitly want raw text saved
```

The `src/config.py` module enforces these flags strictly:

- If `SAFE_MODE=true`, raw policy/denial text is **never** persisted, even if `PERSIST_RAW_TEXT` was turned on.
- If flags have invalid values, the app will raise a `ConfigError` instead of silently misbehaving.

---

## Running the Streamlit app (v1 UX)

From the repo root, with your virtualenv activated and `.env` configured:

```bash
streamlit run frontend/app.py
```

This will start Streamlit on `http://localhost:8501`.

### New claim flow

1. Go to the **New claim** page (default).
2. Fill in:

   - **Claim nickname** (optional; used in filenames and headings)
   - **State** (optional; future hook for state‑specific guidance)

3. Upload:

   - **Policy PDF** – HO3 form for now (other forms may work but are less tested).
   - **Denial letter PDF** – corresponding denial for this claim.

4. Click **Analyze claim**.
5. Watch the bottom status bar as the app walks through:

   - Step 1/4 – Analyzing policy PDF
   - Step 2/4 – Analyzing denial letter
   - Step 3/4 – Building A–G dispute report
   - Step 4/4 – Done

6. When complete, the page scrolls to the **Results** section.

### Results view

The results page is split into:

- **Dispute overview**

  - A plain‑language narrative paragraph
  - 2–4 bullet **Key takeaways** for quick gut‑check

- **Actions**

  - Button to **Download dispute report (Markdown)** – can be pasted into Word/Docs as a starting draft

- **Detailed dispute views** (tabs):

  - **Dispute summary (A–G)** – structured expanders for A–G with inline citations
  - **Policy highlights** – checklist view of helpful provisions vs exclusions
  - **Denial reasons** – bullet list of carrier’s reasons mapped to policy concepts
  - **Confidence / debug** – meta notes and flags where the model is less confident

Under the A–G tab there is an optional **“Full policy breakdown”** section that can show more verbose policy summaries when needed.

---

## CLI utilities (optional)

You can also run the underlying pipelines from the command line without Streamlit.

### Summarize a policy PDF

```bash
python -m src.run_baseline_policy_summary --policy-pdf path/to/policy.pdf
```

Outputs a JSON file like `data/processed/<stem>.json` containing section summaries.

### Summarize a denial letter

```bash
python -m src.run_denial_summary --denial-pdf path/to/denial.pdf
```

Outputs a JSON or Markdown summary for the denial (depending on current implementation).

### Build a combined dispute report (used by the frontend)

The Streamlit app uses `src/demo_api.py` to:

1. Run the policy and denial pipelines.
2. Call `build_denial_aware_report(...)` from `summarizer_frontier.py`.
3. Render the final Markdown via `report_builder.render_dispute_markdown(...)`.

If you want to script this yourself, `demo_api.py` is the best entry point to study.

---

## W&B telemetry (optional)

The app supports optional [Weights & Biases](https://wandb.ai) logging for run-level telemetry.  Enable it to compare models, track quality, and catch regressions.

### What gets logged

| Namespace | Fields | When |
|-----------|--------|------|
| `llm/*` | `model`, `stage`, `latency_ms`, `prompt_tokens`, `completion_tokens`, `total_tokens`, `success`, `attempt`, `error_type`, `temperature` | Every LLM call |
| `run/*` | `total_tokens`, `total_prompt_tokens`, `total_completion_tokens`, `total_latency_ms`, `calls`, `errors` | Once, at run finish |
| `quality/*` | `ag_present_count`, `ag_order_ok` | Once, after dispute report generation |
| `run/` (config) | `claim_id`, `mode`, `git_commit`, `safe_mode`, `persist_raw_text`, `default_model` | Set at run start |

**Privacy**: No raw policy, denial, report, or prompt text is ever sent to W&B. Only hashes, counts, timings, and flags.

### Enabling W&B

Add to your `.env`:

```bash
WANDB_ENABLED=true
WANDB_PROJECT=policy-dispute-ai
WANDB_ENTITY=itprodirect     # optional; your W&B team/user name
```

W&B runs are created automatically per claim in `demo_api.py` (Streamlit) or per model in `scripts/model_compare.py`.

### Model comparison

Compare models side-by-side, each producing a separate W&B run:

```bash
# Default: runs gpt-4.1-mini against bundled fixtures
python -m scripts.model_compare

# Custom fixtures and models
python -m scripts.model_compare \
  --policy_text_fixture data/processed_safe/HO3_TRUE_FL_2021.json \
  --denial_text_fixture data/raw_denials/HO3_TRUE_FL_2021_denial.txt \
  --models gpt-4.1-mini,gpt-4.1,gpt-4o-mini
```

Filter runs in the W&B UI by config value `run/mode`:
- `policy_only` -- policy-only analysis from Streamlit
- `dispute` -- full dispute report from Streamlit
- `model_compare` -- model comparison script

### Where to find run config in W&B

Open any run in the W&B dashboard, then: **Overview tab > Config section**.  The `run/*` fields (claim_id, mode, git_commit, safe_mode, default_model) are there.  They are also saved in the run's `config.yaml` under the Files tab.

---

## Data handling & safety

This repo is meant for **local experiments**, not production.

- PDFs are uploaded to `data/uploads/` (which is **gitignored**) for the duration of a run.
- Processed summaries and dispute reports are written to `data/processed/` for inspection.
- All calls to OpenAI go through your own API key.
- Use `SAFE_MODE=true` if you want to avoid persisting raw policy/denial text to disk.

**Do not commit real client data** to the repo, and be careful when sharing outputs that may contain PII or sensitive claim details.

---

## Roadmap / ideas

Some obvious next steps:

- **Better HO3 coverage & carrier diversity** – tune sectioning + prompts across more forms.
- **State‑aware guidance** – use the `state` field to condition dispute angles.
- **Multi‑claim workspace** – basic history of recent analyses.
- ** richer policy / denial upload validation** – catch wrong file types, corrupt PDFs, etc.
- **Export templates** – Word / Docs templates for CRNs, dispute letters, or attorney memos.

If you experiment with the repo and find issues or ideas, feel free to open GitHub Issues or PRs.

---

## Legal disclaimer

- This project is **not legal advice** and does **not** create an attorney–client relationship.
- Outputs are AI‑generated and may be incomplete, inaccurate, or outdated.
- Always verify results against the actual policy, denial letter, and applicable law before using anything in a real dispute.

---

## License

This repo is under the MIT license (see `LICENSE`). Use it, fork it, and adapt it to your own workflows at your own risk.
