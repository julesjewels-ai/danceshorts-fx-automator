import json
import os
import logging
import pandas as pd
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

    def __init__(self, report_file: str, options_file: str):
        """
        Initialize the automator.

        Args:
            report_file (str): Path to production_report.csv
            options_file (str): Path to metadata_options.json
        """
        self.report_file = report_file
        self.options_file = options_file
        self.report_data: pd.DataFrame = pd.DataFrame()
        self.options: Dict[str, Any] = {}
        self.selected_style: Dict[str, Any] = {}
        self.scene_start_times: Dict[int, float] = {}

    def load_configurations(self) -> None:
        """
        Loads and validates configuration files.
        """
        if not os.path.exists(self.report_file):
            raise FileNotFoundError(f"{self.report_file} not found.")
        
        if not os.path.exists(self.options_file):
            raise FileNotFoundError(f"{self.options_file} not found.")

        self._load_production_report()

        with open(self.options_file, 'r') as f:
            self.options = json.load(f)
            logger.info(f"Loaded options from {self.options_file}")

        self._apply_style_logic()

    def _load_production_report(self) -> None:
        """
        Loads the production report CSV into a pandas DataFrame.
        """
        try:
            self.report_data = pd.read_csv(self.report_file)
            logger.info(f"Loaded production report from {self.report_file}")
        except Exception as e:
            logger.error(f"Failed to load production report: {e}")
            raise

    def _apply_style_logic(self) -> None:
        """
        Selects the 'Recommended' style (Option 2) by default.
        """
        # Defaulting to Option 2 per requirements
        options_data = self.options.get('options', {})
        recommended_key = str(self.options.get('recommended', '2'))

        if recommended_key in options_data:
            self.selected_style = options_data[recommended_key]
            logger.info(f"Selected Style: {self.selected_style.get('style', 'Unknown')} (Option {recommended_key})")
        else:
            logger.warning(f"Option {recommended_key} not found. Falling back to Option 2 or first available.")
            if '2' in options_data:
                self.selected_style = options_data['2']
            else:
                self.selected_style = next(iter(options_data.values())) if options_data else {}

    def _stitch_scenes(self) -> VideoFileClip:
        """
        Stitches scenes together with cross-dissolve transitions.
        """
        # Iterate over DataFrame rows
        scenes_data = self.report_data.to_dict('records')
        clips = []

        # Track timeline for overlays
        current_timeline_time = 0.0
        padding = 0.5  # Overlap for cross-dissolve

        for i, scene in enumerate(scenes_data):
            # Normalize keys if necessary or assume title case from CSV
            source = scene.get('Source') or scene.get('source')
            start = float(scene.get('Start') or scene.get('start', 0))
            duration = float(scene.get('Duration') or scene.get('duration', 5))
            scene_id = scene.get('Scene') or scene.get('scene', i + 1)

            if not source or not os.path.exists(source):
                logger.warning(f"Source file {source} not found. Skipping.")
                continue

            clip = VideoFileClip(source).subclipped(start, start + duration)

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

            # Record the start time of this scene in the final timeline
            self.scene_start_times[scene_id] = current_timeline_time

            # Apply CrossFadeIn to subsequent clips for transition effect
            if i > 0:
                clip = clip.with_effects([vfx.CrossFadeIn(padding)])

            clips.append(clip)

            # Increment timeline time
            # The next clip starts `padding` seconds before this one ends
            current_timeline_time += (duration - padding)

        if not clips:
            raise ValueError("No valid clips found to stitch.")

        # method='compose' and padding required for overlapping transitions
        final_clip = concatenate_videoclips(clips, method="compose", padding=-padding)
        return final_clip

    def _apply_overlays(self, base_clip: VideoFileClip) -> CompositeVideoClip:
        """
        Applies beat-synced text overlays based on style options.
        """
        overlays_data = self.selected_style.get('text_overlay', [])
        style = self.selected_style

        font = style.get('font', 'Arial')
        color = style.get('color', 'white')

        text_clips = [base_clip]

        for overlay in overlays_data:
            text = overlay.get('text', '')
            trigger = overlay.get('trigger', '')
            duration = overlay.get('duration', 2.0) # Default duration if not specified

            start_time = 0.0

            # Parse Trigger
            try:
                scene_num_str = ''.join(filter(str.isdigit, trigger))
                if scene_num_str:
                    scene_num = int(scene_num_str)
                    start_time = self.scene_start_times.get(scene_num, 0.0)
                else:
                    logger.warning(f"No scene number found in trigger '{trigger}'. Defaulting to 0.")
            except Exception as e:
                logger.warning(f"Error parsing trigger '{trigger}': {e}. Defaulting to 0.")

            # Create TextClip
            # Using method='caption' to wrap text if needed, or default
            try:
                txt_clip = (TextClip(text=text, font_size=70, color=color, font=font, size=(base_clip.w, None), method='caption')
                            .with_position('center')
                            .with_start(start_time)
                            .with_duration(duration))
                text_clips.append(txt_clip)
            except Exception as e:
                logger.warning(f"Failed to create TextClip for '{text}': {e}. Trying fallback font.")
                # Fallback without font specification (uses default)
                try:
                    txt_clip = (TextClip(text=text, font_size=70, color=color, size=(base_clip.w, None), method='caption')
                                .with_position('center')
                                .with_start(start_time)
                                .with_duration(duration))
                    text_clips.append(txt_clip)
                except Exception as e2:
                    logger.error(f"Failed to create TextClip fallback: {e2}")

        return CompositeVideoClip(text_clips)

    def _export_metadata_sidecar(self) -> None:
        """
        Generates a sidecar text file with Title, Description, and Tags.
        """
        output_filename = "final_dance_short_metadata.txt"
        try:
            with open(output_filename, 'w') as f:
                f.write(f"Title: {self.selected_style.get('title', '')}\n\n")
                f.write(f"Description:\n{self.selected_style.get('description', '')}\n\n")
                f.write(f"Tags:\n{self.selected_style.get('tags', '')}\n")
            logger.info(f"Metadata sidecar file generated: {output_filename}")
        except Exception as e:
            logger.error(f"Failed to generate metadata sidecar: {e}")

    def process_pipeline(self, dry_run: bool = False) -> None:
        """
        Executes the video processing pipeline: stitching -> overlays -> rendering.
        
        Args:
            dry_run (bool): If True, skips actual video rendering.
        """
        scenes_count = len(self.report_data)
        logger.info(f"Processing {scenes_count} scenes for 9:16 vertical render.")
        logger.info(f"Using style: {self.selected_style.get('style', 'Unknown')}")
        
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

            logger.info("Step 3: Generating Metadata Sidecar...")
            self._export_metadata_sidecar()

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise
