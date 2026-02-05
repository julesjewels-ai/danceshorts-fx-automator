import pytest
import json
import os
from src.core.app import DanceShortsAutomator

@pytest.fixture
def mock_data_files(tmp_path):
    """Creates temporary JSON files for testing."""
    instr_file = tmp_path / "veo_instructions.json"
    opts_file = tmp_path / "metadata_options.json"

    instr_data = {"scenes": [{"id": 1, "source": "test.mp4", "speed": 1.0}]}
    opts_data = {
        "option_1": {"title": "Option 1 Title", "text_overlay": ["Text 1"]},
        "option_2": {"title": "Option 2 Recommended", "text_overlay": ["Text 2"]},
        "recommended": 2
    }

    with open(instr_file, 'w') as f:
        json.dump(instr_data, f)
    with open(opts_file, 'w') as f:
        json.dump(opts_data, f)

    return str(instr_file), str(opts_file)

def test_initialization(mock_data_files):
    """Test that the class initializes correctly."""
    instr, opts = mock_data_files
    app = DanceShortsAutomator(instr, opts)
    assert app.instruction_file == instr
    assert app.options_file == opts

def test_load_configurations_selects_recommended(mock_data_files):
    """Test that the recommended option is selected by default."""
    instr, opts = mock_data_files
    app = DanceShortsAutomator(instr, opts)
    app.load_configurations()
    
    assert app.selected_style['title'] == "Option 2 Recommended"
    assert app.selected_style['text_overlay'] == ["Text 2"]

def test_missing_files_raises_error():
    """Test error handling for missing files."""
    app = DanceShortsAutomator("ghost.json", "phantom.json")
    with pytest.raises(FileNotFoundError):
        app.load_configurations()

def test_dry_run_pipeline(mock_data_files, caplog):
    """Test the dry run execution flow."""
    instr, opts = mock_data_files
    app = DanceShortsAutomator(instr, opts)
    app.load_configurations()
    
    with caplog.at_level("INFO"):
        app.process_pipeline(dry_run=True)
    
    assert "[DRY-RUN]" in caplog.text
    assert "Option 2 Recommended" in caplog.text