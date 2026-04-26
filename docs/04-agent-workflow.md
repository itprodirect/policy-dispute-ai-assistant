# Agent Workflow

Use this workflow for Codex, Claude Code, and future agent sessions.

## One Issue, One PR

- Pick one GitHub issue or one tightly scoped docs task.
- Keep each branch and PR focused on that single concern.
- Do not bundle work across phases. Do not mix Phase 2 model/API refactor work into Phase 1B or Phase 1C PRs.

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

Use `docs/09-session-log.md` for meaningful sessions that change project direction, durable docs, or implementation state.

- Keep entries short.
- Capture Goal, Completed, Decisions, Validation, Deferred, and Next session starter.
- Do not use `logs/` unless the issue explicitly requires archival session artifacts.

## Session closeout protocol

At the end of a meaningful session:

1. Update `docs/06-heartbeat.md` with current truth and next action.
2. Add a `docs/09-session-log.md` entry.
3. Add a `docs/05-decision-log.md` entry only if a meaningful decision was made.
4. Update `docs/08-memory.md` only for durable milestones, not routine work.
5. Keep docs concise and factual.
6. Do not update archive/log/screenshot files unless the issue explicitly requires it.

## PR Closeout

- Run `git status --short`.
- Verify changed files match the issue scope.
- Summarize validation in the PR body.
- Include screenshots for UI changes.
