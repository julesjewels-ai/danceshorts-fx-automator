from moviepy import ColorClip, TextClip, CompositeVideoClip
import os

def create_clip(filename, color, text, duration=8):
    # Create a color clip
    # 720x1280 (9:16 aspect ratio)
    w, h = 720, 1280
    color_clip = ColorClip(size=(w, h), color=color, duration=duration)

    # Add text to identify the clip
    # Note: MoviePy v2 TextClip usage might vary slightly, but assuming standard parameters or using fallback if font issues.
    # If font is None, it might use default.
    try:
        txt_clip = TextClip(text=text, font_size=100, color='white', size=(w, None), method='caption')
        txt_clip = txt_clip.with_position('center').with_duration(duration)
        final_clip = CompositeVideoClip([color_clip, txt_clip])
    except Exception as e:
        print(f"TextClip failed: {e}. Creating just ColorClip.")
        final_clip = color_clip

    final_clip.write_videofile(filename, fps=24, codec='libx264', audio_codec='aac')
    print(f"Created {filename}")

def main():
    clips = [
        ("clip1.mp4", (255, 0, 0), "Clip 1"),   # Red
        ("clip2.mp4", (0, 255, 0), "Clip 2"),   # Green
        ("clip3.mp4", (0, 0, 255), "Clip 3"),   # Blue
        ("clip4.mp4", (255, 255, 0), "Clip 4")  # Yellow
    ]

    for filename, color, text in clips:
        create_clip(filename, color, text)

if __name__ == "__main__":
    main()
