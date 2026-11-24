"""
Desktop Wallpaper Pose Animator & Interaction Engine
Robust, crash-proof Windows background engine for desktop wallpaper interactions:
1. INSTANT HOVER: Deliberately hovering cursor over 'hiak' smoothly pixel-morphs into 'harsha' (Option 4 Cyber-Bot), holds for 2.6s, and returns to 'hiak'.
2. PURE PIXELS ONLY: While pixelating/animating, ONLY the glitching pixels are shown (NO cartoon character at all).
3. ALWAYS-ON CLICKS: Clicking anywhere on the desktop wallpaper instantly advances mascot emotion poses.
4. DPI-AWARE & PERSISTENT: Auto-attaches to the interactive user desktop, accounts for 150% scaling, and recovers automatically.
"""
import ctypes
from ctypes import wintypes
from datetime import datetime
import json
import os
from pathlib import Path
import sys
import threading
import time

STUDIO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(STUDIO_ROOT))

from core.profile import ProfileManager
from core.wallpaper import apply_desktop_wallpaper, apply_lock_screen_wallpaper

POSES_DIR = STUDIO_ROOT / "assets" / "wallpapers" / "poses"
MORPH_DIR = STUDIO_ROOT / "assets" / "wallpapers" / "poses_hiak_harsha_morph"
STATE_FILE = STUDIO_ROOT / "config" / "wallpaper_pose.json"
LOG_FILE = STUDIO_ROOT / "logs" / "animator.log"

POSE_FILES = [
    "1_neutral.png",
    "2_happy.png",
    "3_wave.png",
    "4_idea.png",
    "5_cool.png",
    "6_coding.png",
    "7_sleepy.png"
]

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Enable Per-Monitor v2 DPI Awareness so coordinates match physical 1920x1200
try:
    shcore = ctypes.windll.shcore
    shcore.SetProcessDpiAwareness(2) # PROCESS_PER_MONITOR_DPI_AWARE
except Exception:
    try:
        user32.SetProcessDPIAware()
    except Exception:
        pass

# Win32 POINT structure for 64-bit systems
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

user32.WindowFromPoint.argtypes = [POINT]
user32.WindowFromPoint.restype = wintypes.HWND
user32.GetCursorPos.argtypes = [ctypes.c_void_p]
user32.GetCursorPos.restype = wintypes.BOOL
user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
user32.GetAncestor.restype = wintypes.HWND
user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetClassNameW.restype = ctypes.c_int
user32.GetForegroundWindow.restype = wintypes.HWND
user32.OpenDesktopW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
user32.OpenDesktopW.restype = wintypes.HANDLE
user32.SetThreadDesktop.argtypes = [wintypes.HANDLE]
user32.SetThreadDesktop.restype = wintypes.BOOL
user32.CloseDesktop.argtypes = [wintypes.HANDLE]
user32.CloseDesktop.restype = wintypes.BOOL


