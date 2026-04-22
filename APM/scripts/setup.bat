@echo off
setlocal enabledelayedexpansion

:: AEngine Unified Installer for Windows
:: This script sets up APM, Security module, and all project dependencies.

:: SCRIPT_DIR = директория скрипта (scripts\), APM_ROOT = на уровень выше
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "APM_ROOT=%%~dpfI"
set "APM_DIR=%APPDATA%\apm"

echo ==========================================
echo     AEngine Zero-Configuration Setup
echo ==========================================

:: Create config directory
if not exist "%APM_DIR%" mkdir "%APM_DIR%"
if not exist "%APM_DIR%\modules" mkdir "%APM_DIR%\modules"

:: Create virtual environment
echo [+] Creating virtual environment in %APM_DIR%\venv...
set "OLD_PYTHONPATH=%PYTHONPATH%"
set "OLD_PYTHONHOME=%PYTHONHOME%"
set "PYTHONPATH="
set "PYTHONHOME="
pushd "%TEMP%"
cmd /d /c python -m venv "%APM_DIR%\venv"
set "VENV_EXIT=%ERRORLEVEL%"
popd
set "PYTHONPATH=%OLD_PYTHONPATH%"
set "PYTHONHOME=%OLD_PYTHONHOME%"
if not "%VENV_EXIT%"=="0" (
    echo [-] Failed to create virtual environment. Ensure Python is in PATH.
    pause
    exit /b 1
)

:: Update pip and install requirements
echo [+] Updating pip...
"%APM_DIR%\venv\Scripts\python.exe" -m pip install --upgrade pip

echo [+] Installing project dependencies...
if exist "%APM_ROOT%\requirements.txt" (
    "%APM_DIR%\venv\Scripts\python.exe" -m pip install -r "%APM_ROOT%\requirements.txt"
) else (
    echo [-] requirements.txt not found in %APM_ROOT%.
)

:: Copy APM files from APM root (not from scripts/)
echo [+] Synchronizing APM modules...
xcopy /E /Y /Q "%APM_ROOT%\*" "%APM_DIR%\"

:: Add to user PATH if not already there
echo [+] Registering 'apm' command for current user...
setx PATH "%PATH%;%APM_DIR%" >nul 2>&1

echo.
echo [+] Setup complete! AEngine is ready to use.
echo [+] Please restart your terminal/IDE to use 'apm' command.
echo ==========================================
pause
