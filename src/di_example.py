from typing import Dict, Type, Any
from src.domain.interfaces import MetadataExporter
from src.infrastructure.exporters import TextFileMetadataExporter

# A simple DI Container simulation
class Container:
    def __init__(self):
        self._registry = {}

    def register(self, interface: Any, implementation: Any):
        self._registry[interface] = implementation

    def resolve(self, interface: Any) -> Any:
        if interface not in self._registry:
            raise ValueError(f"No implementation registered for {interface}")
        return self._registry[interface]

def main():
    # 1. Setup Container
    container = Container()

    # 2. Register Implementation
    # We register the TextFileMetadataExporter instance as the implementation for MetadataExporter protocol
    exporter_instance = TextFileMetadataExporter(encoding='utf-8')
    container.register(MetadataExporter, exporter_instance)

    # 3. Resolve and Use
    # In a real app, this would happen inside a service that depends on MetadataExporter
    exporter = container.resolve(MetadataExporter)

    sample_data = {
        "title": "My Awesome Video",
        "description": "This is a description.",
        "tags": ["awesome", "video", "dance"]
    }

    output_file = "sample_output_metadata.txt"
    print(f"Exporting metadata to {output_file} using {type(exporter).__name__}...")

    try:
        exporter.export(sample_data, output_file)
        print("Export successful!")

        # Verify output
        with open(output_file, 'r') as f:
            print("\n--- Output Content ---")
            print(f.read())
            print("----------------------")

    except Exception as e:
        print(f"Export failed: {e}")

if __name__ == "__main__":
    main()
