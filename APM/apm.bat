@echo off
python "%APPDATA%\apm\apm.py" %*

if not exist "%TEMP%\apm_goto.tmp" goto :eof

set /p APM_GOTO_PATH=<"%TEMP%\apm_goto.tmp"
del "%TEMP%\apm_goto.tmp"
cd /d "%APM_GOTO_PATH%"
set "APM_GOTO_PATH="