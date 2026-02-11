from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class RotType(str, Enum):
    BRITTLE_MOCKING = "BRITTLE_MOCKING"
    CONTEXT_BLOAT = "CONTEXT_BLOAT"
    REDUNDANT_COVERAGE = "REDUNDANT_COVERAGE"
    TAUTOLOGY = "TAUTOLOGY"
    HIGH_CHURN = "HIGH_CHURN"

class Action(str, Enum):
    QUARANTINE = "QUARANTINE"
    COMPACT_SNAPSHOTS = "COMPACT_SNAPSHOTS"
    DELETE = "DELETE"
    NONE = "NONE"

@dataclass
class TestFileHealth:
    file_path: str
    associated_source_files: List[str]
    loc: int
    mock_density: float
    churn_rate: int
    token_cost: int
    unique_coverage_lines: int
    is_critical_path: bool

@dataclass
class RotVerdict:
    file: str
    score: float
    tags: List[RotType]
    suggested_action: Action
    rationale: str = ""
