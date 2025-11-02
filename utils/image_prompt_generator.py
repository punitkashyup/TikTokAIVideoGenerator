import json
import os
from pathlib import Path
from textwrap import dedent
from openai import OpenAI
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_openai_api_key() -> str:
    """Get OpenAI API key from environment variable"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not found. Please set it in .env file.")
    return api_key

def generate_image_prompts(script_data: Dict) -> List[Dict]:
    """
    Generate 18-20 image prompts using OpenAI GPT-4o and the provided metadata schema.
    Returns a list of image prompts following the specified structure.
    """
    try:
        openai_api_key = get_openai_api_key()

        client = OpenAI(api_key=openai_api_key)

        scenes = script_data.get("scenes", [])
        script_text = script_data.get("script", "")

        prompt = dedent(f"""
        You are a creative visual director and AI prompt engineer specialized in generating cinematic, mythological image prompts
        for AI image generation models (like Midjourney, DALL·E, or Leonardo AI).

        Create **18–20 detailed image prompts** based on the following Indian mythology-inspired video script and scenes.

        Each prompt should visually represent key story moments, emotions, and divine symbolism from the scenes.

        VIDEO SCRIPT:
        {script_text}

        SCENES:
        {json.dumps(scenes, indent=2)}

        Follow this EXACT JSON structure (no markdown, no explanations, JSON only):

        {{
        "prompts": [
            {{
            "subject": "Lord Hanuman flying toward the sun",
            "artform": ["digital painting", "concept art", "cinematic illustration"],
            "phototype": ["wide shot", "dramatic lighting"],
            "scene_details": {{
                "place": ["ancient India", "celestial sky", "temple surroundings"],
                "lighting": ["golden sunrise", "divine glow"],
                "composition": ["dynamic motion", "focus on emotion and scale"]
            }},
            "background": ["clouds", "mountains", "divine aura"],
            "additional_details": {{
                "wearing": "traditional ornaments and sacred thread",
                "holding": "mace or mountain"
            }},
            "photography_style": ["Indian mythology art", "epic fantasy realism"],
            "device": ["digital art tablet"],
            "artist": ["Raja Ravi Varma", "Greg Rutkowski"]
            }}
            // Repeat until 20 unique prompts
        ]
        }}

        Rules:
        1. Generate **exactly 20 prompts** inspired by the script and scenes.
        2. Ensure each prompt fits Indian mythology or epic storytelling tone (not sci-fi or modern tech).
        3. Use natural, culturally accurate visuals — temples, rivers, divine light, nature, weapons, crowns, etc.
        4. Keep the JSON valid and strictly follow the given format.
        5. Do not include markdown or extra commentary — only pure JSON output.
        """)

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=4096,
            response_format={"type": "json_object"}
        )

        response = json.loads(completion.choices[0].message.content)
        
        prompts = response.get("prompts") or response  
        
        MIN_PROMPTS = 18
        MAX_PROMPTS = 25
        if not isinstance(prompts, list) or not (MIN_PROMPTS <= len(prompts) <= MAX_PROMPTS):
            raise ValueError(
                f"Invalid response format. Got {len(prompts) if isinstance(prompts, list) else 0} prompts. "
                f"Expected between {MIN_PROMPTS}-{MAX_PROMPTS} prompts."
            )
            
        required_keys = {"subject", "artform", "phototype", "scene_details"}
        for i, prompt in enumerate(prompts):
            if not all(key in prompt for key in required_keys):
                raise ValueError(f"Prompt {i+1} missing required keys: {required_keys}")

        return prompts

    except json.JSONDecodeError:
        raise ValueError("Failed to parse API response as JSON")
    except Exception as e:
        raise RuntimeError(f"Image prompt generation failed: {str(e)}")

def save_image_prompts(prompts: List[Dict], output_path: Path) -> None:
    """Save the image prompts as a JSON file"""
    with open(output_path, "w") as f:
        json.dump({"prompts": prompts}, f, indent=2)
    print(f"✅ Saved {len(prompts)} image prompts to: {output_path}")

def main(script_path: Path, output_path: Path) -> None:
    """Generate and save image prompts"""
    try:
        with open(script_path, "r") as f:
            script_data = json.load(f)
        
        prompts = generate_image_prompts(script_data)
        
        save_image_prompts(prompts, output_path)
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")