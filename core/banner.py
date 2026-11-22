"""
Terminal Welcome Banner Manager
Configures PowerShell profile and Command Prompt to display
the customized avatar ANSI banner when opening a new terminal session,
and registers instant 1-click CLI functions like `style next` or `style cyber`.
"""
import os
import subprocess
from pathlib import Path


def get_powershell_profile_path() -> Path:
    """Gets the standard Windows PowerShell profile path."""
    docs = Path(os.environ.get("USERPROFILE", "C:/Users")) / "Documents"
    profile_dir = docs / "WindowsPowerShell"
    profile_dir.mkdir(parents=True, exist_ok=True)
    return profile_dir / "Microsoft.PowerShell_profile.ps1"


def get_pwsh_profile_path() -> Path:
    """Gets PowerShell 7 (Core) profile path if exists."""
    docs = Path(os.environ.get("USERPROFILE", "C:/Users")) / "Documents"
    profile_dir = docs / "PowerShell"
    profile_dir.mkdir(parents=True, exist_ok=True)
    return profile_dir / "Microsoft.PowerShell_profile.ps1"


BANNER_MARKER_START = "# === AVATAR STUDIO BANNER START ==="
BANNER_MARKER_END = "# === AVATAR STUDIO BANNER END ==="


def install_powershell_banner(banner_ans_path: str, user_name: str = "Madhav", style_name: str = "Retro Pixel Art") -> bool:
    """
    Appends or updates the welcome banner and instant style function in the PowerShell profile.
    """
    resolved_banner = str(Path(banner_ans_path).resolve()).replace("\\", "\\\\")
    snippet = f"""{BANNER_MARKER_START}
if ($host.Name -match 'ConsoleHost' -or $env:WT_SESSION) {{
    try {{
        $bannerFile = "{resolved_banner}"
        if (Test-Path $bannerFile) {{
            Write-Host ""
            Get-Content -Path $bannerFile -Encoding UTF8 | Write-Output
            Write-Host "`n  ⚡ Welcome back, {user_name}! Active Style: [{style_name}]" -ForegroundColor Cyan
            Write-Host "  💡 Tip: Type 'style next' or 'style cyber' to switch anytime!`n" -ForegroundColor DarkGray
        }}
    }} catch {{}}
}}

# 1-Click Terminal Switcher Function
function style {{
    param([string]$target = "next")
    if ($target -eq "next") {{
        & python "C:\\Users\\madha\\custom-avatar-studio\\cli.py" next
    }} else {{
        & python "C:\\Users\\madha\\custom-avatar-studio\\cli.py" switch $target
    }}
}}
Set-Alias -Name avatar -Value style -Force -ErrorAction SilentlyContinue
{BANNER_MARKER_END}
"""
    targets = [get_powershell_profile_path(), get_pwsh_profile_path()]
    for p in targets:
        content = ""
        if p.exists():
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

        if BANNER_MARKER_START in content and BANNER_MARKER_END in content:
            pre = content.split(BANNER_MARKER_START)[0]
            post = content.split(BANNER_MARKER_END)[1]
            content = pre.rstrip() + "\n\n" + post.lstrip()

        new_content = content.strip() + "\n\n" + snippet
        with open(p, "w", encoding="utf-8") as f:
            f.write(new_content)

    return True


def remove_powershell_banner() -> bool:
    """Removes the AvatarStudio banner from PowerShell profiles."""
    targets = [get_powershell_profile_path(), get_pwsh_profile_path()]
    for p in targets:
        if p.exists():
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            if BANNER_MARKER_START in content and BANNER_MARKER_END in content:
                pre = content.split(BANNER_MARKER_START)[0]
                post = content.split(BANNER_MARKER_END)[1]
                content = (pre.rstrip() + "\n" + post.lstrip()).strip()
                with open(p, "w", encoding="utf-8") as f:
                    f.write(content)
    return True
