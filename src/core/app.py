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
        Selects the recommended style by default.
        """
        recommended_idx = self.options.get('recommended', 2)
        option_key = f"option_{recommended_idx}"

        if option_key in self.options:
            self.selected_style = self.options[option_key]
            logger.info(f"Selected Style: {self.selected_style.get('title', 'Unknown')} ({option_key})")
        else:
            logger.warning(f"{option_key} not found in metadata. Falling back to option_2 or first available.")
            if 'option_2' in self.options:
                self.selected_style = self.options['option_2']
            else:
                # Find any key starting with 'option_'
                options = [v for k, v in self.options.items() if k.startswith('option_')]
                self.selected_style = options[0] if options else {}

    def _stitch_scenes(self) -> VideoFileClip:
        """
        Stitches scenes together with cross-dissolve transitions.
        """
        scenes_data = self.instructions.get('scenes', [])
        clips = []

        for i, scene in enumerate(scenes_data):
            source = scene.get('source')
            start = scene.get('start', 0)
            duration = scene.get('duration', 5)
            speed = scene.get('speed', 1.0)

            if not os.path.exists(source):
                logger.warning(f"Source file {source} not found. Skipping.")
                continue

            clip = VideoFileClip(source).subclipped(start, start + duration)

            if speed != 1.0:
                clip = clip.with_effects([vfx.MultiplySpeed(speed)])

            # Ensure 9:16 aspect ratio (720x1280) via Crop-to-Fill
            target_w, target_h = 720, 1280
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
        Applies text overlays from the selected metadata option, distributed evenly.
        """
        texts = self.selected_style.get('text_overlay', [])
        if not texts:
            logger.info("No text overlays found in selected style.")
            return base_clip

        # Default styling
        font = 'Impact'
        color = 'white'

        text_clips = [base_clip]
        total_duration = base_clip.duration
        num_texts = len(texts)
        if num_texts == 0:
             return base_clip

        segment_duration = total_duration / num_texts

        for i, text in enumerate(texts):
            start = i * segment_duration
            duration = segment_duration

            # Create TextClip
            try:
                txt_clip = (TextClip(text=text, font_size=70, color=color, font=font, size=(base_clip.w, None), method='caption')
                            .with_position('center')
                            .with_start(start)
                            .with_duration(duration))
                text_clips.append(txt_clip)
            except Exception as e:
                logger.warning(f"Failed to create TextClip for '{text}': {e}. Trying fallback font.")
                try:
                    txt_clip = (TextClip(text=text, font_size=70, color=color, size=(base_clip.w, None), method='caption')
                                .with_position('center')
                                .with_start(start)
                                .with_duration(duration))
                    text_clips.append(txt_clip)
                except Exception as e2:
                    logger.error(f"Failed to create TextClip fallback: {e2}")

        return CompositeVideoClip(text_clips)

    def process_pipeline(self, dry_run: bool = False) -> None:
        """
        Executes the video processing pipeline: stitching -> overlays -> rendering.
        
        Args:
            dry_run (bool): If True, skips actual video rendering.
        """
        scenes = self.instructions.get('scenes', [])
        logger.info(f"Processing {len(scenes)} scenes for 9:16 vertical render.")
        logger.info(f"Using style: {self.selected_style.get('title', 'Unknown')}")
        
        if dry_run:
            logger.info("[DRY-RUN] Video processing simulated. No file written.")
            return

        try:
            logger.info("Step 1: Stitching Scenes...")
            stitched_clip = self._stitch_scenes()

            logger.info(f"Step 2: Applying Text Overlays using style: {self.selected_style}...")
            final_clip = self._apply_overlays(stitched_clip)

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
