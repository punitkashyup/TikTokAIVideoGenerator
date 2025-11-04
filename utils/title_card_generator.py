import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import Optional

def get_hindi_font(font_size: int = 100) -> Optional[ImageFont.FreeTypeFont]:
    """
    Get a font that supports Hindi/Devanagari script.
    Tries multiple common Hindi fonts and falls back to default if none found.
    """
    # List of Hindi-compatible fonts to try (in order of preference)
    hindi_fonts = [
        # macOS fonts
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/DevanagariSangamMN.ttc",
        "/System/Library/Fonts/Supplemental/Kohinoor.ttc",
        # Common Linux fonts
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        # Windows fonts
        "C:\\Windows\\Fonts\\Arial.ttf",
        "C:\\Windows\\Fonts\\ArialUni.ttf",
        "mangal.ttf",
    ]

    # Try each font
    for font_path in hindi_fonts:
        try:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                print(f"✅ Using font: {font_path}")
                return font
        except Exception as e:
            continue

    # If no Hindi font found, try system default
    try:
        font = ImageFont.truetype("Arial.ttf", font_size)
        print("⚠️  Using Arial font (may not display Hindi correctly)")
        return font
    except:
        # Last resort: PIL default font (won't support Hindi well)
        print("⚠️  Using default font (Hindi may not display correctly)")
        return ImageFont.load_default()

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.Draw) -> list:
    """
    Wrap text to fit within max_width.
    Returns list of text lines.
    """
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines if lines else [text]

def create_title_card(
    first_image_path: Path,
    title: str,
    output_path: Path,
    font_size: int = 110,
    text_color: tuple = (255, 223, 0),  # Bright yellow
    stroke_color: tuple = (0, 0, 0),     # Black
    stroke_width: int = 8
) -> bool:
    """
    Create a title card by cloning the first image and adding a large Hindi title overlay.

    Args:
        first_image_path: Path to the first generated image (e.g., images/1.jpeg)
        title: The Hindi title text to overlay
        output_path: Where to save the title card (e.g., images/0.jpeg)
        font_size: Font size for the title (default: 110)
        text_color: RGB tuple for text color (default: bright yellow)
        stroke_color: RGB tuple for stroke/outline color (default: black)
        stroke_width: Width of text stroke (default: 8)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Load the first image
        if not first_image_path.exists():
            print(f"❌ First image not found: {first_image_path}")
            return False

        img = Image.open(first_image_path).convert("RGB")
        width, height = img.size
        print(f"📸 Loaded image: {width}x{height}")

        # Prepare drawing context directly on the image (no overlay)
        draw = ImageDraw.Draw(img)

        # Get Hindi-compatible font
        font = get_hindi_font(font_size)

        # Wrap text to fit image width (leave 10% margin on each side)
        max_text_width = int(width * 0.8)
        lines = wrap_text(title, font, max_text_width, draw)
        print(f"📝 Text wrapped into {len(lines)} line(s)")

        # Calculate total text block height
        line_spacing = int(font_size * 0.2)
        total_text_height = 0
        line_heights = []

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_height = bbox[3] - bbox[1]
            line_heights.append(line_height)
            total_text_height += line_height

        total_text_height += line_spacing * (len(lines) - 1)

        # Center text vertically
        y = (height - total_text_height) // 2

        # Draw each line centered horizontally
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            x = (width - line_width) // 2

            # Draw text with thick black stroke for visibility
            draw.text(
                (x, y),
                line,
                font=font,
                fill=text_color,
                stroke_width=stroke_width,
                stroke_fill=stroke_color
            )

            y += line_heights[i] + line_spacing

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save the title card
        img.save(output_path, quality=95)
        print(f"✅ Title card saved to: {output_path}")

        return True

    except Exception as e:
        print(f"❌ Failed to create title card: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Test title card generator"""
    # Example usage
    test_image = Path("test_images/1.jpeg")
    test_title = "क्या शिव ने सच में यह किया? 😱"
    output = Path("test_images/0.jpeg")

    print(f"\n🎨 Creating title card...")
    print(f"   Image: {test_image}")
    print(f"   Title: {test_title}")
    print(f"   Output: {output}")

    success = create_title_card(test_image, test_title, output)

    if success:
        print(f"\n✅ Title card created successfully!")
    else:
        print(f"\n❌ Failed to create title card")

if __name__ == "__main__":
    main()
