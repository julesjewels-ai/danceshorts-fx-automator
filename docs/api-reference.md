# API Reference

## Overview

This document provides detailed API documentation for the **DanceShorts FX Automator** Python modules.

---

## Module: `src.core.app`

The core application logic for video processing.

### Class: `DanceShortsAutomator`

Main class that orchestrates the video editing pipeline.

```python
class DanceShortsAutomator:
    """
    Core logic for the video editing pipeline.
    
    Parses instructions and metadata to stitch scenes and apply overlays
    specifically tuned for YouTube Shorts (9:16 aspect ratio).
    """
```

#### Constructor

```python
def __init__(self, instruction_file: str, options_file: str)
```

Initialize the automator with configuration file paths.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `instruction_file` | `str` | Path to the veo_instructions.json file |
| `options_file` | `str` | Path to the metadata_options.json file |

**Returns:** `None`

**Example:**

```python
from src.core.app import DanceShortsAutomator

app = DanceShortsAutomator(
    instruction_file='veo_instructions.json',
    options_file='metadata_options.json'
)
```

---

#### Method: `load_configurations()`

```python
def load_configurations(self) -> None
```

Loads and validates JSON configuration files.

**Parameters:** None

**Returns:** `None`

**Raises:**

| Exception | Condition |
|-----------|-----------|
| `FileNotFoundError` | If instruction_file or options_file doesn't exist |
| `JSONDecodeError` | If configuration files contain invalid JSON |

**Side Effects:**
- Populates `self.instructions` with scene data
- Populates `self.options` with style options
- Selects and stores the default style in `self.selected_style`
- Logs configuration loading status

**Example:**

```python
app = DanceShortsAutomator('veo_instructions.json', 'metadata_options.json')
app.load_configurations()  # Loads and validates configs

# Access loaded data
print(app.instructions)  # {'scenes': [...]}
print(app.selected_style)  # {'style': 'Recommended', ...}
```

---

#### Method: `_apply_style_logic()` (Private)

```python
def _apply_style_logic(self) -> None
```

Selects the 'Recommended' style (Option 2) by default.

**Parameters:** None

**Returns:** `None`

**Behavior:**
- Always attempts to select Option 2 from metadata_options.json
- Falls back to first available option if Option 2 doesn't exist
- Logs the selected style name

**Side Effects:**
- Sets `self.selected_style` to the chosen option dictionary

**Note:** This is a private method automatically called by `load_configurations()`.

---

#### Method: `process_pipeline()`

```python
def process_pipeline(self, dry_run: bool = False) -> None
```

Executes the complete video processing pipeline.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `dry_run` | `bool` | `False` | If True, simulates processing without rendering |

**Returns:** `None`

**Pipeline Steps:**
1. **Scene Stitching** - Concatenates video clips with transitions
2. **Overlay Application** - Applies beat-synced text overlays
3. **Rendering** - Exports final 9:16 MP4 video

**Output:**
- Creates `final_dance_short.mp4` in the current directory
- In dry-run mode, only logs actions without creating video file

**Example:**

```python
# Standard execution
app.process_pipeline()

# Dry run (testing)
app.process_pipeline(dry_run=True)
```

---

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `instruction_file` | `str` | Path to scene instruction JSON |
| `options_file` | `str` | Path to style options JSON |
| `instructions` | `Dict[str, Any]` | Loaded scene instructions |
| `options` | `Dict[str, Any]` | Loaded style options |
| `selected_style` | `Dict[str, Any]` | The chosen text overlay style |

---

## Module: `main`

Entry point for the command-line interface.

### Function: `setup_logging()`

```python
def setup_logging() -> None
```

Configures the logging system with standardized format.

