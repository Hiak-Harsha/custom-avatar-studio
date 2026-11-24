"""
Detached Launcher for HIAK Wallpaper Interaction Engine
Spawns pythonw.exe outside any terminal/subshell session and ensures it survives command exits.
"""
import subprocess
import time
from pathlib import Path

STUDIO_ROOT = Path(__file__).parent.parent.resolve()
DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_BREAKAWAY_FROM_JOB = 0x01000000

# Terminate only existing wallpaper_animator.py instances (leave other pythonw processes untouched)
subprocess.run(
    [
        "powershell", "-NoProfile", "-Command",
        "Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'python*' -and $_.CommandLine -like '*wallpaper_animator.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
    ],
    capture_output=True
)
time.sleep(0.5)

cmd = ["C:\\Python314\\pythonw.exe", str(STUDIO_ROOT / "core" / "wallpaper_animator.py"), "listen"]
try:
    p = subprocess.Popen(
        cmd,
        cwd=str(STUDIO_ROOT),
        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_BREAKAWAY_FROM_JOB,
        close_fds=True
    )
except PermissionError:
    p = subprocess.Popen(
        cmd,
        cwd=str(STUDIO_ROOT),
        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
        close_fds=True
    )
print(f"Launched detached wallpaper animator! PID: {p.pid}")
