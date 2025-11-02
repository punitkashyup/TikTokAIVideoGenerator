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

def calculate_image_duration(audio_path: Path, num_images: int) -> float:
    """
    Calculate the duration each image should be displayed based on audio length.
    """
    try:
        audio = AudioFileClip(str(audio_path))
        audio_duration = audio.duration
        return audio_duration / num_images
    except Exception as e:
        raise RuntimeError(f"Failed to calculate image duration: {str(e)}")

def create_video_clip(image_folder: Path, audio_path: Path, output_path: Path) -> None:
    """
    Create a video from images and audio.
    """
    try:
        image_files = sorted(image_folder.glob("*.jpeg"))
        if not image_files:
            raise ValueError("No images found in the specified folder")

        image_duration = calculate_image_duration(audio_path, len(image_files))
        print(f"⏱️  Each image will be displayed for {image_duration:.2f} seconds")

        clips = []
        for i, image_file in enumerate(image_files):
            clip = ImageSequenceClip([str(image_file)], durations=[image_duration])
            
            if i > 0:
                clip = fadein(clip, 0.5)  
            if i < len(image_files) - 1:
                clip = fadeout(clip, 0.5) 
            
            clips.append(clip)

        video = concatenate_videoclips(clips, method="compose")

        audio = AudioFileClip(str(audio_path))
        video = video.set_audio(audio)

        video.write_videofile(
            str(output_path),
            fps=30,  
            codec="libx264",  
            audio_codec="aac", 
            threads=4  
        )

        print(f"✅ Video saved to: {output_path}")

    except Exception as e:
        raise RuntimeError(f"Failed to create video: {str(e)}")

def main(image_folder: Path, audio_path: Path, output_path: Path) -> None:
    """
    Generate a video from images and audio.
    """
    try:
        create_video_clip(image_folder, audio_path, output_path)
    except Exception as e:
        print(f"❌ Error: {str(e)}")