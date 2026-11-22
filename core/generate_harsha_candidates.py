"""
Generates 4 distinct character design candidates for HARSHA:
1. Cyber-Tech Brick Mascot (Cyan over-ear headphones + AR developer glasses)
2. Neon-Cyan Electric Brick (Color-shifted sleek cyan/teal palette with glowing eyes)
3. Hacker Hoodie & Coffee Brick (Black dev hoodie + steaming pixel coffee cup)
4. Cyber-Bot Floating Companion (Futuristic hovering pixel bot with glowing visor)
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

STUDIO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(STUDIO_ROOT))

from core.opencode_font import render_opencode_image, BG
from core.generator import composite_lockup

MASCOTS_DIR = STUDIO_ROOT / "assets" / "mascots" / "hiak"
CANDIDATES_DIR = STUDIO_ROOT / "assets" / "mascots" / "candidates"
CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)
WALLPAPERS_DIR = STUDIO_ROOT / "assets" / "wallpapers"


def create_candidate_1_cyber_tech() -> Image.Image:
    """Cyber-Tech Brick: Orange brick body + Glowing Cyan Headphones + AR Tech Glasses"""
    base = Image.open(str(MASCOTS_DIR / "coding.png")).convert("RGBA")
    w, h = base.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # 1. Glowing Cyan Headphones
    # Left ear cup
    draw.rounded_rectangle([w*0.06, h*0.28, w*0.19, h*0.52], radius=6, fill=(0, 240, 255, 255), outline=(0, 180, 200, 255), width=2)
    # Right ear cup
    draw.rounded_rectangle([w*0.81, h*0.28, w*0.94, h*0.52], radius=6, fill=(0, 240, 255, 255), outline=(0, 180, 200, 255), width=2)
    # Headband arc over top
    draw.arc([w*0.12, h*0.02, w*0.88, h*0.48], start=180, end=0, fill=(0, 240, 255, 255), width=5)
    
    # 2. Sleek Dark AR Tech Glasses with cyan glow reflection
    draw.rounded_rectangle([w*0.28, h*0.35, w*0.72, h*0.45], radius=3, fill=(15, 15, 20, 240), outline=(0, 240, 255, 200), width=2)
    draw.line([w*0.32, h*0.37, w*0.48, h*0.37], fill=(0, 255, 255, 200), width=2)
    draw.line([w*0.54, h*0.37, w*0.68, h*0.37], fill=(0, 255, 255, 200), width=2)
    
    result = Image.alpha_composite(base, overlay)
    return result


def create_candidate_2_neon_cyan() -> Image.Image:
    """Neon-Cyan Electric Brick: Color-shifted cool cyan body with electric white/blue highlights"""
    base = Image.open(str(MASCOTS_DIR / "coding.png")).convert("RGBA")
    pixels = base.load()
    w, h = base.size
    
    # Shift orange hues to cyan / electric teal
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a > 40:
                # If orange/terracotta body (r > g and r > b)
                if r > 120 and r > b * 1.5:
                    # Map to vivid cyan/teal
                    avg = (r + g) // 2
                    new_r = int(avg * 0.12)
                    new_g = int(avg * 0.88)
                    new_b = int(avg * 0.98)
                    pixels[x, y] = (new_r, new_g, new_b, a)
                    
    # Add electric glowing eyes/visor overlay
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    # Glowing white/cyan eye highlights
    draw.rectangle([w*0.38, h*0.35, w*0.44, h*0.42], fill=(255, 255, 255, 255))
    draw.rectangle([w*0.58, h*0.35, w*0.64, h*0.42], fill=(255, 255, 255, 255))
    result = Image.alpha_composite(base, overlay)
    return result


def create_candidate_3_hacker_hoodie() -> Image.Image:
    """Hacker Hoodie & Coffee: Dark developer hoodie + Steaming pixel coffee mug"""
    base = Image.open(str(MASCOTS_DIR / "coding.png")).convert("RGBA")
    w, h = base.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # 1. Dark charcoal/purple developer hoodie rim around brick
    draw.rounded_rectangle([w*0.14, h*0.15, w*0.86, h*0.65], radius=10, outline=(35, 35, 45, 255), width=7)
    draw.arc([w*0.18, h*0.08, w*0.82, h*0.35], start=180, end=0, fill=(30, 30, 40, 255), width=8)
    
    # 2. Steaming coffee mug next to laptop
    mug_x, mug_y = int(w * 0.78), int(h * 0.58)
    draw.rectangle([mug_x, mug_y, mug_x + 18, mug_y + 22], fill=(220, 220, 230, 255), outline=(60, 60, 70, 255), width=2)
    # Mug handle
    draw.arc([mug_x + 14, mug_y + 4, mug_x + 24, mug_y + 18], start=270, end=90, fill=(200, 200, 210, 255), width=2)
    # Steam waves
    draw.line([mug_x + 6, mug_y - 3, mug_x + 6, mug_y - 9], fill=(160, 160, 180, 180), width=2)
    draw.line([mug_x + 12, mug_y - 5, mug_x + 12, mug_y - 12], fill=(160, 160, 180, 180), width=2)
    
    # Dev sticker on laptop lid
    draw.rectangle([w*0.48, h*0.68, w*0.54, h*0.74], fill=(0, 240, 255, 255))
    
    result = Image.alpha_composite(base, overlay)
    return result


def create_candidate_4_cyber_bot() -> Image.Image:
    """Cyber-Bot: Futuristic floating hover companion with glowing LED matrix eye & antennae"""
    w, h = 260, 260
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    
    # Hover shadow on floor
    draw.ellipse([w*0.30, h*0.84, w*0.70, h*0.92], fill=(15, 15, 20, 180))
    
    # Dual antennae
    draw.line([w*0.35, h*0.14, w*0.35, h*0.26], fill=(100, 100, 120, 255), width=4)
    draw.ellipse([w*0.32, h*0.08, w*0.38, h*0.15], fill=(0, 240, 255, 255))
    
    draw.line([w*0.65, h*0.14, w*0.65, h*0.26], fill=(100, 100, 120, 255), width=4)
    draw.ellipse([w*0.62, h*0.08, w*0.68, h*0.15], fill=(0, 240, 255, 255))
    
    # Main Bot Body (Chiseled modern dark graphite chassis)
    draw.rounded_rectangle([w*0.20, h*0.26, w*0.80, h*0.72], radius=14, fill=(35, 38, 48, 255), outline=(70, 75, 95, 255), width=3)
    
    # Glowing Cyan Visor Screen
    draw.rounded_rectangle([w*0.28, h*0.36, w*0.72, h*0.56], radius=8, fill=(10, 15, 25, 255), outline=(0, 240, 255, 200), width=2)
    
    # Expressive LED pixel eyes on visor (Happy ^_^)
    # Left eye ^
    draw.line([w*0.36, h*0.48, w*0.42, h*0.43], fill=(0, 240, 255, 255), width=3)
    draw.line([w*0.42, h*0.43, w*0.48, h*0.48], fill=(0, 240, 255, 255), width=3)
    # Right eye ^
    draw.line([w*0.52, h*0.48, w*0.58, h*0.43], fill=(0, 240, 255, 255), width=3)
    draw.line([w*0.58, h*0.43, w*0.64, h*0.48], fill=(0, 240, 255, 255), width=3)
    
    # Hover thruster glow at bottom
    draw.polygon([(w*0.42, h*0.72), (w*0.58, h*0.72), (w*0.50, h*0.82)], fill=(0, 240, 255, 220))
    draw.polygon([(w*0.46, h*0.72), (w*0.54, h*0.72), (w*0.50, h*0.78)], fill=(255, 255, 255, 255))
    
    return im


def generate_all_candidates():
    # Render base HARSHA logo
    harsha_logo = render_opencode_image("harsha", scale=18, bg_color=None)
    
    candidates = [
        ("candidate_1_cyber_tech", create_candidate_1_cyber_tech(), "Option 1: Cyber-Tech Brick (Cyan Headphones + AR Glasses)"),
        ("candidate_2_neon_cyan", create_candidate_2_neon_cyan(), "Option 2: Neon Cyan Electric Brick (Full Color-Shift)"),
        ("candidate_3_hacker_hoodie", create_candidate_3_hacker_hoodie(), "Option 3: Dev Hoodie & Steaming Coffee Brick"),
        ("candidate_4_cyber_bot", create_candidate_4_cyber_bot(), "Option 4: Floating Cyber-Bot Companion (LED Visor)")
    ]
    
    for slug, mascot_img, title in candidates:
        # Save isolated mascot PNG
        m_path = CANDIDATES_DIR / f"{slug}.png"
        mascot_img.save(str(m_path))
        
        # Save 1920x1080 wallpaper lockup with HARSHA logo
        wall = composite_lockup(harsha_logo, mascot_img, canvas_size=(1920, 1080), spacing=40)
        wall_path = CANDIDATES_DIR / f"{slug}_wallpaper.png"
        wall.save(str(wall_path))
        print(f"Generated {slug}: {wall_path}")


if __name__ == "__main__":
    generate_all_candidates()
