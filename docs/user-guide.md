# User Guide

## Introduction

This guide provides detailed instructions on how to use **DanceShorts FX Automator** to create professionally edited dance videos for social media platforms.

## Workflow Overview

The typical workflow consists of four main steps:

1. **Prepare Video Clips** - Gather your raw dance footage
2. **Configure Scenes** - Edit `veo_instructions.json` to define scene order and timing
3. **Choose Style** - Select a text overlay style in `metadata_options.json`
4. **Run Pipeline** - Execute the automator to generate your final video

## Step-by-Step Guide

### Step 1: Prepare Your Video Clips

Before running the automator, ensure your video clips are ready:

1. Place all source video files in an accessible directory
2. Note the filenames and paths for each clip
3. Recommended formats: MP4, MOV, AVI

**Best Practices:**
- Use consistent resolution across all clips
- Pre-trim clips to reduce processing time
- Name files descriptively (e.g., `intro_spin.mp4`, `beat_drop.mp4`)

### Step 2: Configure Scene Instructions

Edit `veo_instructions.json` to define how your video will be stitched together:

```json
{
  "scenes": [
    {
      "id": 1,
      "source": "path/to/intro_spin.mp4",
      "start": 0,
      "duration": 3.5
    },
    {
      "id": 2,
      "source": "path/to/beat_drop.mp4",
      "start": 1.2,
      "duration": 5
    },
    {
      "id": 3,
      "source": "path/to/finale.mp4",
      "start": 0,
      "duration": 4
    }
  ]
}
```

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique identifier for the scene (determines order) |
| `source` | string | Path to the video file (relative or absolute) |
| `start` | float | Start time in seconds within the source clip |
| `duration` | float | How many seconds to include from the clip |

**Tips:**
- Scenes are processed in order by `id`
- Use `start` to skip intros or unwanted footage
- Keep `duration` tight to maintain viewer engagement

### Step 3: Choose Text Overlay Style

The automator defaults to **Option 2 (Recommended)**, but you can customize styles in `metadata_options.json`:

```json
{
  "options": {
    "1": {
      "style": "Minimal",
      "font": "Arial",
      "color": "white"
    },
    "2": {
      "style": "Recommended",
      "font": "Impact",
      "color": "yellow"
    },
    "3": {
      "style": "Cinematic",
      "font": "Serif",
      "color": "white"
    }
  }
}
```

**Style Customization:**

| Property | Options | Description |
|----------|---------|-------------|
| `style` | Any string | Display name for the style |
| `font` | Font name | System font or web-safe font |
| `color` | Color name/hex | Text color (e.g., "yellow", "#FFD700") |

**Note:** The system always uses Option 2 by default. To change this behavior, you'll need to modify the code in `src/core/app.py`.

### Step 4: Run the Automator

Execute the video processing pipeline:

```bash
# Standard run
python main.py

# Dry run (simulates without rendering)
python main.py --dry-run
```

**What Happens:**

1. **Configuration Loading** - Validates and loads JSON files
2. **Scene Stitching** - Concatenates clips with cross-dissolve transitions
3. **Overlay Application** - Adds beat-synced text overlays
4. **Rendering** - Exports final 9:16 MP4 video

**Output:**
- File: `final_dance_short.mp4`
- Location: Project root directory
- Format: Vertical 9:16, H.264, AAC audio

## Advanced Usage

### Custom Output Filename

Currently, the output is hardcoded as `final_dance_short.mp4`. To change this, edit `src/core/app.py`:

```python
# Line 80 in src/core/app.py
output_filename = "my_custom_name.mp4"
```

### Beat-Synced Overlays

Text overlays are designed to sync with beat markers. To customize timing:

1. Analyze your audio track to find beat timestamps
2. Add `beat_markers` to your scene configuration
3. Modify the overlay logic in `process_pipeline()`

### Processing Multiple Projects

To process different projects without overwriting configurations:

```bash
# Create project-specific directories
mkdir project1 project2

# Run with specific config paths (requires code modification)
python main.py --instructions project1/veo_instructions.json \
               --options project1/metadata_options.json
```

## Command-Line Options

```bash
python main.py [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--version` | Display version information |
| `--dry-run` | Simulate processing without rendering |
| `-h, --help` | Show help message |

## Makefile Commands

The included Makefile provides convenient shortcuts:

```bash
make install   # Create venv and install dependencies
make run       # Run the application
make test      # Run test suite
make clean     # Remove cache files and temporary data
```

## Output Specifications

### Video Specifications

- **Resolution**: 1080x1920 (9:16 aspect ratio)
- **Frame Rate**: Inherits from source clips (typically 30fps or 60fps)
- **Codec**: H.264 (libx264)
- **Bitrate**: Adaptive based on source quality
- **Audio**: AAC, preserved from source clips

### Platform Compatibility

The output is optimized for:

| Platform | Max Duration | Recommended Specs |
|----------|--------------|-------------------|
| YouTube Shorts | 60 seconds | 9:16, 1080x1920 ✓ |
| TikTok | 10 minutes | 9:16, 1080x1920 ✓ |
| Instagram Reels | 90 seconds | 9:16, 1080x1920 ✓ |

## Tips for Best Results

1. **Keep it Short** - Aim for 15-30 seconds for maximum engagement
2. **Strong Opening** - Use your best move in the first 2 seconds
3. **Beat Alignment** - Time your cuts to match musical beats
4. **Consistent Quality** - Use clips with similar lighting and resolution
5. **Test Often** - Use `--dry-run` to validate configurations quickly

## Next Steps

- 📊 Review [Configuration Guide](configuration.md) for advanced options
- 🎨 Explore [Advanced Features](advanced-features.md)
- 🧪 Check [Testing Guide](testing.md) to ensure quality
- ❓ See [FAQ](faq.md) for common questions
