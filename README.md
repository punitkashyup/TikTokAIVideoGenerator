# TikTok AI Video Generator

This project is a Python-based tool for generating vertical videos optimized for platforms like TikTok, Instagram Reels, and YouTube Shorts. It uses state-of-the-art AI models for script generation, image creation, audio synthesis, and captioning to automate the entire video creation process.

## Example output
<a href=".github/final_video_with_captions.mp4">
  <img src="https://i.imgur.com/xUXDj6q.jpeg" width="20%" height="20%" alt="Watch Video">
</a>

[Full Video](.github/final_video_with_captions.mp4)
---

## Features

- **Script Generation**: Create engaging video scripts using OpenAI's GPT-4o model.
- **Image Generation**: Generate high-quality images using Google Gemini 2.0 Flash (experimental).
- **Audio Generation**: Convert scripts to natural-sounding audio using ElevenLabs with Eleven Multilingual v2 (Hindi voice support).
- **Caption Generation**: Transcribe audio to precise word-level captions using OpenAI's Whisper model.
- **Video Composition**: Combine images, audio, and captions into a final video using MoviePy.
- **Cross-Platform Support**: Automatically detects and configures ImageMagick on Windows, macOS, and Linux.
- **User Choice**: Choose between generating a full video or just the script, images, and audio.

---

## Prerequisites

Before running the project, ensure you have the following:

