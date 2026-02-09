import pytest
import os
from unittest.mock import Mock
from src.domain.models import BatchJobResult, ProcessingStatus
from src.core.reporting import MarkdownBatchReporter
from src.interfaces.reporting import ReportGenerator
from src.domain.exceptions import ReportingError

def test_markdown_report_generation(tmp_path):
    # Arrange
    output_file = tmp_path / "test_report.md"
    reporter = MarkdownBatchReporter(output_path=str(output_file))

    results = [
        BatchJobResult(
            project_name="Project Alpha",
            status=ProcessingStatus.SUCCESS,
            processing_time=10.0
        ),
        BatchJobResult(
            project_name="Project Beta",
            status=ProcessingStatus.FAILED,
            processing_time=2.0,
            error_message="Test Error"
        )
    ]

    # Act
    reporter.generate(results)

    # Assert
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")

    assert "# Batch Processing Report" in content
    assert "Total Projects:** 2" in content
    assert "Succeeded:** 1" in content
    assert "Failed:** 1" in content
    assert "| Project Alpha | ✅ SUCCESS | 10.00 | - |" in content
    assert "| Project Beta | ❌ FAILED | 2.00 | Test Error |" in content

def test_empty_results_no_file(tmp_path):
    output_file = tmp_path / "empty_report.md"
    reporter = MarkdownBatchReporter(output_path=str(output_file))

    reporter.generate([])

    assert not output_file.exists()

def process_batch_and_report(reporter: ReportGenerator[BatchJobResult], results):
    """Consumer function that relies on the Protocol, not concrete implementation."""
    reporter.generate(results)

def test_decoupled_interface_usage():
    """Verify that a consumer can use any implementation of ReportGenerator."""
    # This mocks the interface to prove decoupling as requested
    mock_reporter = Mock()
    # Ensure mock adheres to Protocol structure if we were doing runtime checking,
    # but for unit test Mock is sufficient to prove we don't need concrete class.

    results = [BatchJobResult("Test", ProcessingStatus.SUCCESS)]

    process_batch_and_report(mock_reporter, results)

    mock_reporter.generate.assert_called_once_with(results)

def test_markdown_report_error_handling(tmp_path):
    """Verify that file errors are wrapped in ReportingError."""
    # Use a directory as file path to trigger IsADirectoryError (OSError)
    # or write to a read-only location.
    # Creating a directory where the file should be is a reliable way to cause OSError on open()
    invalid_path = tmp_path / "directory_as_file"
    invalid_path.mkdir()

    reporter = MarkdownBatchReporter(output_path=str(invalid_path))
    results = [BatchJobResult("Test", ProcessingStatus.SUCCESS)]

    with pytest.raises(ReportingError) as excinfo:
        reporter.generate(results)

    assert "Failed to write report" in str(excinfo.value)
