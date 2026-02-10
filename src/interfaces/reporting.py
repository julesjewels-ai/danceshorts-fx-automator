from typing import Protocol, TypeVar, Sequence

T_contra = TypeVar("T_contra", contravariant=True)

class ReportGenerator(Protocol[T_contra]):
    """
    Protocol for generating reports from a sequence of results.
    Strictly decoupled from the implementation of report generation.
    """

    def generate(self, results: Sequence[T_contra]) -> str:
        """
        Generates a report string from the given results.

        Args:
            results: A sequence of items to report on.

        Returns:
            A string representation of the report (e.g., Markdown, CSV, JSON).
        """
        ...
