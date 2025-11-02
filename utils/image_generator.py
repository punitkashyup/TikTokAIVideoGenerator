import os
import json
import base64
from pathlib import Path
from typing import List, Dict
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_google_api_key() -> str:
    """Get Google API key from environment variable"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not found. Please set it in .env file.")
    return api_key

def generate_images(image_prompts_path: str, output_dir: str) -> None:
    """
    Generate images from JSON prompts file using Google Gemini Imagen model
    Args:
        image_prompts_path: Path to JSON file with prompts
        output_dir: Directory to save generated images
    """
    image_prompts_path = Path(image_prompts_path)
    output_dir = Path(output_dir)

    if not image_prompts_path.exists():
        raise FileNotFoundError(f"Prompt file {image_prompts_path} not found")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Configure Google Gemini API
    api_key = get_google_api_key()
    genai.configure(api_key=api_key)

    # Initialize the Imagen model
    model = genai.ImageGenerationModel("imagen-4.0-generate-001")

    with open(image_prompts_path, "r") as f:
        prompts_data = json.load(f)

    if "prompts" not in prompts_data or not isinstance(prompts_data["prompts"], list):
        raise ValueError("Invalid prompts format - expected {'prompts': [...]}")

    for i, prompt_data in enumerate(prompts_data["prompts"], 1):
        print(f"🖼️  Generating image {i}/{len(prompts_data['prompts'])}...")

        prompt_text = (
            f"{prompt_data['subject']}, {', '.join(prompt_data['artform'])}, "
            f"shot with {prompt_data['device'][0]}, "
            f"style: {', '.join(prompt_data['photography_style'])}, "
            f"lighting: {', '.join(prompt_data['scene_details']['lighting'])}, "
            f"composition: {', '.join(prompt_data['scene_details']['composition'])}, "
            f"additional details: {prompt_data['additional_details']}"
        )

        try:
            # Generate image using Google Gemini Imagen
            result = model.generate_images(
                prompt=prompt_text,
                number_of_images=1,
                aspect_ratio="9:16",  # Vertical format for TikTok/Reels
                safety_filter_level="block_only_high",
                person_generation="allow_adult"
            )

            if result.images:
                image_data = result.images[0]

                existing_files = list(output_dir.glob("*.jpeg"))
                next_number = len(existing_files) + 1
                image_path = output_dir / f"{next_number}.jpeg"

                # Save the image
                image_data._pil_image.save(image_path, format="JPEG")
                print(f"✅ Image saved to {image_path}")
            else:
                print(f"⚠️ No image generated for prompt {i}")

        except Exception as e:
            print(f"⚠️ Failed to generate image {i}: {str(e)}")

if __name__ == "__main__":
    generate_images(
        image_prompts_path="C:\\Users\\Gabriel\\Documents\\TikTokAIVideoGenerator\\video8\\image_prompts.json",
        output_dir="generated_images"
    )