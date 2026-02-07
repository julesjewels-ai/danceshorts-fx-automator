# DanceShorts FX Automator - Documentation

Welcome to the **DanceShorts FX Automator** documentation! This guide will help you automate the creation of professional dance videos optimized for YouTube Shorts, TikTok, and Instagram Reels.

## 📚 Documentation Index

### 🎨 Visual Guide (Start Here!)

- **[Visual Guide](visual-guide.md)** - **Perfect for non-technical users!**
  - See what the tool does with images and diagrams
  - Understand the workflow visually
  - No technical jargon!

### Getting Started

- **[Getting Started Guide](getting-started.md)** - Installation, prerequisites, and quick start
  - Installation instructions
  - Prerequisites and dependencies
  - Quick start tutorial
  - First run walkthrough

### Usage Guides

- **[User Guide](user-guide.md)** - Comprehensive step-by-step instructions
  - Complete workflow overview
  - Scene configuration
  - Style customization
  - Best practices and tips

- **[Configuration Guide](configuration.md)** - JSON schema and advanced configuration
  - veo_instructions.json reference
  - metadata_options.json reference
  - Configuration templates
  - Validation and troubleshooting

### Reference

- **[API Reference](api-reference.md)** - Python API documentation
  - DanceShortsAutomator class
  - Method signatures
  - Type definitions
  - Code examples

- **[FAQ](faq.md)** - Frequently asked questions
  - Common issues and solutions
  - Best practices
  - Platform-specific tips
  - Advanced usage

## 🚀 Quick Links

### For Beginners

