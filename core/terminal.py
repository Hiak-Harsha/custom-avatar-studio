"""
Windows Terminal Settings Manager
Updates Windows Terminal settings.json to apply custom background wallpaper,
opacity, alignment, and stretch mode.
"""
import json
import os
import shutil
from pathlib import Path


def get_terminal_settings_path() -> Path:
    """Finds the Windows Terminal settings.json file."""
    # Check Packaged (Windows Store)
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    packaged_path = Path(local_app_data) / "Packages" / "Microsoft.WindowsTerminal_8wekyb3d8bbwe" / "LocalState" / "settings.json"
    if packaged_path.exists():
        return packaged_path

    # Check Unpackaged (Scoop, manual, preview)
    preview_packaged = Path(local_app_data) / "Packages" / "Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe" / "LocalState" / "settings.json"
    if preview_packaged.exists():
        return preview_packaged

    unpackaged_path = Path(local_app_data) / "Microsoft" / "Windows Terminal" / "settings.json"
    if unpackaged_path.exists():
        return unpackaged_path

    # Return default packaged path even if not yet created
    return packaged_path


def backup_settings(settings_path: Path):
    """Creates a one-time backup of original settings."""
    backup_path = settings_path.with_suffix(".json.avatarstudio.bak")
    if not backup_path.exists() and settings_path.exists():
        shutil.copy2(settings_path, backup_path)


def apply_terminal_background(
    image_path: str,
    opacity: float = 0.35,
    alignment: str = "bottomRight",
    stretch: str = "uniformToFill",
    target_profile: str = "defaults"
) -> bool:
    """
    Applies the image background to Windows Terminal.
    target_profile: "defaults" (applies to CMD, PowerShell, WSL, etc.)
                    or profile name like "Command Prompt"
    """
    settings_path = get_terminal_settings_path()
    if not settings_path.exists():
        raise FileNotFoundError(f"Windows Terminal settings not found at: {settings_path}")

    backup_settings(settings_path)

    resolved_image = str(Path(image_path).resolve())

    with open(settings_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "profiles" not in data:
        data["profiles"] = {}

    bg_config = {
        "backgroundImage": resolved_image,
        "backgroundImageOpacity": float(opacity),
        "backgroundImageAlignment": alignment,
        "backgroundImageStretchMode": stretch
    }

    if target_profile == "defaults":
        if "defaults" not in data["profiles"]:
            data["profiles"]["defaults"] = {}
        data["profiles"]["defaults"].update(bg_config)
    else:
        # Search in list
        profile_list = data["profiles"].get("list", [])
        matched = False
        for p in profile_list:
            if p.get("name") == target_profile:
                p.update(bg_config)
                matched = True
                break
        if not matched:
            data["profiles"]["defaults"].update(bg_config)

    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return True


def remove_terminal_background() -> bool:
    """Removes the custom background from Windows Terminal defaults."""
    settings_path = get_terminal_settings_path()
    if not settings_path.exists():
        return False

    with open(settings_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    keys = [
        "backgroundImage",
        "backgroundImageOpacity",
        "backgroundImageAlignment",
        "backgroundImageStretchMode"
    ]

    changed = False
    if "profiles" in data and "defaults" in data["profiles"]:
        for k in keys:
            if k in data["profiles"]["defaults"]:
                del data["profiles"]["defaults"][k]
                changed = True

    if changed:
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    return True
