import json
import os
from pathlib import Path
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

def generate_viral_titles(script_data: dict, topic: str, style: str, num_titles: int = 4) -> list:
    """
    Generate multiple viral, attention-grabbing Hindi title options for the video using OpenAI GPT-4o.

    Args:
        script_data: The script data containing scenes and narration
        topic: The video topic
        style: The video style (e.g., educational, funny, inspirational)
        num_titles: Number of title options to generate (default: 4)

    Returns:
        A list of viral Hindi title strings optimized for TikTok/Reels/Shorts
    """
    try:
        openai_api_key = get_openai_api_key()
        client = OpenAI(api_key=openai_api_key)

        # Get first scene and script preview for context
        first_scene = script_data.get("scenes", [{}])[0]
        script_preview = script_data.get("script", "")[:200]  # First 200 chars

        prompt = dedent(f"""
        You are a viral content expert specializing in creating attention-grabbing titles for TikTok, Instagram Reels, and YouTube Shorts.

        Create {num_titles} DIFFERENT VIRAL, clickable HINDI titles for this video that will maximize views and engagement.

        VIDEO TOPIC: {topic}
        VIDEO STYLE: {style}

        SCRIPT PREVIEW:
        {script_preview}...

        FIRST SCENE:
        {first_scene.get('voiceover_text', '')}

        TITLE REQUIREMENTS:
        1. **Language**: PURE HINDI ONLY - Use Devanagari script (not Hinglish, not English)
        2. **Length**: 30-50 characters in Devanagari
        3. **Hook**: Start with attention-grabbing Hindi phrases:
           - "क्या आपको पता है..." (Do you know...)
           - "यह रहस्य..." (This mystery...)
           - "अविश्वसनीय..." (Unbelievable...)
           - "सच्चाई..." (The truth...)
        4. **Emotion**: Use powerful Hindi words that trigger curiosity, shock, or intrigue
        5. **Readability**: Clear, bold Hindi text easy to read on mobile
        6. **Viral Elements**:
           - Create curiosity gap
           - Use numbers or specific details
           - Create sense of urgency or exclusivity
        7. **NO EMOJIS**: Do NOT use any emojis - HINDI TEXT ONLY
        8. **Variety**: Make each title DIFFERENT with different hooks and angles

        EXAMPLES OF VIRAL HINDI TITLES:
        - "क्या शिव ने सच में यह किया?"
        - "99% लोग नहीं जानते यह रहस्य!"
        - "मार्कंडेय की अमर कहानी"
        - "महाभारत का छुपा सच!"
        - "यह रहस्य आपको हैरान कर देगा!"

        Generate {num_titles} DIFFERENT viral HINDI titles (Devanagari script) that will make people STOP scrolling and watch.
        Return ONLY the titles, one per line, numbered 1-{num_titles}.
        Format:
        1. [Title 1]
        2. [Title 2]
        3. [Title 3]
        4. [Title 4]
        """)

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,  # Higher temperature for more variety
            max_tokens=300
        )

        response = completion.choices[0].message.content.strip()

        # Parse the numbered list
        titles = []
        lines = response.split('\n')

        for line in lines:
            line = line.strip()
            # Remove numbering (1., 2., etc.) and clean up
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove number and dot/dash at start
                title = line.lstrip('0123456789.-) ').strip()
                # Clean up any quotes or extra formatting
                title = title.strip('"').strip("'").strip()
                if title:
                    titles.append(title)

        # If we didn't get enough titles, generate fallbacks
        while len(titles) < num_titles:
            titles.append(f"{topic} - अद्भुत कहानी {len(titles) + 1}!")

        print(f"✅ Generated {len(titles)} viral Hindi title options")
        return titles[:num_titles]  # Return exactly num_titles

    except Exception as e:
        print(f"⚠️  Failed to generate viral titles: {str(e)}")
        # Return fallback Hindi titles
        return [
            f"{topic} - अद्भुत कहानी!",
            f"{topic} का रहस्य!",
            f"क्या आप जानते हैं {topic}?",
            f"{topic} की सच्चाई!"
        ][:num_titles]

def generate_viral_title(script_data: dict, topic: str, style: str) -> str:
    """
    Generate a single viral Hindi title (backward compatibility).

    Args:
        script_data: The script data containing scenes and narration
        topic: The video topic
        style: The video style (e.g., educational, funny, inspirational)

    Returns:
        A viral Hindi title string optimized for TikTok/Reels/Shorts
    """
    titles = generate_viral_titles(script_data, topic, style, num_titles=1)
    return titles[0]

def save_title(title: str, output_path: Path) -> None:
    """Save the title to a text file"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(title)
    print(f"✅ Title saved to: {output_path}")

def main():
    """Test title generator"""
    # Example script data
    test_script = {
        "script": "Kya aapko pata hai Markandeya ki amar kahani? Yeh ek aisa rahasya hai jo bahut kam log jaante hain...",
        "scenes": [
            {
                "scene_number": 1,
                "voiceover_text": "Kya aapko pata hai ki kaise ek 16 saal ka balak mrityu ko harakar amar ban gaya?",
                "duration_seconds": 3
            }
        ]
    }

    print("\n✨ Generating 4 viral Hindi title options...")
    titles = generate_viral_titles(test_script, "Markandeya Story", "educational", num_titles=4)

    print("\n📝 VIRAL TITLE OPTIONS:")
    print("="*60)
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")
    print("="*60)

if __name__ == "__main__":
    main()
