"""
Floating HIAK Desktop Mascot Companion
Interactive desktop pet that moves, hops, and strolls across your desktop.

Features:
- CLICK TO JUMP: Clicking on the mascot triggers a physics parabolic hop & bounce with speech bubble!
- AUTO-WALK MODE: Mascot strolls happily across your desktop above the taskbar!
- DRAGGABLE: Click and drag to place anywhere on your screen.
- EASY CLOSE: Red [✕] button, Esc key, or Right-Click -> Close.
"""
import os
import random
import sys
import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk, ImageSequence

STUDIO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(STUDIO_ROOT))


def ensure_single_instance():
    """Kills any previous companion.py instances so only one window runs."""
    import subprocess
    curr_pid = os.getpid()
    ps_cmd = f"""
    Get-CimInstance Win32_Process -Filter "name = 'pythonw.exe' or name = 'python.exe'" | 
    Where-Object {{ $_.CommandLine -like '*companion.py*' -and $_.ProcessId -ne {curr_pid} }} | 
    ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }}
    """
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True)
    except Exception:
        pass


class DesktopCompanionApp:
    def __init__(self, root, gif_path=None):
        self.root = root
        self.root.title("HIAK Mascot Companion")
        self.root.overrideredirect(True)          # Borderless
        self.root.attributes("-topmost", True)    # Float on top
        self.root.configure(bg="#0a0a0a")

        self.available_gifs = {
            "avatar": STUDIO_ROOT / "assets" / "whatsapp" / "hiak_moving_avatar.gif",
            "claude": STUDIO_ROOT / "assets" / "wallpapers" / "hiak_moving_mascot.gif",
            "tech": STUDIO_ROOT / "assets" / "wallpapers" / "hiak_tech_mascot_moving.gif"
        }

        self.current_gif_path = Path(gif_path) if gif_path else self.available_gifs["avatar"]
        if not self.current_gif_path.exists():
            self.current_gif_path = self.available_gifs["claude"]

        # Screen dimensions
        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()
        self.win_w = 340
        self.win_h = 180

        # Initial Position: bottom right
        self.pos_x = self.sw - self.win_w - 40
        self.pos_y = self.sh - self.win_h - 60
        self.root.geometry(f"{self.win_w}x{self.win_h}+{self.pos_x}+{self.pos_y}")

        # State flags
        self.is_hopping = False
        self.is_walking = False
        self.walk_direction = 1     # 1 = right, -1 = left
        self.walk_step = 0

        self.setup_ui()
        self.load_gif(self.current_gif_path)

        # Global Hotkey: Esc to exit
        self.root.bind("<Escape>", lambda e: self.close())
        self.root.bind("q", lambda e: self.close())

    def setup_ui(self):
        # Outer container with crisp dark border
        self.border_frame = tk.Frame(self.root, bg="#262626", padx=1, pady=1)
        self.border_frame.pack(fill="both", expand=True)

        inner_frame = tk.Frame(self.border_frame, bg="#0a0a0a")
        inner_frame.pack(fill="both", expand=True)

        # Top Control Bar (Title + Walk Toggle + Close [✕] Button)
        top_bar = tk.Frame(inner_frame, bg="#141414", height=26)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        title_lbl = tk.Label(
            top_bar,
            text="🐾 HIAK",
            font=("Segoe UI", 8, "bold"),
            fg="#00e5ff",
            bg="#141414",
            padx=6
        )
        title_lbl.pack(side="left")

        # Walk toggle button
        self.walk_btn = tk.Button(
            top_bar,
            text="🚶 Walk: OFF",
            font=("Segoe UI", 7, "bold"),
            fg="#888888",
            bg="#1f1f1f",
            activebackground="#00e5ff",
            activeforeground="#000000",
            relief="flat",
            padx=6,
            pady=1,
            cursor="hand2",
            command=self.toggle_walking
        )
        self.walk_btn.pack(side="left", padx=4)

        # Reactive Speech Bubble Label
        self.speech_lbl = tk.Label(
            top_bar,
            text="✨ Click me!",
            font=("Segoe UI", 8),
            fg="#38ef7d",
            bg="#141414"
        )
        self.speech_lbl.pack(side="left", padx=6)

        # Clearly Visible Close Button [✕]
        self.close_btn = tk.Button(
            top_bar,
            text="✕",
            font=("Segoe UI", 9, "bold"),
            fg="#ffffff",
            bg="#e84118",
            activebackground="#c23616",
            activeforeground="#ffffff",
            relief="flat",
            width=3,
            cursor="hand2",
            command=self.close
        )
        self.close_btn.pack(side="right")

        # Mascot Animation Display Label
        self.anim_lbl = tk.Label(inner_frame, bg="#0a0a0a", cursor="hand2")
        self.anim_lbl.pack(fill="both", expand=True)

        # Drag & Click Detection
        self.drag_data = {"x": 0, "y": 0, "start_root_x": 0, "start_root_y": 0, "is_dragging": False}
        for widget in [top_bar, title_lbl, self.anim_lbl]:
            widget.bind("<Button-1>", self.on_mouse_down)
            widget.bind("<B1-Motion>", self.on_mouse_drag)
            widget.bind("<ButtonRelease-1>", self.on_mouse_up)

        # Right-click Context Menu
        self.context_menu = tk.Menu(self.root, tearoff=0, bg="#1a1a1a", fg="#ffffff", activebackground="#00e5ff", activeforeground="#000000")
        self.context_menu.add_command(label="🎯 Jump / Hop", command=self.do_hop)
        self.context_menu.add_command(label="🚶 Toggle Auto-Walk", command=self.toggle_walking)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🧱 Switch to Claude Brick", command=lambda: self.switch_gif("claude"))
        self.context_menu.add_command(label="🤖 Switch to HIAK Tech Mascot", command=lambda: self.switch_gif("tech"))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="❌ Close Mascot (Esc)", command=self.close)

        for widget in [top_bar, title_lbl, self.speech_lbl, self.anim_lbl]:
            widget.bind("<Button-3>", self.show_context_menu)

    def load_gif(self, gif_path: Path):
        self.current_gif_path = gif_path
        pil_gif = Image.open(str(gif_path))
        self.frames = []
        target_w = self.win_w - 20
        target_h = self.win_h - 38

        for frame in ImageSequence.Iterator(pil_gif):
            f = frame.copy().convert("RGB")
            f.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
            self.frames.append(ImageTk.PhotoImage(f))

        self.frame_idx = 0
        self.animate()

    def animate(self):
        if not hasattr(self, "frames") or not self.frames:
            return
        self.anim_lbl.config(image=self.frames[self.frame_idx])
        self.frame_idx = (self.frame_idx + 1) % len(self.frames)
        self.anim_after_id = self.root.after(600, self.animate)

    # Mouse Click & Drag Logic
    def on_mouse_down(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        self.drag_data["start_root_x"] = self.root.winfo_x()
        self.drag_data["start_root_y"] = self.root.winfo_y()
        self.drag_data["is_dragging"] = False

    def on_mouse_drag(self, event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        if abs(dx) > 4 or abs(dy) > 4:
            self.drag_data["is_dragging"] = True
            new_x = self.root.winfo_x() + dx
            new_y = self.root.winfo_y() + dy
            self.pos_x = new_x
            self.pos_y = new_y
            self.root.geometry(f"+{new_x}+{new_y}")

    def on_mouse_up(self, event):
        # If user clicked without dragging -> TRIGGER HOP MOTION!
        if not self.drag_data["is_dragging"]:
            self.do_hop()

    # Physics Parabolic Hop Animation
    def do_hop(self):
        if self.is_hopping:
            return
        self.is_hopping = True

        phrases = [
            "⚡ HIAK!", "🚀 Let's code!", "🎉 Wohoo!", "😎 Too cool!", 
            "💡 Big idea!", "✨ High five!", "💻 Battlestation!", "🔥 Let's build!"
        ]
        self.speech_lbl.config(text=random.choice(phrases), fg="#00e5ff")

        # Smooth jump curve offsets (in pixels)
        offsets = [-6, -14, -24, -32, -38, -42, -44, -42, -38, -32, -24, -14, -6, 0, 5, 2, 0]
        base_x = self.root.winfo_x()
        base_y = self.root.winfo_y()

        def hop_step(step_idx):
            if step_idx < len(offsets):
                dy = offsets[step_idx]
                # Small forward momentum during jump if walking
                step_dx = (2 * self.walk_direction) if self.is_walking else 0
                curr_x = self.root.winfo_x() + step_dx
                self.root.geometry(f"+{curr_x}+{base_y + dy}")
                self.root.after(22, lambda: hop_step(step_idx + 1))
            else:
                self.root.geometry(f"+{self.root.winfo_x()}+{base_y}")
                self.is_hopping = False
                self.root.after(1500, lambda: self.speech_lbl.config(text="✨ Click me!", fg="#38ef7d"))

        hop_step(0)

    # Walking Motion Logic
    def toggle_walking(self):
        self.is_walking = not self.is_walking
        if self.is_walking:
            self.walk_btn.config(text="🚶 Walk: ON", fg="#000000", bg="#38ef7d")
            self.speech_lbl.config(text="🚶 Strolling...", fg="#38ef7d")
            self.walk_loop()
        else:
            self.walk_btn.config(text="🚶 Walk: OFF", fg="#888888", bg="#1f1f1f")
            self.speech_lbl.config(text="✨ Click me!", fg="#38ef7d")

    def walk_loop(self):
        if not self.is_walking:
            return

        if not self.is_hopping:
            curr_x = self.root.winfo_x()
            curr_y = self.root.winfo_y()
            step_pixels = 3 * self.walk_direction

            # Boundary check: bounce off monitor walls
            if curr_x + step_pixels + self.win_w >= self.sw - 10:
                self.walk_direction = -1
                self.speech_lbl.config(text="↩️ Turning around!", fg="#00e5ff")
            elif curr_x + step_pixels <= 10:
                self.walk_direction = 1
                self.speech_lbl.config(text="↪️ Turning around!", fg="#00e5ff")

            new_x = curr_x + (3 * self.walk_direction)
            self.root.geometry(f"+{new_x}+{curr_y}")

        self.root.after(45, self.walk_loop)

    def switch_gif(self, key: str):
        if key in self.available_gifs and self.available_gifs[key].exists():
            if hasattr(self, "anim_after_id"):
                self.root.after_cancel(self.anim_after_id)
            self.load_gif(self.available_gifs[key])

    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def close(self):
        self.is_walking = False
        if hasattr(self, "anim_after_id"):
            self.root.after_cancel(self.anim_after_id)
        self.root.destroy()


def launch_desktop_companion(gif_path: str = None):
    ensure_single_instance()
    root = tk.Tk()
    app = DesktopCompanionApp(root, gif_path)
    root.mainloop()


if __name__ == "__main__":
    gif = sys.argv[1] if len(sys.argv) > 1 else None
    launch_desktop_companion(gif)
