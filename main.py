import os
from pathlib import Path
from utils.script_generator import generate_script, save_script
from utils.title_generator import generate_viral_titles, save_title
from utils.title_card_generator import create_title_card
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
        title_path = project_path / "title.txt"
        image_prompts_path = project_path / "image_prompts.json"
        images_dir = project_path / "images"
        audio_dir = project_path / "audio"
        captions_dir = project_path / "captions"
        video_path = project_path / "final_video.mp4"
        final_video_path = project_path / "final_video_with_captions.mp4"

        print("\n🚀 Generating script with OpenAI GPT-4o...")
        script_data = generate_script(topic, style, target_audience, cta)
        save_script(script_data, script_path)

        print("\n✨ Generating viral Hindi title options with GPT-4o...")
        title_options = generate_viral_titles(script_data, topic, style, num_titles=4)

        # Display title options to user
        print("\n" + "="*60)
        print("📝 VIRAL TITLE OPTIONS:")
        print("="*60)
        for i, title in enumerate(title_options, 1):
            print(f"{i}. {title}")
        print("="*60)

        # Get user selection
        while True:
            try:
                choice = input("\nSelect title number (1-4): ").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= 4:
                    viral_title = title_options[choice_num - 1]
                    print(f"\n✅ Selected: {viral_title}")
                    break
                else:
                    print("⚠️  Please enter a number between 1 and 4")
            except ValueError:
                print("⚠️  Please enter a valid number")
            except KeyboardInterrupt:
                print("\n\n❌ Process cancelled by user")
                return

        save_title(viral_title, title_path)

        print("\n🎨 Generating image prompts with GPT-4o...")
        generate_image_prompts(script_path, image_prompts_path)

        print("\n🌄 Generating images with Google Gemini (gemini-2.5-flash-image)...")
        generate_images(image_prompts_path, images_dir)

        print("\n🎬 Creating title card with Hindi title overlay...")
        first_image = images_dir / "1.jpeg"
        title_card = images_dir / "0.jpeg"
        if first_image.exists():
            create_title_card(first_image, viral_title, title_card)
        else:
            print("⚠️  First image not found, skipping title card creation")

        print("\n🔊 Generating audio with Google Gemini TTS...")
        generate_audio(script_path, audio_dir)

        print("\n🔍 Generating captions with OpenAI Whisper...")
        generate_captions(audio_dir / "voiceover.wav", captions_dir)

        print("\n🎥 Composing video with MoviePy...")
        create_video(images_dir, audio_dir / "voiceover.wav", video_path, script_path)

        print("\n📝 Adding captions to video...")
        add_captions(video_path, captions_dir / "captions.json", final_video_path)

        print("\n" + "="*60)
        print("✨ VIDEO GENERATION COMPLETE! ✨")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"  📝 Title: {viral_title}")
        print(f"  ⏱️  Total duration: {script_data['total_duration']}s + 2.5s title card = {script_data['total_duration'] + 2.5}s")
        print(f"  🎬 Number of scenes: {len(script_data['scenes'])}")
        print(f"  🎬 Title card: {'✓' if os.path.exists(title_card) else '✗'}")
        print(f"  🖼️  Generated images: {len(list(images_dir.glob('*.jpeg')))}/20")
        print(f"  🔊 Audio generated: {'✓' if os.path.exists(audio_dir / 'voiceover.wav') else '✗'}")
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