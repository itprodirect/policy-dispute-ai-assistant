Archived note: This document is preserved for project history. It may contain stale issue status or paths. See docs/01-current-state.md and docs/03-roadmap.md for current status.

# v1.5 Demo Polish — Audit & Issue Plan

**Status:** Audit + implementation plan. Foundation fixes #10 and #24 are complete; Phase 1 demo-hardening issues #12, #13, #14, #16, and #17 are complete. Issue #15 remains open for README screenshots and repo first-impression polish.
**Audience:** Codex 5.5 Pro implementation, plus reviewers converting items into GitHub issues.
**Goal:** Take the existing internal Streamlit prototype and turn it into something that holds up under a portfolio screenshot, a 60–90 second walkthrough video, and a selective live demo — without rewriting the backend.

---

## 1. Current-state audit (concise)

### 1.1 What works now
- **End-to-end pipeline is real.** PDF → sectioning → per-section LLM summary → denial-aware A–G report (`src/summarizer_frontier.py`, `src/demo_api.py`).
- **A–G dispute report is structurally sound.** Pydantic-style dataclasses (`schemas.DisputeReport`) cover all 7 sections, and both Markdown and `.docx` renderers exist (`src/report_builder.py`).
- **Streamlit v1 UX is fairly complete.** Sidebar nav, value-prop intake page, `st.status`-style 4-step progress, results hero with key takeaways, A–G tabs, Confidence tab, downloadable Markdown + Word, claim history page, and Recent claims entry point (SQLite at `data/claims.db`).
- **Citation linking is implemented.** `src/citation_linking.py` matches A–G citations back to raw section text and surfaces "View source" expanders in live runs (`tests/test_citation_linking.py` covers the matching logic).
- **Demo Mode and hosted-demo safety exist.** Sidebar Demo Mode loads deterministic demo files with zero API calls; `DEMO_FORCE_ON=true` locks hosted demos to that path, disables uploads/live analysis, and boots without `OPENAI_API_KEY`.
- **Privacy hygiene is present.** `SAFE_MODE` and `PERSIST_RAW_TEXT` flags in `src/config.py` route outputs to `data/processed_safe/` and strip raw text before returning to the UI.
- **Telemetry hooks are wired.** Optional W&B logging via `src/wandb_telemetry.py` (claim-level rollups, A–G presence metrics) — useful but off by default.
- **Disclaimers are present** in three places (intake page markdown, results page caption, rendered Markdown/Word reports) — framing is not legal advice.

### 1.2 What is demo-worthy now (with caveats)
- The **A–G structure** itself is the real differentiator and looks credible in screenshots.
- The **claim-history page** is a non-trivial feature that signals "real product" without being noisy.
- The **Word and Markdown export** is a strong "portfolio proof" — concrete artifacts a viewer can open.
- The **citation accordions** (`View source: COVERAGE A - DWELLING`) are a strong screenshot moment **if** the demo path can render them.

