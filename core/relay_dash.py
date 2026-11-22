"""
Option A: Relay Dash Animation Engine
Generates dynamic motion frames where:
1. Claude dashes off to the right with speed lines.
2. Cyber-Bot enters from the left edge with glowing cyan thruster trails.
3. Cyber-Bot glides into docking position beside 'harsha'.
4. On return, Cyber-Bot boosts off to the left and Claude bounds back in from the right!
"""
from collections import deque
import math
from pathlib import Path
import random
import sys
import numpy as np
from PIL import Image, ImageDraw

STUDIO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(STUDIO_ROOT))

from core.opencode_font import render_opencode_image, BG
from core.pixel_morph import generate_morph_text_image
from core.reformat_wallpapers import make_claude_transparent

CLAUDE_DIR = STUDIO_ROOT / "assets" / "mascots" / "claude"
BOT_DIR = STUDIO_ROOT / "assets" / "mascots" / "cyber_bot"
WALLPAPERS_DIR = STUDIO_ROOT / "assets" / "wallpapers"
MORPH_DIR = WALLPAPERS_DIR / "poses_hiak_harsha_morph"

SCREEN_W = 1920
SCREEN_H = 1200
SCALE = 14
TARGET_H = 112
SPACING = 30


def get_scaled_mascot(img: Image.Image, target_h: int = TARGET_H) -> Image.Image:
    """Auto-crops to content and scales to exact target_h."""
    bbox = img.getbbox()
    cropped = img.crop(bbox) if bbox else img
    ratio = target_h / cropped.height
    target_w = int(cropped.width * ratio)
    return cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)


def add_thruster_particles(canvas: Image.Image, bot_x: int, bot_y: int, bot_w: int, bot_h: int, direction: int = 1):
    """
    Draws sleek glowing cyan cyber-thruster particles trailing behind Cyber-Bot.
    direction: 1 = moving right (trail to the left), -1 = moving left (trail to the right).
    """
    draw = ImageDraw.Draw(canvas, "RGBA")
    random.seed(bot_x + bot_y)
    
    # Thruster nozzles are at bottom of bot
    nozzle_y = bot_y + bot_h - 18
    nozzle_x = bot_x + 12 if direction == 1 else bot_x + bot_w - 12
    
    # Particle trail colors: bright cyan, electric blue, soft white
    colors = [
        (0, 229, 255, 230),   # #00e5ff
        (0, 160, 255, 180),   # cyan-blue
        (120, 240, 255, 255), # bright core
        (0, 80, 220, 120)     # outer glow
    ]
    
    num_particles = 45
    for _ in range(num_particles):
        # Distance behind the bot
        dist = random.uniform(10, 220)
        px = nozzle_x - (dist * direction) + random.uniform(-10, 10)
        # Vertical spread flares out slightly
        spread = (dist / 220.0) * 16.0
        py = nozzle_y + random.uniform(-spread, spread)
        
        # Particle size (shrinks as it gets farther)
        p_size = max(2, int((1.0 - dist / 240.0) * 6))
        color = random.choice(colors)
        
        # Draw glowing particle block
        draw.rectangle([px, py, px + p_size, py + p_size], fill=color)


def add_dash_lines(canvas: Image.Image, x: int, y: int, h: int):
    """Draws retro horizontal speed lines behind Claude dashing right."""
    draw = ImageDraw.Draw(canvas, "RGBA")
    random.seed(x + y)
    
    line_colors = [
        (203, 111, 86, 180),  # Claude terracotta
        (128, 128, 128, 140), # Gray
        (238, 238, 238, 160)  # White speed spark
    ]
    
    for _ in range(12):
        lx_start = x - random.uniform(20, 140)
        lx_end = x - random.uniform(5, 25)
        ly = y + random.uniform(15, h - 15)
        lw = random.randint(2, 4)
        col = random.choice(line_colors)
        draw.line([(lx_start, ly), (lx_end, ly)], fill=col, width=lw)


