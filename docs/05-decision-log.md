# Decision Log

## 2026-04-25

### Preserve research and not-legal-advice framing

The app stays framed as an educational research prototype. It is not a legal product, not a coverage decision, and not a replacement for professional review.

### Force Demo Mode for hosted public demos

Hosted demos should use `DEMO_FORCE_ON=true` so uploads and live API-backed analysis are disabled and deterministic demo-safe artifacts are used.

### Finish README screenshots before Phase 2

README screenshots and first-impression polish were completed before starting Phase 2 so visitors see the current v1 UX without relying on stale issue notes.

### Add CI before deeper behavior work

Phase 2 should begin with #19 GitHub Actions CI for pytest before deployment prep or deeper app behavior changes.

### Defer model/API modernization

Responses API migration, Structured Outputs, model swapping, prompt changes, and report schema changes are deferred until after Phase 2 setup work and only after focused inspection or measurement.
