import sys
from typing import TextIO

from src.domain.models import NotificationLevel
from src.domain.exceptions import NotificationError
from src.interfaces.notification import NotificationService

class ConsoleNotificationService(NotificationService[str]):
    """
    A concrete implementation of NotificationService that writes to a text stream.

    This class demonstrates dependency injection by accepting an output stream
    in its constructor, rather than hardcoding sys.stdout.
    """

    def __init__(self, stream: TextIO = sys.stdout):
        """
        Initialize the service.

        Args:
            stream: The text stream to write notifications to. Defaults to stdout.
        """
        self.stream = stream

    def send(self, message: str, level: NotificationLevel = NotificationLevel.INFO) -> None:
        """
        Writes a formatted notification to the stream.

        Args:
            message: The message string.
            level: The severity level.

        Raises:
            NotificationError: If writing to the stream fails.
        """
        try:
            prefix = f"[{level.name}]"
            self.stream.write(f"{prefix} {message}\n")
            self.stream.flush()
        except Exception as e:
            # Wrap low-level IO errors in our domain exception
            raise NotificationError(f"Failed to write notification: {e}") from e
