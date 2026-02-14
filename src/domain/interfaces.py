from typing import Protocol, TypeVar, Any, Dict

T = TypeVar("T", contravariant=True)

class Exporter(Protocol[T]):
    """Generic interface for data exporters."""

    def export(self, data: T, destination: str) -> None:
        """
        Exports data to the specified destination.

        Args:
            data: The data to export.
            destination: The target destination (e.g., file path).

        Raises:
            ForgeExporterError: If the export fails.
        """
        ...

class MetadataExporter(Exporter[Dict[str, Any]], Protocol):
    """Specialized exporter for metadata dictionaries."""
    pass