**Configuration:**
- **Level:** INFO
- **Format:** `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Output:** Console (stdout)

**Example:**

```python
import logging
from main import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
logger.info("Application started")
```

---

### Function: `create_dummy_inputs_if_missing()`

```python
def create_dummy_inputs_if_missing() -> None
```

Generates sample JSON files if they don't exist.

**Behavior:**
- Creates `veo_instructions.json` with 2 sample scenes
- Creates `metadata_options.json` with 3 style presets
- Only creates files if they don't already exist
- Logs creation actions

**Use Case:**
Enables immediate execution for first-time users or testing.

---

### Function: `main()`

```python
def main() -> None
```

Main entry point for the CLI application.

**Command-Line Arguments:**

| Argument | Type | Description |
|----------|------|-------------|
| `--version` | flag | Display version and exit |
| `--dry-run` | flag | Simulate processing without rendering |

**Exit Codes:**

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Error occurred (see logs) |

**Example Usage:**

```bash
# Standard execution
python main.py

# Dry run mode
python main.py --dry-run

# Show version
python main.py --version
```

---

## Type Definitions

### Scene Object

```python
{
    "id": int,           # Unique scene identifier
    "source": str,       # Path to source video file
    "start": float,      # Start timestamp in seconds
    "duration": float    # Duration in seconds
}
```

### Style Option Object

```python
{
    "style": str,        # Display name
    "font": str,         # Font family name
    "color": str,        # Color name or hex code
    # Additional optional properties...
}
```

---

## Error Handling

### Exception Types

| Exception | When Raised | Suggested Action |
|-----------|-------------|------------------|
| `FileNotFoundError` | Configuration file missing | Check file paths, run auto-generator |
| `JSONDecodeError` | Invalid JSON syntax | Validate JSON at jsonlint.com |
| `KeyError` | Missing required field | Verify schema compliance |
| `Exception` | General failure | Check logs for details |

### Error Recovery

```python
from src.core.app import DanceShortsAutomator
import logging

try:
    app = DanceShortsAutomator('veo_instructions.json', 'metadata_options.json')
    app.load_configurations()
    app.process_pipeline()
except FileNotFoundError as e:
    logging.error(f"Configuration file missing: {e}")
    # Regenerate default configs
    from main import create_dummy_inputs_if_missing
    create_dummy_inputs_if_missing()
except Exception as e:
    logging.error(f"Processing failed: {e}")
    raise
```

---

## Usage Examples

### Basic Programmatic Usage

```python
import logging
from src.core.app import DanceShortsAutomator

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize automator
app = DanceShortsAutomator(
    instruction_file='my_scenes.json',
    options_file='my_styles.json'
)

# Load configurations
app.load_configurations()

# Process video
app.process_pipeline(dry_run=False)

print(f"Video saved as: final_dance_short.mp4")
```

### Custom Processing Pipeline

```python
from src.core.app import DanceShortsAutomator

class CustomAutomator(DanceShortsAutomator):
    """Extended automator with custom logic."""
    
    def process_pipeline(self, dry_run=False):
        """Override with custom processing."""
        scenes = self.instructions.get('scenes', [])
        
        # Custom pre-processing
        self.validate_scenes(scenes)
        
        # Call parent implementation
        super().process_pipeline(dry_run)
        
        # Custom post-processing
        self.apply_custom_filters()
    
    def validate_scenes(self, scenes):
        """Custom validation logic."""
        for scene in scenes:
            if scene['duration'] > 30:
                raise ValueError(f"Scene {scene['id']} exceeds max duration")
    
    def apply_custom_filters(self):
        """Apply additional filters."""
        print("Applying custom color grading...")

# Usage
app = CustomAutomator('veo_instructions.json', 'metadata_options.json')
app.load_configurations()
app.process_pipeline()
```

---

## Integration Guide

### Using as a Library

Install in another project:

```bash
pip install -e /path/to/danceshorts-fx-automator
```

Import and use:

```python
from src.core.app import DanceShortsAutomator

def process_dance_video(scenes_config, style_config):
    """Process a dance video with custom configs."""
    app = DanceShortsAutomator(scenes_config, style_config)
    app.load_configurations()
    app.process_pipeline()
    return "final_dance_short.mp4"
```

---

## See Also

- [User Guide](user-guide.md) - High-level usage instructions
- [Configuration Guide](configuration.md) - JSON schema documentation
- [Testing Guide](testing.md) - Testing strategies
