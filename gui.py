"""
AvatarStudio Desktop GUI
A sleek, modern Tkinter-based control panel to preview styles, switch wallpapers,
customize opacity, apply configurations everywhere, and copy assets for WhatsApp.
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from PIL import Image, ImageTk

STUDIO_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(STUDIO_ROOT))

from core.profile import ProfileManager
from core.wallpaper import apply_desktop_wallpaper, apply_lock_screen_wallpaper
from core.terminal import apply_terminal_background
from core.banner import install_powershell_banner, remove_powershell_banner
from core.screensaver import open_screensaver_settings
from core.export import export_html_card
from core.whatsapp import copy_image_to_clipboard


class AvatarStudioGUI:
    def __init__(self, root, studio_root: str):
        self.root = root
        self.studio_root = Path(studio_root)
        self.pm = ProfileManager(str(self.studio_root))

        self.root.title("AvatarStudio — 1-Click Persona, Wallpaper & WhatsApp Switcher")
        self.root.geometry("960x690")
        self.root.minsize(890, 630)
        self.root.configure(bg="#11131a")

        self.load_data()
        self.setup_ui()
        self.select_style(self.active_style_id, apply_now=False)

    def load_data(self):
        self.styles_data = self.pm.get_styles().get("styles", {})
        self.profile = self.pm.get_profile()
        self.active_style_id = self.profile.get("active_style", "hiak_pixel")
        self.user_name = self.profile.get("user_name", "Madhav")

    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#181b26", height=65, padx=20, pady=10)
        header.pack(fill="x", side="top")

        title_frame = tk.Frame(header, bg="#181b26")
        title_frame.pack(side="left")

        title_lbl = tk.Label(
            title_frame,
            text="⚡ AvatarStudio",
            font=("Segoe UI", 16, "bold"),
            fg="#00e5ff",
            bg="#181b26"
        )
        title_lbl.pack(anchor="w")

        self.user_lbl = tk.Label(
            title_frame,
            text=f"User: {self.user_name}  |  Active: {self.styles_data.get(self.active_style_id, {}).get('name', 'None')}",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#181b26"
        )
        self.user_lbl.pack(anchor="w")

        # Right header buttons
        right_hdr = tk.Frame(header, bg="#181b26")
        right_hdr.pack(side="right")

        cycle_btn = tk.Button(
            right_hdr,
            text="🔀 1-Click Next Style",
            font=("Segoe UI", 10, "bold"),
            bg="#00e5ff",
            fg="#000",
            relief="flat",
            padx=14,
            pady=6,
            command=self.cycle_next,
            cursor="hand2"
        )
        cycle_btn.pack(side="left", padx=10)

        cust_btn = tk.Button(
            right_hdr,
            text="👤 Customize Persona",
            font=("Segoe UI", 9),
            bg="#2a2e40",
            fg="#e2e8f0",
            relief="flat",
            padx=10,
            pady=6,
            command=self.open_customize_dialog,
            cursor="hand2"
        )
        cust_btn.pack(side="left")

        # Main Layout: 2 Columns
        main_pane = tk.Frame(self.root, bg="#11131a", padx=15, pady=12)
        main_pane.pack(fill="both", expand=True)

        # Left Column: Styles list (Instant 1-Click Switching)
        left_col = tk.Frame(main_pane, bg="#181b26", width=290, padx=12, pady=12)
        left_col.pack(side="left", fill="y", padx=(0, 10))
        left_col.pack_propagate(False)

        tk.Label(
            left_col,
            text="1-CLICK STYLES (CLICK TO APPLY)",
            font=("Segoe UI", 8, "bold"),
            fg="#38ef7d",
            bg="#181b26"
        ).pack(anchor="w", pady=(0, 8))

        self.style_buttons = {}
        for sid, sinfo in self.styles_data.items():
            btn = tk.Button(
                left_col,
                text=f"{sinfo.get('name')}\n• {sinfo.get('vibe')}",
                font=("Segoe UI", 9),
                justify="left",
                bg="#212534",
                fg="#f1f5f9",
                activebackground="#00e5ff",
                activeforeground="#000",
                relief="flat",
                padx=10,
                pady=7,
                cursor="hand2",
                command=lambda s=sid: self.select_style(s, apply_now=True)
            )
            btn.pack(fill="x", pady=2)
            self.style_buttons[sid] = btn

        # Right Column: Preview & Apply Controls
        right_col = tk.Frame(main_pane, bg="#181b26", padx=15, pady=12)
        right_col.pack(side="left", fill="both", expand=True)

        hdr_right = tk.Frame(right_col, bg="#181b26")
        hdr_right.pack(fill="x")

        self.curr_name_lbl = tk.Label(
            hdr_right,
            text="",
            font=("Segoe UI", 13, "bold"),
            fg="#f8fafc",
            bg="#181b26"
        )
        self.curr_name_lbl.pack(side="left")

        self.badge_lbl = tk.Label(
            hdr_right,
            text="⚡ ACTIVE",
            font=("Segoe UI", 8, "bold"),
            fg="#000",
            bg="#38ef7d",
            padx=6,
            pady=2
        )
        self.badge_lbl.pack(side="left", padx=10)

        self.curr_desc_lbl = tk.Label(
            right_col,
            text="",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#181b26",
            wraplength=500,
            justify="left"
        )
        self.curr_desc_lbl.pack(anchor="w", pady=(2, 6))

        # Preview Image Frame
        self.preview_canvas = tk.Label(right_col, bg="#0b0d13", relief="solid", borderwidth=1)
        self.preview_canvas.pack(fill="x", pady=4)

        # Settings Options Frame
        opts_frame = tk.Frame(right_col, bg="#181b26", pady=6)
        opts_frame.pack(fill="x")

        # Terminal Opacity
        tk.Label(
            opts_frame,
            text="Terminal Opacity:",
            font=("Segoe UI", 9),
            fg="#cbd5e1",
            bg="#181b26"
        ).grid(row=0, column=0, sticky="w", pady=2)

        self.opacity_var = tk.DoubleVar(value=self.profile.get("terminal", {}).get("opacity", 0.35))
        self.opacity_scale = tk.Scale(
            opts_frame,
            from_=0.10,
            to=0.90,
            resolution=0.05,
            orient="horizontal",
            variable=self.opacity_var,
            bg="#181b26",
            fg="#00e5ff",
            highlightthickness=0,
            troughcolor="#2a2e40",
            length=180,
            command=lambda v: self.on_opacity_change()
        )
        self.opacity_scale.grid(row=0, column=1, sticky="w", padx=10, pady=2)

        # Checkboxes for target integrations
        self.chk_terminal = tk.BooleanVar(value=True)
        self.chk_desktop = tk.BooleanVar(value=True)
        self.chk_lock_screen = tk.BooleanVar(value=self.pm.is_lock_screen_enabled())
        self.chk_banner = tk.BooleanVar(value=True)

        cb_frame = tk.Frame(opts_frame, bg="#181b26")
        cb_frame.grid(row=1, column=0, columnspan=2, sticky="w", pady=4)

        tk.Checkbutton(
            cb_frame,
            text="Windows Terminal (CMD / PowerShell background)",
            variable=self.chk_terminal,
            font=("Segoe UI", 9),
            fg="#e2e8f0",
            bg="#181b26",
            selectcolor="#11131a",
            activebackground="#181b26",
            activeforeground="#00e5ff"
        ).pack(anchor="w")

        tk.Checkbutton(
            cb_frame,
            text="Desktop Wallpaper",
            variable=self.chk_desktop,
            font=("Segoe UI", 9),
            fg="#e2e8f0",
            bg="#181b26",
            selectcolor="#11131a",
            activebackground="#181b26",
            activeforeground="#00e5ff"
        ).pack(anchor="w")

        tk.Checkbutton(
            cb_frame,
            text="Lock Screen Wallpaper (Syncs Windows Lock Screen)",
            variable=self.chk_lock_screen,
            font=("Segoe UI", 9),
            fg="#e2e8f0",
            bg="#181b26",
            selectcolor="#11131a",
            activebackground="#181b26",
            activeforeground="#00e5ff"
        ).pack(anchor="w")

        tk.Checkbutton(
            cb_frame,
            text="HIAK CLI Welcome Banner (Shows blocky pixel logo on launch)",
            variable=self.chk_banner,
            font=("Segoe UI", 9),
            fg="#e2e8f0",
            bg="#181b26",
            selectcolor="#11131a",
            activebackground="#181b26",
            activeforeground="#00e5ff"
        ).pack(anchor="w")

        # Action Buttons
        btn_frame = tk.Frame(right_col, bg="#181b26", pady=6)
        btn_frame.pack(fill="x")

        wa_copy_btn = tk.Button(
            btn_frame,
            text="📱 Copy for WhatsApp (Ctrl+V)",
            font=("Segoe UI", 9, "bold"),
            bg="#25D366",
            fg="#000",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.copy_for_whatsapp
        )
        wa_copy_btn.pack(side="left", padx=(0, 8))

        wa_folder_btn = tk.Button(
            btn_frame,
            text="📂 WhatsApp Folder",
            font=("Segoe UI", 9),
            bg="#2a2e40",
            fg="#e2e8f0",
            relief="flat",
            padx=10,
            pady=6,
            cursor="hand2",
            command=self.open_wa_folder
        )
        wa_folder_btn.pack(side="left", padx=(0, 8))

        scr_btn = tk.Button(
            btn_frame,
            text="🖥️ Screensaver",
            font=("Segoe UI", 9),
            bg="#2a2e40",
            fg="#e2e8f0",
            relief="flat",
            padx=10,
            pady=6,
            cursor="hand2",
            command=open_screensaver_settings
        )
        scr_btn.pack(side="left", padx=(0, 8))

        exp_btn = tk.Button(
            btn_frame,
            text="📄 Persona Card",
            font=("Segoe UI", 9),
            bg="#2a2e40",
            fg="#e2e8f0",
            relief="flat",
            padx=10,
            pady=6,
            cursor="hand2",
            command=self.export_card
        )
        exp_btn.pack(side="left")

        # Status Bar
        self.status_bar = tk.Label(
            self.root,
            text="⚡ Ready. Click any style to switch instantly in 1 click!",
            font=("Segoe UI", 9),
            fg="#38ef7d",
            bg="#0b0d13",
            anchor="w",
            padx=15,
            pady=6
        )
        self.status_bar.pack(fill="x", side="bottom")

    def select_style(self, style_id: str, apply_now: bool = True):
        self.selected_style_id = style_id
        for sid, btn in self.style_buttons.items():
            if sid == style_id:
                btn.configure(bg="#00e5ff", fg="#000")
            else:
                btn.configure(bg="#212534", fg="#f1f5f9")

        sinfo = self.styles_data.get(style_id, {})
        self.curr_name_lbl.config(text=sinfo.get("name", style_id))
        self.curr_desc_lbl.config(text=sinfo.get("description", ""))

        wall_rel = sinfo.get("wallpaper")
        if wall_rel:
            wall_path = self.studio_root / wall_rel
            if wall_path.exists():
                try:
                    img = Image.open(str(wall_path))
                    img.thumbnail((480, 205), Image.Resampling.LANCZOS)
                    self.tk_preview = ImageTk.PhotoImage(img)
                    self.preview_canvas.config(image=self.tk_preview)
                except Exception as e:
                    self.preview_canvas.config(text=f"Preview error: {e}", image="")

        if apply_now:
            self.apply_current(silent=True)

    def cycle_next(self):
        next_id = self.pm.cycle_next_style()
        self.select_style(next_id, apply_now=True)

    def on_opacity_change(self):
        profile = self.pm.get_profile()
        profile["terminal"]["opacity"] = round(self.opacity_var.get(), 2)
        self.pm.save_profile(profile)
        sinfo = self.styles_data.get(self.selected_style_id, {})
        wall_path = self.studio_root / sinfo.get("wallpaper", "")
        if self.chk_terminal.get() and wall_path.exists():
            apply_terminal_background(str(wall_path), opacity=profile["terminal"]["opacity"])

    def apply_current(self, silent: bool = False):
        style_id = self.selected_style_id
        self.pm.set_active_style(style_id)
        sinfo = self.styles_data.get(style_id, {})
        wall_path = self.studio_root / sinfo.get("wallpaper", "")
        banner_path = self.studio_root / sinfo.get("banner", "")

        opacity = round(self.opacity_var.get(), 2)
        applied = []

        if self.chk_terminal.get():
            try:
                apply_terminal_background(str(wall_path), opacity=opacity)
                applied.append("Terminal")
            except Exception:
                pass

        if self.chk_desktop.get():
            try:
                apply_desktop_wallpaper(str(wall_path))
                applied.append("Desktop")
            except Exception:
                pass

        self.pm.set_lock_screen_enabled(self.chk_lock_screen.get())
        if self.chk_lock_screen.get():
            try:
                apply_lock_screen_wallpaper(str(wall_path))
                applied.append("Lock Screen")
            except Exception:
                pass

        if self.chk_banner.get():
            try:
                install_powershell_banner(
                    str(banner_path),
                    user_name=self.user_name,
                    style_name=sinfo.get("name", style_id)
                )
                applied.append("Banner")
            except Exception:
                pass
        else:
            remove_powershell_banner()

        self.user_lbl.config(text=f"User: {self.user_name}  |  Active: {sinfo.get('name')}")
        self.badge_lbl.config(text="⚡ ACTIVE", bg="#38ef7d")
        msg = f"Switched to {sinfo.get('name')} ({', '.join(applied)})!"
        self.status_bar.config(text=f"✅ {msg}", fg="#38ef7d")
        if not silent:
            messagebox.showinfo("Success", msg)

    def copy_for_whatsapp(self):
        sinfo = self.styles_data.get(self.selected_style_id, {})
        wa_dp = self.studio_root / "assets" / "whatsapp" / f"{self.selected_style_id}_whatsapp_dp.jpg"
        if not wa_dp.exists():
            wa_dp = self.studio_root / "assets" / "whatsapp" / "hiak_whatsapp_dp.jpg"
        if not wa_dp.exists():
            wa_dp = self.studio_root / sinfo.get("avatar", "")

        try:
            copy_image_to_clipboard(str(wa_dp))
            self.status_bar.config(text="📱 Copied image to clipboard! Open WhatsApp and press Ctrl + V.", fg="#25D366")
            messagebox.showinfo("WhatsApp Ready", "Image copied to Windows Clipboard!\n\nNow open WhatsApp (Desktop or Web) and simply press Ctrl + V.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy image: {e}")

    def open_wa_folder(self):
        wa_dir = self.studio_root / "assets" / "whatsapp"
        os.system(f'explorer "{wa_dir}"')

    def export_card(self):
        style_id = self.selected_style_id
        sinfo = self.styles_data.get(style_id, {})
        avatar_path = self.studio_root / sinfo.get("avatar", "")
        wall_path = self.studio_root / sinfo.get("wallpaper", "")
        out_html = self.studio_root / "assets" / f"persona_card_{style_id}.html"

        export_html_card(
            str(avatar_path),
            str(wall_path),
            self.user_name,
            sinfo.get("name", style_id),
            str(out_html)
        )
        os.system(f'start "" "{out_html}"')
        self.status_bar.config(text=f"📄 Opened Persona Card in browser.", fg="#00e5ff")

    def open_customize_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Customize Persona")
        win.geometry("400x260")
        win.configure(bg="#181b26")
        win.grab_set()

        tk.Label(win, text="Custom Persona Setup", font=("Segoe UI", 12, "bold"), fg="#00e5ff", bg="#181b26").pack(pady=10)

        f = tk.Frame(win, bg="#181b26", padx=20)
        f.pack(fill="both")

        tk.Label(f, text="Your Name:", font=("Segoe UI", 9), fg="#cbd5e1", bg="#181b26").grid(row=0, column=0, sticky="w", pady=5)
        name_entry = tk.Entry(f, font=("Segoe UI", 9), width=25)
        name_entry.insert(0, self.user_name)
        name_entry.grid(row=0, column=1, pady=5)

        tk.Label(f, text="Role / Persona:", font=("Segoe UI", 9), fg="#cbd5e1", bg="#181b26").grid(row=1, column=0, sticky="w", pady=5)
        role_entry = tk.Entry(f, font=("Segoe UI", 9), width=25)
        role_entry.insert(0, "Tech Creator & Coder")
        role_entry.grid(row=1, column=1, pady=5)

        def save():
            new_name = name_entry.get().strip() or "Madhav"
            new_role = role_entry.get().strip() or "Tech Creator"
            self.pm.add_or_update_user(new_name, favorite_style=self.selected_style_id, persona=new_role)
            self.user_name = new_name
            self.user_lbl.config(text=f"User: {self.user_name}  |  Active: {self.styles_data.get(self.selected_style_id, {}).get('name')}")
            win.destroy()
            self.status_bar.config(text=f"Saved profile for {new_name}!", fg="#38ef7d")

        tk.Button(
            win,
            text="Save Persona",
            font=("Segoe UI", 10, "bold"),
            bg="#00e5ff",
            fg="#000",
            relief="flat",
            padx=15,
            pady=5,
            cursor="hand2",
            command=save
        ).pack(pady=15)


def launch_gui(studio_root: str):
    root = tk.Tk()
    app = AvatarStudioGUI(root, studio_root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui(str(STUDIO_ROOT))
