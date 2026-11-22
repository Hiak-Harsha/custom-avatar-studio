"""
Pixel Morph & Dissolve Engine
Generates smooth retro pixel-dissolve / glitch transition frames between two names
(e.g., 'hiak' <-> 'harsha') paired with reactive mascot emotion states.
"""
import random
import sys
from pathlib import Path
from typing import List, Tuple
from PIL import Image, ImageDraw

STUDIO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(STUDIO_ROOT))

from core.opencode_font import render_opencode_image, build_text_grid, BG, GRAY, GRAY_SHADOW, WHITE, WHITE_SHADOW

MASCOTS_DIR = STUDIO_ROOT / "assets" / "mascots" / "hiak"
WALLPAPERS_DIR = STUDIO_ROOT / "assets" / "wallpapers"
WHATSAPP_DIR = STUDIO_ROOT / "assets" / "whatsapp"


def composite_frame(text_img: Image.Image, mascot_img: Image.Image, canvas_size=(1920, 1080), spacing=40) -> Image.Image:
    canvas = Image.new("RGB", canvas_size, BG)
    target_h = 144
    
    # Scale mascot to match 144px height
    m_ratio = target_h / mascot_img.height
    target_w = int(mascot_img.width * m_ratio)
    scaled_mascot = mascot_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Text image is scaled to 144px height (scale=18 * 8 rows = 144)
    total_w = text_img.width + spacing + target_w
    start_x = (canvas_size[0] - total_w) // 2
    start_y = (canvas_size[1] - target_h) // 2

    canvas.paste(text_img, (start_x, start_y), text_img)
    canvas.paste(scaled_mascot, (start_x + text_img.width + spacing, start_y), scaled_mascot)
    return canvas


def generate_morph_text_image(text1: str, text2: str, progress: float, scale: int = 18) -> Image.Image:
    """
    Renders an intermediate pixelated dissolve state between text1 and text2.
    progress: 0.0 (100% text1) -> 1.0 (100% text2).
    """
    grid1 = build_text_grid(text1)
    grid2 = build_text_grid(text2)
    
    rows = 8
    cols1 = len(grid1[0]) if grid1 else 0
    cols2 = len(grid2[0]) if grid2 else 0
    max_cols = max(cols1, cols2)
    
    # Pad grids to max_cols (center aligned)
    pad1_left = (max_cols - cols1) // 2
    pad2_left = (max_cols - cols2) // 2
    
    img_w = max_cols * scale
    img_h = rows * scale
    
    im = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    pixels = im.load()
    
    # Determine which pixels show based on progress and pseudo-random pixel dissolve
    random.seed(int(progress * 1000))
    
    for r in range(rows):
        for c in range(max_cols):
            # Sample from text1
            c1 = c - pad1_left
            color1 = grid1[r][c1] if (0 <= c1 < cols1) else BG
            
            # Sample from text2
            c2 = c - pad2_left
            color2 = grid2[r][c2] if (0 <= c2 < cols2) else BG
            
            is_active1 = (color1 != BG)
            is_active2 = (color2 != BG)
            
            chosen_color = None
            
            if progress <= 0.05:
                if is_active1:
                    chosen_color = color1
            elif progress >= 0.95:
                if is_active2:
                    chosen_color = color2
            else:
                # Glitch / Dissolve probability
                threshold = progress
                # Add digital pixel scatter / noise
                noise = random.random()
                
                if noise < threshold:
                    # Tending toward text2
                    if is_active2 and random.random() < 0.85:
                        chosen_color = color2
                    elif is_active1 and random.random() < 0.2:
                        chosen_color = color1
                    elif random.random() < 0.08: # occasional glitch particle
                        chosen_color = random.choice([GRAY, WHITE, GRAY_SHADOW, WHITE_SHADOW])
                else:
                    # Tending toward text1
                    if is_active1 and random.random() < 0.85:
                        chosen_color = color1
                    elif is_active2 and random.random() < 0.2:
                        chosen_color = color2
                    elif random.random() < 0.08:
                        chosen_color = random.choice([GRAY, WHITE, GRAY_SHADOW, WHITE_SHADOW])
            
            if chosen_color:
                r_start = r * scale
                c_start = c * scale
                for y in range(r_start, r_start + scale):
                    for x in range(c_start, c_start + scale):
                        pixels[x, y] = (*chosen_color, 255)
                        
    return im


