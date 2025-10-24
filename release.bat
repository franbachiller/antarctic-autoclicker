@echo off
REM Configurar token de GitHub
set GITHUB_TOKEN=GITHUB_TOKEN_REMOVED

echo ============================================
echo ANTARCTIC - RELEASE MANAGER
echo ============================================
echo.
echo Este script te ayudara a crear una nueva release
echo.

REM Verificar que existe el ejecutable
if not exist "dist\Antarctic.exe" (
    echo ERROR: No se encontro dist\Antarctic.exe
    echo.
    echo Compila primero con: compile_antarctic.bat
    echo.
    pause
    exit /b 1
)

echo Ejecutable encontrado: dist\Antarctic.exe
echo.

REM Solicitar version
set /p VERSION="Ingresa la version (ej: 1.0.1): "

if "%VERSION%"=="" (
    echo ERROR: Version requerida
    pause
    exit /b 1
)

echo.
echo ============================================
echo Creando release v%VERSION%
echo ============================================
echo.

REM Ejecutar script de Python
python tools\release.py --version %VERSION%

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================
    echo ERROR: Fallo al crear release
    echo ============================================
    pause
    exit /b 1
)

echo.
echo ============================================
echo Release creada exitosamente!
echo ============================================
pause

