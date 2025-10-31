#!/usr/bin/env python3
"""
ANTARCTIC RELEASE MANAGER - AUTOMATICO
=======================================
Script para crear releases automáticamente en GitHub

Este script hace:
  1. Compila el ejecutable con PyInstaller
  2. Crea la release en GitHub
  3. Sube el .exe a la release

Uso simple:
    release.bat
    (Te pedirá la versión y hará todo automáticamente)

Uso avanzado:
    python tools/release.py --version 1.0.1 --token YOUR_GITHUB_TOKEN

    O configurar GITHUB_TOKEN como variable de entorno:
    set GITHUB_TOKEN=your_token_here
    python tools/release.py --version 1.0.1

Opciones:
    --skip-compile    Saltar compilación (si ya compilaste manualmente)
    --notes "..."     Especificar notas de release directamente
"""

import argparse
import os
import sys
import requests
import json
from pathlib import Path

# Configuración
GITHUB_REPO = "Narfbach/antarctic-releases"
EXE_PATH = "dist/Antarctic.exe"


def create_github_release(version, token, exe_path, release_notes="", github_repo=None):
    """
    Crea una release en GitHub y sube el ejecutable

    Args:
        version: Versión (ej: "1.0.1")
        token: GitHub Personal Access Token
        exe_path: Path al ejecutable
        release_notes: Notas de la release
        github_repo: Repositorio de GitHub (ej: "usuario/repo")

    Returns:
        bool: True si fue exitoso
    """

    # Usar el repo proporcionado o el default
    repo = github_repo or GITHUB_REPO

    # Validar que existe el ejecutable
    if not os.path.exists(exe_path):
        print(f"[ERROR] No se encontro el ejecutable en {exe_path}")
        print("   Compila primero con: compile_antarctic.bat")
        return False

    # Preparar datos de la release
    tag_name = f"v{version}"
    release_data = {
        "tag_name": tag_name,
        "name": f"Antarctic v{version}",
        "body": release_notes or f"Release version {version}",
        "draft": False,
        "prerelease": False
    }

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    print(f"\n[*] Creando release v{version}...")

    # Crear la release
    api_url = f"https://api.github.com/repos/{repo}/releases"

    try:
        response = requests.post(api_url, headers=headers, json=release_data)
        response.raise_for_status()

        release = response.json()
        release_id = release['id']
        upload_url = release['upload_url'].split('{')[0]  # Remove template

        print(f"[OK] Release creada: {release['html_url']}")

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 422:
            print(f"[ERROR] La version {tag_name} ya existe")
            print("   Usa una version diferente o elimina la release existente")
        else:
            print(f"[ERROR] Error al crear release: {e}")
            print(f"   Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    # Subir el ejecutable
    print(f"\n[*] Subiendo {os.path.basename(exe_path)}...")
    
    try:
        file_name = os.path.basename(exe_path)
        file_size = os.path.getsize(exe_path)
        
        print(f"   Tamaño: {file_size / (1024*1024):.2f} MB")
        
        with open(exe_path, 'rb') as f:
            upload_headers = {
                "Authorization": f"token {token}",
                "Content-Type": "application/octet-stream"
            }
            
            upload_response = requests.post(
                f"{upload_url}?name={file_name}",
                headers=upload_headers,
                data=f
            )
            upload_response.raise_for_status()
        
        print(f"[OK] Ejecutable subido exitosamente")

    except Exception as e:
        print(f"[ERROR] Error al subir ejecutable: {e}")
        return False

    print(f"\n[OK] Release v{version} creada exitosamente!")
    print(f"URL: {release['html_url']}")
    print(f"\nLos usuarios ahora pueden actualizar automaticamente a v{version}")

    return True


def get_release_notes():
    """Solicita las notas de la release al usuario"""
    print("\n[*] Ingresa las notas de la release (presiona Enter dos veces para terminar):")
    print("   Ejemplo:")
    print("   - Nueva funcionalidad X")
    print("   - Corrección de bug Y")
    print("   - Mejora de rendimiento Z")
    print()

    lines = []
    empty_count = 0

    while True:
        line = input()
        if not line:
            empty_count += 1
            if empty_count >= 2:
                break
        else:
            empty_count = 0
            lines.append(line)

    return "\n".join(lines)


def compile_executable():
    """Compila el ejecutable usando PyInstaller"""
    import subprocess

    print("\n[*] Compilando ejecutable...")

    # Verificar que existe el spec file
    spec_file = "antarctic.spec"
    if not os.path.exists(spec_file):
        print(f"[ERROR] No se encontro {spec_file}")
        return False

    try:
        # Ejecutar PyInstaller
        result = subprocess.run(
            ["pyinstaller", spec_file, "--clean", "--noconfirm"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("[OK] Compilacion exitosa!")
            return True
        else:
            print(f"[ERROR] Error en compilacion:")
            print(result.stderr)
            return False

    except FileNotFoundError:
        print("[ERROR] PyInstaller no esta instalado")
        print("   Instala con: pip install pyinstaller")
        return False
    except Exception as e:
        print(f"[ERROR] Error al compilar: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Crear release de Antarctic en GitHub")
    parser.add_argument("--version", required=True, help="Versión de la release (ej: 1.0.1)")
    parser.add_argument("--token", help="GitHub Personal Access Token (o usar variable GITHUB_TOKEN)")
    parser.add_argument("--notes", help="Notas de la release (opcional)")
    parser.add_argument("--exe", default=EXE_PATH, help=f"Path al ejecutable (default: {EXE_PATH})")
    parser.add_argument("--repo", default=GITHUB_REPO, help=f"Repositorio GitHub (default: {GITHUB_REPO})")
    parser.add_argument("--skip-compile", action="store_true", help="Saltar compilación automática")
    
    args = parser.parse_args()
    
    # Obtener token
    token = args.token or os.environ.get('GITHUB_TOKEN')

    if not token:
        print("[ERROR] Se requiere un GitHub token")
        print("\nOpciones:")
        print("  1. Usar --token: python tools/release.py --version 1.0.1 --token YOUR_TOKEN")
        print("  2. Variable de entorno: set GITHUB_TOKEN=YOUR_TOKEN")
        print("\nCrea un token en: https://github.com/settings/tokens")
        print("   Permisos necesarios: repo (Full control of private repositories)")
        sys.exit(1)

    # Usar el repo especificado o el default
    github_repo = args.repo

    # Validar formato de versión
    version = args.version.lstrip('v')
    parts = version.split('.')

    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        print("[ERROR] Formato de version invalido")
        print("   Usa formato semver: X.Y.Z (ej: 1.0.1)")
        sys.exit(1)

    print("=" * 60)
    print("ANTARCTIC RELEASE MANAGER")
    print("=" * 60)
    print(f"Versión: v{version}")
    print(f"Repositorio: {github_repo}")
    print(f"Ejecutable: {args.exe}")
    print("=" * 60)

    # Obtener notas de la release si no se proporcionaron
    release_notes = args.notes
    if not release_notes:
        release_notes = get_release_notes()

    # Confirmar
    print(f"\n[?] Crear release v{version}? (y/n): ", end='')
    confirm = input().lower()

    if confirm != 'y':
        print("[*] Cancelado")
        sys.exit(0)

    # Paso 1: Compilar ejecutable (si no se saltó)
    if not args.skip_compile:
        print("\n" + "=" * 60)
        print("PASO 1/2: Compilando ejecutable")
        print("=" * 60)
        if not compile_executable():
            print("\n[ERROR] La compilacion fallo")
            print("Puedes compilar manualmente con: compile_antarctic.bat")
            print("   O usar --skip-compile si ya compilaste")
            sys.exit(1)

        # Verificar que el ejecutable existe
        if not os.path.exists(args.exe):
            print(f"\n[ERROR] No se encontro el ejecutable en {args.exe}")
            sys.exit(1)
    else:
        print("\n[*] Saltando compilacion (--skip-compile)")
        if not os.path.exists(args.exe):
            print(f"\n[ERROR] No se encontro el ejecutable en {args.exe}")
            print("   Compila primero con: compile_antarctic.bat")
            sys.exit(1)

    # Paso 2: Crear release en GitHub
    print("\n" + "=" * 60)
    print("PASO 2/2: Creando release en GitHub")
    print("=" * 60)
    success = create_github_release(version, token, args.exe, release_notes, github_repo)

    if success:
        print("\n" + "=" * 60)
        print("[OK] RELEASE COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print(f"\nRelease v{version} publicada!")
        print(f"URL: https://github.com/{github_repo}/releases/tag/v{version}")
        print("\nPara la proxima release, simplemente ejecuta:")
        print(f"   release.bat")
        sys.exit(0)
    else:
        print("\n[ERROR] Release fallida")
        sys.exit(1)


if __name__ == "__main__":
    main()

