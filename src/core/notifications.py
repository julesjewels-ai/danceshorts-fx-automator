import sys
from typing import TextIO, Any
from src.domain.models import Notification
from src.domain.exceptions import NotificationError
from src.interfaces.notification import NotificationService

class ConsoleNotificationService:
    """
    Concrete implementation of NotificationService for console output.

    This class is strictly decoupled from the console implementation by
    injecting the output stream.
    """

    def __init__(self, stream: TextIO = sys.stdout):
        """
        Initialize the service with a text stream.

        Args:
            stream: A file-like object for writing text (e.g., sys.stdout, io.StringIO).
        """
        self.stream = stream

    def send(self, notification: Notification) -> None:
        """
        Formats and writes the notification to the stream.

        Args:
            notification: The domain notification object.

        Raises:
            NotificationError: If writing to the stream fails.
        """
        try:
            prefix = f"[{notification.level.name}]"
            message = f"{prefix} {notification.message}\n"

            if notification.context:
                # Simple formatting for context
                context_str = ", ".join(f"{k}={v}" for k, v in notification.context.items())
                message += f"   Context: {context_str}\n"

            self.stream.write(message)
            self.stream.flush()

        except Exception as e:
            raise NotificationError(f"Failed to write notification: {e}") from e
