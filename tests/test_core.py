import pytest
import json
import os
from src.core.app import DanceShortsAutomator

@pytest.fixture
def mock_data_files(tmp_path):
    """Creates temporary JSON files for testing."""
    instr_file = tmp_path / "veo_instructions.json"
    opts_file = tmp_path / "metadata_options.json"
    report_file = tmp_path / "production_report.csv"

    # Minimal valid data for new logic
    instr_data = {
        "scenes": [
            {"id": 1, "start_keyframe": "k1.jpg", "end_keyframe": "k2.jpg", "prompt": "test"}
        ]
    }
    opts_data = {
        "options": {
            "1": {"style": "Basic"},
            "2": {"style": "Recommended", "color": "Red", "text_overlay": []}
        }
    }
    # CSV content
    report_content = "Scene,Start,End,Duration,Action\n1,0,5,5,Start\n"

    with open(instr_file, 'w') as f:
        json.dump(instr_data, f)
    with open(opts_file, 'w') as f:
        json.dump(opts_data, f)
    with open(report_file, 'w') as f:
        f.write(report_content)

    return str(report_file), str(instr_file), str(opts_file)

def test_initialization(mock_data_files):
    """Test that the class initializes correctly."""
    report, instr, opts = mock_data_files
    app = DanceShortsAutomator(report, instr, opts)
    assert app.instruction_file == instr
    assert app.options_file == opts
    assert app.report_file == report

def test_load_configurations_selects_option_2(mock_data_files):
    """Test that Option 2 (Recommended) is selected by default."""
    report, instr, opts = mock_data_files
    app = DanceShortsAutomator(report, instr, opts)
    app.load_configurations()
    
    assert app.selected_style['style'] == "Recommended"
    assert app.selected_style['color'] == "Red"

def test_missing_files_raises_error():
    """Test error handling for missing files."""
    app = DanceShortsAutomator("ghost.csv", "ghost.json", "phantom.json")
    with pytest.raises(FileNotFoundError):
        app.load_configurations()

def test_dry_run_pipeline(mock_data_files, caplog):
    """Test the dry run execution flow."""
    report, instr, opts = mock_data_files
    app = DanceShortsAutomator(report, instr, opts)
    app.load_configurations()
    
    with caplog.at_level("INFO"):
        app.process_pipeline(dry_run=True)
    
    assert "[DRY-RUN]" in caplog.text
    assert "Recommended" in caplog.text
