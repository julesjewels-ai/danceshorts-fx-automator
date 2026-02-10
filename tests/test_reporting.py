import unittest
from unittest.mock import Mock
from src.domain.models import BatchJobResult, JobStatus
from src.core.reporting import MarkdownBatchReporter
from src.interfaces.reporting import ReportGenerator

class TestMarkdownBatchReporter(unittest.TestCase):
    def test_generate_report(self):
        reporter = MarkdownBatchReporter(title="Test Report")
        results = [
            BatchJobResult(project_name="P1", status=JobStatus.COMPLETED, duration_seconds=10.0),
            BatchJobResult(project_name="P2", status=JobStatus.FAILED, error_message="Error")
        ]

        report = reporter.generate(results)

        self.assertIn("# Test Report", report)
        self.assertIn("Total Jobs:** 2", report)
        self.assertIn("✅ COMPLETED", report)
        self.assertIn("❌ FAILED", report)
        self.assertIn("P1", report)
        self.assertIn("P2", report)

class TestDecoupledConsumer(unittest.TestCase):
    def test_consumer_uses_interface(self):
        """
        Prove that a consumer depends on the interface, not the implementation.
        We mock the interface.
        """
        # Define a consumer function (or class) that takes the interface
        def process_and_report(reporter: ReportGenerator[BatchJobResult], items):
            return reporter.generate(items)

        # Create a mock that adheres to the ReportGenerator protocol
        mock_reporter = Mock(spec=ReportGenerator)
        mock_reporter.generate.return_value = "Mocked Report"

        items = [BatchJobResult(project_name="test", status=JobStatus.PENDING)]

        # Inject the mock
        result = process_and_report(mock_reporter, items)

        # Verify interaction
        self.assertEqual(result, "Mocked Report")
        mock_reporter.generate.assert_called_once_with(items)

if __name__ == '__main__':
    unittest.main()
