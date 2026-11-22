@echo off
set STUDIO_DIR=C:\Users\madha\custom-avatar-studio

if "%1"=="" goto gui
if "%1"=="gui" goto gui
if "%1"=="switch" goto switch
if "%1"=="list" goto list
if "%1"=="preview" goto preview
if "%1"=="banner" goto banner
if "%1"=="export" goto export

python "%STUDIO_DIR%\cli.py" %*
goto end

:gui
python "%STUDIO_DIR%\gui.py"
goto end

:switch
python "%STUDIO_DIR%\cli.py" switch %2 %3
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
