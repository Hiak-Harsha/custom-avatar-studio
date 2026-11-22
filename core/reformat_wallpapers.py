"""
Reformat Wallpaper Suite for Medium Scale & Exact 1920x1200 Center Alignment
DESIGNATED MASCOTS:
- HIAK: Designated Brown Claude Mascot (assets/mascots/claude/)
- HARSHA: Designated Option 4 Floating Cyber-Bot (assets/mascots/cyber_bot/)

EQUAL SIZING:
- Auto-crops transparent borders from both mascots so they have identical visual height (112px).
- Claude and Cyber-Bot are both matched to the exact height of the OpenCode logo!

STRICT DISPLAY RULE:
- BEFORE hover / default state: Shows HIAK with designated Brown Claude Mascot
- WHILE ANIMATING / PIXELATING: Shows ONLY the glitching/dissolving PIXELS! NO CARTOON MASCOT AT ALL!
- AFTER hover / HARSHA state: Shows HARSHA with designated Option 4 Floating Cyber-Bot
- WHILE RETURNING / PIXELATING: Shows ONLY the glitching/dissolving PIXELS! NO CARTOON MASCOT AT ALL!

Uses GIF disposal=2 (Restore to background) so no previous frame pixels leak through!
"""
from collections import deque
from pathlib import Path
import sys
import numpy as np
from PIL import Image

STUDIO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(STUDIO_ROOT))

from core.opencode_font import render_opencode_image, BG
from core.pixel_morph import generate_morph_text_image

CLAUDE_DIR = STUDIO_ROOT / "assets" / "mascots" / "claude"
BOT_DIR = STUDIO_ROOT / "assets" / "mascots" / "cyber_bot"
WALLPAPERS_DIR = STUDIO_ROOT / "assets" / "wallpapers"
POSES_DIR = WALLPAPERS_DIR / "poses"
MORPH_DIR = WALLPAPERS_DIR / "poses_hiak_harsha_morph"

SCREEN_W = 1920
SCREEN_H = 1200
SCALE = 14          # Medium OpenCode scale: 8 rows * 14px = 112px height
TARGET_H = 112      # Exact lockup height
SPACING = 30        # Spacing between logo and mascot


def make_claude_transparent(img_path) -> Image.Image:
    """Removes the outer cream/tan background from the Claude mascot images."""
    im = Image.open(str(img_path)).convert("RGBA")
    arr = np.array(im)
    h, w = arr.shape[:2]
    
    corners = [arr[0, 0, :3], arr[0, w-1, :3], arr[h-1, 0, :3], arr[h-1, w-1, :3]]
    bg_ref = np.median(corners, axis=0).astype(float)
    
    diff = np.linalg.norm(arr[:, :, :3].astype(float) - bg_ref, axis=2)
    is_bg_candidate = diff < 38
    
    visited = np.zeros((h, w), dtype=bool)
    queue = deque()
    
    for x in range(w):
        if is_bg_candidate[0, x]: queue.append((0, x)); visited[0, x] = True
        if is_bg_candidate[h-1, x]: queue.append((h-1, x)); visited[h-1, x] = True
    for y in range(h):
        if is_bg_candidate[y, 0]: queue.append((y, 0)); visited[y, 0] = True
        if is_bg_candidate[y, w-1]: queue.append((y, w-1)); visited[y, w-1] = True
        
    while queue:
        cy, cx = queue.popleft()
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx] and is_bg_candidate[ny, nx]:
                visited[ny, nx] = True
                queue.append((ny, nx))
                
    arr[visited, 3] = 0
    return Image.fromarray(arr)


def composite_centered(text_img: Image.Image, mascot_img: Image.Image = None, canvas_w=SCREEN_W, canvas_h=SCREEN_H) -> Image.Image:
    canvas = Image.new("RGB", (canvas_w, canvas_h), BG)
    
    if mascot_img is not None:
        # Auto-crop content bounding box to eliminate empty border padding
        bbox = mascot_img.getbbox()
        if bbox:
            cropped = mascot_img.crop(bbox)
        else:
            cropped = mascot_img
            
        # Scale cropped mascot so its actual height is TARGET_H (112px) - matching text height & Cyber-Bot!
        m_ratio = TARGET_H / cropped.height
        target_w = int(cropped.width * m_ratio)
        scaled_mascot = cropped.resize((target_w, TARGET_H), Image.Resampling.LANCZOS)
        
        # Calculate center bounding box for text + mascot
        total_w = text_img.width + SPACING + target_w
        start_x = (canvas_w - total_w) // 2
        start_y = (canvas_h - TARGET_H) // 2

        canvas.paste(text_img, (start_x, start_y), text_img)
        canvas.paste(scaled_mascot, (start_x + text_img.width + SPACING, start_y), scaled_mascot)
    else:
        # PURE PIXELS ONLY during animation: NO CARTOON MASCOT SHOWN!
        start_x = (canvas_w - text_img.width) // 2
        start_y = (canvas_h - TARGET_H) // 2
        canvas.paste(text_img, (start_x, start_y), text_img)
        
    return canvas


