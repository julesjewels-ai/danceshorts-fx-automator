import pytest
from unittest.mock import Mock, patch, mock_open, call
from src.domain.interfaces import MetadataExporter
from src.infrastructure.exporters import TextFileMetadataExporter
from src.domain.exceptions import ForgeExporterError

def export_service(exporter: MetadataExporter, data: dict, output_path: str):
    """
    A service function that depends on the MetadataExporter interface.
    This demonstrates decoupling because it works with any implementation of the interface.
    """
    exporter.export(data, output_path)

def test_export_service_uses_interface_correctly():
    """
    Verifies that a consumer of the MetadataExporter interface interacts with it correctly,
    proving decoupling from the concrete implementation.
    """
    # 1. Arrange
    # Create a mock that adheres to the MetadataExporter protocol
    # Note: spec=MetadataExporter might not work perfectly with Protocol on some python versions for runtime checking,
    # but for mocking it's usually fine or we can just use a plain Mock if we don't need strict spec validation.
    mock_exporter = Mock()

    test_data = {"title": "Test Video", "description": "Test Desc", "tags": ["test"]}
    test_path = "test_output.txt"

    # 2. Act
    export_service(mock_exporter, test_data, test_path)

    # 3. Assert
    # Verify the interface method was called with expected arguments
    mock_exporter.export.assert_called_once_with(test_data, test_path)

def test_text_file_exporter_implementation():
    """
    Verifies the concrete implementation writes the correct format to the file.
    """
    exporter = TextFileMetadataExporter()
    data = {
        "title": "My Title",
        "description": "My Description",
        "tags": ["tag1", "tag2"]
    }

    # Mock 'open' and 'os.makedirs' to avoid file system operations
    with patch("builtins.open", mock_open()) as mock_file, \
         patch("os.makedirs") as mock_makedirs:

        exporter.export(data, "path/to/output.txt")

        # Verify directory creation
        mock_makedirs.assert_called_once()

        # Verify file opening
        mock_file.assert_called_once_with("path/to/output.txt", "w", encoding="utf-8")

        # Verify content written
        handle = mock_file()
        expected_calls = [
            call("TITLE: My Title\n\n"),
            call("DESCRIPTION:\nMy Description\n\n"),
            call("TAGS: tag1, tag2\n")
        ]
        # We check if write was called. Since we do multiple writes, checking any specific one or order is good.
        # Let's check that title was written.
        handle.write.assert_any_call("TITLE: My Title\n\n")
        handle.write.assert_any_call("DESCRIPTION:\nMy Description\n\n")
        handle.write.assert_any_call("TAGS: tag1, tag2\n")

def test_exporter_raises_custom_exception():
    exporter = TextFileMetadataExporter()

    with patch("builtins.open", side_effect=IOError("Disk full")):
         with patch("os.makedirs"):
            with pytest.raises(ForgeExporterError) as excinfo:
                exporter.export({}, "out.txt")

            assert "Failed to export metadata" in str(excinfo.value)
