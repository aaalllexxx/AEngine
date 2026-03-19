@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   AEngine - Автоматический установщик
echo ========================================
echo.

:: Проверка прав администратора
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ВНИМАНИЕ] Для установки Python и Git требуются права администратора.
    echo Запустите этот скрипт от имени администратора.
    echo.
    pause
    exit /b 1
)

:: Проверка Python
echo [1/5] Проверка Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Python не найден. Установка Python...
    echo.
    echo Загрузка Python 3.11...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile '%TEMP%\python-installer.exe'}"
    
    echo Установка Python (это может занять несколько минут)...
    start /wait %TEMP%\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    del %TEMP%\python-installer.exe
    
    :: Обновление PATH
    call refreshenv >nul 2>&1
    
    echo Python успешно установлен!
) else (
    echo Python уже установлен.
)
echo.

:: Проверка Git
echo [2/5] Проверка Git...
git --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Git не найден. Установка Git...
    echo.
    echo Загрузка Git...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe' -OutFile '%TEMP%\git-installer.exe'}"
    
    echo Установка Git (это может занять несколько минут)...
    start /wait %TEMP%\git-installer.exe /VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /COMPONENTS="icons,ext\reg\shellhere,assoc,assoc_sh"
    
    del %TEMP%\git-installer.exe
    
    :: Обновление PATH
    call refreshenv >nul 2>&1
    
    echo Git успешно установлен!
) else (
    echo Git уже установлен.
)
echo.

:: Обновление pip
echo [3/5] Обновление pip...
python -m pip install --upgrade pip --quiet
echo pip обновлен.
echo.

:: Установка зависимостей
echo [4/5] Установка зависимостей Python...
if exist "APM\requirements.txt" (
    python -m pip install -r APM\requirements.txt --quiet
    echo Зависимости установлены.
) else (
    echo [ПРЕДУПРЕЖДЕНИЕ] Файл APM\requirements.txt не найден.
)
echo.

:: Установка APM
echo [5/5] Установка APM (Package Manager)...
if exist "APM\scripts\setup.bat" (
    cd APM\scripts
    call setup.bat
    cd ..\..
    echo APM установлен.
) else (
    echo [ПРЕДУПРЕЖДЕНИЕ] Скрипт установки APM не найден.
)
echo.

echo ========================================
echo   Установка завершена!
echo ========================================
echo.
echo Теперь вы можете использовать команду 'apm' для управления проектами.
echo.
echo Примеры команд:
echo   apm create          - Создать новый проект
echo   apm list            - Показать все проекты
echo   apm docs            - Открыть документацию
echo.
pause
