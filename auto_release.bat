@echo off
REM ============================================
REM ANTARCTIC - AUTO RELEASE (TODO AUTOMATICO)
REM ============================================
REM
REM Este script hace TODO automaticamente:
REM   1. Configura variables de entorno
REM   2. Solicita version
REM   3. Compila el ejecutable
REM   4. Crea release en GitHub
REM   5. Actualiza API de updates
REM   6. Commit y push automatico
REM
REM Solo abre este archivo y sigue las instrucciones!
REM ============================================

title Antarctic Auto Release

echo.
echo ============================================
echo   ANTARCTIC - AUTO RELEASE SYSTEM
echo ============================================
echo.
echo Este script hara TODO automaticamente.
echo Solo necesitas proporcionar la version.
echo.

REM Verificar que estamos en el directorio correcto
if not exist "src\antarctic.py" (
    echo ERROR: Ejecuta este script desde la raiz del proyecto
    pause
    exit /b 1
)

REM Configurar variables de entorno
echo [1/7] Configurando variables de entorno...

REM Verificar si existe set_env.bat
if exist set_env.bat (
    call set_env.bat
    echo      OK - Variables configuradas desde set_env.bat
) else (
    echo      ERROR: No se encontro set_env.bat
    echo      Crea el archivo set_env.bat con:
    echo      set GITHUB_TOKEN=tu_token
    echo      set ADMIN_KEY=tu_admin_key
    pause
    exit /b 1
)
echo.

REM Solicitar version
echo [2/7] Ingresa la nueva version
set /p VERSION="      Version (ej: 1.0.3): "

if "%VERSION%"=="" (
    echo      ERROR: Version requerida
    pause
    exit /b 1
)

echo      OK - Version: %VERSION%
echo.

REM Solicitar notas de release
echo [3/7] Notas de la release (opcional)
set /p NOTES="      Notas (Enter para omitir): "

if "%NOTES%"=="" (
    set NOTES=Release version %VERSION%
)

echo      OK - Notas: %NOTES%
echo.

REM Actualizar version.txt
echo [4/7] Actualizando version.txt...
echo %VERSION% > src\version.txt
echo      OK - version.txt actualizado
echo.

REM Compilar ejecutable
echo [5/7] Compilando ejecutable...
echo      Esto puede tardar 1-2 minutos...
cd build
call compile.bat >nul 2>&1
cd ..

if not exist "dist\Antarctic.exe" (
    echo      ERROR: Compilacion fallida
    echo      Intenta compilar manualmente: compile_antarctic.bat
    pause
    exit /b 1
)

echo      OK - Ejecutable compilado
echo.

REM Crear release en GitHub
echo [6/7] Creando release en GitHub...
python tools\release.py --version %VERSION% --notes "%NOTES%" --skip-compile

if %ERRORLEVEL% NEQ 0 (
    echo      ERROR: Fallo al crear release
    pause
    exit /b 1
)

echo      OK - Release creada en GitHub
echo.

REM Actualizar API de updates
echo [7/7] Actualizando API de updates...
python tools\migrate_to_github_releases.py

if %ERRORLEVEL% NEQ 0 (
    echo      ERROR: Fallo al actualizar API
    pause
    exit /b 1
)

echo      OK - API actualizada
echo.

REM Commit y push
echo [8/8] Haciendo commit y push...
git add api/updates/ src/version.txt
git commit -m "Release version %VERSION%"
git push origin main

if %ERRORLEVEL% NEQ 0 (
    echo      ADVERTENCIA: Fallo al hacer push
    echo      Puedes hacerlo manualmente despues
)

echo.
echo ============================================
echo   RELEASE COMPLETADO EXITOSAMENTE!
echo ============================================
echo.
echo Version: %VERSION%
echo Release: https://github.com/Narfbach/antarctic-autoclicker/releases/tag/v%VERSION%
echo.
echo Los usuarios veran la actualizacion automaticamente.
echo Vercel desplegara los cambios en unos minutos.
echo.
pause

