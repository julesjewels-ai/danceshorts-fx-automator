import io
import pytest
from src.core.notifications import ConsoleNotificationService
from src.domain.models import Notification, NotificationLevel
from src.domain.exceptions import NotificationError

def test_console_notification_service_writes_to_stream():
    """
    Verifies that the ConsoleNotificationService correctly writes formatted
    notifications to the injected stream.
    """
    # 1. Arrange: Create a mock stream (StringIO)
    mock_stream = io.StringIO()
    service = ConsoleNotificationService(stream=mock_stream)

    notification = Notification(
        message="Test Message",
        level=NotificationLevel.INFO,
        context={"key": "value"}
    )

    # 2. Act: Send the notification
    service.send(notification)

    # 3. Assert: Verify the stream content
    output = mock_stream.getvalue()
    assert "[INFO] Test Message" in output
    assert "Context: key=value" in output

def test_console_notification_service_handles_write_error():
    """
    Verifies that the service raises NotificationError when writing fails.
    """
    # 1. Arrange: Create a stream that raises an exception on write
    class BrokenStream:
        def write(self, text):
            raise IOError("Disk full")
        def flush(self):
            pass

    service = ConsoleNotificationService(stream=BrokenStream())

    notification = Notification(message="Fail", level=NotificationLevel.ERROR)

    # 2. Act & Assert: Expect NotificationError
    with pytest.raises(NotificationError) as exc_info:
        service.send(notification)

    assert "Disk full" in str(exc_info.value)
