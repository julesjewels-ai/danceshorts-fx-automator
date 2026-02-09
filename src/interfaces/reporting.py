from typing import Protocol, List, TypeVar

T = TypeVar("T")

class ReportGenerator(Protocol[T]):
    """
    Protocol defining the contract for generating reports.
    Implementations should handle formatting and output.
    """

    def generate(self, results: List[T]) -> None:
        """
        Generates a report from the given list of results.

        Args:
            results: A list of result objects to report on.
        """
        ...
