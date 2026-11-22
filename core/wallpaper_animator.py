"""
Desktop Wallpaper Pose Animator
Handles moving the character on the Windows Desktop Wallpaper:
1. next_pose(): Advances to the next pose frame in sequence on every click.
2. auto_animate(): Continuously cycles through the poses like an animated wallpaper.
3. listen_for_desktop_clicks(): Seamlessly detects mouse clicks on the desktop wallpaper.
"""
import ctypes
from ctypes import wintypes
import json
import os
import sys
import time
from pathlib import Path

STUDIO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(STUDIO_ROOT))

from core.wallpaper import apply_desktop_wallpaper

POSES_DIR = STUDIO_ROOT / "assets" / "wallpapers" / "poses"
STATE_FILE = STUDIO_ROOT / "config" / "wallpaper_pose.json"

POSE_FILES = [
    "1_neutral.png",
    "2_happy.png",
    "3_wave.png",
    "4_idea.png",
    "5_cool.png",
    "6_coding.png",
    "7_sleepy.png"
]


def get_poses_dir() -> Path:
    from core.profile import ProfileManager
    try:
        pm = ProfileManager(str(STUDIO_ROOT))
        active = pm.get_active_style()
        poses_rel = active.get("poses_dir")
        if poses_rel:
            p = STUDIO_ROOT / poses_rel
            if p.exists():
                return p
    except Exception:
        pass
    return POSES_DIR


def get_current_pose_index() -> int:
    if not STATE_FILE.exists():
        return 0
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("current_index", 0)
    except Exception:
        return 0


def save_current_pose_index(idx: int):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"current_index": idx, "pose": POSE_FILES[idx]}, f)


def advance_wallpaper_pose() -> str:
    """Advances the desktop wallpaper to the next frame/pose in sequence."""
    poses_dir = get_poses_dir()
    idx = get_current_pose_index()
    next_idx = (idx + 1) % len(POSE_FILES)
    save_current_pose_index(next_idx)

    target_file = poses_dir / POSE_FILES[next_idx]
    if target_file.exists():
        apply_desktop_wallpaper(str(target_file))

    return POSE_FILES[next_idx]


def auto_animate_loop(interval: float = 1.2):
    """Continuously cycles the desktop wallpaper frames."""
    print(f"🎬 Auto-animating wallpaper every {interval}s... Press Ctrl+C to stop.")
    while True:
        pose = advance_wallpaper_pose()
        print(f"  ✨ Moved to pose: {pose}")
        time.sleep(interval)


def is_desktop_surface(pt_x, pt_y) -> bool:
    """Checks if the point clicked is the Windows desktop wallpaper background."""
    user32 = ctypes.windll.user32
    pt = wintypes.POINT(pt_x, pt_y)
    hwnd = user32.WindowFromPoint(pt)
    class_buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, class_buf, 256)
    cname = class_buf.value

    # Direct desktop classes in Windows
    if cname in ["SysListView32", "WorkerW", "Progman", "SHELLDLL_DefView"]:
        return True

    # Check parent
    parent_hwnd = user32.GetParent(hwnd)
    if parent_hwnd:
        user32.GetClassNameW(parent_hwnd, class_buf, 256)
        if class_buf.value in ["SHELLDLL_DefView", "Progman", "WorkerW"]:
            return True

    return False


def listen_for_desktop_clicks():
    """
    Polls GetAsyncKeyState for left mouse clicks on the desktop surface.
    Extremely lightweight, zero admin rights, zero injection.
    """
    user32 = ctypes.windll.user32
    pt = wintypes.POINT()
    was_down = False
    last_advance_time = 0.0

    print("Desktop click listener active! Click your desktop wallpaper to move the character.")
    while True:
        is_down = bool(user32.GetAsyncKeyState(0x01) & 0x8000)
        if is_down and not was_down:
            now = time.time()
            if now - last_advance_time > 0.4:
                user32.GetCursorPos(ctypes.byref(pt))
                if is_desktop_surface(pt.x, pt.y):
                    last_advance_time = now
                    try:
                        pose = advance_wallpaper_pose()
                        print(f"Desktop clicked! Moved wallpaper to: {pose}")
                    except Exception as e:
                        pass
        was_down = is_down
        time.sleep(0.025)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "next":
            pose = advance_wallpaper_pose()
            print(f"Moved wallpaper to: {pose}")
        elif arg == "auto":
            auto_animate_loop()
        elif arg == "listen":
            listen_for_desktop_clicks()
    else:
        pose = advance_wallpaper_pose()
        print(f"Moved wallpaper to: {pose}")
