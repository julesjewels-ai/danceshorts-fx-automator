class NotificationError(Exception):
    """Base exception for notification failures."""
    pass

class ConfigurationError(NotificationError):
    """Raised when a notification service is misconfigured."""
    pass
