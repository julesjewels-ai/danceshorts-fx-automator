import io
import pytest
from src.core.notifications import ConsoleNotificationService
from src.domain.models import NotificationLevel
from src.domain.exceptions import NotificationError

def test_console_notification_service_writes_to_stream():
    # Arrange
    mock_stream = io.StringIO()
    service = ConsoleNotificationService(stream=mock_stream)
    message = "Test message"
    level = NotificationLevel.INFO

    # Act
    service.send(message, level)

    # Assert
    output = mock_stream.getvalue()
    assert "[INFO] Test message\n" == output

def test_console_notification_service_different_level():
    # Arrange
    mock_stream = io.StringIO()
    service = ConsoleNotificationService(stream=mock_stream)
    message = "Warning message"
    level = NotificationLevel.WARNING

    # Act
    service.send(message, level)

    # Assert
    output = mock_stream.getvalue()
    assert "[WARNING] Warning message\n" == output

def test_notification_error_on_closed_stream():
    # Arrange
    mock_stream = io.StringIO()
    mock_stream.close() # Induce failure
    service = ConsoleNotificationService(stream=mock_stream)

    # Act & Assert
    with pytest.raises(NotificationError):
        service.send("Should fail")
