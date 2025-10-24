"""
ANTARCTIC AUTO-UPDATER
======================
Sistema de actualización automática usando API propia
"""

import requests
import os
import sys
import tempfile
import subprocess
import shutil
from pathlib import Path
import json
import hashlib

# Importar configuración
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config_updater import UPDATE_API_URL
except:
    UPDATE_API_URL = "https://antarctic-autoclicker.vercel.app/api/updates"

CURRENT_VERSION = "1.0.0"


class Updater:
    def __init__(self, current_version=CURRENT_VERSION, api_url=UPDATE_API_URL):
        self.current_version = current_version
        self.api_url = api_url
        
    def get_latest_version(self):
        """
        Obtiene la última versión disponible desde la API

        Returns:
            tuple: (version_string, download_url, release_notes) o (None, None, None) si falla
        """
        try:
            response = requests.get(f"{self.api_url}/latest", timeout=10)
            response.raise_for_status()

            data = response.json()

            # Obtener versión
            version = data.get('version', '').lstrip('v')

            # Obtener URL de descarga
            download_url = data.get('download_url')

            # Obtener notas de la release
            release_notes = data.get('release_notes', 'No release notes available')

            return version, download_url, release_notes

        except Exception as e:
            print(f"Error checking for updates: {e}")
            return None, None, None
    
    def is_update_available(self):
        """
        Verifica si hay una actualización disponible
        
        Returns:
            tuple: (bool, version, download_url, notes) - True si hay update disponible
        """
        latest_version, download_url, notes = self.get_latest_version()
        
        if not latest_version or not download_url:
            return False, None, None, None
        
        # Comparar versiones
        if self._compare_versions(latest_version, self.current_version) > 0:
            return True, latest_version, download_url, notes
        
        return False, latest_version, download_url, notes
    
    def _compare_versions(self, v1, v2):
        """
        Compara dos versiones en formato semver (x.y.z)
        
        Returns:
            int: 1 si v1 > v2, -1 si v1 < v2, 0 si son iguales
        """
        try:
            parts1 = [int(x) for x in v1.split('.')]
            parts2 = [int(x) for x in v2.split('.')]
            
            # Rellenar con ceros si tienen diferente longitud
            max_len = max(len(parts1), len(parts2))
            parts1 += [0] * (max_len - len(parts1))
            parts2 += [0] * (max_len - len(parts2))
            
            for p1, p2 in zip(parts1, parts2):
                if p1 > p2:
                    return 1
                elif p1 < p2:
                    return -1
            
            return 0
        except:
            return 0
    
    def download_update(self, download_url, progress_callback=None):
        """
        Descarga la actualización
        
        Args:
            download_url: URL del archivo a descargar
            progress_callback: Función callback(bytes_downloaded, total_bytes)
        
        Returns:
            str: Path del archivo descargado o None si falla
        """
        try:
            # Crear directorio temporal
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, 'Antarctic_Update.exe')
            
            # Descargar con progreso
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback:
                            progress_callback(downloaded, total_size)
            
            return temp_file
            
        except Exception as e:
            print(f"Error downloading update: {e}")
            return None
    
    def apply_update(self, update_file):
        """
        Aplica la actualización reemplazando el ejecutable actual
        
        Args:
            update_file: Path del nuevo ejecutable descargado
        
        Returns:
            bool: True si se inició el proceso de actualización
        """
        try:
            # Obtener path del ejecutable actual
            if getattr(sys, 'frozen', False):
                current_exe = sys.executable
            else:
                # En desarrollo, simular
                print("Running in development mode - update simulation")
                return False
            
            # Crear script batch para reemplazar el ejecutable
            batch_script = self._create_update_script(current_exe, update_file)
            
            # Ejecutar el script y cerrar la aplicación
            subprocess.Popen(batch_script, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            return True
            
        except Exception as e:
            print(f"Error applying update: {e}")
            return False
    
    def _create_update_script(self, current_exe, new_exe):
        """
        Crea un script batch que reemplaza el ejecutable y reinicia la app

        Args:
            current_exe: Path del ejecutable actual
            new_exe: Path del nuevo ejecutable

        Returns:
            str: Path del script batch
        """
        temp_dir = tempfile.gettempdir()
        script_path = os.path.join(temp_dir, 'antarctic_update.bat')

        # Crear backup del ejecutable actual
        backup_exe = current_exe + '.backup'

        # Script que espera a que se cierre la app, reemplaza el exe y reinicia
        script_content = f'''@echo off
echo Waiting for Antarctic to close...
timeout /t 3 /nobreak >nul

REM Kill any remaining processes
taskkill /F /IM Antarctic.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Create backup
echo Creating backup...
copy /Y "{current_exe}" "{backup_exe}" >nul

REM Replace with new version
echo Installing update...
move /Y "{new_exe}" "{current_exe}"

REM Check if update was successful
if exist "{current_exe}" (
    echo Update successful! Starting Antarctic...
    timeout /t 1 /nobreak >nul
    start "" "{current_exe}"
    del "{backup_exe}" >nul 2>&1
) else (
    echo Update failed! Restoring backup...
    move /Y "{backup_exe}" "{current_exe}"
    start "" "{current_exe}"
)

REM Clean up
timeout /t 2 /nobreak >nul
del "%~f0"
'''

        with open(script_path, 'w') as f:
            f.write(script_content)

        return script_path
    
    def check_and_update(self, auto_install=False, progress_callback=None):
        """
        Verifica y opcionalmente instala actualizaciones
        
        Args:
            auto_install: Si True, instala automáticamente sin preguntar
            progress_callback: Función callback(bytes_downloaded, total_bytes)
        
        Returns:
            dict: Información sobre el resultado
        """
        # Verificar si hay actualización
        has_update, version, url, notes = self.is_update_available()
        
        result = {
            'has_update': has_update,
            'version': version,
            'notes': notes,
            'downloaded': False,
            'installed': False,
            'error': None
        }
        
        if not has_update:
            return result
        
        if auto_install:
            # Descargar
            update_file = self.download_update(url, progress_callback)
            
            if update_file:
                result['downloaded'] = True
                
                # Aplicar actualización
                if self.apply_update(update_file):
                    result['installed'] = True
                else:
                    result['error'] = 'Failed to apply update'
            else:
                result['error'] = 'Failed to download update'
        
        return result


def get_version_from_file():
    """Lee la versión desde un archivo version.txt si existe"""
    try:
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        version_file = os.path.join(base_path, 'version.txt')
        
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                return f.read().strip()
    except:
        pass
    
    return CURRENT_VERSION


# Ejemplo de uso
if __name__ == "__main__":
    updater = Updater()
    
    print(f"Current version: {updater.current_version}")
    print("Checking for updates...")
    
    has_update, version, url, notes = updater.is_update_available()
    
    if has_update:
        print(f"\n✓ Update available: v{version}")
        print(f"\nRelease notes:\n{notes}")
        print(f"\nDownload URL: {url}")
        
        choice = input("\nDownload and install? (y/n): ")
        
        if choice.lower() == 'y':
            def progress(downloaded, total):
                percent = (downloaded / total) * 100 if total > 0 else 0
                print(f"\rDownloading: {percent:.1f}%", end='')
            
            result = updater.check_and_update(auto_install=True, progress_callback=progress)
            
            if result['installed']:
                print("\n\n✓ Update installed! Restarting...")
            else:
                print(f"\n\n✗ Update failed: {result.get('error', 'Unknown error')}")
    else:
        print("\n✓ You're running the latest version!")

