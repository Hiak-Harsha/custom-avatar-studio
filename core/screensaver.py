"""
Windows Screen Saver Manager
Provides full integration for Windows screensaver:
1. Native Fullscreen Animated Player (Tkinter 60fps)
2. Windows System Screensaver Configuration (Control Panel & Registry)
"""
import os
import subprocess
import sys
import winreg
from pathlib import Path

STUDIO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(STUDIO_ROOT))


def launch_screensaver_player():
    """Launches the dedicated fullscreen Python screensaver player."""
    player_script = STUDIO_ROOT / "core" / "screensaver_player.py"
    subprocess.Popen([sys.executable, str(player_script)])


def open_screensaver_settings():
    """Opens the Windows Screen Saver Settings dialog directly."""
    subprocess.Popen(["control", "desk.cpl,,@screensaver"])


def configure_windows_screensaver(timeout_minutes: int = 5):
    """
    Registers PhotoScreensaver.scr in Windows Control Panel registry,
    enables the screensaver, and sets the timeout.
    """
    timeout_sec = str(timeout_minutes * 60)
    system32 = Path(os.environ.get("WINDIR", "C:/Windows")) / "System32"
    photo_scr = system32 / "PhotoScreensaver.scr"
    scr_path = str(photo_scr) if photo_scr.exists() else str(system32 / "scrnsave.scr")

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Control Panel\Desktop",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "SCRNSAVE.EXE", 0, winreg.REG_SZ, scr_path)
        winreg.SetValueEx(key, "ScreenSaveActive", 0, winreg.REG_SZ, "1")
        winreg.SetValueEx(key, "ScreenSaveTimeOut", 0, winreg.REG_SZ, timeout_sec)
        winreg.CloseKey(key)
        print(f"✅ Windows Screensaver configured: {scr_path} (Timeout: {timeout_minutes}m)")
    except Exception as e:
        print(f"⚠️ Screensaver registry note: {e}")

    # Also open settings so user can see it verified
    open_screensaver_settings()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() in ["settings", "setup"]:
        configure_windows_screensaver()
    else:
        launch_screensaver_player()
