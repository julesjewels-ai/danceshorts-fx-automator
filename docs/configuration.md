# Configuration Guide

## Overview

This guide provides comprehensive documentation for configuring **DanceShorts FX Automator** through its JSON configuration files.

## Configuration Files

### 1. veo_instructions.json

This file defines the video editing instructions, including which clips to use and how to sequence them.

#### Schema

```json
{
  "scenes": [
    {
      "id": <integer>,
      "source": "<string>",
      "start": <float>,
      "duration": <float>
    }
  ]
}
```

#### Field Reference

##### scenes (array, required)

An array of scene objects that define the video structure.

##### Scene Object Properties

| Property | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `id` | integer | Yes | Unique scene identifier. Determines processing order (ascending). | `1` |
| `source` | string | Yes | Path to source video file (relative or absolute). | `"clips/dance.mp4"` |
| `start` | float | Yes | Start timestamp in seconds within the source file. | `2.5` |
| `duration` | float | Yes | Duration in seconds to extract from the source. | `5.0` |

#### Examples

**Basic Configuration:**

```json
{
  "scenes": [
    {
      "id": 1,
      "source": "intro.mp4",
      "start": 0,
      "duration": 3
    },
    {
      "id": 2,
      "source": "main.mp4",
      "start": 1.5,
      "duration": 8
    }
  ]
}
```

**Multi-Clip Sequence:**

```json
{
  "scenes": [
    {
      "id": 1,
      "source": "clips/warmup.mp4",
      "start": 5.2,
      "duration": 2.8
    },
    {
      "id": 2,
      "source": "clips/performance.mp4",
      "start": 0,
      "duration": 12.5
    },
    {
      "id": 3,
      "source": "clips/finale.mp4",
      "start": 3.1,
      "duration": 4.3
    },
    {
      "id": 4,
      "source": "clips/credits.mp4",
      "start": 0,
      "duration": 2
    }
  ]
}
```

**Reusing Source Clips:**

```json
{
  "scenes": [
    {
      "id": 1,
      "source": "master_take.mp4",
      "start": 0,
      "duration": 3
    },
    {
      "id": 2,
      "source": "other_angle.mp4",
      "start": 2,
      "duration": 5
    },
    {
      "id": 3,
      "source": "master_take.mp4",
      "start": 10,
      "duration": 4
    }
  ]
}
```

#### Best Practices

1. **Sequential IDs** - Number scenes sequentially (1, 2, 3...) for clarity
2. **Precise Timing** - Use decimal values (e.g., `2.5`) for accurate cuts
3. **Verify Sources** - Ensure all source files exist before running
4. **Reasonable Durations** - Keep total duration under 60 seconds for Shorts
5. **Buffer Zones** - Leave 0.5s buffer at clip boundaries to avoid artifacts

---

### 2. metadata_options.json

This file defines text overlay styles and formatting options.

#### Schema

```json
{
  "options": {
    "<option_id>": {
      "style": "<string>",
      "font": "<string>",
      "color": "<string>",
      ... additional properties
    }
  }
}
```

#### Field Reference

##### options (object, required)

A dictionary of style options indexed by numeric string keys.

##### Option Object Properties

| Property | Type | Required | Description | Default |
|----------|------|----------|-------------|---------|
| `style` | string | Yes | Display name for the style | - |
| `font` | string | Yes | Font family name | `"Arial"` |
| `color` | string | No | Text color (name or hex) | `"white"` |
| `size` | integer | No | Font size in pixels | `72` |
| `position` | string | No | Overlay position | `"bottom"` |

#### Examples

**Minimal Styles:**

```json
{
  "options": {
    "1": {
      "style": "Minimal",
      "font": "Arial"
    },
    "2": {
      "style": "Recommended",
      "font": "Impact",
      "color": "yellow"
    }
  }
}
```

**Rich Styles with Extended Properties:**

