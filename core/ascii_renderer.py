"""
ASCII and ANSI TrueColor Art Renderer
Converts any image into gorgeous, high-resolution 24-bit TrueColor ANSI half-blocks
for displaying directly in CMD, PowerShell, or bash terminals.
Also creates 1:1 avatar crops for profile icons.
"""
import os
from pathlib import Path
from PIL import Image


def crop_avatar(image_path: str, output_path: str, box_center: tuple = None, size: int = 512):
    """
    Crops a square avatar focusing on the character.
    box_center is (ratio_x, ratio_y) from 0.0 to 1.0. Defaults to (0.5, 0.5).
    """
    img = Image.open(image_path)
    w, h = img.size
    crop_size = min(w, h)

    cx = int(w * (box_center[0] if box_center else 0.5))
    cy = int(h * (box_center[1] if box_center else 0.5))

    left = max(0, min(cx - crop_size // 2, w - crop_size))
    top = max(0, min(cy - crop_size // 2, h - crop_size))
    right = left + crop_size
    bottom = top + crop_size

    cropped = img.crop((left, top, right, bottom))
    cropped = cropped.resize((size, size), Image.Resampling.LANCZOS)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cropped.save(output_path, quality=95)
    return output_path


def image_to_ansi_truecolor(image_path: str, width: int = 56) -> str:
    """
    Converts image to ANSI truecolor string using half-block character '▀'.
    Each character cell renders TWO vertical pixels:
    - Foreground color = Upper pixel
    - Background color = Lower pixel
    """
    img = Image.open(image_path).convert("RGB")
    orig_w, orig_h = img.size

    # Terminal chars are typically ~2:1 height:width, but half-block '▀' stacks 2 pixels vertically!
    # So 1 terminal char row = 2 pixel rows. Aspect ratio remains 1:1!
    aspect = orig_h / orig_w
    target_h = int(width * aspect)
    # Ensure even height for pairing
    if target_h % 2 != 0:
        target_h += 1

    img = img.resize((width, target_h), Image.Resampling.LANCZOS)
    pixels = img.load()

    lines = []
    for y in range(0, target_h, 2):
        line = ""
        for x in range(width):
            r1, g1, b1 = pixels[x, y]
            if y + 1 < target_h:
                r2, g2, b2 = pixels[x, y + 1]
                # Top pixel fg, bottom pixel bg, char '▀'
                line += f"\033[38;2;{r1};{g1};{b1}m\033[48;2;{r2};{g2};{b2}m▀"
            else:
                line += f"\033[38;2;{r1};{g1};{b1}m▀"
        line += "\033[0m"
        lines.append(line)

    return "\n".join(lines)


def generate_banners_and_avatars(base_dir: str):
    """
    Processes all wallpapers in assets/wallpapers to produce:
    - assets/avatars/<style>.jpg
    - assets/banners/<style>.ans
    """
    base = Path(base_dir)
    wallpapers_dir = base / "assets" / "wallpapers"
    avatars_dir = base / "assets" / "avatars"
    banners_dir = base / "assets" / "banners"

    avatars_dir.mkdir(parents=True, exist_ok=True)
    banners_dir.mkdir(parents=True, exist_ok=True)

    focus_centers = {
        "pixel_art": (0.35, 0.55),
        "cyberpunk_anime": (0.35, 0.45),
        "lofi_ghibli": (0.40, 0.55),
    }

    results = {}
    for img_file in wallpapers_dir.glob("*.jpg"):
        style_id = img_file.stem
        avatar_path = avatars_dir / f"{style_id}.jpg"
        banner_path = banners_dir / f"{style_id}.ans"

        center = focus_centers.get(style_id, (0.5, 0.5))
        crop_avatar(str(img_file), str(avatar_path), box_center=center, size=512)

        ansi_art = image_to_ansi_truecolor(str(img_file), width=54)
        with open(banner_path, "w", encoding="utf-8") as f:
            f.write(ansi_art)

        results[style_id] = {
            "avatar": str(avatar_path),
            "banner": str(banner_path)
        }

    return results
