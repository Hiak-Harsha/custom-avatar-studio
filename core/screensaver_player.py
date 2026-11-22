"""
Native Fullscreen Screensaver Player for Windows
Displays the animated HIAK <-> HARSHA pixel morph and reactive mascot loop.
Exits immediately on any mouse movement, click, or keyboard input.
"""
import sys
import time
from pathlib import Path
import tkinter as tk
from PIL import Image, ImageTk

STUDIO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(STUDIO_ROOT))

MORPH_DIR = STUDIO_ROOT / "assets" / "wallpapers" / "poses_hiak_harsha_morph"
BG_COLOR = "#0A0A0A"


class ScreensaverApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("HIAK HARSHA Screensaver")
        
        # Configure borderless fullscreen
        self.root.configure(bg=BG_COLOR)
        self.root.attributes("-fullscreen", True)
        self.root.config(cursor="none") # Hide mouse cursor in screensaver
        
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        
        self.canvas = tk.Canvas(
            self.root,
            width=self.screen_w,
            height=self.screen_h,
            bg=BG_COLOR,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Frame sequence & timings (ms) with Option 4 Cyber-Bot for Harsha
        self.frame_specs = [
            ("1_1_hiak_solid.png", 1400),
            ("2_2_hiak_cool.png", 1100),
            ("3_3_dissolve_start.png", 120),
            ("4_4_glitch_midway.png", 120),
            ("5_5_harsha_forming.png", 150),
            ("6_6_harsha_cyber_bot_coding.png", 1800),
            ("7_7_harsha_cyber_bot_happy.png", 1200),
            ("8_8_morph_return.png", 140),
        ]
        
        self.cached_images = []
        self._load_and_cache_frames()
        
        self.current_frame_idx = 0
        self.img_item = self.canvas.create_image(
            self.screen_w // 2,
            self.screen_h // 2,
            image=self.cached_images[0] if self.cached_images else None
        )
        
        # Mouse movement tracking (avoid exiting on jitter < 15px)
        self.last_mouse_x = None
        self.last_mouse_y = None
        
        # Bind exit triggers
        self.root.bind("<Key>", self.exit_screensaver)
        self.root.bind("<Button>", self.exit_screensaver)
        self.root.bind("<Motion>", self.handle_motion)
        
        # Start playback loop
        self.schedule_next_frame()

    def _load_and_cache_frames(self):
        for fname, _ in self.frame_specs:
            p = MORPH_DIR / fname
            if not p.exists():
                p = STUDIO_ROOT / "assets" / "wallpapers" / "poses" / "1_neutral.png"
            
            with Image.open(str(p)) as im:
                # Fit image nicely on the screen while maintaining 16:9 aspect ratio
                im_ratio = im.width / im.height
                screen_ratio = self.screen_w / self.screen_h
                
                if screen_ratio > im_ratio:
                    new_h = self.screen_h
                    new_w = int(new_h * im_ratio)
                else:
                    new_w = self.screen_w
                    new_h = int(new_w / im_ratio)
                
                resized = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
                
                # Composite onto exact black canvas matching screen
                canvas_im = Image.new("RGB", (self.screen_w, self.screen_h), (10, 10, 10))
                paste_x = (self.screen_w - new_w) // 2
                paste_y = (self.screen_h - new_h) // 2
                canvas_im.paste(resized, (paste_x, paste_y))
                
                self.cached_images.append(ImageTk.PhotoImage(canvas_im))

    def schedule_next_frame(self):
        if not self.cached_images:
            return
        
        # Update canvas
        self.canvas.itemconfig(self.img_item, image=self.cached_images[self.current_frame_idx])
        
        _, duration_ms = self.frame_specs[self.current_frame_idx]
        self.current_frame_idx = (self.current_frame_idx + 1) % len(self.cached_images)
        
        self.root.after(duration_ms, self.schedule_next_frame)

    def handle_motion(self, event):
        if self.last_mouse_x is None:
            self.last_mouse_x = event.x
            self.last_mouse_y = event.y
            return
        
        dx = abs(event.x - self.last_mouse_x)
        dy = abs(event.y - self.last_mouse_y)
        if dx > 15 or dy > 15:
            self.exit_screensaver()

    def exit_screensaver(self, event=None):
        self.root.destroy()


def run_screensaver():
    root = tk.Tk()
    app = ScreensaverApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_screensaver()
