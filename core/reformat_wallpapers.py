"""
Reformat Wallpaper Suite for Medium Scale & Exact 1920x1200 Center Alignment
ONLY uses the designated cartoons:
- HIAK: Designated Orange Brick Mascot
- HARSHA: Designated Option 4 Floating Cyber-Bot
NO intermediate or unrelated cartoons appear during the transition!
"""
import sys
from pathlib import Path
from PIL import Image

STUDIO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(STUDIO_ROOT))

from core.opencode_font import render_opencode_image, BG
from core.pixel_morph import generate_morph_text_image

MASCOTS_DIR = STUDIO_ROOT / "assets" / "mascots" / "hiak"
BOT_DIR = STUDIO_ROOT / "assets" / "mascots" / "cyber_bot"
WALLPAPERS_DIR = STUDIO_ROOT / "assets" / "wallpapers"
POSES_DIR = WALLPAPERS_DIR / "poses"
MORPH_DIR = WALLPAPERS_DIR / "poses_hiak_harsha_morph"

SCREEN_W = 1920
SCREEN_H = 1200
SCALE = 14          # Medium OpenCode scale: 8 rows * 14px = 112px height
TARGET_H = 112      # Exact lockup height
SPACING = 30        # Spacing between logo and mascot


def composite_centered(text_img: Image.Image, mascot_img: Image.Image, canvas_w=SCREEN_W, canvas_h=SCREEN_H) -> Image.Image:
    canvas = Image.new("RGB", (canvas_w, canvas_h), BG)
    
    # Scale mascot to match TARGET_H (112px)
    m_ratio = TARGET_H / mascot_img.height
    target_w = int(mascot_img.width * m_ratio)
    scaled_mascot = mascot_img.resize((target_w, TARGET_H), Image.Resampling.LANCZOS)
    
    # Calculate exact center bounding box
    total_w = text_img.width + SPACING + target_w
    start_x = (canvas_w - total_w) // 2
    start_y = (canvas_h - TARGET_H) // 2

    canvas.paste(text_img, (start_x, start_y), text_img)
    canvas.paste(scaled_mascot, (start_x + text_img.width + SPACING, start_y), scaled_mascot)
    return canvas


def reformat_all():
    print(f"📐 Reformatting wallpapers: ONLY designated cartoons (Orange Brick for HIAK, Cyber-Bot for HARSHA)...")
    
    # 1. Base HIAK logo at scale 14
    hiak_logo = render_opencode_image("hiak", scale=SCALE, bg_color=None)
    
    # 2. Re-render 7 HIAK poses in assets/wallpapers/poses (Designated Orange Brick poses)
    POSES_DIR.mkdir(parents=True, exist_ok=True)
    pose_files = [
        ("1_neutral.png", "neutral.png"),
        ("2_happy.png", "happy.png"),
        ("3_wave.png", "excited.png"),
        ("4_idea.png", "idea.png"),
        ("5_cool.png", "cool.png"),
        ("6_coding.png", "coding.png"),
        ("7_sleepy.png", "sleepy.png")
    ]
    for out_name, m_file in pose_files:
        m_img = Image.open(str(MASCOTS_DIR / m_file)).convert("RGBA")
        wp = composite_centered(hiak_logo, m_img)
        wp.save(str(POSES_DIR / out_name), quality=95)
    print("  ✅ 7 HIAK desktop poses updated (1920x1200 medium centered)")

    # 3. Clean Morph Sequence: ONLY the designated Orange Brick & Option 4 Cyber-Bot!
    # No random / intermediate cartoon faces!
    MORPH_DIR.mkdir(parents=True, exist_ok=True)
    
    # Designated mascot assets
    brick_img = Image.open(str(MASCOTS_DIR / "neutral.png")).convert("RGBA")
    cyber_bot_img = Image.open(str(BOT_DIR / "happy.png")).convert("RGBA")

    stages = [
        # Stage 1: Pure HIAK + Designated Orange Brick
        (0.0, brick_img, "1_1_hiak_solid.png"),
        (0.0, brick_img, "2_2_hiak_cool.png"),
        # Stage 2: Dissolve starts: HIAK text glitches, Orange Brick stays clean!
        (0.3, brick_img, "3_3_dissolve_start.png"),
        # Stage 3: Glitch midway: text morphing, Cyber-Bot takes over!
        (0.7, cyber_bot_img, "4_4_glitch_midway.png"),
        # Stage 4: Pure HARSHA + Designated Option 4 Cyber-Bot!
        (1.0, cyber_bot_img, "5_5_harsha_forming.png"),
        (1.0, cyber_bot_img, "6_6_harsha_cyber_bot_coding.png"),
        (1.0, cyber_bot_img, "7_7_harsha_cyber_bot_happy.png"),
        # Stage 5: Return morph: text dissolves back to HIAK with Orange Brick!
        (0.4, brick_img, "8_8_morph_return.png"),
    ]
    
    frames_1200p = []
    for prog, m_img, out_name in stages:
        text_img = generate_morph_text_image("hiak", "harsha", prog, scale=SCALE)
        wp = composite_centered(text_img, m_img)
        wp.save(str(MORPH_DIR / out_name), quality=95)
        frames_1200p.append(wp)
        
    # Alias for backwards compatibility
    frames_1200p[5].save(str(MORPH_DIR / "6_6_harsha_coding.png"))

    # Save animated morph GIF
    gif_path = WALLPAPERS_DIR / "hiak_harsha_morph.gif"
    frames_1200p[0].save(
        str(gif_path),
        save_all=True,
        append_images=frames_1200p[1:],
        duration=[1200, 1000, 180, 200, 300, 1500, 1200, 250],
        loop=0,
        optimize=True
    )
    print("  ✅ Morph sequence & animated GIF updated: ONLY designated cartoons!")


if __name__ == "__main__":
    reformat_all()
