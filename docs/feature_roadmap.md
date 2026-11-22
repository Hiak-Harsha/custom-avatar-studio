# HIAK × HARSHA Mascot Studio: Feature Roadmap

This document persists the feature ideas and expansion concepts for the **HIAK × HARSHA Mascot Studio**. You can reference this roadmap anytime to implement any of these modules.

---

## 1. ⚡ Live System & Hardware Reactivity
Make your mascots react dynamically to your computer's real-time hardware status:
- **CPU / Build Stress Mode**: When compiling code or running heavy processes (CPU > 80%), Claude switches to `thinking.png` or Cyber-Bot activates glowing cyan thrusters.
- **Low Battery / Night Owl**: When battery drops below 20% or after 11:00 PM, the mascot smoothly shifts to `sleepy.png` with a dark night aesthetic.
- **Music / Media Sync**: Displays subtle animated musical notes or a speech bubble showing the active Spotify/YouTube Music track.

---

## 2. 🔊 Retro 8-Bit & Cyber Sound Effects
- **Haptic Audio**: A gentle 8-bit click sound when advancing poses on the desktop wallpaper.
- **Sci-Fi Glitch Audio**: A retro digital warp / pixel-dissolve SFX when your cursor hovers over `hiak` to morph into `harsha`.
- **Toggle Control**: Easily enable/disable via CLI (`hiak sound on` / `hiak sound off`).

---

## 3. 🛡️ Windows System Tray Companion Menu
A dedicated icon in your Windows notification area (next to the clock):
- **Right-Click Context Menu**:
  - 🔄 *Switch Persona (HIAK ⇄ HARSHA)*
  - 🎭 *Cycle Next Mascot Pose*
  - 🖥️ *Screensaver Preview (1-Click Launch)*
  - 👁️ *Toggle Desktop Icons (Show / Hide)*
  - 📊 *Live Engine Status & Diagnostics*

---

## 4. 💻 Developer & Git Hooks Integration
- **Git Commit Celebration**: A post-commit hook that triggers a quick celebratory animation in your terminal whenever you commit or push code.
- **Pomodoro Focus Timer**: A timer mode where the mascot wears glasses (`coding.png`) during a 25-minute focus sprint, then offers a break alert.

---

## 5. 🌐 GitHub Profile & Social Exports
- **Dynamic GitHub README Banner**: An animated SVG/GIF banner for your GitHub profile looping the `hiak` ⇄ `harsha` pixel morph.
- **Animated WhatsApp / Telegram Stickers**: Export `.webp` animated sticker packs ready to send in developer chats.

---

## 6. 🐾 Interactive Floating Taskbar Pet
- A lightweight companion mode (based on `core/companion.py`) where a mini Claude or Cyber-Bot strolls along the top of your Windows taskbar and hops when clicked.

---

## 7. 🚀 Kinetic Mascot Transit During Pixel Morph
- **Concept**: While the text is glitching and dissolving from `hiak` to `harsha`, the character performs a dynamic swoop across the screen:
  - Claude runs / dashes off to the right.
  - Cyber-Bot enters with blue thrusters from the left, swooping across the pixel storm into its designated docking spot next to `harsha`.
