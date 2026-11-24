"""
AvatarStudio CLI
Command-line interface to switch styles, apply wallpapers to Windows Terminal & Desktop,
toggle welcome banners, manage user personas, and export/copy for WhatsApp.
"""
import argparse
import os
import sys
from pathlib import Path

STUDIO_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(STUDIO_ROOT))

from core.profile import ProfileManager
from core.wallpaper import apply_desktop_wallpaper, apply_lock_screen_wallpaper, get_lock_screen_wallpaper
from core.terminal import apply_terminal_background, remove_terminal_background
from core.banner import install_powershell_banner, remove_powershell_banner
from core.screensaver import open_screensaver_settings, launch_screensaver_player
from core.export import export_html_card
from core.whatsapp import copy_image_to_clipboard, create_whatsapp_dp, create_whatsapp_chat_wallpaper


def apply_active_style(
    pm: ProfileManager,
    silent: bool = False,
    terminal_only: bool = False,
    desktop_only: bool = False,
    lock_screen_only: bool = False
):
    style = pm.get_active_style()
    profile = pm.get_profile()
    user_name = profile.get("user_name", "Madhav")
    style_name = style.get("name", "Active Style")
    style_id = style.get("id", "hiak_pixel")

    wall_path = STUDIO_ROOT / style["wallpaper"]
    banner_path = STUDIO_ROOT / style["banner"]

    apply_all = not (terminal_only or desktop_only or lock_screen_only)

    if apply_all or terminal_only:
        try:
            opacity = profile.get("terminal", {}).get("opacity", 0.35)
            alignment = profile.get("terminal", {}).get("alignment", "bottomRight")
            stretch = profile.get("terminal", {}).get("stretch", "uniformToFill")
            term_bg = STUDIO_ROOT / style.get("gif", style["wallpaper"])
            apply_terminal_background(str(term_bg), opacity=opacity, alignment=alignment, stretch=stretch)
            if not silent:
                print(f"  ✅ Windows Terminal background updated! ({style_name})")
        except Exception as e:
            if not silent:
                print(f"  ⚠️ Terminal update note: {e}")

    if apply_all or desktop_only:
        try:
            apply_desktop_wallpaper(str(wall_path))
            if not silent:
                print(f"  ✅ Windows Desktop Wallpaper updated! ({style_name})")
        except Exception as e:
            if not silent:
                print(f"  ⚠️ Desktop Wallpaper update note: {e}")

    if lock_screen_only or (apply_all and pm.is_lock_screen_enabled()):
        try:
            apply_lock_screen_wallpaper(str(wall_path))
            if not silent:
                print(f"  ✅ Windows Lock Screen wallpaper updated! ({style_name})")
        except Exception as e:
            if not silent:
                print(f"  ⚠️ Lock Screen update note: {e}")

    if apply_all and profile.get("banner", {}).get("show_on_powershell_startup", True):
        try:
            install_powershell_banner(str(banner_path), user_name=user_name, style_name=style_name)
            if not silent:
                print(f"  ✅ Terminal startup HIAK pixel greeting banner synchronized!")
        except Exception:
            pass


def cmd_list(args, pm: ProfileManager):
    styles = pm.get_styles().get("styles", {})
    profile = pm.get_profile()
    active_id = profile.get("active_style", "hiak_pixel")

    print("\n" + "=" * 60)
    print(f"  🎨 AVATAR STUDIO — AVAILABLE STYLES (User: {profile.get('user_name', 'Madhav')})")
    print("=" * 60)
    for sid, s in styles.items():
        is_active = " [ACTIVE ★]" if sid == active_id else ""
        print(f"\n  • ID: {sid}{is_active}")
        print(f"    Name: {s.get('name')}")
        print(f"    Vibe: {s.get('vibe')}")
        print(f"    Description: {s.get('description')}")
    print("\n" + "=" * 60)
    print("  Use 'python cli.py switch <id>' or 'python cli.py next' to switch instantly!\n")


