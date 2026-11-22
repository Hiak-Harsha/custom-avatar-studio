"""
Profile and Persona Manager
Handles user profiles, active style configurations, and user trait personalization
so any person can create, customize, and switch styles.
"""
import json
from pathlib import Path


class ProfileManager:
    def __init__(self, studio_root: str):
        self.studio_root = Path(studio_root)
        self.config_dir = self.studio_root / "config"
        self.profile_file = self.config_dir / "current_profile.json"
        self.styles_file = self.config_dir / "styles.json"

    def get_profile(self) -> dict:
        if not self.profile_file.exists():
            return {
                "user_name": "Madhav",
                "active_style": "pixel_art",
                "terminal": {"opacity": 0.35, "alignment": "bottomRight", "stretch": "uniformToFill"},
                "desktop": {"enabled": True}
            }
        with open(self.profile_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_profile(self, data: dict):
        with open(self.profile_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def get_styles(self) -> dict:
        if not self.styles_file.exists():
            return {}
        with open(self.styles_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_styles(self, data: dict):
        with open(self.styles_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def get_active_style(self) -> dict:
        styles_data = self.get_styles()
        profile_data = self.get_profile()
        active_id = profile_data.get("active_style", "pixel_art")
        styles = styles_data.get("styles", {})
        return styles.get(active_id, list(styles.values())[0] if styles else {})

    def set_active_style(self, style_id: str):
        styles_data = self.get_styles()
        aliases = {
            "pixel": "pixel_art",
            "retro": "pixel_art",
            "cyber": "cyberpunk_anime",
            "cyberpunk": "cyberpunk_anime",
            "anime": "cyberpunk_anime",
            "ghibli": "lofi_ghibli",
            "lofi": "lofi_ghibli",
            "pixar": "pixar_3d",
            "3d": "pixar_3d",
            "comic": "comic_popart",
            "pop": "comic_popart",
            "popart": "comic_popart"
        }
        resolved_id = aliases.get(style_id.lower().strip(), style_id)
        if resolved_id not in styles_data.get("styles", {}):
            raise ValueError(f"Style '{style_id}' not found. Available: {list(styles_data.get('styles', {}).keys())}")
        profile_data = self.get_profile()
        profile_data["active_style"] = resolved_id
        styles_data["active_style"] = resolved_id
        self.save_profile(profile_data)
        self.save_styles(styles_data)
        return resolved_id

    def cycle_next_style(self) -> str:
        styles_data = self.get_styles()
        style_keys = list(styles_data.get("styles", {}).keys())
        if not style_keys:
            return "pixel_art"
        profile_data = self.get_profile()
        current_id = profile_data.get("active_style", style_keys[0])
        try:
            current_index = style_keys.index(current_id)
            next_index = (current_index + 1) % len(style_keys)
        except ValueError:
            next_index = 0
        next_id = style_keys[next_index]
        self.set_active_style(next_id)
        return next_id

    def add_or_update_user(self, name: str, favorite_style: str = "pixel_art", persona: str = "Tech Creator"):
        profile = self.get_profile()
        profile["user_name"] = name
        profile["active_style"] = favorite_style
        users = profile.get("profiles_list", [])
        matched = False
        for u in users:
            if u["name"].lower() == name.lower():
                u["favorite_style"] = favorite_style
                u["persona"] = persona
                matched = True
                break
        if not matched:
            users.append({"name": name, "favorite_style": favorite_style, "persona": persona})
        profile["profiles_list"] = users
        self.save_profile(profile)
