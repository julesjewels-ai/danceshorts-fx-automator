# DanceShorts FX Automator

A Python-based video editing pipeline that automates post-production for dance videos. It parses 'veo_instructions.json' to stitch scenes and 'metadata_options.json' to apply beat-synced text overlays. It defaults to the 'Recommended' style (Option 2) and renders a vertical 9:16 MP4 suitable for YouTube Shorts.

**NEW:** Now supports batch processing to process multiple videos at once!

## Tech Stack

- Python
- MoviePy
- Pillow
- Pandas
- JSON
- FFmpeg

## Features

- JSON Metadata Parsing
- Automated Scene Stitching
- Beat-Synced Text Overlays
- 9:16 Vertical Formatting
- Cross-Dissolve Transitions
- **Batch Processing** - Process multiple videos in one command

## Quick Start

```bash
# Clone and setup
git clone https://github.com/julesjewels-ai/danceshorts-fx-automator.git
cd danceshorts-fx-automator
make install

# Run single video (original mode)
make run

# Run batch processing
python main.py --batch
```

## Setup

```bash
pip install -r requirements.txt
```

## Usage

### Single Video Mode (Original)

Process a single video using JSON files in the root directory:

```bash
make install && make run
# or
python main.py
```

### Batch Processing Mode

Process multiple videos organized in project folders:

```bash
python main.py --batch
```

#### Batch Folder Structure

Organize your videos in the `inputs/` directory, with one subfolder per project:

```
inputs/
├── video_project_1/
│   ├── veo_instructions.json
│   ├── metadata_options.json
│   ├── style_options.json
│   ├── clip1.mp4
│   ├── clip2.mp4
│   └── custom_audio.mp3 (optional)
├── video_project_2/
│   ├── veo_instructions.json
│   ├── metadata_options.json
│   ├── style_options.json
│   └── ...
```

**Required files per project folder:**
- `veo_instructions.json` - Scene definitions
- `metadata_options.json` - Text overlays and SEO metadata
- `style_options.json` - Visual styling

**Video and audio files** should be placed in the same folder and referenced with relative paths in `veo_instructions.json`.

#### Batch Output

Rendered videos will be saved to `outputs/`:

```
outputs/
├── video_project_1_final.mp4
├── video_project_2_final.mp4
└── video_project_3_final.mp4
```

#### Batch Options

```bash
# Use custom input/output directories
python main.py --batch --input-dir my_videos --output-dir renders

# Dry run (simulate without rendering)
python main.py --batch --dry-run
```

## Development

```bash
make install  # Create venv and install dependencies
make run      # Run the application
make test     # Run tests
make clean    # Remove cache files
```

## Testing

```bash
pytest tests/ -v
```

## Examples

See the `inputs/example_project/` folder for a complete example of the batch processing structure.
