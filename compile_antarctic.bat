@echo off
echo ============================================
echo ANTARCTIC - QUICK BUILD
echo ============================================
echo.
echo Navegando a carpeta de compilacion...
cd build
echo.
echo Ejecutando script de compilacion...
call compile.bat
echo.
echo Regresando a directorio raiz...
cd ..
echo.
echo ============================================
echo Compilacion finalizada
echo El ejecutable esta en: dist\Antarctic.exe
echo ============================================
pause
