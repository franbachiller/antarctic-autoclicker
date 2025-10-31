@echo off
echo ============================================
echo LIMPIEZA DE ARCHIVOS DE COMPILACION
echo ============================================
echo.

echo Eliminando carpeta obfuscated...
if exist obfuscated rmdir /s /q obfuscated
echo OK

echo Eliminando archivos .spec...
if exist *.spec del /q *.spec
echo OK

echo.
echo ============================================
echo LIMPIEZA COMPLETADA
echo ============================================
pause

