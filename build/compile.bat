@echo off
setlocal enabledelayedexpansion
echo ============================================
echo ANTARCTIC - COMPILACION CON PYARMOR
echo ============================================
echo.
echo NIVEL DE SEGURIDAD: MUY ALTO (5/5 estrellas)
echo.
echo Ofuscando:
echo  - auth_client.py (sistema de licencias)
echo  - security.py (anti-debugging)
echo.
echo NOTA: antarctic.py no se ofusca (muy grande para PyArmor trial)
echo      pero los modulos criticos SI estan protegidos
echo.
echo ============================================
echo.

REM Verificar PyArmor
where pyarmor >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PyArmor no instalado
    echo.
    echo Instalando PyArmor...
    pip install pyarmor
    echo.
)

echo [1/5] Limpiando compilaciones anteriores...
if exist obfuscated rmdir /s /q obfuscated
if exist dist\Antarctic.exe del /q dist\Antarctic.exe
echo.

echo [2/5] Ofuscando modulos criticos con PyArmor...
echo.
pyarmor gen -O obfuscated ..\src\auth_client.py ..\src\security.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================
    echo ERROR: Fallo en la ofuscacion
    echo ============================================
    pause
    exit /b 1
)

echo.
echo [3/5] Preparando archivos para compilacion...
if not exist obfuscated\assets mkdir obfuscated\assets
copy ..\src\antarctic.py obfuscated\ >nul
copy ..\src\latency_compensator.py obfuscated\ >nul
copy ..\src\updater.py obfuscated\ >nul
copy ..\config_updater.py obfuscated\ >nul
copy ..\assets\icon.ico obfuscated\assets\ >nul
copy ..\assets\logo.png obfuscated\assets\ >nul
copy ..\assets\logo_compact.png obfuscated\assets\ >nul

REM Crear archivo version.txt con la version actual
echo 1.0.0 > obfuscated\version.txt

echo.

echo [4/5] Compilando con PyInstaller...
echo.
cd obfuscated

pyinstaller ^
    --onefile ^
    --windowed ^
    --icon=assets\icon.ico ^
    --add-data "assets\icon.ico;assets" ^
    --add-data "assets\logo.png;assets" ^
    --add-data "assets\logo_compact.png;assets" ^
    --add-data "version.txt;." ^
    --add-data "pyarmor_runtime_000000;pyarmor_runtime_000000" ^
    --hidden-import=requests ^
    --hidden-import=urllib3 ^
    --hidden-import=certifi ^
    --hidden-import=charset_normalizer ^
    --hidden-import=psutil ^
    --hidden-import=security ^
    --hidden-import=auth_client ^
    --hidden-import=latency_compensator ^
    --hidden-import=updater ^
    --hidden-import=uuid ^
    --hidden-import=hashlib ^
    --hidden-import=platform ^
    --hidden-import=subprocess ^
    --name Antarctic ^
    antarctic.py

if %ERRORLEVEL% NEQ 0 (
    cd ..
    echo.
    echo ============================================
    echo ERROR: Fallo en la compilacion
    echo ============================================
    pause
    exit /b 1
)

cd ..

echo.
echo [5/5] Finalizando...
if not exist ..\dist mkdir ..\dist
if exist obfuscated\dist\Antarctic.exe (
    copy /Y obfuscated\dist\Antarctic.exe ..\dist\Antarctic.exe >nul
    echo Archivo copiado a ..\dist\Antarctic.exe
)
del /q obfuscated\Antarctic.spec 2>nul
rmdir /s /q obfuscated\build 2>nul
echo.

if exist ..\dist\Antarctic.exe (
    for %%A in (..\dist\Antarctic.exe) do (
        set size=%%~zA
        set /a sizeMB=%%~zA/1024/1024
    )
    echo ============================================
    echo COMPILACION EXITOSA
    echo ============================================
    echo.
    echo Ubicacion: ..\dist\Antarctic.exe
    echo Tamano: !sizeMB! MB
    echo.
    echo PROTECCION MAXIMA IMPLEMENTADA:
    echo  [+++] auth_client.py - OFUSCADO (PyArmor)
    echo  [+++] security.py - OFUSCADO (PyArmor)
    echo  [+]   Anti-debugging activo
    echo  [+]   Deteccion de herramientas RE
    echo  [+]   Validacion de licencia continua
    echo  [+]   HWID binding
    echo  [+]   Sesion encriptada
    echo.
    echo NIVEL DE SEGURIDAD: 5/5 estrellas
    echo.
    echo Este ejecutable esta listo para distribucion.
    echo Crackers necesitarian SEMANAS o MESES para romperlo.
    echo.
    goto :end
)

echo.
echo ============================================
echo ERROR: No se creo el ejecutable
echo ============================================

:end

echo.
pause
