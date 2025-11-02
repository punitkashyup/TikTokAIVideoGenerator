import os
import platform
import shutil
from pathlib import Path
from typing import List, Dict
import json
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings

# Auto-detect ImageMagick binary based on platform
def get_imagemagick_binary():
    """Automatically detect ImageMagick binary path based on platform"""
    system = platform.system()

    if system == "Windows":
        # Common Windows installation paths
        possible_paths = [
            r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe",
            r"C:\Program Files\ImageMagick\magick.exe",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
    elif system == "Darwin":  # macOS
        # Try to find convert in common locations
        convert_path = shutil.which("convert")
        if convert_path:
            return convert_path
        # Common Homebrew paths
        possible_paths = [
            "/opt/homebrew/bin/convert",  # Apple Silicon
            "/usr/local/bin/convert",      # Intel Mac
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
    elif system == "Linux":
        convert_path = shutil.which("convert")
        if convert_path:
            return convert_path

    return None

# Set ImageMagick binary
imagemagick_path = get_imagemagick_binary()
if imagemagick_path:
    change_settings({"IMAGEMAGICK_BINARY": imagemagick_path})
    print(f"✓ ImageMagick found at: {imagemagick_path}")
else:
    print("⚠️ ImageMagick not found. Please install it:")
    print("  macOS: brew install imagemagick")
    print("  Linux: sudo apt-get install imagemagick")
    print("  Windows: Download from https://imagemagick.org/script/download.php")

def load_captions(captions_path: Path) -> List[Dict]:
    """Load captions from a JSON file."""
    try:
        with open(captions_path, "r") as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load captions: {str(e)}")

def group_words_into_captions(captions: List[Dict], max_words_per_caption: int = 4) -> List[Dict]:
    """
    Group words into captions with a maximum number of words per caption.
    Split captions at punctuation marks to maintain natural pauses.
    """
    grouped_captions = []
    current_group = []
    current_start = None
    current_end = None

    for caption in captions:
        text = caption["text"]
        start = caption["start"]
        end = caption["end"]

        ends_with_punctuation = any(text.endswith(p) for p in [".", ",", "!", "?", ";", ":"])

        current_group.append(text)
        if current_start is None:
            current_start = start
        current_end = end

        if ends_with_punctuation or len(current_group) >= max_words_per_caption:
            grouped_captions.append({
                "start": current_start,
                "end": current_end,
                "text": " ".join(current_group)
            })
            current_group = []
            current_start = None
            current_end = None

    if current_group:
        grouped_captions.append({
            "start": current_start,
            "end": current_end,
            "text": " ".join(current_group)
        })

    return grouped_captions

def add_captions_to_video(video_path: Path, captions_path: Path, output_path: Path) -> None:
    """
    Add captions to the video at the specified timestamps.
    """
    try:
        video = VideoFileClip(str(video_path))

        captions = load_captions(captions_path)

        grouped_captions = group_words_into_captions(captions, max_words_per_caption=4)

        text_clips = []
        for caption in grouped_captions:
            text_clip = TextClip(
                caption["text"],
                fontsize=90,  
                color="yellow",
                font="EastMan", 
                stroke_color="black",  
                stroke_width=2,
                size=(video.size[0] * 0.8, None),  
                method="caption"  
            ).set_position(("center", "center")) \
             .set_start(caption["start"]) \
             .set_end(caption["end"])
            text_clips.append(text_clip)

        final_video = CompositeVideoClip([video] + text_clips)

        final_video.write_videofile(
            str(output_path),
            fps=30,
            codec="libx264",
            audio_codec="aac",
            threads=4
        )

        print(f"✅ Video with captions saved to: {output_path}")

    except Exception as e:
        raise RuntimeError(f"Failed to add captions to video: {str(e)}")

def main(video_path: Path, captions_path: Path, output_path: Path) -> None:
    """
    Add captions to the video and save the final output.
    """
    try:
        if not video_path.exists():
            raise FileNotFoundError(f"Video file {video_path} not found")
        if not captions_path.exists():
            raise FileNotFoundError(f"Captions file {captions_path} not found")

        print("\n📝 Adding captions to video...")
        add_captions_to_video(video_path, captions_path, output_path)

    except Exception as e:
        print(f"❌ Error: {str(e)}")