def generate_relay_dash_suite():
    print("🚀 Generating Option A: Relay Dash Animation Suite...")
    
    # 1. Base logos & mascots
    hiak_logo = render_opencode_image("hiak", scale=SCALE, bg_color=None)
    harsha_logo = render_opencode_image("harsha", scale=SCALE, bg_color=None)
    
    claude_neutral = get_scaled_mascot(make_claude_transparent(CLAUDE_DIR / "neutral.png"))
    claude_dash = get_scaled_mascot(make_claude_transparent(CLAUDE_DIR / "determined.png"))
    claude_land = get_scaled_mascot(make_claude_transparent(CLAUDE_DIR / "playful.png"))
    
    bot_happy = get_scaled_mascot(Image.open(str(BOT_DIR / "happy.png")).convert("RGBA"))
    bot_coding = get_scaled_mascot(Image.open(str(BOT_DIR / "coding.png")).convert("RGBA"))

    # Layout targets:
    # HIAK lockup: total_w = 266 + 30 + 155 = 451. start_x = (1920 - 451)//2 = 734
    hiak_x, hiak_y = 734, 544
    claude_rest_x, claude_rest_y = hiak_x + hiak_logo.width + SPACING, 544
    
    # HARSHA lockup: total_w = 406 + 30 + 79 = 515. start_x = (1920 - 515)//2 = 702
    harsha_x, harsha_y = 702, 544
    bot_dock_x, bot_dock_y = harsha_x + harsha_logo.width + SPACING, 544
    
    morph_center_x = (SCREEN_W - 406) // 2
    
    frames = []
    
    # =========================================================================
    # FRAME 0: Solid HIAK + Resting Claude Mascot (1800ms)
    # =========================================================================
    f0 = Image.new("RGB", (SCREEN_W, SCREEN_H), BG)
    f0.paste(hiak_logo, (hiak_x, hiak_y), hiak_logo)
    f0.paste(claude_neutral, (claude_rest_x, claude_rest_y), claude_neutral)
    f0.save(str(MORPH_DIR / "1_1_hiak_solid.png"), quality=95)
    f0.save(str(MORPH_DIR / "2_2_hiak_cool.png"), quality=95)
    frames.append(f0)
    
    # =========================================================================
    # FRAME 1: Dissolve Begins -> Claude Dashes Right! (140ms)
    # =========================================================================
    f1 = Image.new("RGB", (SCREEN_W, SCREEN_H), BG)
    t1 = generate_morph_text_image("hiak", "harsha", 0.25, scale=SCALE)
    f1.paste(t1, (morph_center_x, hiak_y), t1)
    # Claude dashes rightward with determined expression
    dash_x = claude_rest_x + 320 # X: 1350
    add_dash_lines(f1, dash_x, claude_rest_y, TARGET_H)
    f1.paste(claude_dash, (dash_x, claude_rest_y), claude_dash)
    f1.save(str(MORPH_DIR / "3_3_dissolve_start.png"), quality=95)
    frames.append(f1)
    
    # =========================================================================
    # FRAME 2: Midway Pixel Storm -> Cyber-Bot Enters from Left! (160ms)
    # =========================================================================
    f2 = Image.new("RGB", (SCREEN_W, SCREEN_H), BG)
    t2 = generate_morph_text_image("hiak", "harsha", 0.55, scale=SCALE)
    f2.paste(t2, (morph_center_x, hiak_y), t2)
    # Cyber-Bot streaks in from left edge with glowing cyan thrusters!
    bot_in_x = 280
    bot_in_y = 525 # floating slightly higher
    add_thruster_particles(f2, bot_in_x, bot_in_y, bot_happy.width, TARGET_H, direction=1)
    f2.paste(bot_happy, (bot_in_x, bot_in_y), bot_happy)
    f2.save(str(MORPH_DIR / "4_4_glitch_midway.png"), quality=95)
    frames.append(f2)
    
    # =========================================================================
    # FRAME 3: Resolving into HARSHA -> Cyber-Bot Gliding into Dock (180ms)
    # =========================================================================
    f3 = Image.new("RGB", (SCREEN_W, SCREEN_H), BG)
    t3 = generate_morph_text_image("hiak", "harsha", 0.85, scale=SCALE)
    f3.paste(t3, (morph_center_x, hiak_y), t3)
    # Cyber-Bot decelerating toward its docking position
    bot_mid_x = bot_dock_x - 180 # X: ~958
    bot_mid_y = 538
    add_thruster_particles(f3, bot_mid_x, bot_mid_y, bot_happy.width, TARGET_H, direction=1)
    f3.paste(bot_happy, (bot_mid_x, bot_mid_y), bot_happy)
    f3.save(str(MORPH_DIR / "5_5_harsha_forming.png"), quality=95)
    frames.append(f3)
    
    # =========================================================================
    # FRAME 4: Solid HARSHA + Cyber-Bot Docked & Happy! (2600ms)
    # =========================================================================
    f4 = Image.new("RGB", (SCREEN_W, SCREEN_H), BG)
    f4.paste(harsha_logo, (harsha_x, harsha_y), harsha_logo)
    f4.paste(bot_coding, (bot_dock_x, bot_dock_y), bot_coding)
    f4.save(str(MORPH_DIR / "6_6_harsha_coding.png"), quality=95)
    f4.save(str(MORPH_DIR / "6_6_harsha_cyber_bot_coding.png"), quality=95)
    f4.save(str(MORPH_DIR / "7_7_harsha_cyber_bot_happy.png"), quality=95)
    frames.append(f4)
    
    # =========================================================================
    # FRAME 5: Return Triggered -> Cyber-Bot Boosts Off Left! (160ms)
    # =========================================================================
    f5 = Image.new("RGB", (SCREEN_W, SCREEN_H), BG)
    t5 = generate_morph_text_image("hiak", "harsha", 0.70, scale=SCALE)
    f5.paste(t5, (morph_center_x, hiak_y), t5)
    # Cyber-Bot boosts off to the left!
    boost_x = 340
    boost_y = 530
    add_thruster_particles(f5, boost_x, boost_y, bot_happy.width, TARGET_H, direction=-1)
    f5.paste(bot_happy, (boost_x, boost_y), bot_happy)
    f5.save(str(MORPH_DIR / "8_8_morph_return.png"), quality=95)
    frames.append(f5)
    
    # =========================================================================
    # FRAME 6: Claude Bounds Back In from Right! (180ms)
    # =========================================================================
    f6 = Image.new("RGB", (SCREEN_W, SCREEN_H), BG)
    t6 = generate_morph_text_image("hiak", "harsha", 0.30, scale=SCALE)
    f6.paste(t6, (morph_center_x, hiak_y), t6)
    # Claude bounds back in from the right edge
    land_x = claude_rest_x + 360 # X: 1390
    add_dash_lines(f6, land_x, claude_rest_y, TARGET_H)
    f6.paste(claude_land, (land_x, claude_rest_y), claude_land)
    f6.save(str(MORPH_DIR / "9_9_morph_return_mid.png"), quality=95)
    frames.append(f6)
    
    # Save animated GIF suite with disposal=2 (380-400ms transit for clear cinematic visibility)
    durations = [2400, 380, 400, 380, 2800, 380, 400]
    disposals = [2] * len(frames)
    
    for fname in ["hiak_harsha_morph.gif", "hiak_harsha_morph_v2.gif", "hiak_harsha_morph_v3.gif", "hiak_harsha_morph_v4.gif"]:
        gif_path = WALLPAPERS_DIR / fname
        frames[0].save(
            str(gif_path),
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            disposal=disposals,
            loop=0,
            optimize=False
        )
        
    print(f"✅ Option A: Relay Dash Animation successfully generated ({len(frames)} frames)!")


if __name__ == "__main__":
    generate_relay_dash_suite()
