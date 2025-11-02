import json
import os
from pathlib import Path
from typing import Optional
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_elevenlabs_api_key() -> str:
    """Get ElevenLabs API key from environment variable"""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY environment variable not found. Please set it in .env file.")
    return api_key

def generate_audio(text: str, output_path: Path, voice_id: str = "1qEiC6qsybMkmnNdVMbK") -> bool:
    """
    Generate audio using ElevenLabs API with Eleven Multilingual v2 model.
    Args:
        text: Text to convert to speech
        output_path: Path to save the audio file
        voice_id: Voice ID (default: "1qEiC6qsybMkmnNdVMbK" - Monika Sogam Hindi)
    Returns:
        True if successful, False otherwise.
    """
    try:
        api_key = get_elevenlabs_api_key()
        client = ElevenLabs(api_key=api_key)

        print(f"🎙️  Generating audio with ElevenLabs (Voice: {voice_id})...")

        # Generate audio using ElevenLabs
        response = client.text_to_speech.convert(
            voice_id=voice_id,
            optimize_streaming_latency="0",
            output_format="mp3_44100_128",
            text=text,
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=0.0,
                use_speaker_boost=True,
            ),
        )

        # Save the audio file
        with open(output_path, "wb") as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)

        print(f"✅ Audio generated using ElevenLabs: {output_path}")
        return True

    except Exception as e:
        print(f"⚠️ ElevenLabs TTS failed: {str(e)}")
        return False

def main(script_path: Path, output_dir: Path) -> None:
    """
    Generate audio from script and save it to the output directory.
    """
    try:
        with open(script_path, "r") as f:
            script_data = json.load(f)
        
        script_text = script_data.get("script", "")
        if not script_text:
            raise ValueError("Script text is empty")

        output_dir.mkdir(parents=True, exist_ok=True)

        audio_path = output_dir / "voiceover.mp3"
        if not generate_audio(script_text, audio_path):
            raise RuntimeError("Failed to generate audio using ElevenLabs")

        print(f"✅ Audio saved to: {audio_path}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")