@echo off
REM Configurar token de GitHub
set GITHUB_TOKEN=GITHUB_TOKEN_REMOVED

echo ============================================
echo ANTARCTIC - RELEASE MANAGER AUTOMATICO
echo ============================================
echo.
echo Este script hara TODO automaticamente:
echo   1. Actualizar version.txt
echo   2. Compilar el ejecutable
echo   3. Crear release en GitHub
echo.

REM Solicitar version
set /p VERSION="Ingresa la version (ej: 1.0.2): "

if "%VERSION%"=="" (
    echo ERROR: Version requerida
    pause
    exit /b 1
)

echo.
echo ============================================
echo Iniciando proceso automatico para v%VERSION%
echo ============================================
echo.

REM Ejecutar script de Python (compila automaticamente)
python tools\release.py --version %VERSION%

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================
    echo ERROR: Fallo en el proceso
    echo ============================================
    pause
    exit /b 1
)

pause

