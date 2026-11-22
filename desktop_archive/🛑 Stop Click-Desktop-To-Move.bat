@echo off
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*wallpaper_animator.py listen*' } | Stop-Process -Force -ErrorAction SilentlyContinue"
echo Click listener stopped!
timeout /t 2 >nul