```json
{
  "options": {
    "1": {
      "style": "Subtle",
      "font": "Helvetica Neue",
      "color": "#FFFFFF",
      "size": 48,
      "position": "bottom",
      "opacity": 0.8
    },
    "2": {
      "style": "Bold",
      "font": "Impact",
      "color": "#FFD700",
      "size": 72,
      "position": "center",
      "stroke": "#000000",
      "stroke_width": 2
    },
    "3": {
      "style": "Elegant",
      "font": "Georgia",
      "color": "white",
      "size": 56,
      "position": "top",
      "shadow": true
    }
  }
}
```

**Platform-Specific Styles:**

```json
{
  "options": {
    "1": {
      "style": "TikTok Style",
      "font": "Montserrat",
      "color": "#FE2C55",
      "size": 64,
      "position": "bottom"
    },
    "2": {
      "style": "Instagram Reel",
      "font": "Arial Black",
      "color": "#E1306C",
      "size": 68,
      "position": "center"
    },
    "3": {
      "style": "YouTube Shorts",
      "font": "Roboto",
      "color": "#FF0000",
      "size": 60,
      "position": "bottom"
    }
  }
}
```

#### Style Selection Logic

**Default Behavior:**
- The system **always selects Option 2** by default
- If Option 2 is missing, it falls back to the first available option

**To Change Default:**

Modify `src/core/app.py`, line 57:

```python
# Change '2' to your desired option
if '1' in options_data:  # Changed from '2' to '1'
    self.selected_style = options_data['1']
```

---

## Validation

### Automatic Validation

The automator validates configurations on load:

1. **File Existence** - Checks if JSON files exist
2. **JSON Syntax** - Validates proper JSON formatting
3. **Required Fields** - Ensures all mandatory fields are present

### Manual Validation

Test your configuration before rendering:

```bash
python main.py --dry-run
```

This runs all validation steps without rendering video.

---

## Environment Variables

Currently, the automator uses hardcoded configuration file paths. For flexibility, consider setting:

```bash
export VEO_INSTRUCTIONS="path/to/custom_instructions.json"
export METADATA_OPTIONS="path/to/custom_options.json"
```

*(Note: This requires code modification to implement)*

---

## Configuration Templates

### Template 1: Quick Dance Clip (15s)

**veo_instructions.json:**
```json
{
  "scenes": [
    {
      "id": 1,
      "source": "dance_clip.mp4",
      "start": 0,
      "duration": 15
    }
  ]
}
```

**metadata_options.json:**
```json
{
  "options": {
    "2": {
      "style": "Recommended",
      "font": "Impact",
      "color": "yellow"
    }
  }
}
```

### Template 2: Three-Part Story (30s)

**veo_instructions.json:**
```json
{
  "scenes": [
    {
      "id": 1,
      "source": "setup.mp4",
      "start": 0,
      "duration": 8
    },
    {
      "id": 2,
      "source": "buildup.mp4",
      "start": 2,
      "duration": 12
    },
    {
      "id": 3,
      "source": "payoff.mp4",
      "start": 1,
      "duration": 10
    }
  ]
}
```

---

## Troubleshooting

### Common Configuration Errors

**Error:** `FileNotFoundError: veo_instructions.json not found`
- **Cause:** Missing configuration file
- **Fix:** Ensure file exists in project root or run app once to auto-generate

**Error:** `JSONDecodeError`
- **Cause:** Invalid JSON syntax
- **Fix:** Validate JSON using [JSONLint](https://jsonlint.com/)

**Error:** `KeyError: 'scenes'`
- **Cause:** Missing required 'scenes' array
- **Fix:** Ensure your JSON has a top-level "scenes" array

**Error:** `Source file not found`
- **Cause:** Invalid path in scene source
- **Fix:** Use absolute paths or verify relative paths from project root

---

## Advanced Configuration

### Future Configuration Options

Planned features for future releases:

- **Transition Types** - Cross-fade, cut, wipe
- **Audio Mixing** - Background music, volume controls
- **Text Content** - Custom overlay text per scene
- **Filters** - Color grading, effects
- **Export Presets** - Platform-specific optimization

To request features, please [open an issue](https://github.com/julesjewels-ai/danceshorts-fx-automator/issues).

---

## See Also

- [User Guide](user-guide.md) - Step-by-step usage instructions
- [Advanced Features](advanced-features.md) - Power user tips
- [API Reference](api-reference.md) - Python API documentation
