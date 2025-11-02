import os
import platform
import shutil
from pathlib import Path
from moviepy.editor import ImageSequenceClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
from moviepy.video.fx.all import fadein, fadeout
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

def create_video_clip(image_folder: Path, audio_path: Path, output_path: Path, script_path: Path) -> None:
    """
    Create a video from images and audio using scene durations from script.json.
    Each image is mapped to its corresponding scene and displayed for the scene's duration.
    """
    try:
        import json

        # Load scene data from script.json
        with open(script_path, "r") as f:
            script_data = json.load(f)

        scenes = script_data.get("scenes", [])
        if not scenes:
            raise ValueError("No scenes found in script.json")

        # Get all images sorted by number
        image_files = sorted(image_folder.glob("*.jpeg"), key=lambda x: int(x.stem))
        if not image_files:
            raise ValueError("No images found in the specified folder")

        num_scenes = len(scenes)
        num_images = len(image_files)

        print(f"📊 Found {num_scenes} scenes and {num_images} images")

        # Use only the first N images where N = number of scenes
        if num_images < num_scenes:
            raise ValueError(f"Not enough images! Need {num_scenes} images for {num_scenes} scenes, but found only {num_images}")

        if num_images > num_scenes:
            print(f"⚠️  Using first {num_scenes} images (found {num_images} total)")
            image_files = image_files[:num_scenes]

        # Create video clips matching each scene duration
        clips = []
        for i, scene in enumerate(scenes):
            scene_num = scene.get("scene_number", i + 1)
            duration = scene.get("duration_seconds", 3)
            visual_desc = scene.get("visual_description", "")[:50]  # First 50 chars

            print(f"⏱️  Scene {scene_num}: {duration}s - {visual_desc}...")

            # Map scene to corresponding image
            image_file = image_files[i]
            clip = ImageSequenceClip([str(image_file)], durations=[duration])

            # Add fade effects (except for first/last)
            if i > 0:
                clip = fadein(clip, 0.5)
            if i < len(scenes) - 1:
                clip = fadeout(clip, 0.5)

            clips.append(clip)

        # Concatenate all clips
        video = concatenate_videoclips(clips, method="compose")

        # Add audio
        audio = AudioFileClip(str(audio_path))
        video = video.set_audio(audio)

        # Write final video (9:16 aspect ratio - vertical format for TikTok/Reels/Shorts)
        # Video resolution is determined by the input images
        video.write_videofile(
            str(output_path),
            fps=30,
            codec="libx264",
            audio_codec="aac",
            threads=4
        )

        print(f"✅ Video saved to: {output_path}")
        print(f"✅ Total video duration: {sum(s.get('duration_seconds', 3) for s in scenes)} seconds")

    except Exception as e:
        raise RuntimeError(f"Failed to create video: {str(e)}")

def main(image_folder: Path, audio_path: Path, output_path: Path, script_path: Path = None) -> None:
    """
    Generate a video from images and audio.
    If script_path is provided, uses scene durations from script.json for timing.
    """
    try:
        if script_path is None:
            raise ValueError("script_path is required to read scene durations")

        create_video_clip(image_folder, audio_path, output_path, script_path)
    except Exception as e:
        print(f"❌ Error: {str(e)}")