# Sales Proof Review

Last updated: 2026-04-28

This document records what this repository can safely support as sales proof, website content, demo material, or client-facing evidence. It is intentionally evidence-bound: do not use it to imply production readiness, legal accuracy, client outcomes, or broad policy-form coverage.

## Sales-Proof Summary

This repo is credible as a private sales demo, technical case study, and portfolio proof for AI-assisted insurance document workflows.

It should be positioned as:

- Internal research prototype.
- Human-review workflow accelerator.
- Demo-safe claim triage example.
- Technical proof that IT Pro Direct can build document intake, LLM analysis, source-linked review, and export workflows.

It should not be positioned as:

- Production SaaS.
- Legal advice.
- Coverage determination.
- Validated claim outcome engine.
- Secure hosted client portal.

## What This Repo Proves

The repo proves the team can build a working vertical slice for insurance claim document review:

- Streamlit claim intake and results UI.
- Homeowners policy PDF and denial-letter workflow.
- A-G dispute report structure for first-pass human review.
- OpenAI Responses API integration through a single wrapper.
- Strict Structured Outputs for final dispute reports.
- Bounded concurrent section-summary calls.
- Focused-analysis mode for core policy sections.
- Demo Mode with deterministic checked-in assets and no API calls.
- Source/citation accordions backed by demo-safe source excerpts.
- Markdown and Word exports with human-readable context.
- Local SQLite claim history.
- Pytest coverage and GitHub Actions CI.
- Benchmark docs for demo parity and live full-vs-focused comparison.

## Client Problem Mapped

The strongest client problem is slow first-pass claim file review.

Public adjusters, coverage attorneys, and claim-review professionals need to quickly understand:

- What the policy may support.
- What exclusions, limitations, and conditions may matter.
- What the carrier said in the denial.
- What dispute angles deserve human review.
- What facts or documents are still missing.

This repo demonstrates a workflow that organizes that review into a structured brief.

## Best-Fit Buyer Or User

Best-fit users:

- Public adjusting firms.
- Coverage attorneys.
- Property claim consultants.
- CAT claim review teams.
- Insurance-document operations teams.

Best-fit buyer:

- A claims leader, firm owner, or operations lead who wants a private AI workflow to speed up document-heavy triage while keeping humans responsible for final judgment.

## Suggested Offer

Offer name:

**AI Claim Triage Prototype Sprint**

Offer shape:

- One document-heavy claim workflow.
- One policy form or claim type first.
- Private/local or demo-safe deployment first.
- Human-reviewed outputs only.
- Exportable review brief.
- Clear privacy, safety, and not-legal-advice framing.

A hosted multi-user claim-review platform remains aspirational. This repo does not prove auth, billing, secure multi-tenant storage, client onboarding, or production compliance.

## Website Section Draft

### Headline

AI-assisted claim review, built for faster first-pass triage.

### Proof Bullets

- Built a working prototype that turns homeowners policy language and denial-letter content into structured A-G dispute summaries.
- Added deterministic Demo Mode with uploads and API calls disabled for safe walkthroughs.
- Implemented source-linked review views, Markdown/Word exports, automated tests, CI, and benchmark reporting.

### Case-Study Paragraph

We built an internal Policy Dispute AI prototype to explore how AI can help claim professionals organize homeowners policy language and denial letters into a faster review brief. The app extracts policy text, groups it into policy sections, summarizes relevant coverage concepts, analyzes denial reasons, and presents a structured A-G dispute report for human review.

### Technical Credibility Paragraph

The prototype uses a Python backend, Streamlit frontend, OpenAI Responses API integration, Structured Outputs for final reports, bounded concurrent section summaries, focused-analysis mode, citation/source accordions, local SQLite claim history, Markdown and Word exports, deterministic offline demo assets, pytest coverage, and GitHub Actions CI. It is explicitly framed as a research prototype, not legal advice or a production legal product.

## Demo Walkthrough

### 90-Second Version

1. Open the app overview and point to the research prototype, not-legal-advice, and AI-generated framing.
2. Turn on Demo Mode or show hosted public demo safety mode.
3. Jump to Results.
4. Show the plain-language dispute overview and key takeaways.
5. Open the A-G dispute structure.
6. Open one source/citation accordion.
7. Show Word and Markdown export buttons.
8. Close by saying this is a human-review accelerator, not a coverage decision engine.

### 5-Minute Version

1. Explain the client problem: long policies and denial letters slow down first-pass review.
2. Show New Claim intake: claim nickname, state, policy PDF, denial PDF.
3. Explain Demo Mode: deterministic, no uploads, no API calls.
4. Show Results overview and review context.
5. Walk through A-G sections: overview, coverage highlights, exclusions, denial reasons, dispute angles, missing information, confidence.
6. Open a source accordion to show citation-linked policy context.
7. Show Word and Markdown exports.
8. Mention technical evidence: tests, CI, benchmark report, focused-analysis mode.
9. End with limitations: prototype, not legal advice, source documents must be reviewed.

## Screenshot And Video Checklist

Existing screenshots:

- `docs/screenshots/01-app-overview-framing.png`
- `docs/screenshots/02-new-claim-upload-form.png`
- `docs/screenshots/03-demo-safety-state.png`
- `docs/screenshots/04-results-overview.png`
- `docs/screenshots/05-results-actions-downloads.png`

Needed before public promotion:

- Fresh screenshots after any copy or UI change.
- One 90-second narrated demo using Demo Mode only.
- One 5-minute technical walkthrough.
- Screenshot with a source/citation accordion open.
- Screenshot of the A-G tabs.
- Screenshot of export context.
- Final check that screenshots show no secrets, real client names, claim numbers, or real client data.

## Claims We Can Safely Make

- Internal research prototype.
- AI-generated, human-review workflow.
- Designed for homeowners policy and denial-letter triage.
- Produces structured A-G dispute summaries.
- Includes deterministic offline demo mode.
- Supports Markdown and Word exports.
- Includes automated tests and GitHub Actions CI.
- Uses demo-safe artifacts for public screenshots.
- Not legal advice and not a coverage decision.

## Claims To Avoid

- Production-ready.
- Legally accurate.
- Determines coverage.
- Wins disputes.
- Replaces attorneys or public adjusters.
- Works for all policy forms.
- Secure SaaS platform.
- Client-proven.
- Handles real client data safely in hosted mode.
- Validated against real claim outcomes.

## Next Work Before Public Promotion

1. Confirm or remove tracked generated `data/processed` artifacts.
2. Make every public artifact explicitly demo-safe and non-client.
3. Create a polished walkthrough video using Demo Mode only.
4. Add a compact public case-study page with careful disclaimers.
5. Add a citation/source screenshot to the README or website.
6. Add a lightweight evaluation note documenting what is tested and what is not.
7. Keep hosted/demo mode locked with uploads and API calls disabled.
8. Do not promote live client use until privacy, deployment, auth, and quality-review gaps are addressed.
