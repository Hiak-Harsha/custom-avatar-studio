' ===================================================================
' HIAK Mascot Studio - Robust Background Animator Launcher
' Ensures proper working directory and silent background execution
' ===================================================================
Option Explicit

Dim WshShell, fso, studioDir, pythonwExe, scriptPath

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

studioDir = "C:\Users\madha\custom-avatar-studio"
pythonwExe = "C:\Python314\pythonw.exe"
scriptPath = studioDir & "\core\wallpaper_animator.py"

' Set working directory to studio root so relative imports and paths always resolve
WshShell.CurrentDirectory = studioDir

' Give Explorer 3 seconds if system is just starting up
WScript.Sleep 3000

' Launch wallpaper animator in background with window style 0 (hidden)
WshShell.Run """" & pythonwExe & """ """ & scriptPath & """ listen", 0, False
