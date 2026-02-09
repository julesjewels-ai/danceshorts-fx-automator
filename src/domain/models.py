from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum, auto

class ProcessingStatus(Enum):
    SUCCESS = auto()
    FAILED = auto()
    SKIPPED = auto()

@dataclass(frozen=True)
class BatchJobResult:
    """Immutable record of a batch processing job outcome."""
    project_name: str
    status: ProcessingStatus
    processing_time: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
