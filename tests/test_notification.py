import pytest
import logging
import json
import os
from unittest.mock import MagicMock
from src.core.notifications import ConsoleNotificationService
from src.core.app import DanceShortsAutomator
from src.domain.models import NotificationLevel
from src.domain.exceptions import NotificationError

def test_console_notification_service_logs(caplog):
    """Test that ConsoleNotificationService logs correctly."""
    service = ConsoleNotificationService()

    # We need to ensure the logger level is set to capture INFO
    with caplog.at_level(logging.INFO):
        service.notify("Test Info", NotificationLevel.INFO)
        service.notify("Test Warning", NotificationLevel.WARNING)
        service.notify("Test Error", NotificationLevel.ERROR)

    # Check that logs contain the expected messages
    assert "[INFO] Test Info" in caplog.text
    assert "[WARNING] Test Warning" in caplog.text
    assert "[ERROR] Test Error" in caplog.text

def test_automator_integration(tmp_path):
    """Test that DanceShortsAutomator uses the injected notification service."""

    # create dummy files
    d = tmp_path / "subdir"
    d.mkdir()
    instr_file = d / "veo_instructions.json"
    opts_file = d / "metadata_options.json"
    style_file = d / "style_options.json"

    with open(instr_file, 'w') as f:
        json.dump({"scenes": []}, f)
    with open(opts_file, 'w') as f:
        json.dump({"recommended": 1, "option_1": {}}, f)
    with open(style_file, 'w') as f:
        json.dump({"default": "1", "options": {"1": {}}}, f)

    # Mock the service
    mock_service = MagicMock()

    app = DanceShortsAutomator(
        instruction_file=str(instr_file),
        options_file=str(opts_file),
        style_file=str(style_file),
        notification_service=mock_service
    )

    app.load_configurations()

    # Run pipeline (dry run)
    app.process_pipeline(dry_run=True)

    # Check that notify was called
    assert mock_service.notify.called

    # Check call arguments
    calls = mock_service.notify.call_args_list

    # 1. "Starting processing..." (INFO)
    args0, _ = calls[0]
    assert "Starting processing" in args0[0]
    assert args0[1] == NotificationLevel.INFO

    # 2. "Dry run completed." (SUCCESS)
    args1, _ = calls[-1]
    assert "Dry run completed" in args1[0]
    assert args1[1] == NotificationLevel.SUCCESS

def test_automator_integration_failure(tmp_path):
    """Test that failure triggers ERROR notification."""

    # Create invalid files to force failure later or create valid files and force failure inside pipeline
    d = tmp_path / "subdir_fail"
    d.mkdir()
    instr_file = d / "veo_instructions.json"
    opts_file = d / "metadata_options.json"
    style_file = d / "style_options.json"

    # Valid initial files so constructor passes
    with open(instr_file, 'w') as f:
        json.dump({"scenes": [{"source": "missing.mp4"}]}, f)
    with open(opts_file, 'w') as f:
        json.dump({"recommended": 1, "option_1": {}}, f)
    with open(style_file, 'w') as f:
        json.dump({"default": "1", "options": {"1": {}}}, f)

    mock_service = MagicMock()

    app = DanceShortsAutomator(
        instruction_file=str(instr_file),
        options_file=str(opts_file),
        style_file=str(style_file),
        notification_service=mock_service
    )

    app.load_configurations()

    # This should fail because 'missing.mp4' does not exist and it's not dry_run or something else
    # Actually _validate_scene_clip checks existence.
    # _process_scene_clip will be called inside _stitch_scenes.
    # If source file is missing, _validate_scene_clip returns None, loop continues.
    # If no clips found, raises ValueError("No valid clips found to stitch.")

    # We want to trigger an exception caught in process_pipeline
    with pytest.raises(ValueError):
        app.process_pipeline(dry_run=False) # Not dry run to force execution

    # Check for ERROR notification
    error_calls = [call for call in mock_service.notify.call_args_list if call[0][1] == NotificationLevel.ERROR]
    assert len(error_calls) > 0
    assert "Pipeline failed" in error_calls[0][0][0]
