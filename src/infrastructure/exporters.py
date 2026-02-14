import os
from typing import Dict, Any, List
from src.domain.interfaces import MetadataExporter
from src.domain.exceptions import ForgeExporterError

class TextFileMetadataExporter:
    """Concrete implementation of MetadataExporter for text files."""

    def __init__(self, encoding: str = 'utf-8'):
        """
        Initializes the exporter.

        Args:
            encoding (str): Encoding to use for file writing.
        """
        self.encoding = encoding

    def export(self, data: Dict[str, Any], destination: str) -> None:
        """
        Writes metadata (title, description, tags) to a text file.

        Args:
            data: Dictionary containing 'title', 'description', and 'tags'.
            destination: Path to the output file.

        Raises:
            ForgeExporterError: If writing to the file fails.
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(os.path.abspath(destination)), exist_ok=True)

            with open(destination, 'w', encoding=self.encoding) as f:
                title = data.get('title', 'Untitled')
                description = data.get('description', 'No description provided.')
                tags = data.get('tags', [])

                # Format tags as comma-separated string if it's a list
                if isinstance(tags, list):
                    tags_str = ", ".join(str(t) for t in tags)
                else:
                    tags_str = str(tags)

                f.write(f"TITLE: {title}\n\n")
                f.write(f"DESCRIPTION:\n{description}\n\n")
                f.write(f"TAGS: {tags_str}\n")

        except (IOError, OSError) as e:
            raise ForgeExporterError(f"Failed to export metadata to {destination}: {e}") from e
