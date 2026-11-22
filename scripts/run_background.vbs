' Instant launcher for updates and CLI
Option Explicit
Dim WshShell
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\madha\custom-avatar-studio"
WshShell.Run """C:\Python314\pythonw.exe"" ""C:\Users\madha\custom-avatar-studio\core\wallpaper_animator.py"" listen", 0, False
