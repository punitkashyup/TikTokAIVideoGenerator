import os
from pathlib import Path
from utils.script_generator import generate_script, save_script
from utils.image_prompt_generator import main as generate_image_prompts
from utils.image_generator import generate_images
from utils.audio_generator import main as generate_audio
from utils.video_composer import main as create_video
from utils.caption_generator import main as generate_captions
from utils.caption_overlay import main as add_captions

def create_project_folder(folder_name: str) -> Path:
    """Create a folder for the project and return its path"""
    project_path = Path(folder_name)
    project_path.mkdir(parents=True, exist_ok=True)
    (project_path / "images").mkdir(exist_ok=True)  
    (project_path / "audio").mkdir(exist_ok=True)  
    (project_path / "captions").mkdir(exist_ok=True)  
    return project_path

def main():
    try:
        print("""
 █████╗ ██╗    ██╗   ██╗██╗██████╗ ███████╗ ██████╗                          
██╔══██╗██║    ██║   ██║██║██╔══██╗██╔════╝██╔═══██╗                         
███████║██║    ██║   ██║██║██║  ██║█████╗  ██║   ██║                         
██╔══██║██║    ╚██╗ ██╔╝██║██║  ██║██╔══╝  ██║   ██║                         
██║  ██║██║     ╚████╔╝ ██║██████╔╝███████╗╚██████╔╝                         
╚═╝  ╚═╝╚═╝      ╚═══╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝                          
                                                                             
 ██████╗ ███████╗███╗   ██╗███████╗██████╗  █████╗ ████████╗ ██████╗ ██████╗ 
██╔════╝ ██╔════╝████╗  ██║██╔════╝██╔══██╗██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗
██║  ███╗█████╗  ██╔██╗ ██║█████╗  ██████╔╝███████║   ██║   ██║   ██║██████╔╝
██║   ██║██╔══╝  ██║╚██╗██║██╔══╝  ██╔══██╗██╔══██║   ██║   ██║   ██║██╔══██╗
╚██████╔╝███████╗██║ ╚████║███████╗██║  ██║██║  ██║   ██║   ╚██████╔╝██║  ██║
 ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
""")
        folder_name = input("Enter the name of the folder to save the project: ").strip()
        topic = input("Enter video topic: ")
        style = input("Enter video style (e.g., funny, educational, inspirational): ")
        target_audience = input("Enter target audience: ")
        cta = input("Enter call to action (CTA): ")
        
        project_path = create_project_folder(folder_name)
        print(f"✅ Created project folder at: {project_path}")

        script_path = project_path / "script.json"
        image_prompts_path = project_path / "image_prompts.json"
        images_dir = project_path / "images"
        audio_dir = project_path / "audio"
        captions_dir = project_path / "captions"
        video_path = project_path / "final_video.mp4"
        final_video_path = project_path / "final_video_with_captions.mp4"

        print("\n🚀 Generating script with OpenAI GPT-4o...")
        script_data = generate_script(topic, style, target_audience, cta)
        save_script(script_data, script_path)

        print("\n🎨 Generating image prompts with GPT-4o...")
        generate_image_prompts(script_path, image_prompts_path)

        print("\n🌄 Generating images with Google Gemini Imagen 4.0...")
        generate_images(image_prompts_path, images_dir)

        print("\n🔊 Generating audio with ElevenLabs (Hindi voice)...")
        generate_audio(script_path, audio_dir)

        print("\n🔍 Generating captions with OpenAI Whisper...")
        generate_captions(audio_dir / "voiceover.mp3", captions_dir)

        print("\n🎥 Composing video with MoviePy...")
        create_video(images_dir, audio_dir / "voiceover.mp3", video_path)

        print("\n📝 Adding captions to video...")
        add_captions(video_path, captions_dir / "captions.json", final_video_path)

        print("\n" + "="*60)
        print("✨ VIDEO GENERATION COMPLETE! ✨")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"  📝 Total duration: {script_data['total_duration']}s")
        print(f"  🎬 Number of scenes: {len(script_data['scenes'])}")
        print(f"  🖼️  Generated images: {len(list(images_dir.glob('*.jpeg')))}/20")
        print(f"  🔊 Audio generated: {'✓' if os.path.exists(audio_dir / 'voiceover.mp3') else '✗'}")
        print(f"  🔍 Captions generated: {'✓' if os.path.exists(captions_dir / 'captions.json') else '✗'}")
        print(f"  🎥 Base video: {'✓' if os.path.exists(video_path) else '✗'}")
        print(f"  🎬 Final video: {'✓' if os.path.exists(final_video_path) else '✗'}")
        print(f"\n📁 Output location: {project_path.absolute()}")
        print(f"🎥 Final video: {final_video_path.name}")
        print("="*60)

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()