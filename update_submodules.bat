@echo off
chcp 65001 >nul
echo ========================================
echo   Обновление Git Submodules
echo ========================================
echo.

echo Обновление всех submodules до последней версии...
git submodule update --remote --merge

echo.
echo ========================================
echo   Готово!
echo ========================================
echo.
echo AEngineApps и APM обновлены до последних версий.
echo.
pause
