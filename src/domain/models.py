from enum import Enum, auto

class NotificationLevel(Enum):
    """
    Severity levels for notifications.
    """
    INFO = auto()
    SUCCESS = auto()
    WARNING = auto()
    ERROR = auto()
