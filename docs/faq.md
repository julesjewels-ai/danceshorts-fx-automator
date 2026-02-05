# Frequently Asked Questions (FAQ)

## General Questions

### What is DanceShorts FX Automator?

**DanceShorts FX Automator** is a Python-based video editing pipeline that automates the creation of dance videos optimized for social media platforms like YouTube Shorts, TikTok, and Instagram Reels. It automatically stitches video clips, applies text overlays, and exports in the vertical 9:16 format.

### What platforms can I target with this tool?

The output is optimized for:
- **YouTube Shorts** (up to 60 seconds)
- **TikTok** (up to 10 minutes)
- **Instagram Reels** (up to 90 seconds)
- **Facebook Reels**
- Any platform supporting 9:16 vertical video

### Do I need video editing experience?

No! The tool is designed to automate the technical aspects. You just need to:
1. Provide video clips
2. Edit simple JSON configuration files
3. Run the command

---

## Installation & Setup

### What are the system requirements?

- **Python:** 3.8 or higher
- **FFmpeg:** Latest version
- **RAM:** 4GB minimum (8GB recommended)
- **Storage:** Varies based on source video sizes
- **OS:** Windows, macOS, or Linux

### How do I install FFmpeg?

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

**Verify installation:**
```bash
ffmpeg -version
```

### The installation fails with "No module named 'moviepy'"

Ensure you've activated the virtual environment and installed dependencies:

```bash
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

---

## Configuration

### Where are the configuration files?

Both files should be in the project root directory:
- `veo_instructions.json` - Defines video scenes
- `metadata_options.json` - Defines text overlay styles

### The app can't find my configuration files

Ensure:
1. Files are in the **project root** (same directory as `main.py`)
2. Filenames are **exactly** `veo_instructions.json` and `metadata_options.json`
3. Files contain **valid JSON** (test at [jsonlint.com](https://jsonlint.com/))

### Can I use custom filenames for configuration?

Currently, the filenames are hardcoded. To use custom names, modify `main.py`:

```python
app = DanceShortsAutomator(
    instruction_file='my_custom_instructions.json',
    options_file='my_custom_styles.json'
)
```

### How do I change the default text overlay style?

The system defaults to **Option 2** in `metadata_options.json`. To change:

**Option 1:** Modify Option 2 directly in the JSON file

**Option 2:** Edit `src/core/app.py` (line 57) to select a different option:
```python
if '1' in options_data:  # Changed from '2'
    self.selected_style = options_data['1']
