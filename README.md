# Policy Dispute AI Assistant

AI assistant for turning **homeowners insurance policies (HO3)** and **claim denial letters** into **dispute‑focused reports**.

- Designed for **public adjusters, coverage counsel, and their teams**
- Built to **surface leverage points and blind spots**, not to replace human judgment
- **Not legal advice** and not a coverage determination

---

## What this tool does

### 1. Policy‑only summary (baseline)

Feed it one or more HO3 policy PDFs and it will:

- Split each policy into logical sections (Definitions, Coverages, Exclusions, Conditions, endorsements, etc.)
- Summarize each section in plain English
- Extract:

  - Key coverages
  - Key exclusions / limitations
  - Notable conditions / duties
  - Possible dispute angles to explore

- Tag sections as **substantive** vs **meta / boilerplate** (regulator pages, ISO copyright, sample notices, etc.)
- Emit a **claim‑facing Markdown report** per policy

Outputs live in `data/processed/<POLICY_ID>.report.md`.

### 2. Policy + denial A–G dispute report (v0)

Given:

- A **policy summary JSON** (from the baseline pipeline), and
- A **denial letter in plain text**

the tool builds a **structured A–G dispute report**:

**A.** Plain‑English overview of the dispute
**B.** Coverage highlights that may support the insured
**C.** Key exclusions / limitations that may hurt the insured
**D.** Denial reasons (as stated / implied by the insurer)
**E.** Possible dispute angles to explore (not legal advice)
**F.** Missing information / suggested next steps
**G.** Confidence + clauses to double‑check

This is the view you’d actually use in a claim review, mediation prep, or internal strategy meeting.

When you run the examples below, dispute reports are written as:

- JSON: `data/processed/<POLICY_ID>__<DENIAL_ID>.dispute.json`
- Markdown: `data/processed/<POLICY_ID>__<DENIAL_ID>.dispute.md`

---

## Who this is for

- **Public adjusters** who want a first pass on complex policies and denials
- **Coverage and property‑damage attorneys** who want faster "issue spotting"
- **Technical folks** building internal tools for claims/legal teams
- Anyone curious about **how AI can assist** in coverage disputes without giving legal advice

If you’re non‑technical, you can still skim the example reports to see the kind of structure this tool produces.

---

## Project structure

```text
data/
  raw_policies/      # Input PDFs (HO3 sample forms, carrier forms)
  raw_denials/       # Input denial letters as .txt
  processed/         # JSON + Markdown outputs

notebooks/           # Exploration / development notebooks

src/
  config.py          # Environment + model settings
  llm_client.py      # OpenAI client + JSON helper
  pdf_loader.py      # PDF -> text
  sectioning.py      # Policy section splitter + role tagging
  summarizer_frontier.py
                     # Section summarizer + denial-aware report builder
  run_baseline_policy_summary.py
                     # CLI: policies -> section summaries (JSON)
  report_builder.py  # CLI helpers + Markdown renderers
  run_denial_summary.py
                     # CLI: policy JSON + denial.txt -> A–G dispute report
```

---

## Getting started

### 1. Clone and create a virtualenv

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

### 2. Configure your OpenAI API key

Create a `.env` file in the project root (you can copy from `.env.example` if it exists):

```bash
OPENAI_API_KEY=sk-...
# optional override, otherwise defaults are set in config.py
OPENAI_MODEL=gpt-4.1-mini
```

The code uses `src/config.py` and `src/llm_client.py` to read these values.

### 3. Add some sample policies

Drop HO3 policy PDFs into:

```text
data/raw_policies/
```

The repo includes anonymized samples, for example:

- `HO3_TRUE_FL_2021.pdf`
- `HO3_USAA_TX_OPIC_2008.pdf`
- ISO and carrier variants

### 4. Run the baseline policy summarizer

This builds normalized JSON summaries and claim‑facing Markdown reports.

```bash
# Summarize all PDFs in data/raw_policies/
python -m src.run_baseline_policy_summary data/raw_policies
```

Outputs:

- JSON: `data/processed/<POLICY_ID>.json`
- Markdown: `data/processed/<POLICY_ID>.report.md`

Open one of the `.report.md` files in VS Code or GitHub to see the structure.

### 5. Add a denial letter

For now, v0 expects a **plain‑text** denial letter.

Put a `.txt` file in:

```text
data/raw_denials/
```

Example (included or easy to recreate):

- `data/raw_denials/HO3_TRUE_FL_2021_denial.txt`

This is a realistic water‑damage denial (late notice, long‑term leakage, deductible issues, etc.).

### 6. Build an A–G dispute report

Use the denial‑aware CLI:

```bash
python -m src.run_denial_summary \
  data/processed/HO3_TRUE_FL_2021.json \
  data/raw_denials/HO3_TRUE_FL_2021_denial.txt
```

This writes:

- JSON: `data/processed/HO3_TRUE_FL_2021__HO3_TRUE_FL_2021_denial.dispute.json`
- Markdown: `data/processed/HO3_TRUE_FL_2021__HO3_TRUE_FL_2021_denial.dispute.md`

Open the `.md` in your editor or on GitHub to see the full A–G analysis.

You can reuse the same denial against different policies to stress‑test behavior:

```bash
python -m src.run_denial_summary \
  data/processed/HO3_USAA_TX_OPIC_2008.json \
  data/raw_denials/HO3_TRUE_FL_2021_denial.txt
```

---

## Command reference

### Baseline policy summary

```bash
python -m src.run_baseline_policy_summary <path-or-directory>
```

Example:

```bash
python -m src.run_baseline_policy_summary data/raw_policies
```

### Policy + denial A–G dispute report

```bash
python -m src.run_denial_summary <policy_summary.json> <denial_letter.txt>
```

Example:

```bash
python -m src.run_denial_summary \
  data/processed/HO3_TRUE_FL_2021.json \
  data/raw_denials/HO3_TRUE_FL_2021_denial.txt
```

---

## Safety, limitations, and disclaimers

This project is **experimental** and intended for **education and workflow support only**.

- It **does not provide legal advice**.
- It **does not make coverage determinations**.
- It can misread OCR’d text, mis‑interpret policy language, or miss important nuances.
- Any outputs **must be reviewed by a licensed professional** before being relied on.

If you use this in real‑world work:

- Treat it as a **research assistant** or “issue spotter,” not a decision‑maker.
- Always cross‑check cited clauses against the actual policy and endorsements.
- Be mindful of confidentiality and PII if you process real claims.

---

## Roadmap (high‑level)

Some directions under consideration:

- **UI demo** (Streamlit or similar) so non‑technical users can drag‑and‑drop policies and denials.
- **Voice mode v1**: push‑to‑talk interface on top of the same A–G analysis.
- Better **section taxonomy** (base form vs endorsements vs meta) in the reports.
- Model/cost tuning and caching for large batches of policies.
- Integration with richer document stores and RAG pipelines for large claim files.

---

## License

This project is licensed under the [MIT License](LICENSE).
