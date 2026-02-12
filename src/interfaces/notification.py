from typing import Protocol, runtime_checkable, TypeVar

# T is the type of the notification payload.
# We use a generic here to allow flexibility in what constitutes a "notification".
# It could be a simple string, a Notification dataclass, or a complex event object.
T = TypeVar("T", contravariant=True)

@runtime_checkable
class NotificationService(Protocol[T]):
    """
    Protocol defining the contract for a notification service.

    This interface adheres to the Interface Segregation Principle by exposing
    only the necessary method to send a notification.
    """

    def send(self, notification: T) -> None:
        """
        Sends a notification to the configured destination.

        Args:
            notification: The notification payload to send.

        Raises:
            NotificationError: If the notification fails to send.
        """
        ...
