import json
import os
import logging
from typing import Dict, Any, List
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip
import moviepy.video.fx as vfx
from src.core.ingestion import DataLoader
from src.core.veo import VeoSynthesizer

logger = logging.getLogger(__name__)

class DanceShortsAutomator:
    """
    Core logic for the video editing pipeline.
    
    Parses instructions and metadata to stitch scenes and apply overlays
    specifically tuned for YouTube Shorts (9:16 aspect ratio).
    """

    def __init__(self, report_file: str, instruction_file: str, options_file: str, assets_dir: str = "data"):
        """
        Initialize the automator.

        Args:
            report_file (str): Path to production_report.csv
            instruction_file (str): Path to veo_instructions.json
            options_file (str): Path to metadata_options.json
            assets_dir (str): Directory containing visual assets.
        """
        self.report_file = report_file
        self.instruction_file = instruction_file
        self.options_file = options_file
        self.assets_dir = assets_dir

        self.data_loader = DataLoader(report_file, instruction_file, options_file)
        self.veo_engine = VeoSynthesizer(output_dir=os.path.join(assets_dir, "generated_clips"))

        self.scenes: List[Dict[str, Any]] = []
        self.options: Dict[str, Any] = {}
        self.selected_style: Dict[str, Any] = {}

    def load_configurations(self) -> None:
        """
        Loads and merges configuration files.
        """
        logger.info("Loading configurations...")
        self.scenes = self.data_loader.get_merged_scene_data()
        self.options = self.data_loader.load_options()
        logger.info(f"Loaded {len(self.scenes)} scenes.")

        self._apply_style_logic()

    def _apply_style_logic(self) -> None:
        """
        Selects the 'Recommended' style (Option 2) by default.
        """
        # Defaulting to Option 2 per requirements
        options_data = self.options.get('options', {})
        if '2' in options_data:
            self.selected_style = options_data['2']
            logger.info(f"Selected Style: {self.selected_style.get('style', 'Unknown')} (Option 2)")
        else:
            logger.warning("Option 2 not found in metadata. Falling back to first available option.")
            self.selected_style = next(iter(options_data.values())) if options_data else {}

    def _generate_scenes(self) -> None:
        """
        Generates video clips for each scene using the Veo engine mock.
        Populates 'generated_clip_path' in scene data.
        """
        logger.info("Generating scenes with Veo Engine...")
        for scene in self.scenes:
            start_key = scene.get('start_keyframe')
            end_key = scene.get('end_keyframe')

            if start_key:
                start_path = os.path.join(self.assets_dir, start_key)
            else:
                start_path = ""

            if end_key:
                end_path = os.path.join(self.assets_dir, end_key)
            else:
                end_path = ""

            duration = scene.get('duration', 5)
            scene_id = scene.get('id')

            try:
                clip_path = self.veo_engine.generate_clip(scene_id, start_path, end_path, duration)
                scene['generated_clip_path'] = clip_path
            except Exception as e:
                logger.error(f"Failed to generate scene {scene_id}: {e}")
                # Fallback? Or continue?
                continue

    def _stitch_scenes(self) -> VideoFileClip:
        """
        Stitches scenes together with cross-dissolve transitions.
        """
        clips = []

        for i, scene in enumerate(self.scenes):
            source = scene.get('generated_clip_path')
            # For generated clips, we use the full duration
            duration = scene.get('duration', 5)

            if not source or not os.path.exists(source):
                logger.warning(f"Source file {source} not found for scene {scene.get('id')}. Skipping.")
                continue

            clip = VideoFileClip(source)
            # Duration should already be correct from generation, but subclip to be safe if needed
            # clip = clip.subclipped(0, duration)

            # Ensure 9:16 aspect ratio (1080x1920) via Crop-to-Fill
            target_w, target_h = 1080, 1920
            target_ratio = target_w / target_h
            current_ratio = clip.w / clip.h

            if current_ratio > target_ratio:
                # Source is wider than target
                clip = clip.resized(height=target_h)
                clip = clip.cropped(width=target_w, height=target_h, x_center=clip.w / 2, y_center=clip.h / 2)
            else:
                # Source is taller or equal
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

    def _calculate_overlay_start(self, trigger: str) -> float:
        """
        Calculates the timestamp for an overlay based on its trigger string.
        Format expected: "Scene X [start|dip|...]"
        """
        trigger = trigger.lower()

        # Simple parsing logic
        import re
        match = re.search(r"scene\s+(\d+)", trigger)
        if not match:
            return 0.0

        scene_id = int(match.group(1))

        # Calculate cumulative start time for the scene
        current_time = 0.0
        scene_found = None
        for s in self.scenes:
            if s['id'] == scene_id:
                scene_found = s
                break
            current_time += s.get('duration', 0)

        if not scene_found:
            return 0.0

        # Refine based on keyword (dip, start, etc)
        # Assuming "dip" happens at 50% of the scene duration if not specified
        if "dip" in trigger:
             return current_time + (scene_found.get('duration', 0) * 0.5)

        return current_time

    def _apply_overlays(self, base_clip: VideoFileClip) -> CompositeVideoClip:
        """
        Applies beat-synced text overlays based on style options.
        """
        # Get overlays from the selected style (Option 2)
        overlays_data = self.selected_style.get('text_overlay', [])

        style = self.selected_style
        font = style.get('font', 'Arial')
        color = style.get('color', 'white')

        text_clips = [base_clip]

        for overlay in overlays_data:
            text = overlay.get('text', '')
            trigger = overlay.get('trigger', '')
            duration = overlay.get('duration', 3)

            start = self._calculate_overlay_start(trigger)

            # Create TextClip
            try:
                # Ensure font is available or fallback to None (default)
                font_to_use = font

                txt_clip = (TextClip(text=text, font_size=70, color=color, font=font_to_use, size=(base_clip.w * 0.8, None), method='caption')
                            .with_position('center')
                            .with_start(start)
                            .with_duration(duration))
                text_clips.append(txt_clip)
            except Exception as e:
                logger.warning(f"Failed to create TextClip for '{text}': {e}. Trying fallback.")
                try:
                    txt_clip = (TextClip(text=text, font_size=70, color=color, size=(base_clip.w * 0.8, None), method='caption')
                                .with_position('center')
                                .with_start(start)
                                .with_duration(duration))
                    text_clips.append(txt_clip)
                except Exception as e2:
                    logger.error(f"Failed to create TextClip fallback: {e2}")

        return CompositeVideoClip(text_clips)

    def _add_audio(self, video_clip: VideoFileClip) -> VideoFileClip:
        """
        Adds audio track to the video.
        """
        # Check for audio files in assets dir
        audio_extensions = ['.wav', '.mp3', '.aac']
        audio_path = None

        for ext in audio_extensions:
            path = os.path.join(self.assets_dir, f"audio_track{ext}")
            if os.path.exists(path):
                audio_path = path
                break

        if not audio_path:
            logger.warning("No audio track found in assets directory.")
            return video_clip

        try:
            audio_clip = AudioFileClip(audio_path)
            # Loop audio if shorter than video, or subclip if longer
            if audio_clip.duration < video_clip.duration:
                # Simple loop not directly supported easily without vfx, let's just use what we have or tile it
                # For now assume it's long enough or just play once
                pass
            else:
                audio_clip = audio_clip.subclipped(0, video_clip.duration)

            return video_clip.with_audio(audio_clip)
        except Exception as e:
            logger.error(f"Failed to add audio: {e}")
            return video_clip

    def _write_sidecar_file(self, output_filename: str) -> None:
        """
        Generates a sidecar text file with metadata.
        """
        base_name = os.path.splitext(output_filename)[0]
        sidecar_path = f"{base_name}_metadata.txt"

        style = self.selected_style
        title = style.get('title', 'Dance Short')
        description = style.get('description', '')
        tags = style.get('tags', [])

        content = f"Title: {title}\n\nDescription:\n{description}\n\nTags:\n{', '.join(tags)}"

        try:
            with open(sidecar_path, 'w') as f:
                f.write(content)
            logger.info(f"Sidecar metadata written to {sidecar_path}")
        except Exception as e:
            logger.error(f"Failed to write sidecar file: {e}")

    def process_pipeline(self, dry_run: bool = False) -> None:
        """
        Executes the video processing pipeline: stitching -> overlays -> rendering.
        
        Args:
            dry_run (bool): If True, skips actual video rendering.
        """
        logger.info(f"Processing {len(self.scenes)} scenes for 9:16 vertical render.")
        logger.info(f"Using style: {self.selected_style.get('style', 'Unknown')}")
        
        if dry_run:
            logger.info("[DRY-RUN] Video processing simulated. No file written.")
            return

        try:
            # Step 0: Generate Scenes
            self._generate_scenes()

            logger.info("Step 1: Stitching Scenes...")
            stitched_clip = self._stitch_scenes()

            logger.info(f"Step 2: Applying Text Overlays using style: {self.selected_style.get('style')}...")
            final_clip = self._apply_overlays(stitched_clip)

            logger.info("Step 3: Adding Audio...")
            final_clip = self._add_audio(final_clip)

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

            logger.info("Generating Sidecar Metadata...")
            self._write_sidecar_file(output_filename)

            logger.info("Render complete.")

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise
