# Example Project Folder

This folder demonstrates the structure required for batch processing with DanceShorts FX Automator.

## Required Files

Each project folder must contain:

1. **veo_instructions.json** - Scene definitions and clip references
2. **metadata_options.json** - Text overlays and SEO metadata
3. **style_options.json** - Visual styling for text overlays

## Video Clips

Place your video clips (`.mp4`, `.mov`, etc.) in this folder and reference them in `veo_instructions.json` using relative paths.

Example:
```json
{
  "scenes": [
    {
      "id": 1,
      "source": "clip1.mp4",
      "start": 0,
      "duration": 2
    }
  ]
}
```

## Custom Audio (Optional)

If you want to use custom audio, place the audio file in this folder and reference it in `veo_instructions.json`:
```json
{
  "audio_source": "custom_music.mp3",
  "scenes": [...]
}
```
