"""
Multi-User Persona & Asset Generation Engine
Synthesizes the complete OpenCode pixel typography + expressive brick mascot pack
for ANY custom name or persona:
- 7 Sequential 1080p Desktop Wallpaper Poses
- Animated Terminal Background GIF
- 24-bit TrueColor ANSI Startup Banner
- WhatsApp Profile Picture, Animated Avatar GIF, & Mobile Chat Wallpaper
- Automatic Profile Registration in styles.json
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from PIL import Image

STUDIO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(STUDIO_ROOT))

from core.opencode_font import render_opencode_image, generate_ansi_banner, BG, GRAY, WHITE

MASCOTS_DIR = STUDIO_ROOT / "assets" / "mascots" / "hiak"
WALLPAPERS_DIR = STUDIO_ROOT / "assets" / "wallpapers"
WHATSAPP_DIR = STUDIO_ROOT / "assets" / "whatsapp"
BANNERS_DIR = STUDIO_ROOT / "assets" / "banners"
AVATARS_DIR = STUDIO_ROOT / "assets" / "avatars"
CONFIG_FILE = STUDIO_ROOT / "config" / "styles.json"

POSE_MAPPING = [
    ("1_neutral", "neutral.png"),
    ("2_happy", "happy.png"),
    ("3_wave", "excited.png"),
    ("4_idea", "idea.png"),
    ("5_cool", "cool.png"),
    ("6_coding", "coding.png"),
    ("7_sleepy", "sleepy.png"),
]


def composite_lockup(logo_img: Image.Image, mascot_img: Image.Image, canvas_size=(1920, 1080), spacing=35) -> Image.Image:
    """
    Composites the pixel logo and the mascot character side-by-side centered on a #0A0A0A canvas.
    """
    canvas = Image.new("RGB", canvas_size, BG)

    # Scale mascot to match logo height
    target_h = logo_img.height
    scale_factor = target_h / mascot_img.height
    target_w = int(mascot_img.width * scale_factor)
    scaled_mascot = mascot_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    total_w = logo_img.width + spacing + target_w
    start_x = (canvas_size[0] - total_w) // 2
    start_y = (canvas_size[1] - target_h) // 2

    # Paste logo
    canvas.paste(logo_img, (start_x, start_y), logo_img)

    # Paste mascot
    mascot_x = start_x + logo_img.width + spacing
    canvas.paste(scaled_mascot, (mascot_x, start_y), scaled_mascot)

    return canvas


def generate_persona(name: str, display_user: str = "Developer", persona: str = "Creator & Coder") -> Dict[str, str]:
    """
    Full pipeline to generate all assets for a given custom name.
    """
    clean_name = name.strip()
    slug = clean_name.lower().replace(" ", "_")

    # 1. Output directories
    poses_dir = WALLPAPERS_DIR / f"poses_{slug}"
    poses_dir.mkdir(parents=True, exist_ok=True)
    WHATSAPP_DIR.mkdir(parents=True, exist_ok=True)
    BANNERS_DIR.mkdir(parents=True, exist_ok=True)
    AVATARS_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Render base OpenCode Logo
    logo_img = render_opencode_image(clean_name, scale=18, bg_color=None)
    logo_path = AVATARS_DIR / f"{slug}_opencode.png"
    logo_img.save(str(logo_path))

    # 3. Generate 24-bit TrueColor ANSI Banner
    banner_path = BANNERS_DIR / f"{slug}.ans"
    generate_ansi_banner(clean_name, user_name=display_user, persona=persona, output_path=str(banner_path))

    # 4. Generate 7 Desktop Wallpaper Poses
    pose_paths = []
    pose_frames = []

    for prefix, mascot_file in POSE_MAPPING:
        m_path = MASCOTS_DIR / mascot_file
        if not m_path.exists():
            continue
        m_img = Image.open(str(m_path)).convert("RGBA")
        wallpaper = composite_lockup(logo_img, m_img, canvas_size=(1920, 1080), spacing=40)
        
        out_p = poses_dir / f"{prefix}.png"
        wallpaper.save(str(out_p), quality=95)
        pose_paths.append(str(out_p))
        pose_frames.append(wallpaper)

    # 5. Generate Animated Terminal Background GIF (1920x1080)
    gif_path = WALLPAPERS_DIR / f"{slug}_moving_mascot.gif"
    if pose_frames:
        pose_frames[0].save(
            str(gif_path),
            save_all=True,
            append_images=pose_frames[1:],
            duration=700,
            loop=0,
            optimize=True
        )

    # 6. Generate WhatsApp Square DP (600x600) & Animated Avatar
    wa_dp_path = WHATSAPP_DIR / f"{slug}_opencode_dp.png"
    wa_avatar_gif = WHATSAPP_DIR / f"{slug}_moving_avatar.gif"

    wa_frames = []
    for prefix, mascot_file in POSE_MAPPING:
        m_path = MASCOTS_DIR / mascot_file
        if not m_path.exists():
            continue
        m_img = Image.open(str(m_path)).convert("RGBA")
        square = composite_lockup(logo_img, m_img, canvas_size=(600, 600), spacing=25)
        wa_frames.append(square)

    if wa_frames:
        wa_frames[0].save(str(wa_dp_path))
        wa_frames[0].save(
            str(wa_avatar_gif),
            save_all=True,
            append_images=wa_frames[1:],
            duration=650,
            loop=0,
            optimize=True
        )

    # 7. Generate WhatsApp Mobile Chat Wallpaper (1080x1920 - 9:16)
    wa_chat_path = WHATSAPP_DIR / f"{slug}_opencode_chat.png"
    if len(wa_frames) > 0:
        chat_wall = composite_lockup(logo_img, Image.open(str(MASCOTS_DIR / "neutral.png")).convert("RGBA"), canvas_size=(1080, 1920), spacing=30)
        chat_wall.save(str(wa_chat_path))

    # 8. Register in styles.json
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            styles_data = json.load(f)
    except Exception:
        styles_data = {"styles": {}}

    new_style_entry = {
        "id": slug,
        "name": f"{clean_name.upper()} OpenCode Mascot",
        "description": f"Custom OpenCode typography for {clean_name} with moving brick mascot companion.",
        "wallpaper": f"assets/wallpapers/poses_{slug}/1_neutral.png",
        "avatar": f"assets/whatsapp/{slug}_opencode_dp.png",
        "banner": f"assets/banners/{slug}.ans",
        "whatsapp_dp": f"assets/whatsapp/{slug}_opencode_dp.png",
        "whatsapp_chat": f"assets/whatsapp/{slug}_opencode_chat.png",
        "gif": f"assets/wallpapers/{slug}_moving_mascot.gif",
        "poses_dir": f"assets/wallpapers/poses_{slug}"
    }

    styles_dict = styles_data.get("styles", {})
    styles_dict[slug] = new_style_entry
    styles_data["styles"] = styles_dict

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(styles_data, f, indent=4)

    return {
        "slug": slug,
        "name": clean_name,
        "banner": str(banner_path),
        "wallpaper_poses": len(pose_paths),
        "terminal_gif": str(gif_path),
        "whatsapp_dp": str(wa_dp_path),
        "whatsapp_gif": str(wa_avatar_gif),
    }


if __name__ == "__main__":
    test_name = sys.argv[1] if len(sys.argv) > 1 else "HARSHA"
    res = generate_persona(test_name, display_user="Harsha", persona="Tech Creator & Coder")
    print("Generation complete!")
    print(json.dumps(res, indent=2))
