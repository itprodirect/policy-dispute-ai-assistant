from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class SectionSummary:
    section_name: str
    summary_overall: str
    key_coverages: List[str]
    key_exclusions: List[str]
    conditions_notable: List[str]
    dispute_angles_possible: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PolicySummary:
    policy_id: str
    sections: List[SectionSummary]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
