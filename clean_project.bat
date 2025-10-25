@echo off
REM ============================================
REM ANTARCTIC - LIMPIEZA DE PROYECTO
REM ============================================
REM Elimina archivos temporales y cache

echo ============================================
echo   LIMPIEZA DE PROYECTO
echo ============================================
echo.

echo Eliminando cache de Python...
if exist __pycache__ rmdir /s /q __pycache__
if exist src\__pycache__ rmdir /s /q src\__pycache__
if exist tools\__pycache__ rmdir /s /q tools\__pycache__
echo OK

echo Eliminando archivos compilados...
del /q *.pyc 2>nul
del /q src\*.pyc 2>nul
del /q tools\*.pyc 2>nul
echo OK

echo Eliminando archivos temporales...
del /q *.tmp 2>nul
del /q *.temp 2>nul
del /q *.log 2>nul
echo OK

echo Eliminando carpeta obfuscated (ya no se usa)...
if exist obfuscated rmdir /s /q obfuscated
echo OK

echo Eliminando carpeta release (ya no se usa)...
if exist release rmdir /s /q release
echo OK

echo Eliminando build/obfuscated (ya no se usa)...
if exist build\obfuscated rmdir /s /q build\obfuscated
echo OK

echo.
echo ============================================
echo   LIMPIEZA COMPLETADA
echo ============================================
echo.
pause

