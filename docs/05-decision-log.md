# Decision Log

Use this format for future entries:

## YYYY-MM-DD HH:MM ET — Decision title

### Context
- What problem or tradeoff existed.

### Decision
- What we decided.

### Consequence
- What this changes or prevents.

### Revisit trigger
- When this decision should be reconsidered.

## 2026-04-25 15:42 ET — Force Demo Mode for hosted public demos

### Context
- Hosted demos need to be deterministic and should not accept uploads or make live API calls.

### Decision
- Use `DEMO_FORCE_ON=true` for hosted public demos.

### Consequence
- Hosted demos use tracked demo-safe artifacts and disable live analysis paths.

### Revisit trigger
- Reconsider when hosted deployment is actively needed and the public-demo threat model changes.

## 2026-04-25 17:37 ET — Preserve research and not-legal-advice framing

### Context
- The app needs demo polish without implying production readiness, legal advice, or real claim outcomes.

### Decision
- Keep the app framed as an educational research prototype, not a legal product or coverage decision.

### Consequence
- README, UI copy, screenshots, and generated reports must preserve AI-generated and not-legal-advice framing.

### Revisit trigger
- Reconsider only if the project scope changes from research prototype to a reviewed production product.

## 2026-04-25 18:24 ET — Finish README screenshots before Phase 1B

### Context
- The repo needed accurate first-impression material before operational closeout.

### Decision
- Complete README screenshots and repo polish before Phase 1B technical work.

### Consequence
- Visitors can understand the current v1 UX without relying on stale issue notes.

### Revisit trigger
- Revisit when UI changes make committed screenshots materially inaccurate.

## 2026-04-25 19:24 ET — Begin Phase 1B with CI

### Context
- Technical closeout needed a reliable automated signal before more cleanup.

### Decision
- Start Phase 1B with #19 GitHub Actions CI for `python -m pytest -q`.

### Consequence
- CI became the merge gate while local pytest remained the fastest development signal.

### Revisit trigger
- Revisit when test coverage or dependency setup changes enough to require a different CI shape.

## 2026-04-25 19:44 ET — Defer walkthrough recipe

### Context
- #20 walkthrough video/screenshot recipe was useful, but model/API/speed work would likely change the demo flow.

### Decision
- Defer #20 until after Phase 2 stabilizes.

### Consequence
- Docs avoid locking in a walkthrough before baseline, model/API, or speed work changes the experience.

### Revisit trigger
- Revisit after Phase 2 upgrades stabilize and a walkthrough can stay accurate.

## 2026-04-25 21:42 ET — Phase 1C wrap

### Context
- Phase 1A demo polish, Phase 1B technical closeout, and Phase 1C local/demo trust polish were complete.

### Decision
- Mark Phase 1 complete, defer #18 Streamlit Community Cloud deployment prep, defer #20 walkthrough video/screenshot recipe, and require Phase 2 to start with baseline benchmarking.

### Consequence
- Phase 2 cannot start with Responses API, Structured Outputs, model swaps, or speed refactors before current-state measurements exist.

### Revisit trigger
- Revisit #18 only when a hosted public demo is needed; revisit #20 after Phase 2 stabilizes.

## 2026-04-26 ET - Close Phase 2 with separate final benchmark report

### Context
- #46 created a historical before-state benchmark report before Phase 2 model/API/speed work.
- #53 needed a final comparison without rewriting that baseline history or expanding product scope.

### Decision
- Keep `benchmarks/phase2-baseline.md` as the immutable historical before-state.
- Add final comparison in a separate `benchmarks/phase2-final.md`.
- Close Phase 2 after #53.

### Consequence
- Future benchmark follow-ups should start from a new issue rather than editing the Phase 2 baseline.
- Post-Phase-2 work such as #18 deployment prep and #20 walkthrough/screenshot recipe stays separate.

### Revisit trigger
- Revisit only if a later benchmark issue adds a new measurement scope, telemetry source, or evaluation harness.
