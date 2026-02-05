from src.core.app import DanceShortsAutomator
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_sidecar():
    print("Testing Sidecar Generation...")
    app = DanceShortsAutomator(
        report_file='production_report.csv',
        options_file='metadata_options.json'
    )
    app.load_configurations()

    # Manually call internal method
    app._export_metadata_sidecar()

    assert os.path.exists("final_dance_short_metadata.txt")

    with open("final_dance_short_metadata.txt", 'r') as f:
        content = f.read()
        print(content)
        assert "Title: Elegance in Motion" in content
        assert "Tags:\n#dance" in content

    print("Sidecar Test Passed.")

if __name__ == "__main__":
    test_sidecar()
