import sys
import os

# Ensure src is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.domain.models import BatchJobResult, JobStatus
from src.interfaces.reporting import ReportGenerator
from src.core.reporting import MarkdownBatchReporter

class BatchProcessor:
    """
    A simple batch processor that depends on a ReportGenerator.
    This demonstrates dependency injection.
    """

    def __init__(self, reporter: ReportGenerator[BatchJobResult]):
        self.reporter = reporter
        self.results = []

    def add_result(self, result: BatchJobResult):
        self.results.append(result)

    def generate_report(self) -> str:
        return self.reporter.generate(self.results)

def main():
    # 1. Instantiate the dependency (Reporter)
    # This is where we choose the implementation.
    markdown_reporter = MarkdownBatchReporter(title="My Awesome Batch Report")

    # 2. Inject dependency into the consumer (Processor)
    processor = BatchProcessor(reporter=markdown_reporter)

    # 3. Use the consumer
    processor.add_result(BatchJobResult(
        project_name="Video Project 1",
        status=JobStatus.COMPLETED,
        duration_seconds=12.5,
        output_path="/outputs/video1.mp4"
    ))

    processor.add_result(BatchJobResult(
        project_name="Video Project 2",
        status=JobStatus.FAILED,
        duration_seconds=2.1,
        error_message="File not found"
    ))

    # Generate and print the report
    report = processor.generate_report()
    print(report)

if __name__ == "__main__":
    main()
