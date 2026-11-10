# Policy Dispute — local-first web app (experimental)

This is the **new, non-Streamlit interface** proposed in [issue #70](https://github.com/itprodirect/policy-dispute-ai-assistant/issues/70).

It runs on your laptop and can later be previewed on Vercel. It is a standalone Next.js / TypeScript UI, but **it is not yet a functional live claims-processing replacement**.

## Run locally (Windows Git Bash)

Install Node.js 22+ and npm, then from the repository root:

```bash
cd web
npm ci
npm run test:demo
npm run typecheck
npm run dev
```

The committed `package-lock.json` pins the full dependency tree. Use `npm ci` for clean installs and CI. When intentionally changing dependencies, run `npm install` and commit both the manifest and updated lockfile.

Open [http://localhost:3000](http://localhost:3000).

For a production-like local check: `npm run build && npm run start`.

## What works in this first slice

- Responsive workspace and navigation between overview, seven report sections (A–G), and demo evidence excerpts.
- The *existing repository's* sanitized report JSON, 13 synthetic citation source excerpts, and original Markdown export.
- Copying the example narrative locally in the browser; Markdown download.
- Explicit offline demo / human-review disclaimer.
- **No** uploads, API calls, real client files, secrets, claim history storage, model selection, or billing.

The copy of the three original demo artifacts is **intentional** so the `web/` app can be built and deployed independently. Run `npm run test:demo` to detect drift from the source demo files in `assets/demo/`.

## Deploy plan

For a Vercel preview, import this GitHub repo and set the project **Root Directory** to `web`. This is an optional *subsequent step*, not done by this branch. Demo content will be public on that preview, as it already is in the public repo. Do not enable claim uploads or live inference on an unauthenticated preview.

For AWS later, prefer a reproducible container build (e.g. Next.js standalone output on ECS/Fargate) while keeping the same UI and using private S3 for documents and a separate queued worker for longer-running analyses. **No AWS infrastructure is provisioned here.**

## Next proposed slices (separate issues and PRs)

1. Measure original Python pipeline by stage with safe fixtures and evaluation of A–G report/citation quality.
2. Introduce a **local-only** API adapter over existing Python business logic, with documented file privacy, data lifecycle, and error handling. No need to rewrite LLM orchestration immediately.
3. Compare modern Responses API models with quality/latency/cost gates, and test OpenAI Decisions/Jev only for bounded triage/classification tasks, not final coverage judgments.
4. Once validated, design authenticated hosted jobs with direct-to-private-S3 uploads, job progress, and secrets held server-side.
5. Optionally replace Python components only when same-fixture profiling proves a payoff; optionally package the web UI as an installable desktop app.

### Safety boundary

This repo is a research prototype for public adjusters/attorneys. Outputs are AI-generated, may be wrong, and require review of the actual policy and denial. It is not legal advice or a coverage determination. **Never commit actual claim documents, claim outputs, PII, or API keys.**
