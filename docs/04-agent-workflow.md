# Agent Workflow

Use this workflow for Codex, Claude Code, and future agent sessions.

## One Issue, One PR

- Pick one GitHub issue or one tightly scoped docs task.
- Keep each branch and PR focused on that single concern.
- Do not bundle Phase 2 work into docs cleanup, CI, deployment, prompt, schema, or model/API changes.

## Inspect Before Editing

- Start with `git status --short`.
- Read the relevant files before changing them.
- Preserve user changes and unrelated work.
- Confirm the changed-file list before committing.

## Boundaries

- Docs-only tasks must not change app code, prompts, schemas, backend architecture, CI, deployment config, models, API behavior, auth, users, billing, or storage.
- App-code tasks should include focused tests or a clear reason tests were not run.
- Preserve research prototype, AI-generated, not-legal-advice, and demo-safe framing.
- Never commit secrets, real client documents, real claim data, real client names, or fake proof such as testimonials.

## Session Logging

Use lightweight session logs when a session is more than a quick one-command maintenance task.

- Create a new `logs/YYYY-MM-DD_<topic>.md` from `logs/SESSION_TEMPLATE.md` at the start of the session.
- Keep logs short.
- Capture Goal, Decisions, Friction, Next - Immediate, and Restart Test.
- Do not edit `logs/SESSION_TEMPLATE.md` directly.

See `logs/README.md` and `logs/SESSION_TEMPLATE.md`.

## PR Closeout

- Run `git status --short`.
- Verify changed files match the issue scope.
- Summarize validation in the PR body.
- Include screenshots for UI changes.
