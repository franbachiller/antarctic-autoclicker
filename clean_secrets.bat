@echo off
echo ============================================
echo LIMPIEZA DE SECRETOS DEL HISTORIAL DE GIT
echo ============================================
echo.
echo ADVERTENCIA: Este script reescribira el historial de Git
echo Asegurate de tener un backup antes de continuar
echo.
set /p CONFIRM="Continuar? (y/n): "

if /i not "%CONFIRM%"=="y" (
    echo Cancelado
    exit /b 1
)

echo.
echo Instalando git-filter-repo si es necesario...
pip install git-filter-repo

echo.
echo Creando backup del repositorio...
cd ..
xcopy /E /I /H /Y Antarctic Antarctic_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
cd Antarctic

echo.
echo Limpiando secretos del historial...

REM Crear archivo de reemplazos
echo GITHUB_TOKEN_REMOVED==^>GITHUB_TOKEN_REMOVED > %TEMP%\git-secrets-replace.txt
echo ADMIN_KEY_REMOVED==^>ADMIN_KEY_REMOVED >> %TEMP%\git-secrets-replace.txt
echo SALT_REMOVED==^>SALT_REMOVED >> %TEMP%\git-secrets-replace.txt
echo SALT_REMOVED==^>SALT_REMOVED >> %TEMP%\git-secrets-replace.txt

REM Aplicar reemplazos
git filter-repo --replace-text %TEMP%\git-secrets-replace.txt --force

echo.
echo ============================================
echo LIMPIEZA COMPLETADA
echo ============================================
echo.
echo Proximos pasos:
echo 1. Verifica que los cambios son correctos
echo 2. Configura las variables de entorno:
echo    set GITHUB_TOKEN=tu_token_aqui
echo    set ADMIN_KEY=tu_admin_key_aqui
echo 3. Force push al repositorio:
echo    git remote add origin https://github.com/Narfbach/antarctic-autoclicker.git
echo    git push origin --force --all
echo 4. Haz el repositorio publico en GitHub
echo.
pause

