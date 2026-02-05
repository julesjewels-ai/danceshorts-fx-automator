# Getting Started with DanceShorts FX Automator

## Overview

**DanceShorts FX Automator** is a Python-based video editing pipeline designed to automate post-production for dance videos. It intelligently parses JSON configuration files to stitch scenes together and apply beat-synced text overlays, producing vertical 9:16 MP4 videos optimized for YouTube Shorts.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **FFmpeg** - Required for video processing
  - macOS: `brew install ffmpeg`
  - Ubuntu: `sudo apt-get install ffmpeg`
  - Windows: [Download FFmpeg](https://ffmpeg.org/download.html)
- **Git** - [Download Git](https://git-scm.com/downloads)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/julesjewels-ai/danceshorts-fx-automator.git
cd danceshorts-fx-automator
```

### 2. Install Dependencies

Using the Makefile (recommended):

```bash
make install
```

Or manually:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Run with Default Settings

The application automatically creates sample configuration files if they don't exist:

```bash
make run
```

Or directly with Python:

```bash
python main.py
```

### Dry Run Mode

Test the pipeline without rendering video:

```bash
python main.py --dry-run
```

### Check Version

```bash
python main.py --version
```

## Project Structure

```
danceshorts-fx-automator/
├── main.py                      # CLI entry point
├── src/
│   └── core/
│       └── app.py              # Core video processing logic
├── veo_instructions.json       # Scene configuration
├── metadata_options.json       # Text overlay styles
├── requirements.txt            # Python dependencies
├── Makefile                    # Build automation
├── tests/                      # Test suite
└── docs/                       # Documentation
```

## Configuration Files

### `veo_instructions.json`

Defines the scenes to be stitched together:

```json
{
  "scenes": [
    {
      "id": 1,
      "source": "clip1.mp4",
      "start": 0,
      "duration": 5
    },
    {
      "id": 2,
      "source": "clip2.mp4",
      "start": 0,
      "duration": 5
    }
  ]
}
```

### `metadata_options.json`

Defines text overlay styles (defaults to Option 2 - "Recommended"):

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
    },
    "3": {
      "style": "Cinematic",
      "font": "Serif"
    }
  }
}
```

## Output

The processed video is saved as:
- **Filename**: `final_dance_short.mp4`
- **Format**: MP4 (H.264)
- **Aspect Ratio**: 9:16 (Vertical)
- **Optimized for**: YouTube Shorts, TikTok, Instagram Reels

## Next Steps

- 📖 Read the [User Guide](user-guide.md) for detailed usage instructions
- ⚙️ Check the [Configuration Guide](configuration.md) for advanced options
- 🧪 See [Testing Guide](testing.md) to run tests
- 🚀 Review [Advanced Features](advanced-features.md) for power user tips

## Troubleshooting

### Common Issues

**Issue**: `FileNotFoundError: veo_instructions.json not found`
- **Solution**: Run the application once to auto-generate sample files, or create the files manually

**Issue**: FFmpeg not found
- **Solution**: Install FFmpeg using the instructions in Prerequisites

**Issue**: Virtual environment not activating
- **Solution**: Ensure you're using the correct activation command for your OS

## Getting Help

- 📝 Check the [FAQ](faq.md)
- 🐛 Report issues on [GitHub Issues](https://github.com/julesjewels-ai/danceshorts-fx-automator/issues)
- 💬 Join our community discussions

## License

This project is licensed under the MIT License - see the LICENSE file for details.
