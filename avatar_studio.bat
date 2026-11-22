@echo off
set STUDIO_DIR=C:\Users\madha\custom-avatar-studio

if "%1"=="" goto gui
if "%1"=="gui" goto gui
if "%1"=="switch" goto switch
if "%1"=="next" goto next
if "%1"=="cycle" goto next
if "%1"=="mascot" goto mascot
if "%1"=="close-mascot" goto close_mascot
if "%1"=="list" goto list
if "%1"=="preview" goto preview
if "%1"=="banner" goto banner
if "%1"=="copy-whatsapp" goto copy_wa
if "%1"=="whatsapp" goto wa_folder
if "%1"=="export" goto export

python "%STUDIO_DIR%\cli.py" %*
goto end

:gui
python "%STUDIO_DIR%\gui.py"
goto end

:mascot
start pythonw "%STUDIO_DIR%\core\companion.py"
goto end

:close_mascot
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*companion.py*' } | Stop-Process -Force -ErrorAction SilentlyContinue"
goto end

:switch
python "%STUDIO_DIR%\cli.py" switch %2 %3
goto end

:next
python "%STUDIO_DIR%\cli.py" next
goto end

:copy_wa
python "%STUDIO_DIR%\cli.py" copy-whatsapp
goto end

:wa_folder
python "%STUDIO_DIR%\cli.py" whatsapp
goto end

:list
python "%STUDIO_DIR%\cli.py" list
goto end

:preview
python "%STUDIO_DIR%\cli.py" preview
goto end

:banner
python "%STUDIO_DIR%\cli.py" banner %2
goto end

:export
python "%STUDIO_DIR%\cli.py" export --open
goto end

:end
