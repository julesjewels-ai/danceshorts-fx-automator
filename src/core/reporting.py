from typing import Sequence, List
from datetime import datetime

from src.interfaces.reporting import ReportGenerator
from src.domain.models import BatchJobResult, JobStatus

class MarkdownBatchReporter:
    """
    Concrete implementation of ReportGenerator for BatchJobResult.
    Generates a Markdown formatted report.
    """

    def __init__(self, title: str = "Batch Processing Report"):
        """
        Initialize the reporter with a title.

        Args:
            title: The title of the report.
        """
        self.title = title

    def generate(self, results: Sequence[BatchJobResult]) -> str:
        """
        Generates a Markdown report from a sequence of BatchJobResults.

        Args:
            results: A sequence of BatchJobResult objects.

        Returns:
            A Markdown formatted string.
        """
        lines: List[str] = []
        lines.append(f"# {self.title}")
        lines.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Summary
        total = len(results)
        success = sum(1 for r in results if r.status == JobStatus.COMPLETED)
        failed = sum(1 for r in results if r.status == JobStatus.FAILED)
        skipped = sum(1 for r in results if r.status == JobStatus.SKIPPED)

        lines.append("## Summary")
        lines.append(f"- **Total Jobs:** {total}")
        lines.append(f"- **Success:** {success}")
        lines.append(f"- **Failed:** {failed}")
        lines.append(f"- **Skipped:** {skipped}")
        lines.append("")

        # Details Table
        lines.append("## Job Details")
        lines.append("| Project | Status | Duration (s) | Output | Error |")
        lines.append("|---|---|---|---|---|")

        for result in results:
            status_icon = {
                JobStatus.COMPLETED: "✅",
                JobStatus.FAILED: "❌",
                JobStatus.SKIPPED: "⏭️",
                JobStatus.PENDING: "⏳",
                JobStatus.RUNNING: "🏃"
            }.get(result.status, "?")

            output = result.output_path if result.output_path else "-"
            error = result.error_message if result.error_message else "-"

            # Escape pipes in strings to avoid breaking markdown table
            project = result.project_name.replace("|", "\\|")
            output = output.replace("|", "\\|")
            error = error.replace("|", "\\|")

            lines.append(f"| {project} | {status_icon} {result.status.name} | {result.duration_seconds:.2f} | {output} | {error} |")

        return "\n".join(lines)
