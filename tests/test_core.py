import pytest
import json
import os
from src.core.app import DanceShortsAutomator

@pytest.fixture
def mock_data_files(tmp_path):
    """Creates temporary JSON files for testing."""
    instr_file = tmp_path / "veo_instructions.json"
    opts_file = tmp_path / "metadata_options.json"

    instr_data = {"scenes": [{"order": 1, "clip_path": "test.mp4"}]}
    opts_data = {
        "recommended": 2,
        "options": [
            {"id": 1, "style": "Basic"},
            {"id": 2, "style": "Recommended", "color": "Red", "title": "Test Title", "tags": ["tag1"]}
        ]
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

def test_load_configurations_selects_option_2(mock_data_files):
    """Test that Option 2 (Recommended) is selected by default."""
    instr, opts = mock_data_files
    app = DanceShortsAutomator(instr, opts)
    app.load_configurations()
    
    assert app.selected_style['style'] == "Recommended"
    assert app.selected_style['color'] == "Red"

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
    assert "Recommended" in caplog.text

def test_sidecar_generation(mock_data_files, tmp_path):
    """Test that the sidecar file is generated correctly."""
    instr, opts = mock_data_files
    app = DanceShortsAutomator(instr, opts)
    app.load_configurations()

    # Switch to tmp_path so we don't pollute repo
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        app.generate_sidecar_file()
        assert os.path.exists("video_metadata.txt")
        with open("video_metadata.txt", 'r') as f:
            content = f.read()
            assert "Title: Test Title" in content
            assert "tag1" in content
    finally:
        os.chdir(original_cwd)