def cmd_switch(args, pm: ProfileManager):
    style_id = args.style_id.lower().strip()
    try:
        resolved_id = pm.set_active_style(style_id)
    except ValueError as e:
        print(f"❌ Error: {e}")
        return

    style = pm.get_active_style()
    if not getattr(args, "silent", False):
        print(f"\n🔄 Switched active style to: {style.get('name')} ({resolved_id})")

    if not getattr(args, "no_apply", False):
        apply_active_style(
            pm,
            silent=getattr(args, "silent", False),
            terminal_only=getattr(args, "terminal_only", False),
            desktop_only=getattr(args, "desktop_only", False),
            lock_screen_only=getattr(args, "lock_only", False)
        )
    if not getattr(args, "silent", False):
        print("\n✨ 1-Click Switch Complete! Open a new CMD or PowerShell window to see your new look!\n")


def cmd_next(args, pm: ProfileManager):
    next_id = pm.cycle_next_style()
    style = pm.get_active_style()
    if not getattr(args, "silent", False):
        print(f"\n🔀 Cycled to next style: {style.get('name')} ({next_id})")
    apply_active_style(pm, silent=getattr(args, "silent", False))
    if not getattr(args, "silent", False):
        print("✨ 1-Click Cycle Complete!\n")


def cmd_preview(args, pm: ProfileManager):
    style = pm.get_active_style()
    banner_file = STUDIO_ROOT / style["banner"]
    if banner_file.exists():
        with open(banner_file, "r", encoding="utf-8") as f:
            print(f.read())
        print(f"\n⚡ Showing ANSI TrueColor preview for: {style.get('name')}\n")
    else:
        print(f"Banner file not found: {banner_file}")


def cmd_apply(args, pm: ProfileManager):
    apply_active_style(
        pm,
        silent=False,
        terminal_only=getattr(args, "terminal_only", False),
        desktop_only=getattr(args, "desktop_only", False),
        lock_screen_only=getattr(args, "lock_only", False)
    )


def cmd_lockscreen(args, pm: ProfileManager):
    action = args.action
    if action == "enable":
        pm.set_lock_screen_enabled(True)
        print("  ✅ Lock Screen auto-sync enabled.")
        apply_active_style(pm, silent=False, lock_screen_only=True)
    elif action == "disable":
        pm.set_lock_screen_enabled(False)
        print("  ⚠️ Lock Screen auto-sync disabled.")
    elif action == "status":
        enabled = pm.is_lock_screen_enabled()
        current_img = get_lock_screen_wallpaper() or "(Windows Spotlight / not set)"
        print(f"\n  🔒 Lock Screen Auto-Sync: {'ENABLED' if enabled else 'DISABLED'}")
        print(f"  🖼️ Current Lock Screen Image: {current_img}\n")
    else:
        from core.wallpaper_animator import get_active_wallpaper_path
        target = get_active_wallpaper_path() or (STUDIO_ROOT / pm.get_active_style()["wallpaper"])
        apply_lock_screen_wallpaper(str(target))
        print(f"  ✅ Windows Lock Screen updated to: {target.name}")


def cmd_banner(args, pm: ProfileManager):
    if args.action == "enable":
        style = pm.get_active_style()
        profile = pm.get_profile()
        banner_path = STUDIO_ROOT / style["banner"]
        install_powershell_banner(str(banner_path), user_name=profile.get("user_name", "Madhav"), style_name=style.get("name"))
        print("  ✅ Terminal welcome banner enabled on startup.")
    elif args.action == "disable":
        remove_powershell_banner()
        print("  ✅ Terminal welcome banner removed from startup.")
    elif args.action == "preview":
        cmd_preview(args, pm)


def cmd_copy_whatsapp(args, pm: ProfileManager):
    style = pm.get_active_style()
    # Check if a WhatsApp DP exists for this style or fallback to avatar
    wa_dp = STUDIO_ROOT / "assets" / "whatsapp" / f"{style['id']}_whatsapp_dp.jpg"
    if not wa_dp.exists():
        # Fallback to general hiak dp or active avatar
        wa_dp = STUDIO_ROOT / "assets" / "whatsapp" / "hiak_whatsapp_dp.jpg"
    if not wa_dp.exists():
        wa_dp = STUDIO_ROOT / style["avatar"]

    try:
        copy_image_to_clipboard(str(wa_dp))
        print("\n" + "=" * 60)
        print("  📱 COPIED TO CLIPBOARD FOR WHATSAPP!")
        print("=" * 60)
        print(f"  Target: {wa_dp.name}")
        print("  Now simply open WhatsApp (Web or Desktop) and press Ctrl + V!")
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"❌ Failed to copy to clipboard: {e}")


