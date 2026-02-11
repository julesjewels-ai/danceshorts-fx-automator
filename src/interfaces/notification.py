from typing import Protocol
from src.domain.models import NotificationLevel

class NotificationService(Protocol):
    """
    Protocol for notification services.
    """
    def notify(self, message: str, level: NotificationLevel) -> None:
        """
        Sends a notification.

        Args:
            message (str): The message content.
            level (NotificationLevel): The severity level of the notification.

        Raises:
            NotificationError: If the notification fails to send.
        """
        ...
