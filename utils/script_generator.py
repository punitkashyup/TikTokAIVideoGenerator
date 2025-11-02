import json
import os
from textwrap import dedent
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_openai_api_key() -> str:
    """Get OpenAI API key from environment variable"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not found. Please set it in .env file.")
    return api_key

def generate_script(topic: str, style: str, target_audience: str, cta: str) -> dict:
    """
    Generates a video script using OpenAI API with GPT-4o.
    Returns a dictionary with script and scene descriptions.
    """
    try:
        openai_api_key = get_openai_api_key()

        client = OpenAI(api_key=openai_api_key)

        prompt = dedent(f"""
        You are a creative assistant specialized in writing short, high-retention video scripts for TikTok/Instagram Reels/Shorts.
        We are making an Indian mythology storytelling video in HINGLISH (Hindi + English mix). Follow these rules exactly:

        **HINGLISH REQUIREMENTS (VERY IMPORTANT):**
        - Mix Hindi and English naturally throughout the script
        - Use common Hindi words like: "kya", "aapko", "pata hai", "kahani", "ek baar", "bahut", "sabse", "lekin", "par", "aur", "yeh"
        - Use Hindi for emotional/cultural words: "bhakt", "shakti", "dharma", "puja", "mandir", "devi", "bhagwan"
        - Example Hinglish: "Kya aapko pata hai Krishna ne ek baar poore pahaad ko apni choti ungli par utha liya tha?"
        - Keep it natural and easy to understand for Indian youth

        1) HOOK (first 3 seconds): Open with a bold Hinglish question or statement
        2) BODY (next ~50–65 seconds): Tell the mythic story in Hinglish with vivid details
        3) CTA (last ~7–10 seconds): Finish with emotional Hinglish CTA

        Content requirements:
        - Topic: {topic}
        - Style: {style}
        - Target Audience: {target_audience}
        - CTA: {cta}

        Output format (JSON only — nothing else):
        {{
        "script": "Full script text to be narrated by TTS (this is the combined narration for the whole video)",
        "scenes": [
            {{
            "scene_number": 1,
            "visual_description": "Detailed visual direction for this scene (up to 500 tokens)",
            "voiceover_text": "Exact spoken text for this scene",
            "duration_seconds": 3
            }},
            ...
        ],
        "total_duration": 60
        }}

        Token and structure constraints (must be followed exactly):
        - The **"script"** field (the narration text) MUST contain between **250 and 280 tokens** (inclusive). Do not output fewer than 250 or more than 280 tokens.
        - Scene descriptions may use up to 500 tokens each.
        - The sum of all scene `duration_seconds` must equal **60**.
        - Respond **only** with the JSON object described above. Do not include any explanation, extra metadata, or markdown.
        - Maintain cultural sensitivity and avoid inventing modern-sounding facts or false historical claims. If a detail is uncertain, present it as "legend" or "according to some stories".

        FINAL CHECK:
        - Before returning, validate twice that the "script" token count is within 250–280 tokens and that `total_duration` is 60.
        - If you cannot meet these constraints, return a JSON error object with keys `error` and `message` (but prefer to produce a compliant script).

        Create the script now.
        """)

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=1200,  # increased to allow room for full JSON wrapper
            response_format={"type": "json_object"}
        )

        # Debug: Print raw response
        raw_content = completion.choices[0].message.content
        print(f"\n[DEBUG] Raw API Response (first 500 chars):\n{raw_content[:500]}...\n")

        try:
            response = json.loads(raw_content)
        except json.JSONDecodeError as e:
            print(f"\n[ERROR] JSON Parse Error: {e}")
            print(f"[ERROR] Response content:\n{raw_content}\n")
            raise ValueError(f"Failed to parse API response as JSON: {e}")

        if not all(key in response for key in ["script", "scenes", "total_duration"]):
            print(f"\n[ERROR] Missing required keys in response")
            print(f"[ERROR] Response keys: {list(response.keys())}")
            print(f"[ERROR] Response content: {json.dumps(response, indent=2)[:1000]}")
            raise ValueError("Invalid JSON structure from API response")

        return response

    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse API response as JSON: {str(e)}")
    except Exception as e:
        print(f"\n[ERROR] Exception type: {type(e).__name__}")
        print(f"[ERROR] Exception message: {str(e)}")
        raise RuntimeError(f"Script generation failed: {str(e)}")

def save_script(script_data: dict, output_path: str) -> None:
    """Save the script as a JSON file"""
    with open(output_path, "w") as f:
        json.dump(script_data, f, indent=2)
    print(f"✅ Script saved to: {output_path}")

def main():
    try:
        topic = input("Enter video topic: ")
        style = input("Enter video style (e.g., funny, educational, inspirational): ")
        target_audience = input("Enter target audience: ")
        cta = input("Enter call to action (CTA): ")
        output_path = "script.json"

        print("\n🚀 Generating script with OpenAI GPT-4o...")
        script_data = generate_script(topic, style, target_audience, cta)
        
        save_script(script_data, output_path)

        print(f"📝 Total duration: {script_data['total_duration']} seconds")
        print(f"🎬 Number of scenes: {len(script_data['scenes'])}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
