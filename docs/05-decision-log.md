# Decision Log

## 2026-04-25

### Preserve research and not-legal-advice framing

The app stays framed as an educational research prototype. It is not a legal product, not a coverage decision, and not a replacement for professional review.

### Force Demo Mode for hosted public demos

Hosted demos should use `DEMO_FORCE_ON=true` so uploads and live API-backed analysis are disabled and deterministic demo-safe artifacts are used.

### Finish README screenshots before Phase 1B

README screenshots and first-impression polish were completed before Phase 1B operational closeout so visitors see the current v1 UX without relying on stale issue notes.

### Begin Phase 1B with CI

Phase 1B should begin with #19 GitHub Actions CI for pytest before stale artifact cleanup or walkthrough recipe work.

### Defer model/API modernization to Phase 2

Responses API migration, Structured Outputs, stage-specific model configuration, and speed/pipeline work are true Phase 2 model/speed refactor items. They are deferred until after Phase 1B and Phase 1C are complete or intentionally deferred, and only after focused inspection or measurement.

## 2026-04-25 - Phase 1C wrap

- Mark Phase 1 complete after Phase 1C technical closeout.
- Defer #18 Streamlit Community Cloud deployment prep.
- Defer #20 walkthrough video and screenshot recipe.
- Require Phase 2 to start with baseline benchmarking.
