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
    If 0.jpeg exists (title card), it's displayed for 2.5s at the start with NO voiceover.
    Remaining images (1.jpeg onwards) are mapped to scenes and displayed for their durations.
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

        # Check if title card exists (0.jpeg)
        title_card_path = image_folder / "0.jpeg"
        has_title_card = title_card_path.exists()
        title_card_duration = 2.5  # Title card displays for 2.5 seconds

        if has_title_card:
            print(f"🎬 Found title card (0.jpeg) - will display for {title_card_duration}s at start")
            # Remove title card from scene images list
            scene_images = [img for img in image_files if img.stem != "0"]
        else:
            scene_images = image_files

        num_scene_images = len(scene_images)

        # Validate we have enough images for scenes
        if num_scene_images < num_scenes:
            raise ValueError(f"Not enough images! Need {num_scenes} images for {num_scenes} scenes, but found only {num_scene_images}")

        if num_scene_images > num_scenes:
            print(f"⚠️  Using first {num_scenes} images for scenes (found {num_scene_images} total)")
            scene_images = scene_images[:num_scenes]

        # Create video clips
        clips = []

        # Add title card if it exists (silent intro with NO voiceover)
        if has_title_card:
            print(f"⏱️  Title Card: {title_card_duration}s (silent intro)")
            title_clip = ImageSequenceClip([str(title_card_path)], durations=[title_card_duration])
            # No fadein for title card - we want it to appear immediately without black frame
            clips.append(title_clip)

        # Create clips for each scene with their durations
        for i, scene in enumerate(scenes):
            scene_num = scene.get("scene_number", i + 1)
            duration = scene.get("duration_seconds", 3)
            visual_desc = scene.get("visual_description", "")[:50]  # First 50 chars

            print(f"⏱️  Scene {scene_num}: {duration}s - {visual_desc}...")

            # Map scene to corresponding image
            image_file = scene_images[i]
            clip = ImageSequenceClip([str(image_file)], durations=[duration])

            # Add fade effects (except for first/last scene)
            if i > 0 or has_title_card:  # Fade in if not first, or if title card exists
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
        total_scene_duration = sum(s.get('duration_seconds', 3) for s in scenes)
        total_video_duration = total_scene_duration + (title_card_duration if has_title_card else 0)
        print(f"✅ Total video duration: {total_video_duration} seconds ({total_scene_duration}s scenes + {title_card_duration if has_title_card else 0}s title card)")

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