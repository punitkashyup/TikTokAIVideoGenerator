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
    Generate exactly 1 image prompt per scene using OpenAI GPT-4o.
    Returns a list of image prompts following the specified structure.
    """
    try:
        openai_api_key = get_openai_api_key()

        client = OpenAI(api_key=openai_api_key)

        scenes = script_data.get("scenes", [])
        script_text = script_data.get("script", "")
        num_scenes = len(scenes)

        prompt = dedent(f"""
        You are a creative visual director and AI prompt engineer specialized in generating cinematic, mythological image prompts
        for AI image generation models (like Midjourney, DALL·E, or Google Gemini).

        Create **exactly {num_scenes} detailed image prompts** - one for each scene below.
        Each prompt should match the corresponding scene's visual_description exactly.

        IMPORTANT: Generate prompts in the SAME ORDER as the scenes (scene 1 → prompt 1, scene 2 → prompt 2, etc.)

        VIDEO SCRIPT:
        {script_text}

        SCENES (Total: {num_scenes}):
        {json.dumps(scenes, indent=2)}

        Follow this EXACT JSON structure (no markdown, no explanations, JSON only):

        {{
        "prompts": [
            {{
            "scene_number": 1,
            "subject": "Based on scene 1's visual_description",
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
                "holding": "relevant objects from scene"
            }},
            "photography_style": ["Indian mythology art", "epic fantasy realism"],
            "device": ["digital art tablet"],
            "artist": ["Raja Ravi Varma", "Greg Rutkowski"]
            }}
            // Repeat for ALL {num_scenes} scenes - one prompt per scene
        ]
        }}

        Rules:
        1. Generate **exactly {num_scenes} prompts** - one for each scene in order.
        2. Each prompt's "subject" must match its corresponding scene's "visual_description".
        3. Include "scene_number" field matching the scene it represents.
        4. Ensure each prompt fits Indian mythology or epic storytelling tone.
        5. Use natural, culturally accurate visuals — temples, rivers, divine light, nature, weapons, crowns, etc.
        6. Keep the JSON valid and strictly follow the given format.
        7. Do not include markdown or extra commentary — only pure JSON output.
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

        # Validate we got exactly the right number of prompts
        if not isinstance(prompts, list) or len(prompts) != num_scenes:
            raise ValueError(
                f"Invalid response format. Got {len(prompts) if isinstance(prompts, list) else 0} prompts. "
                f"Expected exactly {num_scenes} prompts (one per scene)."
            )

        required_keys = {"subject", "artform", "phototype", "scene_details", "scene_number"}
        for i, prompt in enumerate(prompts):
            if not all(key in prompt for key in required_keys):
                raise ValueError(f"Prompt {i+1} missing required keys: {required_keys}")

            # Verify scene_number matches
            expected_scene_num = i + 1
            if prompt.get("scene_number") != expected_scene_num:
                print(f"⚠️  Warning: Prompt {i+1} has scene_number {prompt.get('scene_number')}, expected {expected_scene_num}")

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