def build_hiak_harsha_morph_pack():
    """
    Builds the complete HIAK <-> HARSHA pixel morph suite:
    - Wallpaper morph frames
    - Seamless animated looping GIF
    - WhatsApp DP & animated sticker
    """
    out_dir = WALLPAPERS_DIR / "poses_hiak_harsha_morph"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    bot_dir = STUDIO_ROOT / "assets" / "mascots" / "cyber_bot"

    # Sequence of transitions with mascot emotion pairs
    # text1 (HIAK + Brick) -> morph glitch -> text2 (HARSHA + Option 4 Cyber-Bot) -> return
    stages = [
        # 1. Solid HIAK (Neutral Orange Brick)
        (0.0, MASCOTS_DIR / "neutral.png", "1_hiak_solid"),
        # 2. HIAK with sunglasses (Cool Orange Brick)
        (0.0, MASCOTS_DIR / "cool.png", "2_hiak_cool"),
        # 3. Dissolve starts (Mascot thinking)
        (0.3, MASCOTS_DIR / "thinking.png", "3_dissolve_start"),
        # 4. Heavy glitch / particle morph
        (0.65, MASCOTS_DIR / "excited.png", "4_glitch_midway"),
        # 5. HARSHA emerges with Option 4 Cyber-Bot!
        (0.9, bot_dir / "coding.png", "5_harsha_forming"),
        # 6. Solid HARSHA + Cyber-Bot Data Stream!
        (1.0, bot_dir / "coding.png", "6_harsha_cyber_bot_coding"),
        # 7. Solid HARSHA + Cyber-Bot Happy ^_^ !
        (1.0, bot_dir / "happy.png", "7_harsha_cyber_bot_happy"),
        # 8. Dissolve back to HIAK
        (0.5, MASCOTS_DIR / "starstruck.png", "8_morph_return"),
    ]
    
    frames_1080p = []
    frames_wa = []
    
    for idx, (prog, m_path, name) in enumerate(stages):
        m_img = Image.open(str(m_path)).convert("RGBA")
        
        # Render morphed text
        text_img = generate_morph_text_image("hiak", "harsha", prog, scale=18)
        
        # 1080p Wallpaper Frame
        wp = composite_frame(text_img, m_img, canvas_size=(1920, 1080), spacing=40)
        wp_path = out_dir / f"{idx+1}_{name}.png"
        wp.save(str(wp_path))
        frames_1080p.append(wp)
        
        # 600x600 WhatsApp Crop
        wa = composite_frame(text_img, m_img, canvas_size=(600, 600), spacing=25)
        frames_wa.append(wa)
        
    # Save animated GIFs
    gif_1080p = WALLPAPERS_DIR / "hiak_harsha_morph.gif"
    frames_1080p[0].save(
        str(gif_1080p),
        save_all=True,
        append_images=frames_1080p[1:],
        duration=[1200, 1000, 250, 300, 350, 1200, 1000, 350],
        loop=0,
        optimize=True
    )
    
    wa_gif = WHATSAPP_DIR / "hiak_harsha_morph_avatar.gif"
    frames_wa[0].save(
        str(wa_gif),
        save_all=True,
        append_images=frames_wa[1:],
        duration=[1200, 1000, 250, 300, 350, 1200, 1000, 350],
        loop=0,
        optimize=True
    )
    
    print("Morph pack generated successfully!")
    print(f"  Frames: {len(frames_1080p)} in {out_dir}")
    print(f"  Wallpaper GIF: {gif_1080p}")
    print(f"  WhatsApp GIF: {wa_gif}")
    return str(gif_1080p)


if __name__ == "__main__":
    build_hiak_harsha_morph_pack()
