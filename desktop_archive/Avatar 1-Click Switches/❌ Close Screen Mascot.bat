@echo off
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*companion.py*' } | Stop-Process -Force -ErrorAction SilentlyContinue"