def cmd_whatsapp_export(args, pm: ProfileManager):
    wa_dir = STUDIO_ROOT / "assets" / "whatsapp"
    wa_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n📂 WhatsApp Assets Directory: {wa_dir}")
    print("Files ready for WhatsApp:")
    for f in wa_dir.glob("*.jpg"):
        print(f"  • {f.name}")
    os.system(f'explorer "{wa_dir}"')


def cmd_screensaver(args, pm: ProfileManager):
    if args.action == "open":
        open_screensaver_settings()
        print("  🖥️ Opened Windows Screen Saver settings.")
    elif args.action == "test":
        launch_screensaver_player()


def cmd_export(args, pm: ProfileManager):
    style = pm.get_active_style()
    profile = pm.get_profile()
    avatar_path = STUDIO_ROOT / style["avatar"]
    wall_path = STUDIO_ROOT / style["wallpaper"]
    out_html = STUDIO_ROOT / "assets" / f"persona_card_{style['id']}.html"
    export_html_card(
        str(avatar_path),
        str(wall_path),
        profile.get("user_name", "Madhav"),
        style.get("name"),
        str(out_html)
    )
    print(f"  📄 Persona Card HTML generated at: {out_html}")
    if args.open:
        os.system(f'start "" "{out_html}"')


def cmd_customize(args, pm: ProfileManager):
    print("\n" + "=" * 60)
    print("  👤 AVATAR STUDIO — PERSONA CUSTOMIZATION WIZARD")
    print("=" * 60)
    name = input("Enter your name (e.g. Madhav, Alex): ").strip() or "Madhav"
    persona = input("Enter your role/persona (e.g. Full-Stack Coder, AI Researcher): ").strip() or "Tech Creator"
    
    styles = pm.get_styles().get("styles", {})
    print("\nChoose default style:")
    s_keys = list(styles.keys())
    for idx, k in enumerate(s_keys, 1):
        print(f"  {idx}. {styles[k].get('name')} ({k})")
    
    choice = input(f"Enter number [1-{len(s_keys)}] (default 1): ").strip()
    try:
        fav_key = s_keys[int(choice) - 1]
    except Exception:
        fav_key = "hiak_pixel"

    pm.add_or_update_user(name, favorite_style=fav_key, persona=persona)
    print(f"\n🎉 Profile saved for {name}! Active style set to {fav_key}.")
    pm.set_active_style(fav_key)
    apply_active_style(pm)


def cmd_gui(args, pm: ProfileManager):
    from gui import launch_gui
    launch_gui(str(STUDIO_ROOT))


