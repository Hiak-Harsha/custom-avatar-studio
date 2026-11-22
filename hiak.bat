@echo off
set STUDIO_DIR=C:\Users\madha\custom-avatar-studio

if "%1"=="move" goto do_move
if "%1"=="next" goto do_move
if "%1"=="listen" goto do_listen
if "%1"=="banner" goto do_banner
if "%1"=="copy" goto do_copy
if "%1"=="status" goto do_status
if "%1"=="create" goto do_create

python "%STUDIO_DIR%\cli.py" %*
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
