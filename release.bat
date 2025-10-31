@echo off
REM Configurar token de GitHub desde variable de entorno
REM Configura GITHUB_TOKEN en tu sistema o crea un archivo .env
if "%GITHUB_TOKEN%"=="" (
    echo ERROR: GITHUB_TOKEN no configurado
    echo Configura la variable de entorno GITHUB_TOKEN con tu Personal Access Token
    pause
    exit /b 1
)

echo ============================================
echo ANTARCTIC - RELEASE MANAGER AUTOMATICO
echo ============================================
echo.
echo Este script hara TODO automaticamente:
echo   1. Compilar el ejecutable
echo   2. Crear release en GitHub
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

