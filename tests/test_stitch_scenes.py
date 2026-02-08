import pytest
import os
from unittest.mock import MagicMock, patch, ANY
from src.core.app import DanceShortsAutomator

@pytest.fixture
def automator():
    automator = DanceShortsAutomator(
        instruction_file="instr.json",
        options_file="opts.json",
        style_file="style.json",
        working_directory="/tmp"
    )
    automator.instructions = {"scenes": []}
    return automator

@patch('src.core.app.VideoFileClip')
@patch('src.core.app.concatenate_videoclips')
@patch('src.core.app.os.path.exists')
def test_stitch_scenes_success(mock_exists, mock_concat, mock_videoclip, automator):
    """Test successful stitching of valid scenes."""
    # Setup mocks
    mock_exists.return_value = True

    mock_clip = MagicMock()
    mock_clip.duration = 10
    mock_clip.w, mock_clip.h = 1920, 1080  # 16:9 aspect ratio

    # Mock chainable methods
    mock_clip.subclipped.return_value = mock_clip
    mock_clip.resized.return_value = mock_clip
    mock_clip.cropped.return_value = mock_clip
    mock_clip.with_effects.return_value = mock_clip

    mock_videoclip.return_value = mock_clip
    mock_concat.return_value = MagicMock()

    # Define scenes
    automator.instructions = {
        "scenes": [
            {"source": "clip1.mp4", "start": 0, "duration": 5},
            {"source": "clip2.mp4", "start": 2, "duration": 3}
        ]
    }

    # Execute
    result = automator._stitch_scenes()

    # Verify
    assert mock_videoclip.call_count == 2
    # Check that clips were processed (resized/cropped for 9:16)
    assert mock_clip.resized.called
    assert mock_clip.cropped.called
    # Check that cross-fade was applied to the second clip
    assert mock_clip.with_effects.called

    mock_concat.assert_called_once()
    args, kwargs = mock_concat.call_args
    assert len(args[0]) == 2  # list of clips
    assert kwargs['method'] == 'compose'
    assert kwargs['padding'] == -0.5

@patch('src.core.app.VideoFileClip')
@patch('src.core.app.os.path.exists')
def test_stitch_scenes_missing_file(mock_exists, mock_videoclip, automator):
    """Test handling of missing source files."""
    mock_exists.return_value = False  # File not found

    automator.instructions = {
        "scenes": [
            {"source": "missing.mp4", "start": 0, "duration": 5}
        ]
    }

    # Expect ValueError because no valid clips were found
    with pytest.raises(ValueError, match="No valid clips found to stitch"):
        automator._stitch_scenes()

    mock_videoclip.assert_not_called()

def test_stitch_scenes_veo_format_error(automator):
    """Test that Veo format scenes raise a ValueError."""
    automator.instructions = {
        "scenes": [
            {"start_image": "img1.png", "end_image": "img2.png", "prompt": "test"}
        ]
    }

    with pytest.raises(ValueError, match="Veo AI generation format"):
        automator._stitch_scenes()

def test_stitch_scenes_missing_source_error(automator):
    """Test that scenes missing 'source' raise a ValueError."""
    automator.instructions = {
        "scenes": [
            {"start": 0, "duration": 5}  # Missing 'source'
        ]
    }

    with pytest.raises(ValueError, match="missing required 'source' field"):
        automator._stitch_scenes()

@patch('src.core.app.VideoFileClip')
@patch('src.core.app.concatenate_videoclips')
@patch('src.core.app.os.path.exists')
def test_stitch_scenes_aspect_ratio_adjustment(mock_exists, mock_concat, mock_videoclip, automator):
    """Test logic for resizing and cropping based on aspect ratio."""
    mock_exists.return_value = True

    # Scene 1: Wider than target (e.g. 16:9)
    wide_clip = MagicMock()
    wide_clip.w, wide_clip.h = 1920, 1080
    wide_clip.subclipped.return_value = wide_clip
    wide_clip.resized.return_value = wide_clip
    wide_clip.cropped.return_value = wide_clip

    # Scene 2: Taller/Equal to target (e.g. 9:16)
    tall_clip = MagicMock()
    tall_clip.w, tall_clip.h = 720, 1280
    tall_clip.subclipped.return_value = tall_clip
    tall_clip.resized.return_value = tall_clip
    tall_clip.cropped.return_value = tall_clip

    mock_videoclip.side_effect = [wide_clip, tall_clip]
    mock_concat.return_value = MagicMock()

    automator.instructions = {
        "scenes": [
            {"source": "wide.mp4", "start": 0, "duration": 5},
            {"source": "tall.mp4", "start": 0, "duration": 5}
        ]
    }

    automator._stitch_scenes()

    # Verify wide clip processing
    # Should resize by height to match target height (1280), then crop width
    wide_clip.resized.assert_called_with(height=1280)
    wide_clip.cropped.assert_called_with(width=720, height=1280, x_center=1920/2, y_center=1080/2)

    # Verify tall clip processing
    # Should resize by width to match target width (720), then crop height
    tall_clip.resized.assert_called_with(width=720)
    tall_clip.cropped.assert_called_with(width=720, height=1280, x_center=720/2, y_center=1280/2)
