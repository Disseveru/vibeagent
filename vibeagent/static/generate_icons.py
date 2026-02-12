#!/usr/bin/env python3
"""
Generate PWA icons for VibeAgent
Creates icons in various sizes required for Android PWA installation
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_icon(size, output_path):
    """Create a simple icon with gradient background and 'VA' text"""
    # Create image with gradient background
    img = Image.new("RGB", (size, size))
    draw = ImageDraw.Draw(img)

    # Create gradient background (purple to blue)
    for i in range(size):
        # Interpolate between two colors
        ratio = i / size
        r = int(102 * (1 - ratio) + 118 * ratio)
        g = int(126 * (1 - ratio) + 75 * ratio)
        b = int(234 * (1 - ratio) + 162 * ratio)
        draw.rectangle([(0, i), (size, i + 1)], fill=(r, g, b))

    # Add text "VA" in the center
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
        "/System/Library/Fonts/Helvetica.ttc",  # macOS
        "C:\\Windows\\Fonts\\arialbd.ttf",  # Windows
    ]
    try:
        # Try to use a nice font with platform-specific paths
        font_size = size // 2
        font = None
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, font_size)
                break
            except (IOError, OSError):
                continue
        if font is None:
            raise IOError(f"No suitable font found. Tried paths: {', '.join(font_paths)}")
    except (IOError, OSError) as e:
        # Fallback to default font
        print(f"Warning: {e}. Using default font.")
        font = ImageFont.load_default()

    text = "VA"

    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Center the text
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - bbox[1]

    # Draw text with white color
    draw.text((x, y), text, fill="white", font=font)

    # Save the icon
    img.save(output_path, "PNG")
    print(f"Created icon: {output_path} ({size}x{size})")


def main():
    """Generate all required icon sizes"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(script_dir, "icons")

    # Ensure icons directory exists
    os.makedirs(icons_dir, exist_ok=True)

    # Icon sizes for Android PWA
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]

    for size in sizes:
        output_path = os.path.join(icons_dir, f"icon-{size}x{size}.png")
        create_icon(size, output_path)

    print("\nAll icons generated successfully!")
    print(f"Icons saved to: {icons_dir}")


if __name__ == "__main__":
    main()
