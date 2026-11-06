"use client";

import { useState } from "react";
import type { Angle, DemoReport, Finding, WorkspaceTab } from "../lib/report";

type WorkspaceProps = {
  report: DemoReport;
  sources: Record<string, string>;
};

const tabs: { id: WorkspaceTab; label: string; short: string }[] = [
  { id: "overview", label: "Overview", short: "01" },
  { id: "analysis", label: "A–G analysis", short: "02" },
  { id: "sources", label: "Evidence excerpts", short: "03" },
];

function SmallLabel({ children }: { children: React.ReactNode }) {
  return <span className="eyebrow">{children}</span>;
}

function FindingRows({ items, onCitation }: { items: Finding[]; onCitation: () => void }) {
  return (
    <ol className="finding-list">
      {items.map((item, index) => (
        <li className="finding" key={index}>
          <span className="finding-index">{String(index + 1).padStart(2, "0")}</span>
          <div>
            <p>{item.text}</p>
            {item.citation ? (
              <button className="citation" onClick={onCitation} type="button" title="Open the source-excerpt index">
                <span aria-hidden="true">↗</span> {item.citation}
              </button>
            ) : null}
          </div>
        </li>
      ))}
    </ol>
  );
}

function AngleRows({ items, onCitation }: { items: Angle[]; onCitation: () => void }) {
  return (
    <ol className="finding-list">
      {items.map((item, index) => (
        <li className="finding" key={index}>
          <span className="finding-index">{String(index + 1).padStart(2, "0")}</span>
          <div>
            <p>{item.text}</p>
            {item.citations.length ? (
              <button className="citation" onClick={onCitation} type="button">
                <span aria-hidden="true">↗</span> {item.citations.join(" · ")}
              </button>
            ) : null}
          </div>
        </li>
      ))}
    </ol>
  );
}

function Section({
  letter,
  title,
  children,
  subheading,
}: {
  letter: string;
  title: string;
  subheading?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="section-card">
      <div className="section-heading">
        <span className="section-letter">{letter}</span>
        <div>
          <h3>{title}</h3>
          {subheading ? <p className="muted">{subheading}</p> : null}
        </div>
      </div>
      {children}
    </section>
  );
}

