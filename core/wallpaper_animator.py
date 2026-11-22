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


MORPH_DIR = STUDIO_ROOT / "assets" / "wallpapers" / "poses_hiak_harsha_morph"


def play_desktop_pixel_morph(duration: float = 3.0):
    """
    Plays the pixelating morph transition on the Windows Desktop Wallpaper:
    hiak -> pixel dissolve glitch -> harsha (holds for 3s) -> morph return -> hiak!
    """
    if not MORPH_DIR.exists():
        return

    try:
        # 1. Dissolve Start
        f1 = MORPH_DIR / "3_3_dissolve_start.png"
        if f1.exists():
            apply_desktop_wallpaper(str(f1))
            time.sleep(0.09)

        # 2. Glitch Midway
        f2 = MORPH_DIR / "4_4_glitch_midway.png"
        if f2.exists():
            apply_desktop_wallpaper(str(f2))
            time.sleep(0.09)

        # 3. Solid HARSHA (Coding on Laptop)
        f3 = MORPH_DIR / "6_6_harsha_coding.png"
        if f3.exists():
            apply_desktop_wallpaper(str(f3))
            time.sleep(duration)

        # 4. Return Morph
        f4 = MORPH_DIR / "8_8_morph_return.png"
        if f4.exists():
            apply_desktop_wallpaper(str(f4))
            time.sleep(0.09)

        # 5. Return to active HIAK pose
        poses_dir = get_poses_dir()
        idx = get_current_pose_index()
        active_pose = poses_dir / POSE_FILES[idx]
        if active_pose.exists():
            apply_desktop_wallpaper(str(active_pose))
    except Exception as e:
        print(f"Morph playback error: {e}")


def is_over_text(pt_x: int, pt_y: int, screen_w: int, screen_h: int) -> bool:
    """
    Checks if cursor is over the 'hiak' text area on the desktop wallpaper.
    Accounts for 1920x1080 aspect ratio filling 1920x1200 or 1920x1080 screens.
    """
    scale_x = screen_w / 1920.0
    scale_y = screen_h / 1080.0
    # Generous text hitbox: roughly center-right of the lockup
    min_x = int(720 * scale_x)
    max_x = int(1420 * scale_x)
    min_y = int(460 * scale_y)
    max_y = int(760 * scale_y)
    return (min_x <= pt_x <= max_x) and (min_y <= pt_y <= max_y)


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
    Polls cursor position and clicks on the desktop surface:
    1. Deliberate hover over 'hiak' -> morphs into 'harsha' for 3 seconds and reverts.
    2. Clicks on the desktop surface -> advances the cartoon character emotions.
    """
    user32 = ctypes.windll.user32
    try:
        user32.SetProcessDPIAware()
    except Exception:
        pass

    screen_w = user32.GetSystemMetrics(0)
    screen_h = user32.GetSystemMetrics(1)
    pt = wintypes.POINT()

    was_down = False
    last_click_time = 0.0
    last_morph_time = 0.0
    hover_start_time = 0.0
    is_hovering_text = False

    print(f"Desktop listener active! Screen: {screen_w}x{screen_h}")
    print("  • Hover over 'hiak' on desktop to morph into 'harsha' (3s auto-revert)")
    print("  • Click on desktop wallpaper to advance cartoon character emotions")

    while True:
        user32.GetCursorPos(ctypes.byref(pt))
        on_desktop = is_desktop_surface(pt.x, pt.y)

        # 1. HOVER DETECTION OVER HIAK TEXT ON DESKTOP
        if on_desktop and is_over_text(pt.x, pt.y, screen_w, screen_h):
            now = time.time()
            if not is_hovering_text:
                is_hovering_text = True
                hover_start_time = now
            elif (now - hover_start_time > 0.25) and (now - last_morph_time > 4.5):
                # Deliberate hover > 250ms, cooldown expired
                last_morph_time = now
                print("✨ Deliberate hover over 'hiak' on desktop! Playing morph to 'harsha'...")
                try:
                    play_desktop_pixel_morph(duration=3.0)
                    last_morph_time = time.time()
                except Exception as e:
                    print(f"Morph error: {e}")
        else:
            is_hovering_text = False

        # 2. CLICK DETECTION (ADVANCE CARTOON MASCOT POSE)
        is_down = bool(user32.GetAsyncKeyState(0x01) & 0x8000)
        if is_down and not was_down:
            now = time.time()
            if now - last_click_time > 0.35:
                if on_desktop:
                    last_click_time = now
                    try:
                        pose = advance_wallpaper_pose()
                        print(f"Desktop clicked! Moved mascot to: {pose}")
                    except Exception as e:
                        pass
        was_down = is_down
        time.sleep(0.03)


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