def log_msg(msg: str):
    """Appends timestamped diagnostic messages to logs/animator.log."""
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        if LOG_FILE.exists() and LOG_FILE.stat().st_size > 500_000:
            LOG_FILE.unlink(missing_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass


def ensure_interactive_desktop() -> bool:
    """
    Ensures the current thread is attached to the Windows interactive user desktop ('default').
    """
    GENERIC_ALL = 0x10000000
    hDesk = None
    try:
        hDesk = user32.OpenDesktopW("default", 0, False, GENERIC_ALL)
        if hDesk:
            ok = bool(user32.SetThreadDesktop(hDesk))
            return ok
    except Exception as e:
        log_msg(f"Failed to attach thread desktop: {e}")
    finally:
        if hDesk:
            try:
                user32.CloseDesktop(hDesk)
            except Exception:
                pass
    return False


_MUTEX_HANDLE = None


def acquire_single_instance_mutex() -> bool:
    """Prevents multiple background animator instances from firing duplicate clicks/morphs."""
    global _MUTEX_HANDLE
    ERROR_ALREADY_EXISTS = 183
    handle = kernel32.CreateMutexW(None, False, "Local\\HIAK_Wallpaper_Animator_Mutex")
    if not handle:
        return True
    if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        kernel32.CloseHandle(handle)
        return False
    _MUTEX_HANDLE = handle
    return True


class LockScreenSyncWorker:
    """Debounced background worker that keeps the Windows Lock Screen synced to the latest pose."""

    def __init__(self, debounce_seconds: float = 0.45):
        self.debounce_seconds = debounce_seconds
        self._lock = threading.Lock()
        self._event = threading.Event()
        self._pending_path: str | None = None
        self._pending_ts: float = 0.0
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def schedule(self, image_path: str):
        with self._lock:
            self._pending_path = image_path
            self._pending_ts = time.time()
        self._event.set()

    def _run(self):
        while True:
            self._event.wait()
            while True:
                with self._lock:
                    path = self._pending_path
                    age = time.time() - self._pending_ts
                if path is None:
                    self._event.clear()
                    break
                remaining = self.debounce_seconds - age
                if remaining > 0:
                    time.sleep(remaining)
                    continue
                with self._lock:
                    if self._pending_path != path:
                        continue
                    self._pending_path = None
                    self._event.clear()
                try:
                    pm = ProfileManager(str(STUDIO_ROOT))
                    if pm.is_lock_screen_enabled():
                        apply_lock_screen_wallpaper(path)
                        log_msg(f"🔒 Lock screen synced to: {Path(path).name}")
                except Exception as e:
                    log_msg(f"Lock screen sync error: {e}")
                break


def get_active_wallpaper_path() -> Path | None:
    """Returns the current active wallpaper file (active pose if available, else style wallpaper)."""
    try:
        pm = ProfileManager(str(STUDIO_ROOT))
        active = pm.get_active_style()
        poses_rel = active.get("poses_dir")
        if poses_rel:
            p_dir = STUDIO_ROOT / poses_rel
            idx = get_current_pose_index()
            pose_path = p_dir / POSE_FILES[idx]
            if pose_path.exists():
                return pose_path
        wall_rel = active.get("wallpaper")
        if wall_rel:
            wall_path = STUDIO_ROOT / wall_rel
            if wall_path.exists():
                return wall_path
    except Exception:
        pass
    fallback = POSES_DIR / POSE_FILES[get_current_pose_index()]
    return fallback if fallback.exists() else None


def get_poses_dir() -> Path:
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


def advance_wallpaper_pose(sync_lock_screen: bool = True) -> str:
    """Advances the desktop wallpaper (and optionally lock screen) to the next frame/pose in sequence."""
    poses_dir = get_poses_dir()
    idx = get_current_pose_index()
    next_idx = (idx + 1) % len(POSE_FILES)
    save_current_pose_index(next_idx)

    target_file = poses_dir / POSE_FILES[next_idx]
    if target_file.exists():
        apply_desktop_wallpaper(str(target_file))
        if sync_lock_screen:
            try:
                if ProfileManager(str(STUDIO_ROOT)).is_lock_screen_enabled():
                    apply_lock_screen_wallpaper(str(target_file))
            except Exception as e:
                log_msg(f"Lock screen pose sync error: {e}")

    return POSE_FILES[next_idx]


def is_over_text(pt_x: int, pt_y: int, screen_w: int, screen_h: int) -> bool:
    """
    Checks if cursor is deliberately hovering over the 'hiak' lockup on the 1920x1200 medium centered wallpaper.
    Physical 'hiak' text box: X=[756, 1022], Y=[544, 656].
    Generous comfortable trigger zone: X=[680, 1100], Y=[480, 720].
    """
    scale_x = screen_w / 1920.0
    scale_y = screen_h / 1200.0
    min_x = int(680 * scale_x)
    max_x = int(1100 * scale_x)
    min_y = int(480 * scale_y)
    max_y = int(720 * scale_y)
    return (min_x <= pt_x <= max_x) and (min_y <= pt_y <= max_y)


def is_desktop_surface(pt_x: int, pt_y: int) -> bool:
    """
    Verifies if (pt_x, pt_y) or the active foreground is on the Windows desktop wallpaper.
    Accounts for hidden icons, WorkerW, Progman, and ignore open application windows.
    """
    try:
        # Check foreground window first
        fg_hwnd = user32.GetForegroundWindow()
        if fg_hwnd:
            fg_root = user32.GetAncestor(fg_hwnd, 2)
            if not fg_root:
                fg_root = fg_hwnd
            progman = user32.FindWindowW("Progman", None)
            if fg_root == progman:
                return True
            buf = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(fg_root, buf, 256)
            if buf.value in ["Progman", "WorkerW"]:
                return True

        # Check window directly under cursor point
        pt = POINT(pt_x, pt_y)
        hwnd = user32.WindowFromPoint(pt)
        if not hwnd or hwnd == user32.GetDesktopWindow():
            return True

        root = user32.GetAncestor(hwnd, 2)
        if not root:
            root = hwnd

        progman = user32.FindWindowW("Progman", None)
        if root == progman:
            return True

        buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(root, buf, 256)
        if buf.value in ["Progman", "WorkerW"]:
            return True

        user32.GetClassNameW(hwnd, buf, 256)
        if buf.value in ["SysListView32", "WorkerW", "Progman", "SHELLDLL_DefView"]:
            return True

        return False
    except Exception as e:
        log_msg(f"is_desktop_surface error: {e}")
        return False


def listen_for_desktop_clicks():
    """
    High-frequency non-blocking state machine for desktop wallpaper interactions:
    1. INSTANT HOVER: Deliberate hover on 'hiak' triggers pixel morph to 'harsha' (pure pixels during transition).
    2. ALWAYS-ON CLICKS: Clicks on desktop wallpaper advance mascot emotions instantly.
    3. DPI-AWARE & SELF-HEALING: Recovers automatically from lock screens or display changes.
    """
    if not acquire_single_instance_mutex():
        log_msg("Another wallpaper animator instance is already running; exiting duplicate.")
        return

    log_msg("Starting HIAK Mascot Studio Wallpaper Engine (DPI-Aware)...")
    lock_sync_worker = LockScreenSyncWorker()
    initial_wp = get_active_wallpaper_path()
    if initial_wp:
        lock_sync_worker.schedule(str(initial_wp))
    
    while True:
        try:
            ensure_interactive_desktop()
            
            screen_w = user32.GetSystemMetrics(0)
            screen_h = user32.GetSystemMetrics(1)
            pt = POINT()

            STATE_IDLE = "IDLE"
            STATE_MORPH_IN_1 = "MORPH_IN_1" # Claude dashes right
            STATE_MORPH_IN_2 = "MORPH_IN_2" # Cyber-Bot enters left with glowing cyan thrusters
            STATE_MORPH_IN_3 = "MORPH_IN_3" # Cyber-Bot glides into dock next to Harsha
            STATE_HOLD_HARSHA = "HOLD_HARSHA" # Solid HARSHA + docked Cyber-Bot coding
            STATE_MORPH_OUT_1 = "MORPH_OUT_1" # Cyber-Bot boosts off to left
            STATE_MORPH_OUT_2 = "MORPH_OUT_2" # Claude bounds back in from right

            current_state = STATE_IDLE
            state_start_time = 0.0
            last_hover_exit_time = 0.0
            was_hovering = False
            was_down = False
            last_click_time = 0.0
            was_locked = False
            last_reattach_attempt = 0.0
            last_progman = user32.FindWindowW("Progman", None)

            log_msg(f"Engine active! Resolution: {screen_w}x{screen_h}. Monitoring clicks & hover...")

            while True:
                now = time.time()
                
                if not user32.GetCursorPos(ctypes.byref(pt)):
                    if not was_locked:
                        was_locked = True
                        log_msg("Session locked / desktop unavailable; waiting for unlock...")
                    if now - last_reattach_attempt >= 1.0:
                        last_reattach_attempt = now
                        ensure_interactive_desktop()
                    time.sleep(0.25)
                    continue

                if was_locked:
                    was_locked = False
                    ensure_interactive_desktop()
                    screen_w = user32.GetSystemMetrics(0)
                    screen_h = user32.GetSystemMetrics(1)
                    last_progman = user32.FindWindowW("Progman", None)
                    current_state = STATE_IDLE
                    was_hovering = False
                    was_down = False
                    last_hover_exit_time = now
                    try:
                        active_wp = get_active_wallpaper_path()
                        if active_wp and active_wp.exists():
                            apply_desktop_wallpaper(str(active_wp), is_transient=False)
                    except Exception as e:
                        log_msg(f"Unlock wallpaper restore error: {e}")
                    log_msg(f"Session unlocked! Resumed desktop interaction ({screen_w}x{screen_h}).")

                # Detect Explorer restarts / display shell changes and restore active wallpaper
                cur_progman = user32.FindWindowW("Progman", None)
                if cur_progman and cur_progman != last_progman:
                    last_progman = cur_progman
                    screen_w = user32.GetSystemMetrics(0)
                    screen_h = user32.GetSystemMetrics(1)
                    try:
                        active_wp = get_active_wallpaper_path()
                        if active_wp and active_wp.exists():
                            apply_desktop_wallpaper(str(active_wp), is_transient=False)
                        log_msg("Explorer desktop shell refreshed; re-applied active wallpaper.")
                    except Exception as e:
                        log_msg(f"Explorer refresh restore error: {e}")

                on_desktop = is_desktop_surface(pt.x, pt.y)

                # ========================================================
                # 1. ALWAYS-ON CLICK DETECTION (NEVER BLOCKED)
                # ========================================================
                is_down = bool(user32.GetAsyncKeyState(0x01) & 0x8000)
                if is_down and not was_down:
                    if on_desktop and (now - last_click_time > 0.22):
                        last_click_time = now
                        try:
                            pose = advance_wallpaper_pose(sync_lock_screen=False)
                            log_msg(f"⚡ Desktop clicked! Advanced mascot to: {pose}")
                            pose_file = get_poses_dir() / pose
                            if pose_file.exists():
                                lock_sync_worker.schedule(str(pose_file))
                            if current_state != STATE_IDLE:
                                current_state = STATE_IDLE
                                last_hover_exit_time = now
                        except Exception as e:
                            log_msg(f"Click advance error: {e}")
                was_down = is_down

                # ========================================================
                # 2. INSTANT HOVER DETECTION (ZERO DELAY)
                # ========================================================
                hovering = on_desktop and is_over_text(pt.x, pt.y, screen_w, screen_h)

                if hovering:
                    if current_state == STATE_IDLE and (now - last_hover_exit_time > 0.5):
                        current_state = STATE_MORPH_IN_1
                        state_start_time = now
                        log_msg("✨ Deliberate hover on 'hiak'! Pixel dissolving (pure pixels)...")
                        try:
                            f1 = MORPH_DIR / "3_3_dissolve_start.png"
                            if f1.exists():
                                apply_desktop_wallpaper(str(f1), is_transient=True)
                        except Exception as e:
                            log_msg(f"Frame 1 error: {e}")
                else:
                    if was_hovering and current_state == STATE_IDLE:
                        last_hover_exit_time = now
                was_hovering = hovering

                # ========================================================
                # 3. NON-BLOCKING MORPH FRAME SEQUENCING (OPTION A: RELAY DASH - BALANCED 300-320ms PACING)
                # ========================================================
                if current_state == STATE_MORPH_IN_1:
                    # Frame 1: Claude dashes off to the right (balanced 0.30s)
                    if now - state_start_time >= 0.30:
                        current_state = STATE_MORPH_IN_2
                        state_start_time = now
                        try:
                            f2 = MORPH_DIR / "4_4_glitch_midway.png"
                            if f2.exists():
                                apply_desktop_wallpaper(str(f2), is_transient=True)
                        except Exception as e:
                            log_msg(f"Frame 2 error: {e}")

                elif current_state == STATE_MORPH_IN_2:
                    # Frame 2: Cyber-Bot streaks in from left edge with cyan thrusters (0.32s)
                    if now - state_start_time >= 0.32:
                        current_state = STATE_MORPH_IN_3
                        state_start_time = now
                        try:
                            f3 = MORPH_DIR / "5_5_harsha_forming.png"
                            if f3.exists():
                                apply_desktop_wallpaper(str(f3), is_transient=True)
                        except Exception as e:
                            log_msg(f"Frame 3 error: {e}")

                elif current_state == STATE_MORPH_IN_3:
                    # Frame 3: Cyber-Bot glides into dock next to Harsha (0.30s)
                    if now - state_start_time >= 0.30:
                        current_state = STATE_HOLD_HARSHA
                        state_start_time = now
                        try:
                            f4 = MORPH_DIR / "6_6_harsha_cyber_bot_coding.png"
                            if not f4.exists():
                                f4 = MORPH_DIR / "6_6_harsha_coding.png"
                            if f4.exists():
                                apply_desktop_wallpaper(str(f4), is_transient=False)
                                log_msg("HARSHA active with Option 4 Floating Cyber-Bot!")
                        except Exception as e:
                            log_msg(f"Harsha solid error: {e}")

                elif current_state == STATE_HOLD_HARSHA:
                    # Hold on HARSHA for 2.7 seconds, then start relay return
                    if now - state_start_time >= 2.7:
                        current_state = STATE_MORPH_OUT_1
                        state_start_time = now
                        try:
                            f5 = MORPH_DIR / "8_8_morph_return.png"
                            if f5.exists():
                                apply_desktop_wallpaper(str(f5), is_transient=True)
                        except Exception as e:
                            log_msg(f"Frame 5 error: {e}")

                elif current_state == STATE_MORPH_OUT_1:
                    # Frame 5: Cyber-Bot boosts off to the left (0.30s)
                    if now - state_start_time >= 0.30:
                        current_state = STATE_MORPH_OUT_2
                        state_start_time = now
                        try:
                            f6 = MORPH_DIR / "9_9_morph_return_mid.png"
                            if f6.exists():
                                apply_desktop_wallpaper(str(f6), is_transient=True)
                        except Exception as e:
                            log_msg(f"Frame 6 error: {e}")

                elif current_state == STATE_MORPH_OUT_2:
                    # Frame 6: Claude bounds back in from right into resting stance (0.32s)
                    if now - state_start_time >= 0.32:
                        current_state = STATE_IDLE
                        last_hover_exit_time = now
                        try:
                            poses_dir = get_poses_dir()
                            idx = get_current_pose_index()
                            active_pose = poses_dir / POSE_FILES[idx]
                            if active_pose.exists():
                                apply_desktop_wallpaper(str(active_pose), is_transient=False)
                                log_msg("Returned to HIAK with Brown Claude Mascot!")
                        except Exception as e:
                            log_msg(f"Return pose error: {e}")

                time.sleep(0.015)

        except Exception as e:
            log_msg(f"Supervisor recovered from exception: {e}")
            time.sleep(1.0)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "next":
            pose = advance_wallpaper_pose()
            print(f"Moved wallpaper to: {pose}")
        elif arg == "listen":
            listen_for_desktop_clicks()
        elif arg == "auto":
            print("Auto-animating wallpaper... Press Ctrl+C to stop.")
            while True:
                pose = advance_wallpaper_pose()
                print(f"  Moved to pose: {pose}")
                time.sleep(1.2)
    else:
        pose = advance_wallpaper_pose()
        print(f"Moved wallpaper to: {pose}")