export function Workspace({ report, sources }: WorkspaceProps) {
  const [tab, setTab] = useState<WorkspaceTab>("overview");
  const [copied, setCopied] = useState(false);
  const sourceCount = Object.keys(sources).length;
  const confidencePercent = report.confidence.score == null ? null : Math.round(report.confidence.score * 100);
  const selectTab = (next: WorkspaceTab) => {
    setTab(next);
    setCopied(false);
  };
  const copySummary = async () => {
    try {
      await navigator.clipboard.writeText(report.plain_summary);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  };

  return (
    <div className="shell">
      <aside className="sidebar" aria-label="Workspace navigation">
        <div className="brand">
          <div className="brand-mark" aria-hidden="true">P<span>.</span></div>
          <div className="brand-text"><strong>POLICY DISPUTE</strong><span>RESEARCH WORKSPACE</span></div>
        </div>
        <div className="side-group">
          <SmallLabel>WORKSPACE</SmallLabel>
          <nav aria-label="Review screens" className="side-nav">
            {tabs.map((item) => (
              <button
                type="button" key={item.id}
                className={tab === item.id ? "side-link active" : "side-link"}
                onClick={() => selectTab(item.id)}
                aria-current={tab === item.id ? "page" : undefined}
              >
                <span className="side-icon">{item.short}</span>{item.label}
                {tab === item.id && <span className="side-arrow" aria-hidden="true">›</span>}
              </button>
            ))}
          </nav>
        </div>
        <div className="sidebar-spacer" />
        <div className="sidebar-note">
          <div className="signal"><span className="signal-dot" /> LOCAL DEMO</div>
          <p>Sample content only. No documents leave your machine. No AI calls are made.</p>
          <span className="build-tag">EXPERIMENTAL · V0.1</span>
        </div>
      </aside>
      <main className="main">
        <div className="topbar">
          <div className="breadcrumb">Workspace <span>/</span> Demonstration claim</div>
          <div className="topbar-right">
            <span className="offline"><span className="signal-dot" /> Offline demo</span>
            <span className="avatar" aria-hidden="true">PD</span>
          </div>
        </div>
        <div className="content">
          <div className="page-title-row">
            <div>
              <SmallLabel>CLAIM REVIEW · DEMONSTRATION</SmallLabel>
              <h1>Policy dispute analysis</h1>
              <p className="lead">Review coverage language, carrier reasoning, and questions worth investigating.</p>
            </div>
            <a className="download-button" href="/demo-report.md" download="policy-dispute-demo.md">
              <span aria-hidden="true">↓</span> Download report
            </a>
          </div>
          <div className="hero">
            <div className="hero-content">
              <div className="hero-meta"><span className="hero-chip">SANITIZED SAMPLE</span><span>HO3 · PROPERTY CLAIM</span></div>
              <h2>A clearer starting point for every disputed claim.</h2>
              <p>AI-assisted issue spotting with human review at the center. This is a research demonstration—not a coverage determination or legal advice.</p>
            </div>
            <div className="hero-art" aria-hidden="true"><div className="hero-art-inner"><span>01</span><i /><span>07</span></div></div>
          </div>
          <div className="metrics" aria-label="Demo report at a glance">
            <div className="metric"><span>Coverage highlights</span><strong>{report.coverage_highlights.length}</strong><small>Provisions to review</small></div>
            <div className="metric"><span>Denial reasons</span><strong>{report.denial_reasons.length}</strong><small>Carrier positions</small></div>
            <div className="metric"><span>Dispute angles</span><strong>{report.dispute_angles.length}</strong><small>Questions to explore</small></div>
            <div className="metric"><span>Information gaps</span><strong>{report.missing_info.length}</strong><small>Follow-up items</small></div>
          </div>
          <div className="workspace-tabs" role="tablist" aria-label="Report views">
            {tabs.map((item) => (
              <button
                id={"tab-" + item.id}
                key={item.id}
                type="button"
                role="tab"
                aria-selected={tab === item.id}
                aria-controls={"panel-" + item.id}
                tabIndex={tab === item.id ? 0 : -1}
                className={tab === item.id ? "tab active" : "tab"}
                onClick={() => selectTab(item.id)}
                onKeyDown={(event) => {
                  if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;
                  event.preventDefault();
                  const index = tabs.findIndex((entry) => entry.id === tab);
                  const offset = event.key === "ArrowRight" ? 1 : -1;
                  const next = tabs[(index + offset + tabs.length) % tabs.length];
                  selectTab(next.id);
                  document.getElementById("tab-" + next.id)?.focus();
                }}
              ><span>{item.label}</span></button>
            ))}
          </div>
          {tab === "overview" && (
            <div id="panel-overview" className="panel-grid" role="tabpanel" aria-labelledby="tab-overview">
              <section className="primary-card">
                <div className="card-title"><div><SmallLabel>SECTION A</SmallLabel><h3>Dispute overview</h3></div><button type="button" className="text-action" onClick={copySummary}>{copied ? "Copied" : "Copy summary"}</button></div>
                <p className="summary-text">{report.plain_summary}</p>
                <div className="card-divider" />
                <div className="card-title"><div><SmallLabel>HIGHLIGHTS</SmallLabel><h3>Potentially relevant coverage</h3></div><button className="text-action" type="button" onClick={() => selectTab("analysis")}>View analysis ↗</button></div>
                <FindingRows items={report.coverage_highlights.slice(0, 3)} onCitation={() => selectTab("sources")} />
              </section>
              <div className="stack">
                <section className="secondary-card">
                  <div className="card-title"><div><SmallLabel>PROFESSIONAL REVIEW</SmallLabel><h3>What to verify next</h3></div></div>
                  <ul className="review-list">
                    {report.missing_info.slice(0, 4).map((item, i) => <li key={i}><span className="empty-check" aria-hidden="true" />{item}</li>)}
                  </ul>
                  <button type="button" className="text-action" onClick={() => selectTab("analysis")}>All {report.missing_info.length} follow-up items ↗</button>
                </section>
                <section className="warning-card">
                  <div className="warning-icon" aria-hidden="true">!</div>
                  <div><strong>Human verification required</strong><p>Generated findings are starting points. Check the policy form, endorsements, claim evidence, and governing law before taking action.</p></div>
                </section>
              </div>
            </div>
          )}
          {tab === "analysis" && (
            <div id="panel-analysis" role="tabpanel" aria-labelledby="tab-analysis" className="analysis-stack">
              <Section letter="A" title="Plain-language overview"><p className="summary-text">{report.plain_summary}</p></Section>
              <Section letter="B" title="Coverage highlights" subheading="Policy provisions potentially supporting the insured"><FindingRows items={report.coverage_highlights} onCitation={() => selectTab("sources")} /></Section>
              <Section letter="C" title="Exclusions and limitations" subheading="Language that may restrict coverage"><FindingRows items={report.exclusions_limitations} onCitation={() => selectTab("sources")} /></Section>
              <Section letter="D" title="Denial reasons" subheading="Positions described in the example denial"><FindingRows items={report.denial_reasons} onCitation={() => selectTab("sources")} /></Section>
              <Section letter="E" title="Dispute angles" subheading="Questions to investigate, not legal conclusions"><AngleRows items={report.dispute_angles} onCitation={() => selectTab("sources")} /></Section>
              <Section letter="F" title="Missing information"><ul className="review-list">{report.missing_info.map((item, i) => <li key={i}><span className="empty-check" aria-hidden="true" />{item}</li>)}</ul></Section>
              <Section letter="G" title="Confidence and verification">
                <div className="confidence"><strong>{confidencePercent == null ? "N/A" : confidencePercent + "%"}</strong><span>Model-reported confidence; not calibrated or independently validated</span></div>
                <p className="summary-text">{report.confidence.notes}</p>
                <SmallLabel>CLAUSES TO DOUBLE-CHECK</SmallLabel>
                <ul className="clause-list">{report.confidence.verify_clauses.map((item, i) => <li key={i}>{item}</li>)}</ul>
              </Section>
            </div>
          )}
          {tab === "sources" && (
            <section id="panel-sources" role="tabpanel" aria-labelledby="tab-sources" className="primary-card sources">
              <div className="card-title"><div><SmallLabel>DEMO EVIDENCE INDEX</SmallLabel><h3>{sourceCount} source excerpts</h3></div><span className="source-count">SANITIZED</span></div>
              <p className="muted source-intro">These are short synthetic, demo-safe examples from the existing prototype. They are not verbatim policy clauses. Always inspect the original documents in a real claim.</p>
              <div className="source-list">
                {Object.entries(sources).map(([label, text], i) => (
                  <details key={label} className="source-item">
                    <summary><span className="source-number">{String(i + 1).padStart(2, "0")}</span><span className="source-label">{label}</span><span className="source-toggle" aria-hidden="true">+</span></summary>
                    <div className="source-excerpt">{text}</div>
                  </details>
                ))}
              </div>
            </section>
          )}
          <footer className="footer"><span>POLICY DISPUTE · RESEARCH PROTOTYPE</span><span>AI-assisted review · No live processing · Demo content only</span></footer>
        </div>
      </main>
    </div>
  );
}
