from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True)
class TestFileHealth:
    file_path: str
    associated_source_files: List[str]

    # METRICS
    loc: int
    mock_density: float # 0 to 1
    churn_rate: float # Commits in last 30 days
    token_cost: int

    # CRITICALITY CHECK
    unique_coverage_lines: int
    is_critical_path: bool

@dataclass
class RotVerdict:
    file: str
    score: float # 0 (Healthy) to 100 (Toxic)
    unique_coverage: int
    tags: List[str] # 'BRITTLE_MOCKING', 'CONTEXT_BLOAT', 'REDUNDANT_COVERAGE', 'TAUTOLOGY'
    suggested_action: str # 'QUARANTINE', 'COMPACT_SNAPSHOTS', 'DELETE', 'NONE'
    rationale: str = ""
