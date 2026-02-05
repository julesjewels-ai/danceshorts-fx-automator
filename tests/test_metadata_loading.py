from src.core.app import DanceShortsAutomator
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_metadata_loading():
    print("Testing Metadata Loading...")
    app = DanceShortsAutomator(
        report_file='production_report.csv',
        options_file='metadata_options.json'
    )
    app.load_configurations()

    print("Selected Style:")
    print(app.selected_style)

    # Check if we loaded the recommended option (2)
    assert app.selected_style.get('style') == "Recommended"
    assert app.selected_style.get('title') == "Elegance in Motion"
    assert "audio_cues" in app.selected_style
    assert len(app.selected_style['text_overlay']) == 3

    print("Metadata Loading Test Passed.")

if __name__ == "__main__":
    test_metadata_loading()
