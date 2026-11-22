@echo off
set STUDIO_DIR=C:\Users\madha\custom-avatar-studio

if "%1"=="move" goto do_move
if "%1"=="next" goto do_move
if "%1"=="listen" goto do_listen
if "%1"=="banner" goto do_banner
if "%1"=="copy" goto do_copy
if "%1"=="status" goto do_status
if "%1"=="create" goto do_create
if "%1"=="screensaver" goto do_screensaver
if "%1"=="icons" goto do_icons

python "%STUDIO_DIR%\cli.py" %*
goto end

:do_icons
if "%2"=="show" (
    powershell -NoProfile -Command "Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced' -Name 'HideIcons' -Value 0; Stop-Process -Name explorer -Force"
    echo Desktop icons are now visible.
    goto end
)
if "%2"=="hide" (
    powershell -NoProfile -Command "Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced' -Name 'HideIcons' -Value 1; Stop-Process -Name explorer -Force"
    echo Desktop icons are now hidden for unobstructed wallpaper view.
    goto end
)
echo Usage: hiak icons [show^|hide]
goto end

:do_screensaver
python "%STUDIO_DIR%\core\screensaver.py" %2 %3
goto end

:do_create
python "%STUDIO_DIR%\cli.py" create %2 %3 %4 %5
goto end

:do_move
python "%STUDIO_DIR%\core\wallpaper_animator.py" next
goto end

:do_listen
start /b pythonw "%STUDIO_DIR%\core\wallpaper_animator.py" listen
goto end

:do_banner
python "%STUDIO_DIR%\cli.py" banner preview
goto end

:do_copy
python "%STUDIO_DIR%\cli.py" copy-whatsapp
goto end

:do_status
echo ========================================================
echo   HIAK Mascot Studio - Live System Status
echo ========================================================
echo Persona:   HIAK (OpenCode Grid Typography + Mascot)
echo Directory: %CD%
echo Studio:    %STUDIO_DIR%
echo.
echo [Background Desktop Click Listener]
powershell -NoProfile -Command "$p = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*wallpaper_animator.py listen*' }; if ($p) { Write-Host '  Status: ACTIVE (PID: ' $p.ProcessId ')' -ForegroundColor Green } else { Write-Host '  Status: INACTIVE (Run hiak listen to start)' -ForegroundColor Yellow }"
echo.
goto end

:end