def reformat_all():
    print("📐 Reformatting wallpapers with EQUAL-SIZED Brown Claude Mascot & Option 4 Cyber-Bot...")
    
    # 1. Base HIAK logo at scale 14
    hiak_logo = render_opencode_image("hiak", scale=SCALE, bg_color=None)
    
    # 2. Re-render 7 HIAK poses with the full-sized Brown Claude Mascot!
    POSES_DIR.mkdir(parents=True, exist_ok=True)
    pose_files = [
        ("1_neutral.png", "neutral.png"),
        ("2_happy.png", "happy.png"),
        ("3_wave.png", "excited.png"),
        ("4_idea.png", "idea.png"),
        ("5_cool.png", "cool.png"),
        ("6_coding.png", "thinking.png"),
        ("7_sleepy.png", "sleepy.png")
    ]
    for out_name, m_file in pose_files:
        m_img = make_claude_transparent(CLAUDE_DIR / m_file)
        wp = composite_centered(hiak_logo, m_img)
        wp.save(str(POSES_DIR / out_name), quality=95)
    print("  ✅ 7 HIAK desktop poses updated (Brown Claude mascot scaled to equal height 112px)")

    # 3. Morph Sequence:
    MORPH_DIR.mkdir(parents=True, exist_ok=True)
    
    claude_img = make_claude_transparent(CLAUDE_DIR / "neutral.png")
    cyber_bot_img = Image.open(str(BOT_DIR / "happy.png")).convert("RGBA")

    stages = [
        # Frame 0: BEFORE hover -> Pure HIAK + Full-sized Brown Claude Mascot
        (0.0, claude_img, "1_1_hiak_solid.png"),
        # Frame 1: WHILE ANIMATING -> PURE PIXELS ONLY! NO MASCOT!
        (0.25, None, "3_3_dissolve_start.png"),
        # Frame 2: HEAVY GLITCH -> PURE PIXELS ONLY! NO MASCOT!
        (0.55, None, "4_4_glitch_midway.png"),
        # Frame 3: RESOLVING INTO HARSHA -> PURE PIXELS ONLY! NO MASCOT!
        (0.85, None, "5_5_harsha_forming.png"),
        # Frame 4: AFTER hover -> Pure HARSHA + Full-sized Option 4 Cyber-Bot!
        (1.0, cyber_bot_img, "6_6_harsha_cyber_bot_coding.png"),
        # Frame 5: WHILE RETURNING -> PURE PIXELS ONLY! NO MASCOT!
        (0.65, None, "8_8_morph_return.png"),
        # Frame 6: GLITCH RETURNING -> PURE PIXELS ONLY! NO MASCOT!
        (0.30, None, "9_9_morph_return_mid.png"),
    ]
    
    frames_1200p = []
    for prog, m_img, out_name in stages:
        text_img = generate_morph_text_image("hiak", "harsha", prog, scale=SCALE)
        wp = composite_centered(text_img, m_img)
        wp.save(str(MORPH_DIR / out_name), quality=95)
        frames_1200p.append(wp)
        
    # Aliases for backwards compatibility
    frames_1200p[4].save(str(MORPH_DIR / "6_6_harsha_coding.png"))
    frames_1200p[0].save(str(MORPH_DIR / "2_2_hiak_cool.png"))
    frames_1200p[4].save(str(MORPH_DIR / "7_7_harsha_cyber_bot_happy.png"))

    # Save animated morph GIFs (hiak_harsha_morph.gif, v2, v3) with disposal=2
    durations = [2400, 140, 160, 180, 2800, 160, 180]
    disposals = [2] * len(frames_1200p)
    
    for fname in ["hiak_harsha_morph.gif", "hiak_harsha_morph_v2.gif", "hiak_harsha_morph_v3.gif"]:
        gif_path = WALLPAPERS_DIR / fname
        frames_1200p[0].save(
            str(gif_path),
            save_all=True,
            append_images=frames_1200p[1:],
            duration=durations,
            disposal=disposals,
            loop=0,
            optimize=False
        )
    print("  ✅ All GIF versions generated with disposal=2 and equal character sizes!")


if __name__ == "__main__":
    reformat_all()
