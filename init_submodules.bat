@echo off
chcp 65001 >nul
echo ========================================
echo   Инициализация Git Submodules
echo ========================================
echo.

echo Инициализация submodules...
git submodule init

echo.
echo Загрузка содержимого submodules...
git submodule update --recursive

echo.
echo ========================================
echo   Готово!
echo ========================================
echo.
echo AEngineApps и APM успешно загружены.
echo.
pause
