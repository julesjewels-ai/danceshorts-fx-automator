from moviepy import ColorClip
import os

def generate_video(filename, color, duration=10):
    print(f"Generating {filename}...")
    clip = ColorClip(size=(1920, 1080), color=color, duration=duration)
    clip.write_videofile(filename, fps=24)

if __name__ == "__main__":
    videos = [
        ("video1.mp4", (255, 0, 0)),   # Red
        ("video2.mp4", (0, 255, 0)),   # Green
        ("video3.mp4", (0, 0, 255)),   # Blue
        ("video4.mp4", (255, 255, 0))  # Yellow
    ]

    for name, color in videos:
        if not os.path.exists(name):
            generate_video(name, color)
        else:
            print(f"{name} already exists.")
