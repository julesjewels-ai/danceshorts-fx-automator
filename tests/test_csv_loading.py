from src.core.app import DanceShortsAutomator
import pandas as pd
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_csv_loading():
    print("Testing CSV Loading...")
    app = DanceShortsAutomator(
        report_file='production_report.csv',
        options_file='metadata_options.json'
    )
    app.load_configurations()

    print("Loaded Report Data:")
    print(app.report_data)

    assert not app.report_data.empty
    assert 'Scene' in app.report_data.columns
    assert 'Source' in app.report_data.columns
    print("CSV Loading Test Passed.")

if __name__ == "__main__":
    test_csv_loading()
