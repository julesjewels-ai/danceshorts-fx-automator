import json
import os
import logging
from typing import Dict, Any, List
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
import moviepy.video.fx as vfx

logger = logging.getLogger(__name__)

class DanceShortsAutomator:
    """
    Core logic for the video editing pipeline.
    
    Parses instructions and metadata to stitch scenes and apply overlays
    specifically tuned for YouTube Shorts (9:16 aspect ratio).
    """

    def __init__(self, instruction_file: str, options_file: str):
        """
        Initialize the automator.

        Args:
            instruction_file (str): Path to veo_instructions.json
            options_file (str): Path to metadata_options.json
        """
        self.instruction_file = instruction_file
        self.options_file = options_file
        self.instructions: Dict[str, Any] = {}
        self.options: Dict[str, Any] = {}
        self.selected_style: Dict[str, Any] = {}

    def load_configurations(self) -> None:
        """
        Loads and validates JSON configuration files.
        """
        if not os.path.exists(self.instruction_file):
            raise FileNotFoundError(f"{self.instruction_file} not found.")
        
        if not os.path.exists(self.options_file):
            raise FileNotFoundError(f"{self.options_file} not found.")

        with open(self.instruction_file, 'r') as f:
            self.instructions = json.load(f)
            logger.info(f"Loaded instructions from {self.instruction_file}")

        with open(self.options_file, 'r') as f:
            self.options = json.load(f)
            logger.info(f"Loaded options from {self.options_file}")

        self._apply_style_logic()

    def _apply_style_logic(self) -> None:
        """
        Selects the 'Recommended' style (Option 2) by default.
        """
        recommended_id = self.options.get('recommended')
        options_data = self.options.get('options', [])

        selected = None

        # Handle list of options (new requirement)
        if isinstance(options_data, list):
            for opt in options_data:
                if opt.get('id') == recommended_id:
                    selected = opt
                    break
        # Handle dict of options (legacy/fallback)
        elif isinstance(options_data, dict):
            if str(recommended_id) in options_data:
                selected = options_data[str(recommended_id)]

        if selected:
            self.selected_style = selected
            logger.info(f"Selected Style: {self.selected_style.get('style', 'Unknown')} (Option {recommended_id})")
        else:
            logger.warning("Recommended option not found. Falling back to first available option.")
            if options_data:
                if isinstance(options_data, list):
                    self.selected_style = options_data[0]
                else:
                    self.selected_style = next(iter(options_data.values()))
            else:
                self.selected_style = {}

    def _stitch_scenes(self) -> VideoFileClip:
        """
        Stitches scenes together with cross-dissolve transitions.
        """
        scenes_data = self.instructions.get('scenes', [])

        # Sort by 'order' if available, otherwise 'id', otherwise keep order
        scenes_data = sorted(scenes_data, key=lambda x: x.get('order', x.get('id', 0)))

        clips = []

        for i, scene in enumerate(scenes_data):
            source = scene.get('clip_path') or scene.get('source')

            if not source or not os.path.exists(source):
                logger.warning(f"Source file {source} not found. Skipping.")
                continue

            clip = VideoFileClip(source)

            # Use explicit start/duration if provided, otherwise use full clip
            if 'start' in scene and 'duration' in scene:
                start = scene.get('start', 0)
                duration = scene.get('duration')
                clip = clip.subclipped(start, start + duration)
            elif 'duration' in scene:
                clip = clip.subclipped(0, scene['duration'])

            # Ensure 9:16 aspect ratio (1080x1920) via Crop-to-Fill
            target_w, target_h = 1080, 1920
            target_ratio = target_w / target_h
            current_ratio = clip.w / clip.h

            if current_ratio > target_ratio:
                # Source is wider than target (e.g. 16:9 vs 9:16)
                # Resize by height to match target height, then crop width
                clip = clip.resized(height=target_h)
                clip = clip.cropped(width=target_w, height=target_h, x_center=clip.w / 2, y_center=clip.h / 2)
            else:
                # Source is taller or equal (e.g. 9:16 or thinner)
                # Resize by width to match target width, then crop height
                clip = clip.resized(width=target_w)
                clip = clip.cropped(width=target_w, height=target_h, x_center=clip.w / 2, y_center=clip.h / 2)

            # Apply CrossFadeIn to subsequent clips for transition effect
            if i > 0:
                clip = clip.with_effects([vfx.CrossFadeIn(0.5)])

            clips.append(clip)

        if not clips:
            raise ValueError("No valid clips found to stitch.")

        # method='compose' and padding required for overlapping transitions
        final_clip = concatenate_videoclips(clips, method="compose", padding=-0.5)
        return final_clip

    def _apply_overlays(self, base_clip: VideoFileClip) -> CompositeVideoClip:
        """
        Applies text overlays based on style options and scene timing.
        """
        # Use overlays from selected style (Option 2)
        overlays_text = self.selected_style.get('overlays', [])

        # Get scenes to calculate timing
        scenes_data = self.instructions.get('scenes', [])
        scenes_data = sorted(scenes_data, key=lambda x: x.get('order', x.get('id', 0)))

        style = self.selected_style
        # Requirement: Serif/Gold. Use Times-New-Roman or generic Serif.
        font = style.get('font', 'Times-New-Roman')
        color = style.get('color', 'Gold')

        text_clips = [base_clip]

        current_time = 0.0
        padding = -0.5 # Match the padding in stitch_scenes

        for i, scene in enumerate(scenes_data):
            # Calculate duration of this scene to determine placement
            source = scene.get('clip_path') or scene.get('source')
            if not source or not os.path.exists(source):
                continue

            # Determine clip duration
            clip_duration = 0
            if 'duration' in scene and 'start' not in scene:
                 # Explicit duration only
                 clip_duration = scene['duration']
            elif 'duration' in scene and 'start' in scene:
                 # Explicit duration with start
                 clip_duration = scene['duration']
            else:
                # Need to read the file to get duration
                try:
                    # Creating a temp clip just to read duration
                    with VideoFileClip(source) as c:
                         clip_duration = c.duration
                except Exception as e:
                    logger.warning(f"Could not read duration for {source}: {e}")
                    # Default fallback
                    clip_duration = 5.0

            # Overlay Text if available for this scene
            if i < len(overlays_text):
                text = overlays_text[i]

                # Position: Lower third (0.75 relative height)
                # Styling: Font size 70, Gold
                try:
                    txt_clip = (TextClip(text=text, font_size=70, color=color, font=font, size=(base_clip.w, None), method='caption')
                                .with_position(('center', 0.75), relative=True)
                                .with_start(current_time + 0.5)  # Start slightly after transition
                                .with_duration(max(1, clip_duration - 1.0))) # Ensure at least 1s duration
                    text_clips.append(txt_clip)
                except Exception as e:
                    logger.warning(f"Failed to create TextClip for '{text}': {e}. Trying fallback.")
                    try:
                        # Fallback without font
                        txt_clip = (TextClip(text=text, font_size=70, color=color, size=(base_clip.w, None), method='caption')
                                    .with_position(('center', 0.75), relative=True)
                                    .with_start(current_time + 0.5)
                                    .with_duration(max(1, clip_duration - 1.0)))
                        text_clips.append(txt_clip)
                    except Exception as e2:
                        logger.error(f"Failed to create TextClip fallback: {e2}")

            # Update current_time for next scene
            current_time += clip_duration + padding

        return CompositeVideoClip(text_clips)

    def generate_sidecar_file(self) -> None:
        """
        Generates a sidecar description file using Title and Tags from Option 2.
        """
        title = self.selected_style.get('title', 'Untitled Dance Video')
        tags = self.selected_style.get('tags', [])

        content = f"Title: {title}\n\nTags:\n" + ", ".join(tags)

        output_path = "video_metadata.txt"
        with open(output_path, 'w') as f:
            f.write(content)
        logger.info(f"Generated sidecar file: {output_path}")

    def process_pipeline(self, dry_run: bool = False) -> None:
        """
        Executes the video processing pipeline: stitching -> overlays -> rendering.
        
        Args:
            dry_run (bool): If True, skips actual video rendering.
        """
        scenes = self.instructions.get('scenes', [])
        logger.info(f"Processing {len(scenes)} scenes for 9:16 vertical render.")
        logger.info(f"Using style: {self.selected_style.get('style', 'Unknown')}")
        
        if dry_run:
            logger.info("[DRY-RUN] Video processing simulated. No file written.")
            return

        try:
            logger.info("Step 1: Stitching Scenes...")
            stitched_clip = self._stitch_scenes()

            logger.info(f"Step 2: Applying Text Overlays using style: {self.selected_style}...")
            final_clip = self._apply_overlays(stitched_clip)

            logger.info("Step 3: Generating Sidecar Metadata File...")
            self.generate_sidecar_file()

            output_filename = "final_dance_short.mp4"
            logger.info(f"Rendering final export to {output_filename}...")

            # Write video file
            final_clip.write_videofile(
                output_filename,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                threads=4
            )
            logger.info("Render complete.")

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise
