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

    def __init__(self, instruction_file: str, options_file: str, style_file: str, working_directory: str = None):
        """
        Initialize the automator.

        Args:
            instruction_file (str): Path to veo_instructions.json
            options_file (str): Path to metadata_options.json
            style_file (str): Path to style_options.json
            working_directory (str): Base directory for resolving relative paths (optional)
        """
        self.instruction_file = instruction_file
        self.options_file = options_file
        self.style_file = style_file
        self.working_directory = working_directory or os.getcwd()
        self.instructions: Dict[str, Any] = {}
        self.metadata_options: Dict[str, Any] = {}
        self.style_options: Dict[str, Any] = {}
        self.selected_style: Dict[str, Any] = {}
        self.selected_metadata: Dict[str, Any] = {}

    def load_configurations(self) -> None:
        """
        Loads and validates JSON configuration files.
        """
        if not os.path.exists(self.instruction_file):
            raise FileNotFoundError(f"{self.instruction_file} not found.")
        
        if not os.path.exists(self.options_file):
            raise FileNotFoundError(f"{self.options_file} not found.")
        
        if not os.path.exists(self.style_file):
            raise FileNotFoundError(f"{self.style_file} not found.")

        with open(self.instruction_file, 'r') as f:
            loaded_data = json.load(f)
            
            # Normalize old format (array) to new format (object with scenes key)
            if isinstance(loaded_data, list):
                logger.info(f"Detected legacy array format in {self.instruction_file}, normalizing...")
                self.instructions = {
                    "scenes": loaded_data,
                    "audio_source": None
                }
            else:
                self.instructions = loaded_data
            
            logger.info(f"Loaded instructions from {self.instruction_file}")

        with open(self.options_file, 'r') as f:
            self.metadata_options = json.load(f)
            logger.info(f"Loaded metadata options from {self.options_file}")
        
        with open(self.style_file, 'r') as f:
            self.style_options = json.load(f)
            logger.info(f"Loaded style options from {self.style_file}")

        self._apply_metadata_selection()
        self._apply_style_logic()
        self._validate_audio_source()

    def _apply_metadata_selection(self) -> None:
        """
        Selects the metadata option based on the 'recommended' field.
        """
        recommended = self.metadata_options.get('recommended', 1)
        option_key = f"option_{recommended}"
        
        if option_key in self.metadata_options:
            self.selected_metadata = self.metadata_options[option_key]
            logger.info(f"Selected metadata option: {recommended} - {self.selected_metadata.get('title', 'Unknown')}")
        else:
            logger.warning(f"Recommended option {recommended} not found. Falling back to option_1.")
            self.selected_metadata = self.metadata_options.get('option_1', {})
    
    def _apply_style_logic(self) -> None:
        """
        Selects the style based on the 'default' field from style_options.json.
        """
        options_data = self.style_options.get('options', {})
        default_style = self.style_options.get('default', '2')
        
        if default_style in options_data:
            self.selected_style = options_data[default_style]
            logger.info(f"Selected Style: {self.selected_style.get('style', 'Unknown')} (Option {default_style})")
        else:
            logger.warning(f"Default style {default_style} not found. Falling back to first available option.")
            self.selected_style = next(iter(options_data.values())) if options_data else {}

    def _validate_audio_source(self) -> None:
        """
        Validates that the custom audio source file exists if specified.
        """
        audio_source = self.instructions.get('audio_source')
        if audio_source:
            # Resolve relative paths from working directory
            audio_path = os.path.join(self.working_directory, audio_source) if not os.path.isabs(audio_source) else audio_source
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio source file not found: {audio_path}")
            logger.info(f"Custom audio source specified: {audio_path}")

    def _apply_custom_audio(self, video_clip: VideoFileClip) -> VideoFileClip:
        """
        Replaces the video's audio with a custom audio file if specified.
        
        Args:
            video_clip: The video clip to apply custom audio to
            
        Returns:
            Video clip with replaced audio, or original clip if no custom audio
        """
        audio_source = self.instructions.get('audio_source')
        
        if not audio_source:
            return video_clip
        
        try:
            from moviepy import AudioFileClip
            # Resolve relative paths from working directory
            audio_path = os.path.join(self.working_directory, audio_source) if not os.path.isabs(audio_source) else audio_source
            logger.info(f"Loading custom audio from: {audio_path}")
            audio_clip = AudioFileClip(audio_path)
            
            # Match audio duration to video duration
            if audio_clip.duration > video_clip.duration:
                # Trim audio to match video length
                audio_clip = audio_clip.subclipped(0, video_clip.duration)
                logger.info(f"Audio trimmed to match video duration: {video_clip.duration:.2f}s")
            elif audio_clip.duration < video_clip.duration:
                # Loop audio to match video length if needed
                logger.warning(f"Audio duration ({audio_clip.duration:.2f}s) is shorter than video ({video_clip.duration:.2f}s). Consider using a longer audio file.")
            
            # Replace the audio
            video_clip = video_clip.with_audio(audio_clip)
            logger.info("Custom audio applied successfully")
            
        except Exception as e:
            logger.error(f"Failed to apply custom audio: {e}")
            raise
        
        return video_clip

    def _validate_scene_clip(self, scene: Dict[str, Any], index: int) -> str:
        """
        Validates scene fields and source file existence.

        Args:
            scene: Scene dictionary
            index: Scene index for error messages

        Returns:
            Resolved source path if valid, None if file missing
            
        Raises:
            ValueError: If scene format is invalid
        """
        source = scene.get('source')

        # Validate that required fields exist
        if source is None:
            # Check if this is a Veo generation format (has start_image/end_image/prompt)
            if 'start_image' in scene or 'end_image' in scene or 'prompt' in scene:
                raise ValueError(
                    f"Scene {index+1} appears to be in Veo AI generation format (contains 'start_image'/'end_image'/'prompt'). "
                    "This tool requires video stitching format with 'source', 'start', and 'duration' fields. "
                    "Please convert your Veo generation instructions to actual video clips first."
                )
            else:
                raise ValueError(
                    f"Scene {index+1} is missing required 'source' field. "
                    "Expected format: {{\"source\": \"clip.mp4\", \"start\": 0, \"duration\": 5}}"
                )

        # Resolve relative paths from working directory
        source_path = os.path.join(self.working_directory, source) if not os.path.isabs(source) else source

        if not os.path.exists(source_path):
            logger.warning(f"Source file {source_path} not found. Skipping.")
            return None
            
        return source_path

    def _process_scene_clip(self, source_path: str, scene: Dict[str, Any], index: int) -> VideoFileClip:
        """
        Loads, trims, resizes, crops, and applies transitions to a clip.
        """
        start = scene.get('start', 0)
        duration = scene.get('duration', 5)

        clip = VideoFileClip(source_path).subclipped(start, start + duration)

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
        if index > 0:
            clip = clip.with_effects([vfx.CrossFadeIn(0.5)])

        return clip

    def _stitch_scenes(self) -> VideoFileClip:
        """
        Stitches scenes together with cross-dissolve transitions.
        """
        scenes_data = self.instructions.get('scenes', [])
        clips = []

        for i, scene in enumerate(scenes_data):
            source_path = self._validate_scene_clip(scene, i)
            if not source_path:
                continue

            clip = self._process_scene_clip(source_path, scene, i)
            clips.append(clip)

        if not clips:
            raise ValueError("No valid clips found to stitch.")

        # method='compose' and padding required for overlapping transitions
        final_clip = concatenate_videoclips(clips, method="compose", padding=-0.5)
        return final_clip

    def _extract_overlays_from_metadata(self, video_duration: float) -> List[Dict[str, Any]]:
        """
        Extracts text overlays from selected metadata and auto-distributes timing.
        
        Args:
            video_duration: Total duration of the stitched video in seconds
            
        Returns:
            List of overlay dictionaries with text, start, and duration
        """
        text_overlay_array = self.selected_metadata.get('text_overlay', [])
        
        if not text_overlay_array:
            logger.warning("No text overlays found in selected metadata option.")
            return []
        
        num_overlays = len(text_overlay_array)
        overlays = []
        
        # Auto-distribute overlays evenly across video duration
        # Each overlay gets equal time slice with slight padding
        overlay_duration = min(2.5, video_duration / num_overlays)  # Max 2.5s per overlay
        interval = video_duration / num_overlays
        
        for i, text in enumerate(text_overlay_array):
            start_time = i * interval
            overlays.append({
                'text': text,
                'start': start_time,
                'duration': overlay_duration
            })
            logger.debug(f"Overlay {i+1}: '{text}' at {start_time:.2f}s for {overlay_duration:.2f}s")
        
        return overlays
    
    def _apply_overlays(self, base_clip: VideoFileClip) -> CompositeVideoClip:
        """
        Applies text overlays based on metadata and style options.
        """
        # Get overlays from metadata with auto-distributed timing
        overlays_data = self._extract_overlays_from_metadata(base_clip.duration)
        style = self.selected_style

        font = style.get('font', 'Arial')
        color = style.get('color', 'white')
        font_size = style.get('font_size', 70)

        text_clips = [base_clip]

        for overlay in overlays_data:
            text = overlay.get('text', '')
            start = overlay.get('start', 0)
            duration = overlay.get('duration', 2)

            # Apply fixes for text cutoff issue:
            # 1. Use max width with padding to prevent edge rendering glitches
            # 2. Add newline hack to ensure descenders (g, y, p, q, j) aren't cropped
            # Limiting to 70% width for better padding on sides
            safe_width = int(base_clip.w * 0.7)
            text_with_margin = text + " \n"

            # Create TextClip
            # Using method='caption' to wrap text if needed, or default
            try:
                txt_clip = (TextClip(text=text_with_margin, font_size=font_size, color=color, font=font, size=(safe_width, None), method='caption')
                            .with_position(('center', 800))
                            .with_start(start)
                            .with_duration(duration))
                text_clips.append(txt_clip)
            except Exception as e:
                logger.warning(f"Failed to create TextClip for '{text}': {e}. Trying fallback font.")
                # Fallback without font specification (uses default)
                try:
                    txt_clip = (TextClip(text=text_with_margin, font_size=font_size, color=color, size=(safe_width, None), method='caption')
                                .with_position(('center', 800))
                                .with_start(start)
                                .with_duration(duration))
                    text_clips.append(txt_clip)
                except Exception as e2:
                    logger.error(f"Failed to create TextClip fallback: {e2}")

        return CompositeVideoClip(text_clips)

    def process_pipeline(self, dry_run: bool = False, output_path: str = None) -> None:
        """
        Executes the video processing pipeline: stitching -> overlays -> rendering.
        
        Args:
            dry_run (bool): If True, skips actual video rendering.
            output_path (str): Custom output path for the final video (optional)
        """
        scenes = self.instructions.get('scenes', [])
        logger.info(f"Processing {len(scenes)} scenes for 9:16 vertical render.")
        logger.info(f"Using metadata option: {self.selected_metadata.get('title', 'Unknown')}")
        logger.info(f"Using style: {self.selected_style.get('style', 'Unknown')}")
        
        if dry_run:
            logger.info("[DRY-RUN] Video processing simulated. No file written.")
            return

        try:
            logger.info("Step 1: Stitching Scenes...")
            stitched_clip = self._stitch_scenes()

            logger.info("Step 2: Applying Custom Audio (if specified)...")
            stitched_clip = self._apply_custom_audio(stitched_clip)

            logger.info(f"Step 3: Applying Text Overlays using style: {self.selected_style}...")
            final_clip = self._apply_overlays(stitched_clip)

            output_filename = output_path or "final_dance_short.mp4"
            logger.info(f"Rendering final export to {output_filename}...")

            # Write video file
            final_clip.write_videofile(
                output_filename,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                threads=4
            )
            logger.info(f"✓ Render complete: {output_filename}")

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise

