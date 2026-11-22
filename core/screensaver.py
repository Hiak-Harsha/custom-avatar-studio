"""
Windows Screen Saver Manager
Provides utility to launch screensaver preview or open the Windows
Screensaver Settings control panel with one click.
"""
import os
import subprocess
import winreg
from pathlib import Path


def open_screensaver_settings():
    """Opens the Windows Screen Saver Settings dialog directly."""
    subprocess.Popen(["control", "desk.cpl,,@screensaver"])


def test_screensaver():
    """Previews the active screensaver."""
    # System32 PhotoScreensaver or default
    system32 = Path(os.environ.get("WINDIR", "C:/Windows")) / "System32"
    scr_files = list(system32.glob("*.scr"))
    # Prefer PhotoScreensaver.scr
    photo_scr = system32 / "PhotoScreensaver.scr"
    target_scr = photo_scr if photo_scr.exists() else (scr_files[0] if scr_files else None)
    if target_scr:
        subprocess.Popen([str(target_scr), "/s"])
    else:
        open_screensaver_settings()


def configure_screensaver_folder(images_dir: str):
    """
    Sets registry keys for PhotoScreensaver to point to our images folder if possible.
    """
    resolved_dir = str(Path(images_dir).resolve())
    try:
        # PhotoScreensaver stores its root in HKCU\Software\Microsoft\Windows Photo Viewer\Slideshow\Screensaver
        key_path = r"Software\Microsoft\Windows Photo Viewer\Slideshow\Screensaver"
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        winreg.SetValueEx(key, "EncryptedPIDL", 0, winreg.REG_SZ, resolved_dir)
        winreg.CloseKey(key)
    except Exception:
        pass
