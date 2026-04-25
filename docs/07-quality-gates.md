# Quality Gates

## Local Validation

- Run `git status --short` before and after work.
- For Python changes, run `python -m pytest -q` unless the task is docs-only or there is a documented blocker.
- For Streamlit UI changes, run `streamlit run frontend/app.py` and verify the changed flow manually.

## README Screenshot Validation

- Confirm every README image path resolves.
- Do not edit committed final screenshots unless a README link is broken or a focused screenshot issue requires it.
- Screenshots must not expose secrets, real client names, real claim numbers, real claim data, or unsafe artifacts.
- Do not add fake testimonials, fake client proof, or implied production outcomes.

## Demo Safety Validation

- `DEMO_FORCE_ON=true` should keep public demos deterministic.
- Hosted demo safety means uploads and live API-backed analysis are disabled.
- Demo artifacts must remain demo-safe and not rely on gitignored local files.

## API-Backed Validation

- Local live analysis requires a valid `.env` with `OPENAI_API_KEY`.
- Prefer `SAFE_MODE=true` and `PERSIST_RAW_TEXT=false`.
- Validate API-backed work with non-sensitive sample files only.
- Always compare generated reports against the source policy and denial; output is AI-generated.

## Future CI

#19 should add GitHub Actions CI for `python -m pytest -q`. Until then, local pytest output is the primary automated validation signal.
