import pytest
import json
import os
from src.core.app import DanceShortsAutomator

@pytest.fixture
def mock_data_files(tmp_path):
    """Creates temporary JSON files for testing."""
    instr_file = tmp_path / "veo_instructions.json"
    opts_file = tmp_path / "metadata_options.json"
    style_file = tmp_path / "style_options.json"

    instr_data = {"scenes": [{"id": 1, "source": "test.mp4"}]}
    opts_data = {
        "option_1": {"title": "Test Option 1", "text_overlay": []},
        "option_2": {"title": "Test Option 2", "text_overlay": []},
        "recommended": 2
    }
    style_data = {
        "options": {
            "1": {"style": "Basic"},
            "2": {"style": "Recommended", "color": "Red"}
        },
        "default": "2"
    }

    with open(instr_file, 'w') as f:
        json.dump(instr_data, f)
    with open(opts_file, 'w') as f:
        json.dump(opts_data, f)
    with open(style_file, 'w') as f:
        json.dump(style_data, f)

    return str(instr_file), str(opts_file), str(style_file)

def test_initialization(mock_data_files):
    """Test that the class initializes correctly."""
    instr, opts, style = mock_data_files
    app = DanceShortsAutomator(instr, opts, style)
    assert app.instruction_file == instr
    assert app.options_file == opts
    assert app.style_file == style

def test_load_configurations_selects_option_2(mock_data_files):
    """Test that Option 2 (Recommended) is selected by default."""
    instr, opts, style = mock_data_files
    app = DanceShortsAutomator(instr, opts, style)
    app.load_configurations()
    
    assert app.selected_style['style'] == "Recommended"
    assert app.selected_style['color'] == "Red"

def test_missing_files_raises_error():
    """Test error handling for missing files."""
    app = DanceShortsAutomator("ghost.json", "phantom.json", "spirit.json")
    with pytest.raises(FileNotFoundError):
        app.load_configurations()

def test_dry_run_pipeline(mock_data_files, caplog):
    """Test the dry run execution flow."""
    instr, opts, style = mock_data_files
    app = DanceShortsAutomator(instr, opts, style)
    app.load_configurations()
    
    with caplog.at_level("INFO"):
        app.process_pipeline(dry_run=True)
    
    assert "[DRY-RUN]" in caplog.text
    assert "Recommended" in caplog.text