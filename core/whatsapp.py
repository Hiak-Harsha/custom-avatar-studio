"""
WhatsApp & Mobile Export Manager
Generates:
1. WhatsApp Profile Picture (Square 1:1, 1024x1024 with circular crop safe margin)
2. WhatsApp Chat Wallpaper / Mobile Wallpaper (Vertical 9:16 portrait, 1080x1920)
3. 1-Click Clipboard Image Copy (press Ctrl+V in WhatsApp Web / Desktop)
"""
import os
import subprocess
from pathlib import Path
from PIL import Image, ImageOps


def create_whatsapp_dp(src_image: str, output_path: str, size: int = 1024, focus: tuple = (0.5, 0.5)) -> str:
    """
    Creates a square profile picture centered on focus point, optimized for WhatsApp DP.
    """
    img = Image.open(src_image).convert("RGB")
    w, h = img.size
    crop_size = min(w, h)

    cx = int(w * focus[0])
    cy = int(h * focus[1])

    left = max(0, min(cx - crop_size // 2, w - crop_size))
    top = max(0, min(cy - crop_size // 2, h - crop_size))
    right = left + crop_size
    bottom = top + crop_size

    cropped = img.crop((left, top, right, bottom))
    cropped = cropped.resize((size, size), Image.Resampling.LANCZOS)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    cropped.save(out, quality=95)
    return str(out.resolve())


def create_whatsapp_chat_wallpaper(src_image: str, output_path: str, target_size: tuple = (1080, 1920)) -> str:
    """
    Creates a vertical 9:16 wallpaper suitable for phone screen & WhatsApp chat background.
    Uses centered crop and vertical atmospheric extension.
    """
    img = Image.open(src_image).convert("RGB")
    target_w, target_h = target_size

    # Fit image to width and fill height with blurred/atmospheric background
    scale = target_w / img.width
    scaled_h = int(img.height * scale)
    scaled_img = img.resize((target_w, scaled_h), Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", (target_w, target_h), (15, 17, 26))

    # Place scaled image vertically centered
    y_offset = (target_h - scaled_h) // 2
    canvas.paste(scaled_img, (0, max(0, y_offset)))

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, quality=92)
    return str(out.resolve())


def copy_image_to_clipboard(image_path: str) -> bool:
    """
    Copies an image directly to the Windows Clipboard using PowerShell and System.Windows.Forms.
    Once copied, you can press Ctrl+V directly into WhatsApp Web, WhatsApp Desktop, Discord, etc.
    """
    resolved = str(Path(image_path).resolve())
    if not os.path.exists(resolved):
        raise FileNotFoundError(f"Image not found: {resolved}")

    ps_script = f"""
Add-Type -AssemblyName System.Windows.Forms
$img = [System.Drawing.Image]::FromFile("{resolved}")
[System.Windows.Forms.Clipboard]::SetImage($img)
$img.Dispose()
"""
    cmd = ["powershell", "-NoProfile", "-Command", ps_script]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode == 0
