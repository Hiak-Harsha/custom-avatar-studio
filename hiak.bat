@echo off
set STUDIO_DIR=C:\Users\madha\custom-avatar-studio

if "%1"=="start" goto do_start
if "%1"=="restart" goto do_restart
if "%1"=="stop" goto do_stop
if "%1"=="logs" goto do_logs
if "%1"=="move" goto do_move
if "%1"=="next" goto do_move
if "%1"=="listen" goto do_start
if "%1"=="banner" goto do_banner
if "%1"=="copy" goto do_copy
if "%1"=="status" goto do_status
if "%1"=="create" goto do_create
if "%1"=="screensaver" goto do_screensaver
if "%1"=="icons" goto do_icons

python "%STUDIO_DIR%\cli.py" %*
goto end

:do_start
powershell -NoProfile -Command "$p = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*wallpaper_animator.py listen*' }; if ($p) { Write-Host 'Wallpaper engine is already active (PID: ' $p.ProcessId ')' -ForegroundColor Green } else { Start-Process 'wscript.exe' -ArgumentList '\"%STUDIO_DIR%\scripts\run_background.vbs\"'; Start-Sleep -Milliseconds 800; Write-Host 'Wallpaper engine started successfully in background!' -ForegroundColor Green }"
goto end

:do_stop
powershell -NoProfile -Command "$procs = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*wallpaper_animator.py listen*' }; if ($procs) { foreach ($p in $procs) { Stop-Process -Id $p.ProcessId -Force }; Write-Host 'Stopped background wallpaper animator.' -ForegroundColor Yellow } else { Write-Host 'No background wallpaper animator was running.' -ForegroundColor Gray }"
goto end

:do_restart
echo Restarting HIAK Mascot Studio background engine...
powershell -NoProfile -Command "$procs = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*wallpaper_animator.py listen*' }; if ($procs) { foreach ($p in $procs) { Stop-Process -Id $p.ProcessId -Force } }"
powershell -NoProfile -Command "Start-Process 'wscript.exe' -ArgumentList '\"%STUDIO_DIR%\scripts\run_background.vbs\"'; Start-Sleep -Milliseconds 900"
echo Done! Check status with: hiak status
goto end

:do_logs
powershell -NoProfile -Command "if (Test-Path '%STUDIO_DIR%\logs\animator.log') { Get-Content '%STUDIO_DIR%\logs\animator.log' -Tail 25 } else { Write-Host 'No log file found yet.' -ForegroundColor Gray }"
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
echo [Background Desktop Interaction Engine]
powershell -NoProfile -Command "$p = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*wallpaper_animator.py listen*' }; if ($p) { Write-Host '  Status: ACTIVE (PID: ' $p.ProcessId ')' -ForegroundColor Green; Write-Host '  Mode:   Instant hover (HIAK -> HARSHA Cyber-Bot) + Always-on clicks' -ForegroundColor Cyan } else { Write-Host '  Status: INACTIVE (Run hiak start to launch)' -ForegroundColor Red }"
echo.
if exist "%STUDIO_DIR%\logs\animator.log" (
    echo [Recent Engine Activity]
    powershell -NoProfile -Command "Get-Content '%STUDIO_DIR%\logs\animator.log' -Tail 5"
    echo.
)
goto end

:end
