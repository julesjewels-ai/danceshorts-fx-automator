import os
import logging
from moviepy import ImageClip, CompositeVideoClip
import moviepy.video.fx as vfx

logger = logging.getLogger(__name__)

class VeoSynthesizer:
    """
    Mocks the generative video synthesis engine.
    """
    def __init__(self, output_dir: str = "generated_clips"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate_clip(self, scene_id: int, start_img: str, end_img: str, duration: float) -> str:
        """
        Generates a video clip transitioning from start_img to end_img.
        Returns the path to the generated .mp4 file.
        """
        output_path = os.path.join(self.output_dir, f"scene_{scene_id}.mp4")

        # If files don't exist, log warning and return None or raise
        if not os.path.exists(start_img):
            raise FileNotFoundError(f"Start keyframe {start_img} not found.")

        try:
            logger.info(f"Generating clip for scene {scene_id} ({duration}s) from {start_img} to {end_img}...")

            # Create clips
            clip_start = ImageClip(start_img).with_duration(duration)

            if end_img and os.path.exists(end_img):
                clip_end = ImageClip(end_img).with_duration(duration)

                # Create a simple cross-dissolve effect to simulate transition
                # Start clip fades out over the last half
                # End clip fades in over the first half?
                # Let's just do a full duration cross dissolve for smooth morph feel.

                clip_end = clip_end.with_effects([vfx.CrossFadeIn(duration)])
                final_clip = CompositeVideoClip([clip_start, clip_end])
            else:
                final_clip = clip_start

            # Resize to ensure it matches target resolution if images are different
            # But we assume input images are correct size for now (1080x1920) based on creation script.

            # Write to file
            # Using ultrafast preset for speed
            final_clip.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                preset='ultrafast',
                logger=None
            )

            logger.info(f"Generated clip for scene {scene_id} at {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate clip for scene {scene_id}: {e}")
            raise
