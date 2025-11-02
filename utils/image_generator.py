import os
import json
import base64
import requests
from pathlib import Path
from typing import List, Dict
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_openrouter_api_key() -> str:
    """Get OpenRouter API key from environment variable"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not found. Please set it in .env file.")
    return api_key

def generate_images(image_prompts_path: str, output_dir: str) -> None:
    """
    Generate images from JSON prompts file using OpenRouter with google/gemini-2.5-flash-image (Nano Banana)
    Args:
        image_prompts_path: Path to JSON file with prompts
        output_dir: Directory to save generated images
    """
    image_prompts_path = Path(image_prompts_path)
    output_dir = Path(output_dir)

    if not image_prompts_path.exists():
        raise FileNotFoundError(f"Prompt file {image_prompts_path} not found")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Configure OpenRouter API
    api_key = get_openrouter_api_key()

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
            # Generate image using OpenRouter - google/gemini-2.5-flash-image (Nano Banana)
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "google/gemini-2.5-flash-image",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt_text
                        }
                    ],
                    "modalities": ["image", "text"]
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()

                # Extract images from response
                if result.get("choices") and len(result["choices"]) > 0:
                    message = result["choices"][0]["message"]

                    if message.get("images") and len(message["images"]) > 0:
                        # Get the first image (base64 encoded data URL)
                        image_data_url = message["images"][0]["image_url"]["url"]

                        # Remove data URL prefix (data:image/png;base64,)
                        if image_data_url.startswith("data:image"):
                            base64_data = image_data_url.split(",", 1)[1]
                            image_bytes = base64.b64decode(base64_data)

                            existing_files = list(output_dir.glob("*.jpeg"))
                            next_number = len(existing_files) + 1
                            image_path = output_dir / f"{next_number}.jpeg"

                            # Save the image
                            img = Image.open(BytesIO(image_bytes))
                            img.save(image_path, format="JPEG")
                            print(f"✅ Image saved to {image_path}")
                        else:
                            print(f"⚠️ Unexpected image format for prompt {i}")
                    else:
                        print(f"⚠️ No image generated for prompt {i}")
                else:
                    print(f"⚠️ No response choices for prompt {i}")
            else:
                print(f"⚠️ Failed to generate image {i}: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"⚠️ Failed to generate image {i}: {str(e)}")

if __name__ == "__main__":
    # Example usage - update paths as needed
    generate_images(
        image_prompts_path="image_prompts.json",
        output_dir="generated_images"
    )