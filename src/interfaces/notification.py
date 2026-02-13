from typing import Protocol, runtime_checkable, TypeVar

from src.domain.models import NotificationLevel

T = TypeVar("T")

@runtime_checkable
class NotificationService(Protocol[T]):
    """
    Protocol for notification services.

    This interface abstracts the mechanism of sending notifications,
    allowing different implementations (e.g., console, email, slack)
    to be swapped without changing the core application logic.
    """

    def send(self, message: T, level: NotificationLevel = NotificationLevel.INFO) -> None:
        """
        Sends a notification.

        Args:
            message: The notification content. The type is generic (T).
            level: The severity level of the notification.

        Raises:
            NotificationError: If the notification fails to send.
        """
        ...
