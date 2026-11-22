"""
Detached Launcher for HIAK Wallpaper Interaction Engine
Spawns pythonw.exe with DETACHED_PROCESS so it runs completely independently of any terminal/subshell session and survives command exits.
"""
import subprocess
import sys
import time
from pathlib import Path
import os

STUDIO_ROOT = Path(__file__).parent.parent.resolve()
DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

# Terminate existing instances
os.system('taskkill /F /IM pythonw.exe 2>nul')
time.sleep(0.5)

# Spawn fully detached background process
p = subprocess.Popen(
    ["C:\\Python314\\pythonw.exe", str(STUDIO_ROOT / "core" / "wallpaper_animator.py"), "listen"],
    cwd=str(STUDIO_ROOT),
    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
    close_fds=True
)
print(f"Launched detached wallpaper animator! PID: {p.pid}")
