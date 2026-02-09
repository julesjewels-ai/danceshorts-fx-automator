import os
from src.domain.models import BatchJobResult, ProcessingStatus
from src.core.reporting import MarkdownBatchReporter

def main():
    # Dependency Injection
    output_file = "example_report.md"
    reporter = MarkdownBatchReporter(output_path=output_file)

    # Simulate batch processing results
    results = [
        BatchJobResult(
            project_name="Video A",
            status=ProcessingStatus.SUCCESS,
            processing_time=12.5,
        ),
        BatchJobResult(
            project_name="Video B",
            status=ProcessingStatus.FAILED,
            processing_time=1.2,
            error_message="FileNotFound: source.mp4",
        ),
        BatchJobResult(
            project_name="Video C",
            status=ProcessingStatus.SKIPPED,
            error_message="Missing configuration",
        ),
    ]

    # Generate Report
    print(f"Generating report to {output_file}...")
    reporter.generate(results)

    # Verify
    if os.path.exists(output_file):
        print("✓ Report generated successfully.")
        print("-" * 20)
        with open(output_file, 'r') as f:
            print(f.read())
        print("-" * 20)
        # Cleanup
        os.remove(output_file)
    else:
        print("✗ Failed to generate report.")

if __name__ == "__main__":
    main()
