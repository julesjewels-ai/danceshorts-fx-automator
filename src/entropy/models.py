from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class RotTag(Enum):
    BRITTLE_MOCKING = "BRITTLE_MOCKING"
    CONTEXT_BLOAT = "CONTEXT_BLOAT"
    REDUNDANT_COVERAGE = "REDUNDANT_COVERAGE"
    TAUTOLOGY = "TAUTOLOGY"

class SuggestedAction(Enum):
    QUARANTINE = "QUARANTINE"
    COMPACT_SNAPSHOTS = "COMPACT_SNAPSHOTS"
    DELETE = "DELETE"
    NONE = "NONE"

@dataclass
class TestFileHealth:
    file_path: str
    associated_source_files: List[str]
    loc: int
    mock_density: float  # 0.0 to 1.0
    churn_rate: int      # Commits in last 30 days
    token_cost: int
    unique_coverage_lines: int
    is_critical_path: bool

@dataclass
class RotVerdict:
    file: str
    score: int  # 0 (Healthy) to 100 (Toxic)
    tags: List[RotTag] = field(default_factory=list)
    suggested_action: SuggestedAction = SuggestedAction.NONE
    rationale: str = ""

@dataclass
class EntropyConfig:
    max_token_context: int = 2000
    max_mock_density: float = 0.55
    min_unique_coverage_threshold: int = 5
    execution_mode: str = "PR_SUGGESTION" # 'PR_SUGGESTION' or 'REPORT_ONLY'
    quarantine_dir: str = "tests/quarantine"