1. **Python 3.11+**: Install Python from [python.org](https://www.python.org/downloads/).
2. **API Keys**:
   - **OpenAI API key** (for script generation and image prompts) - [Get API Key](https://platform.openai.com/api-keys)
   - **Google Gemini API key** (for image generation) - [Get API Key](https://makersuite.google.com/app/apikey)
   - **ElevenLabs API key** (for audio synthesis) - [Get API Key](https://elevenlabs.io/app/settings/api-keys)
3. **FFmpeg**: Required for audio and video processing. Download from [ffmpeg.org](https://ffmpeg.org/).
4. **ImageMagick**: Required for caption overlay on videos.
   - **macOS**: `brew install imagemagick`
   - **Linux**: `sudo apt-get install imagemagick`
   - **Windows**: [Download from ImageMagick](https://imagemagick.org/script/download.php)

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/GabrielLaxy/TikTokAIVideoGenerator.git
   cd TikTokAIVideoGenerator
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API keys in `.env` file:**

   The project includes a `.env` file. Update it with your actual API keys:

   ```env
   # OpenAI API Configuration
   OPENAI_API_KEY=your-openai-api-key-here

   # Google Gemini API Configuration
   GOOGLE_API_KEY=your-google-api-key-here

   # ElevenLabs API Configuration
   ELEVENLABS_API_KEY=your-elevenlabs-api-key-here
   ```

4. **Install FFmpeg:**
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt-get install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/) and add to PATH

5. **Install ImageMagick:**
   - **macOS**: `brew install imagemagick`
   - **Linux**: `sudo apt-get install imagemagick`
   - **Windows**: Download from [ImageMagick](https://imagemagick.org/script/download.php)

   > **Note**: The project automatically detects ImageMagick on all platforms. No manual configuration needed!

---

## Usage

Run the program:
```bash
python main.py
```

### Workflow

1. **Input Details**:
   - Enter the project folder name, video topic, style, target audience, and call-to-action (CTA).

2. **Generated Files**:
   - The project folder will contain:
     - `script.json`: Generated script.
     - `image_prompts.json`: Image prompts.
     - `images/`: Generated images.
     - `audio/voiceover.mp3`: Generated audio.
     - `captions/captions.json`: Generated captions (if full video is selected).
     - `final_video.mp4`: Video without captions (if full video is selected).
     - `final_video_with_captions.mp4`: Final video with captions (if full video is selected).

---

## Workflow Details

### 1. Script Generation
- Uses **OpenAI GPT-4o** to generate engaging scripts based on user inputs.
- Model: `gpt-4o`
- Optimized for Indian mythology storytelling with Hinglish support.
- Saves the script as `script.json`.

### 2. Image Prompt Generation
- Uses **OpenAI GPT-4o** to create 18-20 detailed image prompts from the script.
- Structured prompts optimized for cinematic, mythological visuals.
- Saves the prompts as `image_prompts.json`.

### 3. Image Generation
- Uses **Google Gemini 2.0 Flash** (experimental) to generate high-quality images.
- Model: `gemini-2.0-flash-exp`
- Aspect ratio: 9:16 (vertical format for TikTok/Reels)
- Saves images in the `images/` folder.

### 4. Audio Generation
- Uses **ElevenLabs** with Eleven Multilingual v2 model.
- Voice: Monika Sogam Hindi (Voice ID: `1qEiC6qsybMkmnNdVMbK`)
- High-quality MP3 output at 44.1kHz, 128kbps.
- Saves the audio as `audio/voiceover.mp3`.

### 5. Caption Generation (Full Video Only)
- Uses **OpenAI Whisper (small.en)** to transcribe audio with word-level timestamps.
- Precise caption synchronization for better viewer engagement.
- Saves captions as `captions/captions.json`.

### 6. Video Composition (Full Video Only)
- Combines images and audio with fade transitions.
- Frame rate: 30 FPS
- Codec: H.264 (libx264) for video, AAC for audio.
- Saves the video as `final_video.mp4`.

### 7. Caption Overlay (Full Video Only)
- Adds styled captions to the video with precise timing.
- Font: EastMan, size 90, yellow text with black stroke.
- Saves the final video as `final_video_with_captions.mp4`.

---

## Customization

### Captions
- Maximum 4 words per caption group.
- Naturally split at punctuation marks.
- Font: EastMan, size 90.
- Style: Yellow text with black stroke (2px width).
- Position: Center-center of the video.
- Width: 80% of video width.

### Video Format
- Resolution: 1080x1920 (vertical format).
- Frame rate: 30 FPS.
- Codec: H.264 (libx264) for video, AAC for audio.
- Image transitions: Fade-in/fade-out (0.5 seconds).

### Voice Settings (ElevenLabs)
You can customize voice settings in `utils/audio_generator.py`:
- **Stability**: 0.5 (controls consistency)
- **Similarity Boost**: 0.75 (voice clarity)
- **Speaker Boost**: Enabled
- **Voice ID**: Change to any ElevenLabs voice ID

---

## Troubleshooting

### ImageMagick Not Found
- The program automatically detects ImageMagick on most systems.
- If not detected, manually install:
  - **macOS**: `brew install imagemagick`
  - **Linux**: `sudo apt-get install imagemagick`
  - **Windows**: [Download installer](https://imagemagick.org/script/download.php)

### FFmpeg Not Found
- Ensure FFmpeg is installed and added to your system PATH.
- Verify installation: `ffmpeg -version`

### API Errors
- Verify that your API keys in `.env` are correct and active.
- Check API quota/credits:
  - **OpenAI**: [Usage Dashboard](https://platform.openai.com/usage)
  - **Google Gemini**: [API Console](https://console.cloud.google.com/)
  - **ElevenLabs**: [Subscription Page](https://elevenlabs.io/app/subscription)

### Voice ID Issues (ElevenLabs)
- Ensure the voice ID in `utils/audio_generator.py` is correct.
- Find voice IDs in your [ElevenLabs Voice Library](https://elevenlabs.io/app/voice-library).

### Dependency Issues
- Reinstall dependencies: `pip install -r requirements.txt --upgrade`
- For Apple Silicon Macs, some packages may require Rosetta 2.

---

## License

This project is licensed under the Creative Commons Zero v1.0 Universal license. See the [LICENSE](LICENSE) file for details.

---

## Technology Stack

- **OpenAI GPT-4o**: Script and image prompt generation.
- **Google Gemini 2.0 Flash**: AI-powered image generation.
- **ElevenLabs**: Premium text-to-speech with multilingual support.
- **OpenAI Whisper**: State-of-the-art speech-to-text transcription.
- **MoviePy**: Video composition and editing.
- **FFmpeg**: Audio/video encoding and processing.
- **ImageMagick**: Image manipulation and text rendering.

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

## Contact

For questions or feedback, contact [gabriel_laxy@proton.me](mailto:gabriel_laxy@proton.me).
