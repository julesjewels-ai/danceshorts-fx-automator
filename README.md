# DanceShorts FX Automator

A Python-based video editing pipeline that automates post-production for dance videos. It parses 'veo_instructions.json' to stitch scenes and 'metadata_options.json' to apply beat-synced text overlays. It defaults to the 'Recommended' style (Option 2) and renders a vertical 9:16 MP4 suitable for YouTube Shorts.

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

## Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd danceshorts-fx-automator
make install

# Run the application
make run
```

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
make install && make run
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