def main():
    parser = argparse.ArgumentParser(description="AvatarStudio - Custom Cartoon Avatar & Terminal Switcher")
    subparsers = parser.add_subparsers(dest="command")

    # list
    subparsers.add_parser("list", help="List all available cartoon/wallpaper styles")

    # next / cycle
    p_next = subparsers.add_parser("next", help="Cycle to the next style in 1 click")
    p_next.add_argument("--silent", action="store_true", help="Quiet mode")

    p_cycle = subparsers.add_parser("cycle", help="Cycle to the next style in 1 click")
    p_cycle.add_argument("--silent", action="store_true", help="Quiet mode")

    # switch
    p_switch = subparsers.add_parser("switch", help="Switch to a style and apply everywhere")
    p_switch.add_argument("style_id", type=str, help="Style ID or alias (hiak, pixel, cyber, ghibli, pixar, comic)")
    p_switch.add_argument("--silent", action="store_true", help="Quiet mode")
    p_switch.add_argument("--terminal-only", action="store_true", help="Only apply to Windows Terminal")
    p_switch.add_argument("--desktop-only", action="store_true", help="Only apply to Desktop Wallpaper")
    p_switch.add_argument("--lock-only", action="store_true", help="Only apply to Windows Lock Screen")
    p_switch.add_argument("--no-apply", action="store_true", help="Change config without applying system changes")

    # preview
    subparsers.add_parser("preview", help="Preview active style ANSI banner in console")

    # apply
    p_apply = subparsers.add_parser("apply", help="Apply current active style to targets")
    p_apply.add_argument("--terminal-only", action="store_true", help="Only apply to Windows Terminal")
    p_apply.add_argument("--desktop-only", action="store_true", help="Only apply to Desktop Wallpaper")
    p_apply.add_argument("--lock-only", action="store_true", help="Only apply to Windows Lock Screen")

    # lockscreen
    p_lock = subparsers.add_parser("lockscreen", help="Manage Windows Lock Screen background sync")
    p_lock.add_argument("action", choices=["apply", "enable", "disable", "status"], default="apply", nargs="?")

    # banner
    p_banner = subparsers.add_parser("banner", help="Manage terminal startup welcome banner")
    p_banner.add_argument("action", choices=["enable", "disable", "preview"], default="preview", nargs="?")

    # copy-whatsapp
    subparsers.add_parser("copy-whatsapp", help="Copy DP directly to Windows clipboard for WhatsApp (Ctrl+V)")

    # whatsapp
    subparsers.add_parser("whatsapp", help="Open WhatsApp export folder")

    # screensaver
    p_scr = subparsers.add_parser("screensaver", help="Manage screensaver settings")
    p_scr.add_argument("action", choices=["open", "test"], default="open", nargs="?")

    # export
    p_exp = subparsers.add_parser("export", help="Export Persona Card HTML/PDF format")
    p_exp.add_argument("--open", action="store_true", help="Open card in browser after generation")

    # customize
    subparsers.add_parser("customize", help="Run interactive persona wizard for any user")

    # create
    p_create = subparsers.add_parser("create", help="Generate complete OpenCode + Mascot pack for any custom name")
    p_create.add_argument("name", type=str, help="Custom name (e.g. HARSHA, ALEX, JOHN, DEV)")
    p_create.add_argument("--user", type=str, default=None, help="Display user name")
    p_create.add_argument("--role", type=str, default="Creator & Coder", help="Role / tagline")

    # gui
    subparsers.add_parser("gui", help="Launch interactive Desktop GUI")

    args = parser.parse_args()
    pm = ProfileManager(str(STUDIO_ROOT))

    if args.command == "create":
        from core.generator import generate_persona
        name = args.name.strip()
        user_name = args.user or name
        persona = args.role or "Creator & Coder"
        print(f"\n✨ Generating OpenCode Mascot Studio pack for: {name}...")
        res = generate_persona(name, display_user=user_name, persona=persona)
        print(f"  ✅ 7 Wallpaper Poses generated in: assets/wallpapers/poses_{res['slug']}/")
        print(f"  ✅ Terminal Animated GIF generated: {res['terminal_gif']}")
        print(f"  ✅ 24-bit TrueColor ANSI banner: {res['banner']}")
        print(f"  ✅ WhatsApp DP & Animated Avatar generated: {res['whatsapp_dp']}")
        print(f"\n🎉 Successfully created profile '{res['slug']}'!")
        print(f"To apply this persona immediately, run:")
        print(f"  hiak switch {res['slug']}\n")
    elif args.command == "list":
        cmd_list(args, pm)
    elif args.command in ["next", "cycle"]:
        cmd_next(args, pm)
    elif args.command == "switch":
        cmd_switch(args, pm)
    elif args.command == "preview":
        cmd_preview(args, pm)
    elif args.command == "apply":
        cmd_apply(args, pm)
    elif args.command == "lockscreen":
        cmd_lockscreen(args, pm)
    elif args.command == "banner":
        cmd_banner(args, pm)
    elif args.command == "copy-whatsapp":
        cmd_copy_whatsapp(args, pm)
    elif args.command == "whatsapp":
        cmd_whatsapp_export(args, pm)
    elif args.command == "screensaver":
        cmd_screensaver(args, pm)
    elif args.command == "export":
        cmd_export(args, pm)
    elif args.command == "customize":
        cmd_customize(args, pm)
    elif args.command == "gui":
        cmd_gui(args, pm)
    else:
        cmd_list(args, pm)


if __name__ == "__main__":
    main()
