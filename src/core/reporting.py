import os
from typing import List
from src.domain.models import BatchJobResult, ProcessingStatus
from src.interfaces.reporting import ReportGenerator
from src.domain.exceptions import ReportingError

class MarkdownBatchReporter:
    """
    Generates a Markdown report summarizing batch job results.
    Implements ReportGenerator[BatchJobResult].
    """

    def __init__(self, output_path: str):
        self.output_path = output_path

    def generate(self, results: List[BatchJobResult]) -> None:
        """
        Generates a Markdown report file from the results.

        Raises:
            ReportingError: If file operations fail.
        """
        if not results:
            return

        total = len(results)
        succeeded = sum(1 for r in results if r.status == ProcessingStatus.SUCCESS)
        failed = sum(1 for r in results if r.status == ProcessingStatus.FAILED)
        skipped = sum(1 for r in results if r.status == ProcessingStatus.SKIPPED)

        lines = [
            "# Batch Processing Report",
            "",
            f"- **Total Projects:** {total}",
            f"- **Succeeded:** {succeeded}",
            f"- **Failed:** {failed}",
            f"- **Skipped:** {skipped}",
            "",
            "## Details",
            "",
            "| Project Name | Status | Duration (s) | Error |",
            "|---|---|---|---|",
        ]

        for result in results:
            status_icon = "✅" if result.status == ProcessingStatus.SUCCESS else "❌" if result.status == ProcessingStatus.FAILED else "⏭️"
            # Escape pipes in error message to avoid breaking table
            error_msg = (result.error_message or "-").replace("|", "\\|")
            lines.append(f"| {result.project_name} | {status_icon} {result.status.name} | {result.processing_time:.2f} | {error_msg} |")

        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(self.output_path)), exist_ok=True)

            with open(self.output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
        except OSError as e:
            raise ReportingError(f"Failed to write report to {self.output_path}: {e}") from e
