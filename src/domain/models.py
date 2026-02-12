from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

class NotificationLevel(Enum):
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()

@dataclass(frozen=True)
class Notification:
    message: str
    level: NotificationLevel
    context: Dict[str, Any] = field(default_factory=dict)
