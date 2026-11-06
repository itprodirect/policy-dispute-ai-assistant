export type Finding = {
  text: string;
  citation: string | null;
};

export type Angle = {
  text: string;
  citations: string[];
};

export type DemoReport = {
  policy_id: string;
  denial_id: string;
  plain_summary: string;
  coverage_highlights: Finding[];
  exclusions_limitations: Finding[];
  denial_reasons: Finding[];
  dispute_angles: Angle[];
  missing_info: string[];
  confidence: {
    score: number | null;
    notes: string;
    verify_clauses: string[];
  };
};

export type WorkspaceTab = "overview" | "analysis" | "sources";