1. **[Installation](getting-started.md#installation)** - Get up and running
2. **[Quick Start](getting-started.md#quick-start)** - Your first video in 5 minutes
3. **[Basic Configuration](user-guide.md#step-2-configure-scene-instructions)** - Understanding JSON configs

### For Power Users

1. **[Advanced Configuration](configuration.md#advanced-configuration)** - Custom setups
2. **[API Integration](api-reference.md#integration-guide)** - Use as a Python library
3. **[Extending the Tool](api-reference.md#custom-processing-pipeline)** - Build custom features

### Troubleshooting

1. **[Common Errors](faq.md#errors--troubleshooting)** - Solutions to frequent issues
2. **[Configuration Validation](configuration.md#validation)** - Verify your configs
3. **[Getting Help](getting-started.md#getting-help)** - Support resources

## 📖 Documentation Overview

### What This Tool Does

**DanceShorts FX Automator** automates the post-production workflow for dance videos:

1. **Scene Stitching** - Concatenate multiple video clips seamlessly
2. **Text Overlays** - Apply beat-synced text with customizable styles
3. **Format Optimization** - Export as vertical 9:16 MP4 for social media

**Input:**
- Raw video clips (MP4, MOV, AVI, etc.)
- JSON configuration files (scenes and styles)

**Output:**
- Polished 9:16 vertical video (`final_dance_short.mp4`)
- Optimized for YouTube Shorts, TikTok, Instagram Reels

### Key Features

✅ **Automated Scene Stitching** - Define clips and let the tool combine them  
✅ **Beat-Synced Overlays** - Text overlays timed to music beats  
✅ **Cross-Dissolve Transitions** - Smooth transitions between scenes  
✅ **9:16 Vertical Format** - Optimized for mobile-first platforms  
✅ **Customizable Styles** - Three preset overlay styles (Minimal, Recommended, Cinematic)  
✅ **Dry-Run Mode** - Test configurations without rendering  
✅ **Auto-Configuration** - Generates sample configs for immediate use  

### Tech Stack

- **Python** - Core application logic
- **MoviePy** - Video editing and rendering
- **Pillow** - Image processing for overlays
- **FFmpeg** - Video codec and format handling
- **Pandas** - Data manipulation
- **JSON** - Configuration format

## 🎯 Choose Your Path

### I'm New to This Tool

**Start here:**
1. Read the [Getting Started Guide](getting-started.md)
2. Follow the [Quick Start](getting-started.md#quick-start) tutorial
3. Try the [User Guide](user-guide.md) step-by-step workflow

### I Want to Create My First Video

**Follow this workflow:**
1. [Install the tool](getting-started.md#installation)
2. [Prepare your video clips](user-guide.md#step-1-prepare-your-video-clips)
3. [Configure scenes](user-guide.md#step-2-configure-scene-instructions)
4. [Run the automator](user-guide.md#step-4-run-the-automator)

### I Need to Troubleshoot

**Check these resources:**
1. [FAQ - Errors & Troubleshooting](faq.md#errors--troubleshooting)
2. [Configuration Validation](configuration.md#validation)
3. [Common Issues](getting-started.md#troubleshooting)

### I Want to Customize or Extend

**Explore these topics:**
1. [Configuration Guide](configuration.md) - Advanced JSON schemas
2. [API Reference](api-reference.md) - Python API details
3. [Custom Processing Pipeline](api-reference.md#custom-processing-pipeline)

### I Want to Integrate This Into My Workflow

**See:**
1. [Using as a Library](api-reference.md#using-as-a-library)
2. [Batch Processing](faq.md#can-i-batch-process-multiple-videos)
3. [Programmatic Usage](api-reference.md#usage-examples)

## 🎬 Example Workflow

Here's a typical workflow to create a 30-second dance short:

### 1. Prepare Clips (5 minutes)

```bash
# Organize your clips
mkdir dance_project
cp ~/Videos/dance_intro.mp4 dance_project/
cp ~/Videos/dance_main.mp4 dance_project/
cp ~/Videos/dance_outro.mp4 dance_project/
```

### 2. Configure Scenes (3 minutes)

Edit `veo_instructions.json`:

```json
{
  "scenes": [
    {"id": 1, "source": "dance_project/dance_intro.mp4", "start": 0, "duration": 5},
    {"id": 2, "source": "dance_project/dance_main.mp4", "start": 2, "duration": 20},
    {"id": 3, "source": "dance_project/dance_outro.mp4", "start": 1, "duration": 5}
  ]
}
```

### 3. Process Video (2 minutes)

```bash
python main.py
```

**Output:** `final_dance_short.mp4` (30 seconds, 9:16 format)

### 4. Upload to Platform

The output is ready to upload directly to YouTube Shorts, TikTok, or Instagram Reels!

## 📊 Documentation Structure

```
docs/
├── README.md              # This file - documentation hub
├── getting-started.md     # Installation and setup
├── user-guide.md          # Step-by-step usage instructions
├── configuration.md       # JSON schema and advanced config
├── api-reference.md       # Python API documentation
└── faq.md                 # Frequently asked questions
```

## 🆘 Getting Help

### Documentation Not Clear?

- **[Open an issue](https://github.com/julesjewels-ai/danceshorts-fx-automator/issues)** - Request clarification
- **[Contribute improvements](../CONTRIBUTING.md)** - Help make docs better

### Found a Bug?

- **[Report it](https://github.com/julesjewels-ai/danceshorts-fx-automator/issues)** - Include steps to reproduce
- **[Check FAQ](faq.md#errors--troubleshooting)** - See if it's already solved

### Need a Feature?

- **[Request it](https://github.com/julesjewels-ai/danceshorts-fx-automator/issues)** - Describe your use case
- **[Contribute it](../CONTRIBUTING.md)** - Build and submit a PR

## 🔗 Additional Resources

- **[GitHub Repository](https://github.com/julesjewels-ai/danceshorts-fx-automator)** - Source code
- **[Issue Tracker](https://github.com/julesjewels-ai/danceshorts-fx-automator/issues)** - Bugs and features
- **[Project README](../README.md)** - Project overview

## 📝 Contributing to Documentation

Documentation improvements are always welcome! To contribute:

1. Fork the repository
2. Edit files in the `docs/` folder
3. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.

## 📄 License

This documentation is part of the DanceShorts FX Automator project, licensed under the MIT License.

---

**Ready to get started?** → [Installation Guide](getting-started.md)

**Need help?** → [FAQ](faq.md)

**Want to dive deep?** → [API Reference](api-reference.md)
