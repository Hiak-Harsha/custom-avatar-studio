@echo off
set STUDIO_DIR=C:\Users\madha\custom-avatar-studio

if "%1"=="move" (
    python "%STUDIO_DIR%\core\wallpaper_animator.py" next
    goto end
)
if "%1"=="next" (
    python "%STUDIO_DIR%\core\wallpaper_animator.py" next
    goto end
)
if "%1"=="listen" (
    start /b pythonw "%STUDIO_DIR%\core\wallpaper_animator.py" listen
    goto end
)
if "%1"=="banner" (
    python "%STUDIO_DIR%\cli.py" banner preview
    goto end
)
if "%1"=="copy" (
    python "%STUDIO_DIR%\cli.py" copy-whatsapp
    goto end
)
if "%1"=="status" (
    echo ========================================================
    echo   ⚡ HIAK Mascot Studio - Live System Status
    echo ========================================================
    echo Persona:   HIAK (OpenCode Grid Typography + Mascot)
    echo Directory: %CD%
    echo Studio:    %STUDIO_DIR%
    echo.
    echo [Background Desktop Click Listener]
    powershell -NoProfile -Command "$p = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*wallpaper_animator.py listen*' }; if ($p) { Write-Host '  Status: ACTIVE (PID: ' $p.ProcessId ')' -ForegroundColor Green } else { Write-Host '  Status: INACTIVE (Run `hiak listen` to start)' -ForegroundColor Yellow }"
    echo.
    goto end
)

python "%STUDIO_DIR%\cli.py" %*

:end
