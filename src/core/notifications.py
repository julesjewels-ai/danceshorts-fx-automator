import logging
from src.domain.models import NotificationLevel
from src.domain.exceptions import NotificationError
from src.interfaces.notification import NotificationService

logger = logging.getLogger(__name__)

class ConsoleNotificationService:
    """
    Implementation of NotificationService that prints to console/stdout.
    """

    def notify(self, message: str, level: NotificationLevel) -> None:
        """
        Prints the notification message to the console with appropriate formatting.

        Args:
            message (str): The message content.
            level (NotificationLevel): The severity level of the notification.

        Raises:
            NotificationError: If there is an issue writing to stdout (unlikely but handled).
        """
        try:
            # Format the output based on level
            prefix = f"[{level.name}]"

            # Use appropriate logging level
            if level == NotificationLevel.ERROR:
                logger.error(f"{prefix} {message}")
            elif level == NotificationLevel.WARNING:
                logger.warning(f"{prefix} {message}")
            else:
                logger.info(f"{prefix} {message}")

        except Exception as e:
            raise NotificationError(f"Failed to send console notification: {e}") from e