```

---

## Video Processing

### What video formats are supported?

Input formats supported by FFmpeg:
- MP4 (recommended)
- MOV
- AVI
- MKV
- WebM

### Can I use clips with different resolutions?

Yes, but for best results:
- Use clips with **consistent resolution**
- The output will be scaled to 1080x1920 (9:16)
- Mixed resolutions may cause quality loss

### How long does processing take?

Processing time depends on:
- Total video duration
- Number of scenes
- Source video quality
- Computer performance

**Typical times:**
- 15-second video: 30-60 seconds
- 30-second video: 1-2 minutes
- 60-second video: 2-4 minutes

### The output video quality is poor

Try:
- Using higher-quality source clips
- Ensuring all clips have similar resolution
- Avoiding excessive compression on source files
- Using clips with consistent frame rates

### Can I add background music?

This feature is not yet implemented. Current workaround:
1. Process the video with the automator
2. Add music using a separate tool (iMovie, DaVinci Resolve, etc.)

---

## Errors & Troubleshooting

### Error: "FileNotFoundError: veo_instructions.json not found"

**Solution:**
Run the app once to auto-generate sample files:
```bash
python main.py
```

Or create the files manually using the templates in the [Configuration Guide](configuration.md).

### Error: "JSONDecodeError: Expecting property name"

**Cause:** Invalid JSON syntax

**Solution:**
1. Copy your JSON content
2. Paste into [jsonlint.com](https://jsonlint.com/)
3. Fix any syntax errors
4. Save the corrected version

### Error: "Source file not found: clip1.mp4"

**Cause:** The video file specified in `veo_instructions.json` doesn't exist

**Solution:**
- Verify the file path is correct
- Use **absolute paths** for files outside the project directory
- Use **relative paths** from the project root for files inside

### The video renders but is completely black

**Possible causes:**
1. Source files are corrupted
2. Start time exceeds video duration
3. Codec compatibility issues

**Solutions:**
1. Verify source videos play correctly
2. Check `start` + `duration` doesn't exceed clip length
3. Re-encode source clips to H.264 MP4

### Error: "Permission denied" when writing output

**Cause:** No write permissions or file is open elsewhere

**Solution:**
- Ensure `final_dance_short.mp4` is not open in another program
- Check folder write permissions
- Run with appropriate permissions

---

## Features & Capabilities

### Can I customize the output filename?

Currently hardcoded as `final_dance_short.mp4`. To change, edit `src/core/app.py` (line 80):

```python
output_filename = "my_custom_name.mp4"
```

### Can I add custom text to overlays?

Not yet implemented in the current version. This is a planned feature for future releases.

### Can I change the aspect ratio?

The tool is optimized for 9:16 vertical video. To support other ratios, you'll need to modify the rendering logic in `src/core/app.py`.

### Does it support transitions between scenes?

Yes! The tool uses **cross-dissolve transitions** by default. Custom transition types (wipes, cuts, etc.) are planned for future versions.

### Can I preview before rendering?

Use dry-run mode to validate configurations:
```bash
python main.py --dry-run
```

This simulates processing without creating the video file.

---

## Best Practices

### How many scenes should I include?

For optimal engagement:
- **15-second video:** 2-4 scenes
- **30-second video:** 4-6 scenes
- **60-second video:** 6-10 scenes

Avoid too many quick cuts (viewer fatigue) or too few (static/boring).

### What's the ideal video duration?

**Platform recommendations:**
- **TikTok:** 15-30 seconds (highest engagement)
- **Instagram Reels:** 15-30 seconds
- **YouTube Shorts:** 30-60 seconds

**General rule:** Shorter is better. Front-load your best content.

### How do I sync cuts to music beats?

1. Use audio analysis software to find beat timestamps
2. Align scene `start` times with beat markers
3. Use quick cuts (2-4 seconds) for high-energy sections
4. Use longer scenes (5-8 seconds) for slower sections

### Should I use the Recommended style?

**Option 2 (Recommended)** uses:
- **Font:** Impact (bold, high contrast)
- **Color:** Yellow (high visibility)

This is ideal for:
- High-energy dance content
- Platforms with lots of competing content
- Maximizing text readability on mobile

Consider **Minimal** or **Cinematic** for:
- Artistic/choreography showcases
- Professional dance portfolios
- When text is secondary to visuals

---

## Advanced Usage

### Can I run this programmatically from my own code?

Yes! Import and use as a Python library:

```python
from src.core.app import DanceShortsAutomator

app = DanceShortsAutomator('scenes.json', 'styles.json')
app.load_configurations()
app.process_pipeline(dry_run=False)
```

See the [API Reference](api-reference.md) for details.

### Can I batch process multiple videos?

Create a script to iterate through configurations:

```python
import os
from src.core.app import DanceShortsAutomator

projects = ['project1', 'project2', 'project3']

for project in projects:
    instructions = f'{project}/veo_instructions.json'
    options = f'{project}/metadata_options.json'
    
    app = DanceShortsAutomator(instructions, options)
    app.load_configurations()
    app.process_pipeline()
    
    # Rename output
    os.rename('final_dance_short.mp4', f'{project}/output.mp4')
```

### Can I extend the DanceShortsAutomator class?

Absolutely! Subclass to add custom functionality:

```python
from src.core.app import DanceShortsAutomator

class MyCustomAutomator(DanceShortsAutomator):
    def process_pipeline(self, dry_run=False):
        # Add custom pre-processing
        self.my_custom_function()
        
        # Call parent
        super().process_pipeline(dry_run)
        
        # Add post-processing
        self.apply_custom_filters()
    
    def my_custom_function(self):
        print("Custom logic here!")
```

---

## Contributing & Support

### How do I report a bug?

1. Check if the issue already exists in [GitHub Issues](https://github.com/julesjewels-ai/danceshorts-fx-automator/issues)
2. If not, create a new issue with:
   - Detailed description
   - Steps to reproduce
   - Error messages/logs
   - System information (OS, Python version)

### Can I request features?

Yes! Open a feature request on [GitHub Issues](https://github.com/julesjewels-ai/danceshorts-fx-automator/issues) with:
- Clear description of the feature
- Use cases
- Examples or mockups (if applicable)

### How can I contribute code?

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.

---

## See Also

- [Getting Started](getting-started.md) - Installation and quick start
- [User Guide](user-guide.md) - Detailed usage instructions
- [Configuration Guide](configuration.md) - JSON schema reference
- [API Reference](api-reference.md) - Python API documentation