### 1.3 What looks prototype-ish or risky for screenshots
- ✅ **Demo Mode now ships with tracked assets.** PR [#25](https://github.com/itprodirect/policy-dispute-ai-assistant/pull/25) moved the deterministic offline bundle to `assets/demo/demo.json` and `assets/demo/demo.report.md`, so fresh clones no longer depend on gitignored `data/processed/demo/`.
- ✅ **Demo Mode now uses a denial-aware dispute bundle.** The tracked demo JSON is a compact A–G dispute report with populated denial reasons and confidence `0.90`, not the old policy-summary-only stub path.
- 🔴 **No sample input PDFs are tracked.** `data/raw_policies/` and `data/raw_denials/` are gitignored. A first-time visitor cannot do a real "upload and run" demo without bringing their own PDFs.
- ✅ **`.env.example` is now safe by default.** PR [#27](https://github.com/itprodirect/policy-dispute-ai-assistant/pull/27) changed `PERSIST_RAW_TEXT=false` and documented that `SAFE_MODE=true` strips raw text even if persistence is changed.
- ✅ **`requirements.txt` now pins direct runtime dependencies.** PR [#27](https://github.com/itprodirect/policy-dispute-ai-assistant/pull/27) added exact pins for the working local versions.
- ✅ **Hosted demo safety is in place.** `DEMO_FORCE_ON=true` locks the app to deterministic Demo Mode, disables uploads/live analysis, and no longer requires `OPENAI_API_KEY`.
- ✅ **New Claim has a 30-second value proposition.** The page now frames what the tool does, who it is for, and what it is not, with research-prototype / not-legal-advice framing.
- ✅ **Confidence/debug no longer dumps raw JSON by default.** The tab is now **Confidence**, with raw A-G JSON and artifact details behind collapsed developer expanders.
- ✅ **Live-analysis progress is cleaner.** The live workflow uses a single `st.status`-style block with explicit Step 1/4 through Step 4/4 labels.
- ✅ **Recent claims entry point exists.** The New Claim page shows up to two Recent claims when local history exists and reuses the existing Claim History detail view.
- 🟡 **Hero takeaways are weak.** The "Key takeaways" picker just grabs the first 3 items from coverage_highlights, then dispute_angles. No prioritization, no insurer-name display, no claim-context summary.
- 🟡 **No README screenshots.** README references screenshots "in the GitHub PR and issues" but the repo itself has zero embedded images. The GitHub repo card is text-only.
- 🟡 **`frontend/data/processed/`** exists as a stale duplicate (gitignored, but leftover from a prior `cwd` issue). Small code-hygiene smell.
- 🟡 **No CI / no badges.** No GitHub Actions; tests aren't being verified on push.

### 1.4 What's missing for a smooth live demo
- A *one-click* "Try this with the bundled sample claim" path that uses real PDFs already in the repo.
- README screenshots and first-impression polish (#15 remains open).
- Curated screenshot assets; add `docs/screenshots/` later only if selected screenshots are committed.
- A real Confidence tab screenshot if the saved capture set does not already include one.
- One live API-backed analysis run before release/demo recording to visually confirm the progress UI.

### 1.5 Architectural notes (not problems, just context)
- The pipeline is OpenAI-only via `chat.completions` with `response_format=json_object` (`src/llm_client.py`). Fine for v1.5; no change needed.
- Sectioning is HO3-tuned (`src/sectioning.py` aliases). Cross-form behavior is a known v2 problem, **not** a v1.5 polish item.
- `src/database.py` SQLite is small and well-scoped. Fine to keep; no need to add server DBs.

---

## 2. Recommended v1.5 target state

A user lands on the GitHub repo. They:
1. See **README screenshots** of the A–G dispute output and a one-line value prop.
2. Click a **deploy link** (or run locally in 5 minutes via the README quickstart).
3. On the running app, they see a **"Try the sample claim" CTA** at the top of the New Claim page — one click and the full A–G report renders against real (sanitized) sample PDFs.
4. The **Demo Mode toggle** still exists for zero-API flows and is wired to a *real* dispute bundle, not a stub.
5. The **Results view** has a clean hero, the four tabs, and a single "Download as Word / Markdown" pair — no raw-JSON-as-default-content visible to a screenshot.
6. The **README** has a clearly marked "*This is a research prototype, not legal advice*" framing block above the fold.
7. Hosting is **Streamlit Community Cloud** with `DEMO_FORCE_ON=true` so the public demo cannot accept user uploads or burn API credits.

What we are explicitly **not** doing in v1.5:
- No frontend rewrite (no Next.js, no React).
- No auth.
- No multi-user database.
- No new LLM features.
- No new policy form support.

---

## 3. Ranked issue plan

Each issue is sized for a focused PR. "Codex-safe" means the scope is narrow enough that an autonomous implementation should work without design judgment.

> **Conventions:** Files listed are *likely* — implementer should confirm. Validation commands assume a working venv with `.env` set.

---

### P0 — Blockers for "fresh clone, single click demo"

#### Issue P0-1 — Track demo assets and ship a real dispute bundle ([#10](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/10)) — Completed in PR [#25](https://github.com/itprodirect/policy-dispute-ai-assistant/pull/25)

**Priority:** P0
**Type:** code + data + docs
**Codex-safe:** ✅ yes (mechanical file moves + `.gitignore` change + small frontend tweak)

**Why it matters:** The single biggest gap. Today, `git clone` → `streamlit run` → toggle Demo Mode = error screen. And even when the assets exist locally, the demo's Section D is empty and confidence is `0.2`. Every screenshot of "Demo Mode" is currently a screenshot of a degraded code path.

**Scope:**
- Create a tracked, versioned location for demo assets: `assets/demo/` (preferred, outside `data/`) **or** carve out `!data/processed/demo/` in `.gitignore`.
- Replace `demo.json` with a *full dispute bundle* (the existing `HO3_USAA_TX_OPIC_2008__HO3_TRUE_FL_2021_denial.dispute.json` is the strongest candidate — confidence 0.9, real plain summary, populated A–G).
- Update `frontend/app.py:DEMO_ASSET_DIR` and `_load_demo_assets()` to point at the new location and prefer the `dispute_report`-shaped payload code path that already exists (`frontend/app.py:196`).
- Optionally include a small `assets/demo/section_text.json` snapshot so citation "View source" accordions also work in Demo Mode.
- Update `RUNBOOK.md` Demo Mode section so the "if missing, copy from..." instructions are removed (no longer required) — or kept as a fallback only.

**Acceptance criteria:**
- A fresh `git clone` followed by `streamlit run frontend/app.py` and toggling Demo Mode renders a populated A–G report with non-empty Section D and `confidence ≥ 0.8` — with **no** local file copying.
- The demo no longer triggers `_build_demo_dispute_report_from_policy()` (the synthesized stub path).
- README/RUNBOOK reflect the new asset path.
- No real client data is added; carrier/policy IDs in the dispute bundle are public form names (HO3 ISO, USAA, TRUE FL — all regulator-filed forms).

**Suggested files:**
- `.gitignore`
- `assets/demo/demo.json` (new, tracked) or `data/processed/demo/demo.json` (un-ignored)
- `assets/demo/demo.report.md` (new)
- `frontend/app.py` (`DEMO_ASSET_DIR`, `_load_demo_assets`, `_demo_asset_instructions`)
- `RUNBOOK.md`

**Validation:**
```bash
git clean -fdx data/ && streamlit run frontend/app.py
# Toggle Demo Mode in sidebar, confirm Section D and Section G populated
```

---

#### Issue P0-2 — Add tracked sample claim PDFs + "Try with sample" button ([#11](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/11))

**Priority:** P0
**Type:** code + data
**Codex-safe:** ✅ yes (additive UI, no risky logic)

**Why it matters:** Demo Mode shows results without input. A "Try with sample" button shows the *real* live pipeline running against bundled inputs — much more impressive in a walkthrough video. It's also the first thing a hiring manager will click.

**Scope:**
- Add 1 sample policy PDF and 1 matching denial PDF to `assets/samples/` (sanitized — no client info). Source candidate: `HO3_USAA_TX_OPIC_2008` (regulator-filed) + a synthetic `HO3_TRUE_FL_2021_denial.pdf`. If the original PDFs are not available in-repo, generate a synthetic 1–2 page denial PDF using fabricated names.
- Add a **"Try with sample claim"** primary button on the New Claim page intake form, above the upload widgets.
- Wire it to read the bundled PDFs and run `_run_full_analysis(...)` with them — same code path as a normal upload.
- Show a small caption: "Sample is a regulator-filed HO3 form + synthetic denial letter. No real client data."

**Acceptance criteria:**
- Clicking the button on a fresh checkout produces a complete A–G report using the live pipeline (requires `OPENAI_API_KEY`).
- Sample PDFs are tracked, < 2 MB each, and contain no real client information.
- The button is disabled when `DEMO_FORCE_ON=true` (see P1-1).

**Suggested files:**
- `assets/samples/HO3_USAA_TX_OPIC_2008.pdf` (new)
- `assets/samples/HO3_TRUE_FL_2021_denial.pdf` (new, synthetic)
- `frontend/app.py` (`_render_intake_form`)
- `README.md` (mention the sample button)

**Validation:**
```bash
streamlit run frontend/app.py
# Click "Try with sample claim", confirm full A-G report renders
```

---

#### Issue P0-3 — Fix `.env.example` defaults + pin `requirements.txt` ([#24](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/24)) — Completed in PR [#27](https://github.com/itprodirect/policy-dispute-ai-assistant/pull/27)

**Priority:** P0
**Type:** docs + ops
**Codex-safe:** ✅ yes (trivial)

**Why it matters:** `.env.example:8` ships `PERSIST_RAW_TEXT=true`, which contradicts the README and is the wrong default for a portfolio repo (a copy-paste user persists raw policy text to disk on first run). Unpinned `requirements.txt` causes Streamlit Community Cloud builds to drift and break weeks later.

**Scope:**
- Change `.env.example` line 8: `PERSIST_RAW_TEXT=false`. Add a comment explaining `SAFE_MODE=true` overrides it anyway.
- Pin every dep in `requirements.txt` to a known-good version. Run `pip freeze | grep -E "^(streamlit|openai|pypdf|python-dotenv|tiktoken|rich|wandb|python-docx)=="` in the working venv and copy the resulting versions.
- Optionally split into `requirements.txt` (runtime) vs `requirements-dev.txt` (pytest, etc.) — not required but recommended.

**Acceptance criteria:**
- `.env.example` defaults to safe-by-default flags.
- `requirements.txt` has exact `==` pins for every direct dep.
- Local `pip install -r requirements.txt` from a clean venv still works end-to-end.

**Suggested files:**
- `.env.example`
- `requirements.txt`

**Validation:**
```bash
python -m venv .venv-test && source .venv-test/Scripts/activate
pip install -r requirements.txt
python -c "import streamlit, openai, pypdf, docx, dotenv; print('OK')"
```

---

### P1 — High-leverage UX & screenshot polish

#### Issue P1-1 — Add `DEMO_FORCE_ON` env flag for hosted demos ([#12](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/12)) — Completed

**Priority:** P1
**Type:** code
**Codex-safe:** ✅ yes

**Why it matters:** Lets us host on Streamlit Community Cloud with no `OPENAI_API_KEY`, no abuse risk, and no "users uploading their own claim PDFs to a public site" surface area. Simplest possible deployment story.

**Scope:**
- Add `DEMO_FORCE_ON=false` to `.env.example` and `src/config.py`.
- When true:
  - Force `SESSION_KEY_DEMO_MODE` to `True` on every rerender.
  - Hide the sidebar toggle (or show it as disabled with a tooltip).
  - Disable the file-uploaders and the "Try with sample" button.
  - Show a banner: "Public demo — live analysis disabled. Run locally for full upload + LLM workflow."

**Acceptance criteria:**
- With `DEMO_FORCE_ON=true`, the app cannot make API calls regardless of UI state.
- With `DEMO_FORCE_ON=false` (default), behavior is unchanged.

**Suggested files:**
- `src/config.py`
- `frontend/app.py`
- `.env.example`

**Validation:**
```bash
DEMO_FORCE_ON=true streamlit run frontend/app.py
# Confirm Demo Mode is locked on, uploaders disabled
```

---

#### Issue P1-2 — Hero polish + 30-second value prop ([#13](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/13)) — Completed

**Priority:** P1
**Type:** design + code
**Codex-safe:** ⚠️ partially — the copy is a design judgment call; the layout is mechanical

**Why it matters:** Today's New Claim page jumps straight to "upload PDFs". A portfolio viewer who doesn't read the README needs a 30-second understanding of what they're looking at, with at least one screenshot-quality moment.

**Scope:**
- Replace the current top-of-page intro paragraph with a 3-column "What this does / Who it's for / What's not" card.
- Tighten page title: "Policy Dispute AI" instead of "Policy Dispute AI – Claim A–G Demo".
- Add a single-line "framing" badge near the top: *"Research prototype • Not legal advice • AI-generated"*.
- Move the existing `st.markdown` disclaimer into the framing badge tooltip / collapsible "About this tool".
- Tighten the Results hero: show policy filename, denial filename, and confidence score as 3 metrics in the right column instead of duplicate "Actions" caption.

**Acceptance criteria:**
- New Claim page shows the value prop above the intake form.
- Results hero has policy/denial/confidence as visible metrics.
- Disclaimer present but no longer dominating the screenshot.

**Suggested files:**
- `frontend/app.py` (`_render_new_claim_page`, `_render_hero`)

**Validation:** Manual screenshot review.

---

#### Issue P1-3 — Clean up Confidence / Debug tab ([#14](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/14)) — Completed

**Priority:** P1
**Type:** code
**Codex-safe:** ✅ yes

**Why it mattered:** Tab #4 (`Confidence / debug`) previously dumped raw `dispute_report` JSON. The completed cleanup made the tab screenshot-ready while keeping raw A-G JSON available in collapsed developer expanders.

**Scope:**
- Rename the tab to **"Confidence"** (drop "/ debug").
- Render G content as the *primary* content of the tab: confidence score, notes, verify-clauses list — using a clean two-column layout.
- Hide raw JSON behind an explicit `st.expander("Show raw A–G JSON (for developers)")` that is collapsed by default.
- Move the `Artifacts / advanced debug` expander on the Results page below the policy breakdown into the same Confidence tab as a sub-expander, so the main results page is cleaner.

**Acceptance criteria:**
- Confidence tab is screenshot-able without JSON visible.
- Raw JSON still accessible for developers.

**Suggested files:**
- `frontend/app.py` (`_render_dispute_tabs`, `_render_results_section`)

**Validation:** Manual.

---

#### Issue P1-4 — README screenshots inline + repo first-impression polish ([#15](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/15))

**Priority:** P1
**Type:** docs + assets
**Codex-safe:** ⚠️ partial — Codex can wire links once screenshots exist; capturing them is human work (see §5).

**Why it matters:** The GitHub repo page is the actual first impression. Right now it's all text. Inline screenshots double the perceived quality.

**Scope:**
- Create `docs/screenshots/` directory (tracked).
- Capture 4–6 screenshots per the checklist in §5 of this document.
- Update `README.md`:
  - Add hero screenshot at the top, just after the status line.
  - Replace the "Screenshots (v1 UX)" section with embedded `![]()` references to actual files.
  - Add a "Live demo" link (if hosted) or "Run locally in 60 seconds" snippet.
  - Add badges: license, Python version, "Demo on Streamlit Cloud" if hosted.
- Confirm `LICENSE` file exists and matches README's MIT claim. If missing, add one.

**Acceptance criteria:**
- README renders 4+ screenshots inline on github.com.
- All screenshots are < 500 KB and 2x DPI for retina.
- All visible content is sanitized (no real names, claim numbers, or PII).

**Suggested files:**
- `docs/screenshots/*.png` (new)
- `README.md`
- `LICENSE` (verify or add)

**Validation:** Push branch, confirm screenshots render on github.com.

---

#### Issue P1-5 — Tighten progress UI and step labels ([#16](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/16)) — Completed

**Priority:** P1
**Type:** code
**Codex-safe:** ✅ yes

**Why it matters:** Current 4-step progress is fine but the bar fills with hardcoded `progress(20)`/`(45)`/`(75)`/`(100)`. Steps don't show estimated time and the `status.write()` calls clobber each other.

**Scope:**
- Replace `st.progress` + `st.empty` pair with a single `st.status("Analyzing claim...", expanded=True)` block from Streamlit ≥ 1.28.
- Inside, use `status.update(label="Step 2/4: Reading denial letter")` so each step is shown sequentially in a clean expandable log.
- After completion, `status.update(state="complete", label="Done — see Results below")` and auto-collapse.

**Acceptance criteria:**
- Progress UI is one tidy `st.status` block, not a bar+text pair.
- All four steps render their labels in sequence.
- Looks clean during a screen recording.

**Suggested files:**
- `frontend/app.py` (`_run_full_analysis`)

**Validation:** Manual run, confirm sequence renders.

---

#### Issue P1-6 — Add "Recent runs" sample card on intake page ([#17](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/17)) — Completed

**Priority:** P1
**Type:** code (small)
**Codex-safe:** ✅ yes

**Why it matters:** If a viewer lands on a fresh local install with empty Claim History, the "Try with sample" path covers them. But if they've already run something, showing a "Recent runs" card directly on the New Claim page (1–2 most recent claims with a "View" link) reinforces the "this is a real workflow" feel.

**Scope:**
- After the intake form, if `get_all_claims()` returns ≥ 1 claim, render a compact "Recent claims" section showing the top 2.
- Each row links to the existing Claim History detail view via session state.

**Acceptance criteria:**
- Intake page shows the 2 most recent claims when any exist.
- Clicking "View" jumps to that claim's detail.
- No change for a fresh install (no recent claims, no card).

**Suggested files:**
- `frontend/app.py` (`_render_new_claim_page`)

**Validation:** Manual.

---

### P2 — Deployment, follow-ons, and proof artifacts

#### Issue P2-1 — Streamlit Community Cloud deployment ([#18](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/18))

**Priority:** P2
**Type:** deployment + docs
**Codex-safe:** ⚠️ partial — Codex can prepare the config; the actual cloud connect is a one-time manual step

**Why it matters:** A live `https://policy-dispute-ai.streamlit.app` link in the README is worth 10 screenshots.

**Scope:**
- Create `.streamlit/config.toml` with theme + page width settings.
- Create `.streamlit/secrets.toml.example` showing the secret structure (`OPENAI_API_KEY`, `DEMO_FORCE_ON`).
- Add `docs/DEPLOY.md` with a step-by-step Community Cloud connect guide.
- Recommend deployment with `DEMO_FORCE_ON=true` (no API key needed in cloud secrets for the demo path).
- Add a "Live demo" link to README once deployed.

**Acceptance criteria:**
- Repo has the config/secrets templates.
- `docs/DEPLOY.md` documents the deploy steps.
- (Manual) live URL added to README.

**Suggested files:**
- `.streamlit/config.toml`
- `.streamlit/secrets.toml.example`
- `docs/DEPLOY.md`
- `README.md`

**Validation:** Manual deploy + visit URL.

---

#### Issue P2-2 — GitHub Actions CI for pytest ([#19](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/19))

**Priority:** P2
**Type:** ops
**Codex-safe:** ✅ yes

**Why it matters:** Free signal that the repo is maintained. Green badge in README. Catches regressions before they hit screenshots.

**Scope:**
- Add `.github/workflows/ci.yml` that runs `pytest -q` on push + PR for Python 3.10, 3.11, 3.12.
- Optionally add `ruff` lint job.
- Add badge to README.

**Acceptance criteria:**
- CI runs and passes on the existing `tests/test_citation_linking.py`.
- Badge renders green in README.

**Suggested files:**
- `.github/workflows/ci.yml`
- `README.md`

**Validation:** Push branch, observe Actions run.

---

#### Issue P2-3 — Walkthrough video script + screenshot script ([#20](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/20))

**Priority:** P2
**Type:** docs
**Codex-safe:** ⚠️ Codex can draft; final recording is human work

**Why it matters:** Re-shoots are inevitable. A scripted recipe makes them deterministic.

**Scope:**
- Add `docs/DEMO_WALKTHROUGH.md` with: target length (60s/90s), shot list, narration script, and Streamlit window settings.
- Optionally: a `scripts/capture_screenshots.py` Playwright/Streamlit script that visits each tab and captures PNGs into `docs/screenshots/`.

**Acceptance criteria:**
- Walkthrough doc exists and is executable in <10 minutes.
- (Stretch) Screenshot script regenerates all README images deterministically.

**Suggested files:**
- `docs/DEMO_WALKTHROUGH.md`
- `scripts/capture_screenshots.py` (optional)

**Validation:** Manual.

---

#### Issue P2-4 — Citation linking in Demo Mode ([#21](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/21))

**Priority:** P2
**Type:** code
**Codex-safe:** ✅ yes (depends on P0-1)

**Why it matters:** The "View source: COVERAGE A - DWELLING" accordion is one of the strongest screenshot moments. Today, it only works in Live Mode.

**Scope:**
- Bundle a redacted/sanitized `section_text.json` with the demo asset.
- In Demo Mode, populate `SESSION_KEY_SECTION_MAP` from this file so accordions render.

**Acceptance criteria:**
- Demo Mode shows working "View source" expanders for every linkable citation.

**Suggested files:**
- `assets/demo/section_text.json` (new, sanitized)
- `frontend/app.py` (`_load_demo_into_session`)

**Validation:** Manual.

---

#### Issue P2-5 — Repo cleanup: remove `frontend/data/`, fix duplicate processed dirs ([#22](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/22))

**Priority:** P2
**Type:** chore
**Codex-safe:** ✅ yes

**Why it matters:** `frontend/data/processed/` is a leftover from a past `cwd` mismatch. It's gitignored but its existence on developer machines is confusing.

**Scope:**
- Verify nothing reads from `frontend/data/`.
- Add a one-time cleanup note in `RUNBOOK.md` ("rm -rf frontend/data if present").
- Optionally: assert in `frontend/app.py` startup that `cwd` is the repo root.

**Acceptance criteria:** No regression; folder still works correctly post-cleanup.

**Suggested files:** `RUNBOOK.md`, optionally `frontend/app.py`.

---

#### Issue P2-6 — Dispute report header — show insurer/policyholder context ([#23](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/23))

**Priority:** P2
**Type:** code (small)
**Codex-safe:** ✅ yes

**Why it matters:** The Markdown/Word exports show `Policy: HO3_USAA_TX_OPIC_2008` and `Denial: HO3_TRUE_FL_2021_denial` — fine for internal use, but the demo screenshot would benefit from a more human-readable header (carrier, claim nickname, state, date).

**Scope:**
- Pass `claim_metadata` (already in session_state) into `render_dispute_markdown` and `render_dispute_docx`.
- Render: `Carrier: USAA  •  State: TX  •  Nickname: Smith wind loss  •  Generated: 2026-04-25`.

**Acceptance criteria:** Exported reports show the human-readable header.

**Suggested files:** `src/report_builder.py`, `frontend/app.py`.

---

## 4. Recommended implementation sequence

Foundation completed:

1. ✅ **P0-1** Track demo assets + ship real dispute bundle. Completed in PR [#25](https://github.com/itprodirect/policy-dispute-ai-assistant/pull/25).
2. ✅ **P0-3** Fix `.env.example` + pin `requirements.txt`. Completed in PR [#27](https://github.com/itprodirect/policy-dispute-ai-assistant/pull/27).
3. ✅ **#12 / P1-1** Add `DEMO_FORCE_ON` for hosted demo safety.
4. ✅ **#13 / P1-2** Polish hero and 30-second value proposition.
5. ✅ **#14 / P1-3** Clean up Confidence tab/debug JSON.
6. ✅ **#16 / P1-5** Tighten analysis progress UI.
7. ✅ **#17 / P1-6** Add Recent claims card.

Next recommended follow-up sequence from the current `main` branch:

1. **#15 / P1-4** README screenshots and repo first-impression polish. Screenshots were captured separately and should be curated before committing any assets.
2. **#18 / P2-1** Prepare Streamlit Community Cloud deployment.
3. **#20 / P2-3** Add screenshot/video walkthrough recipe.
4. **#11 / P0-2** Add tracked sample claim PDFs and "Try with sample" button, if a true live sample-input path is still desired.

Do not close #15 until README screenshots are actually selected, committed, and rendered correctly on GitHub.

---

## 5. Screenshot / video capture checklist

### 5.1 Pre-capture setup
- [ ] Run with the polished UI (after P1-2/3/5).
- [ ] Browser at **1440 × 900** (good GitHub README aspect ratio) or **1920 × 1080** for video.
- [ ] Streamlit "wide" layout enabled (already is — `st.set_page_config(layout="wide")`).
- [ ] Use deterministic Demo Mode for zero-API screenshots, or run one live API-backed analysis with valid local PDFs when capturing the progress UI.
- [ ] Light theme — don't ship a dark-mode screenshot if README is light.
- [ ] Hide the browser bookmarks bar; hide any extension icons that contain personal info.
- [ ] Use a clean/sanitized `data/claims.db` for Claim History / Recent claims shots; do not show a developer's accumulated test runs.

### 5.2 Required shots
1. **Landing / intake**: hero with value prop card, "Try with sample" button visible.
2. **Mid-analysis**: `st.status` block with Step 3/4 highlighted (live capture during a real API-backed run).
3. **Results hero**: confidence metric visible, plain-language overview, key takeaways, both download buttons.
4. **A–G dispute tab**: section B and C expanded, citation accordions visible.
5. **Citation expander expanded**: showing real policy section text under "View source".
6. **Confidence tab**: clean confidence display, no raw JSON.
7. **Claim History page**: 2–3 sanitized rows.
8. **Downloaded `.docx` opened in Word**: 1 page showing the rendered A–G output (this is the strongest "portfolio proof" shot).

### 5.3 Walkthrough video (60–90s)
- 0–10s: README/landing → "Try with sample" click.
- 10–30s: `st.status` progress flow runs (live), Results hero appears.
- 30–55s: scroll through A–G tabs, click a "View source" accordion.
- 55–75s: hit "Download as Word", open the file, scroll once.
- 75–90s: cut back to README, point at the disclaimer + GitHub link.

### 5.4 What NOT to capture
- Real client names, claim numbers, addresses — even by accident in a sample PDF.
- Your `OPENAI_API_KEY` in any terminal pane.
- Stack traces or `[BLE001]` errors.
- Any path in `data/processed_safe/` that was generated from real client data.

---

## 6. Hosting recommendation

**Recommendation: Streamlit Community Cloud, locked to Demo Mode.**

| Option | Verdict | Why |
| --- | --- | --- |
| **Streamlit Community Cloud** | ✅ **Recommended** | Free, native Streamlit support, 1-click GitHub integration, fast cold start, secrets management built-in. Pair with `DEMO_FORCE_ON=true` so no API key is needed and uploads are disabled. |
| Render / Railway | ⚠️ Possible | More flexible (custom domain, uptime SLAs) but adds Dockerfile work and a paid tier for uptime. Not worth it for v1.5. |
| Vercel / Netlify | ❌ Skip | Not a Streamlit-native platform; requires SSR/serverless adapters that are more work than the demo deserves. |
| Self-host (Render free) | ❌ Skip | Cold-start latency makes for a bad first impression. |
| Hugging Face Spaces (Streamlit) | ⚠️ Alternative | Decent fallback if Streamlit Cloud has quota issues; good ML community discoverability. |

**Hosted demo profile:**
- Branch: `main` (or a dedicated `demo` branch for safety).
- Secrets: `DEMO_FORCE_ON=true`, no `OPENAI_API_KEY` needed.
- Behavior: visitors see Demo Mode loaded automatically with the bundled real dispute bundle. Uploads + Live Mode are disabled with a banner pointing them at `git clone` for the full workflow.

---

## 7. Recommended next PRs

### Recommended next PR — **#15 / P1-4: README screenshots + first-impression polish**

**Why next:** The Phase 1 code hardening is complete, but the GitHub repo still needs curated screenshots to show the polished New Claim page, Results hero, A-G structure, and clean Confidence tab. Screenshots were captured separately; this follow-up should select, sanitize, and wire them into the README.

**Concrete first steps for the implementer:**
1. Review the saved screenshot set and discard anything with personal data, noisy browser chrome, raw JSON, or stale UI.
2. Capture a real Confidence tab screenshot if it is missing.
3. Add `docs/screenshots/` only if selected screenshots are being committed.
4. Update `README.md` with inline images and concise first-impression copy.
5. Before final release/demo recording, run one live API-backed analysis with valid PDFs to visually confirm the progress UI.

### Optional later PR — **#11 / P0-2: Sample PDFs + "Try with sample" button**

**Why later:** Local mode still supports full uploads, and hosted demos are safe through `DEMO_FORCE_ON`. A tracked sample-input path would make live pipeline demos easier, but it requires careful sample document curation and is separate from the Phase 1 hardening wrap.

---

## 8. Risks / things NOT to do yet

- ❌ **Do NOT add user authentication.** This is a portfolio demo; auth is overkill, makes hosting harder, and signals "trying too hard."
- ❌ **Do NOT introduce a server-side database** (Postgres, Supabase, etc.). The existing SQLite is fine for the demo workflow.
- ❌ **Do NOT rewrite the frontend in Next.js / React.** The Streamlit frontend works, the value is in the A–G logic, and a rewrite is a multi-week distraction with no portfolio upside.
- ❌ **Do NOT treat Phase 1 as model/API modernization.** No LLM prompt changes, report schema changes, Responses/API migration, or backend architecture rebuild were part of the demo-hardening pass.
- ❌ **Do NOT add new policy form support** (HO5, HO6, commercial forms). v1.5 is polish, not coverage expansion.
- ❌ **Do NOT add legal-advice claims, attorney listings, jurisdiction matchmaking, or "guaranteed outcomes" copy.** The "not legal advice" framing must stay front and center.
- ❌ **Do NOT commit any real client documents**, even sanitized ones. Use regulator-filed forms (HO3 ISO, USAA OPIC, TRUE FL) and synthetic denials only.
- ❌ **Do NOT bake real client testimonials or "case studies" into the README.** If you want social proof, link to public model-form PDFs and your own analysis output, not anyone else's claim.
- ❌ **Do NOT add observability/eval infrastructure beyond the existing W&B hooks.** Keep telemetry off-by-default; portfolio viewers don't need a metrics dashboard.
- ❌ **Do NOT enable Live Mode on the public hosted demo.** Bake `DEMO_FORCE_ON=true` into the hosted deployment so the Streamlit Community Cloud instance can never burn API credits or accept third-party PDFs.
- ⚠️ **Be cautious with sample PDFs.** Even regulator-filed forms have copyright headers. Verify HO3 ISO 1999 III and USAA OPIC TX 2008 are in fact freely redistributable — if not, generate a clean-room synthetic HO3-shaped form for the sample bundle.
- ⚠️ **Track dependency cleanup for W&B.** `wandb==0.24.0` is pinned because it was the known working local version during PR #27 validation, but `pip install -r requirements.txt` warned that this candidate is yanked upstream. Do not change it incidentally inside UI/demo PRs; open a focused dependency cleanup issue or PR if replacing it.

---

*End of audit.*
