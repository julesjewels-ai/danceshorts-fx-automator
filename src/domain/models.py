from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional

class JobStatus(Enum):
    """
    Status of a batch processing job.
    """
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    SKIPPED = auto()

@dataclass(frozen=True)
class BatchJobResult:
    """
    Immutable result of a single job in a batch process.
    """
    project_name: str
    status: JobStatus
    duration_seconds: float = 0.0
    output_path: Optional[str] = None
    error_message: Optional[str] = None

    def is_success(self) -> bool:
        return self.status == JobStatus.COMPLETED
