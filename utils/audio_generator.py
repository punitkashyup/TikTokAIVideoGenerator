import json
import os
from pathlib import Path
from typing import Optional
import wave
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables from .env file
load_dotenv()

def get_google_api_key() -> str:
    """Get Google API key from environment variable"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not found. Please set it in .env file.")
    return api_key

def wave_file(filename: str, pcm: bytes, channels: int = 1, rate: int = 24000, sample_width: int = 2):
    """Save PCM audio data as a WAV file"""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)

def generate_audio(text: str, output_path: Path, voice_name: str = "Kore") -> bool:
    """
    Generate audio using Google Gemini TTS API.
    Args:
        text: Text to convert to speech
        output_path: Path to save the audio file
        voice_name: Voice name (default: "Kore")
    Returns:
        True if successful, False otherwise.
    """
    try:
        api_key = get_google_api_key()
        client = genai.Client(api_key=api_key)

        print(f"🎙️  Generating audio with Google Gemini TTS (Voice: {voice_name})...")

        # Generate audio using Google Gemini TTS
        response = client.models.generate_content(
            model="gemini-2.5-pro-preview-tts",
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_name,
                        )
                    )
                ),
            )
        )

        # Extract audio data from response
        audio_data = response.candidates[0].content.parts[0].inline_data.data

        # Save as WAV file
        wave_file(str(output_path), audio_data)

        print(f"✅ Audio generated using Google Gemini TTS: {output_path}")
        return True

    except Exception as e:
        print(f"⚠️ Google Gemini TTS failed: {str(e)}")
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

        audio_path = output_dir / "voiceover.wav"
        if not generate_audio(script_text, audio_path):
            raise RuntimeError("Failed to generate audio using Google Gemini TTS")

        print(f"✅ Audio saved to: {audio_path}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")