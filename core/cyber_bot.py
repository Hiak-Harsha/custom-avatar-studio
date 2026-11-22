"""
Option 4: Floating Cyber-Bot Companion System
Generates the complete sprite sheet and emotion expressions for the
Cyber-Bot companion (dual cyan antennae, dark graphite chassis, glowing LED visor, hover thrusters).
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

STUDIO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(STUDIO_ROOT))

BOT_DIR = STUDIO_ROOT / "assets" / "mascots" / "cyber_bot"
BOT_DIR.mkdir(parents=True, exist_ok=True)


def draw_base_bot() -> Tuple[Image.Image, ImageDraw.Draw]:
    w, h = 260, 260
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)

    # 1. Hover shadow on floor
    draw.ellipse([w*0.28, h*0.85, w*0.72, h*0.93], fill=(15, 15, 20, 180))

    # 2. Dual Antennae
    draw.line([w*0.35, h*0.14, w*0.35, h*0.26], fill=(100, 100, 120, 255), width=4)
    draw.ellipse([w*0.32, h*0.08, w*0.38, h*0.15], fill=(0, 240, 255, 255))

    draw.line([w*0.65, h*0.14, w*0.65, h*0.26], fill=(100, 100, 120, 255), width=4)
    draw.ellipse([w*0.62, h*0.08, w*0.68, h*0.15], fill=(0, 240, 255, 255))

    # 3. Main Graphite Chassis
    draw.rounded_rectangle([w*0.20, h*0.26, w*0.80, h*0.72], radius=14, fill=(35, 38, 48, 255), outline=(70, 75, 95, 255), width=3)

    # 4. Glowing Visor Frame
    draw.rounded_rectangle([w*0.28, h*0.36, w*0.72, h*0.56], radius=8, fill=(10, 15, 25, 255), outline=(0, 240, 255, 200), width=2)

    # 5. Blue Hover Thruster
    draw.polygon([(w*0.42, h*0.72), (w*0.58, h*0.72), (w*0.50, h*0.83)], fill=(0, 240, 255, 220))
    draw.polygon([(w*0.46, h*0.72), (w*0.54, h*0.72), (w*0.50, h*0.78)], fill=(255, 255, 255, 255))

    return im, draw, w, h


def create_bot_happy() -> Image.Image:
    """Happy Visor: ^ _ ^"""
    im, draw, w, h = draw_base_bot()
    # Left eye ^
    draw.line([w*0.36, h*0.48, w*0.42, h*0.43], fill=(0, 240, 255, 255), width=3)
    draw.line([w*0.42, h*0.43, w*0.48, h*0.48], fill=(0, 240, 255, 255), width=3)
    # Right eye ^
    draw.line([w*0.52, h*0.48, w*0.58, h*0.43], fill=(0, 240, 255, 255), width=3)
    draw.line([w*0.58, h*0.43, w*0.64, h*0.48], fill=(0, 240, 255, 255), width=3)
    return im


def create_bot_coding() -> Image.Image:
    """Coding / Data Stream: Binary matrix & HUD scanline"""
    im, draw, w, h = draw_base_bot()
    # Binary stream in visor
    draw.rectangle([w*0.35, h*0.43, w*0.39, h*0.49], fill=(0, 240, 255, 255)) # 1
    draw.rectangle([w*0.43, h*0.43, w*0.49, h*0.49], fill=(0, 240, 255, 255)) # 0
    draw.rectangle([w*0.45, h*0.45, w*0.47, h*0.47], fill=(10, 15, 25, 255))
    draw.rectangle([w*0.53, h*0.43, w*0.59, h*0.49], fill=(0, 240, 255, 255)) # 0
    draw.rectangle([w*0.55, h*0.45, w*0.57, h*0.47], fill=(10, 15, 25, 255))
    draw.rectangle([w*0.63, h*0.43, w*0.67, h*0.49], fill=(0, 240, 255, 255)) # 1
    
    # Glowing scanline across visor
    draw.line([w*0.30, h*0.46, w*0.70, h*0.46], fill=(255, 255, 255, 160), width=1)
    return im


def create_bot_cool() -> Image.Image:
    """Cool: Cyber shades / visor glare"""
    im, draw, w, h = draw_base_bot()
    # Diagonal sleek cyan glare
    draw.polygon([(w*0.32, h*0.38), (w*0.40, h*0.38), (w*0.34, h*0.54), (w*0.28, h*0.54)], fill=(0, 255, 255, 200))
    # Confident visor smirk line
    draw.line([w*0.42, h*0.47, w*0.58, h*0.45], fill=(0, 240, 255, 255), width=3)
    return im


def build_all_bot_assets():
    happy = create_bot_happy()
    coding = create_bot_coding()
    cool = create_bot_cool()

    happy.save(str(BOT_DIR / "happy.png"))
    coding.save(str(BOT_DIR / "coding.png"))
    cool.save(str(BOT_DIR / "cool.png"))
    happy.save(str(BOT_DIR / "neutral.png"))

    print("All Cyber-Bot emotion assets generated in:", BOT_DIR)


if __name__ == "__main__":
    from typing import Tuple
    build_all_bot_assets()
