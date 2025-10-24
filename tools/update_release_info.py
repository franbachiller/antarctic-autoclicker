#!/usr/bin/env python3
"""
ANTARCTIC - UPDATE RELEASE INFO
================================
Script para actualizar la información de la última versión en la API

Uso:
    python tools/update_release_info.py --version 1.0.3 --url "https://..." --notes "Release notes"
"""

import argparse
import sys
from pathlib import Path

def update_latest_js(version, download_url, release_notes):
    """
    Actualiza el archivo api/updates/latest.js con la nueva versión
    """
    latest_js_path = Path("api/updates/latest.js")
    
    if not latest_js_path.exists():
        print(f"[ERROR] No se encontró {latest_js_path}")
        return False
    
    # Leer el archivo actual
    content = latest_js_path.read_text(encoding='utf-8')
    
    # Buscar y reemplazar la versión
    import re
    
    # Reemplazar version
    content = re.sub(
        r"version:\s*['\"][\d.]+['\"]",
        f"version: '{version}'",
        content
    )
    
    # Reemplazar download_url
    content = re.sub(
        r"download_url:\s*process\.env\.LATEST_EXE_URL\s*\|\|\s*['\"].*?['\"]",
        f"download_url: process.env.LATEST_EXE_URL || '{download_url}'",
        content
    )
    
    # Reemplazar release_notes
    if release_notes:
        # Escapar caracteres especiales en las notas
        escaped_notes = release_notes.replace('`', '\\`').replace('${', '\\${')
        content = re.sub(
            r"release_notes:\s*`[^`]*`",
            f"release_notes: `\n{escaped_notes}\n      `",
            content,
            flags=re.DOTALL
        )
    
    # Escribir el archivo actualizado
    latest_js_path.write_text(content, encoding='utf-8')
    
    print(f"[OK] Actualizado {latest_js_path}")
    print(f"     Version: {version}")
    print(f"     URL: {download_url}")
    
    return True


def update_download_js(version, download_url):
    """
    Actualiza el archivo api/updates/download.js con la nueva versión
    """
    download_js_path = Path("api/updates/download.js")
    
    if not download_js_path.exists():
        print(f"[ERROR] No se encontró {download_js_path}")
        return False
    
    # Leer el archivo actual
    content = download_js_path.read_text(encoding='utf-8')
    
    # Buscar la sección de downloadUrls
    import re
    
    # Agregar la nueva versión al mapeo
    new_entry = f"      '{version}': process.env.LATEST_EXE_URL || '{download_url}',"
    
    # Buscar el objeto downloadUrls y agregar la nueva entrada
    content = re.sub(
        r"(const downloadUrls = \{[^}]*)'([\d.]+)':",
        f"\\1'{version}': process.env.LATEST_EXE_URL || '{download_url}',\n      '\\2':",
        content,
        count=1
    )
    
    # Actualizar la versión por defecto
    content = re.sub(
        r"const targetVersion = version \|\| '[\d.]+'",
        f"const targetVersion = version || '{version}'",
        content
    )
    
    # Escribir el archivo actualizado
    download_js_path.write_text(content, encoding='utf-8')
    
    print(f"[OK] Actualizado {download_js_path}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Actualizar información de release en la API")
    parser.add_argument("--version", required=True, help="Versión (ej: 1.0.3)")
    parser.add_argument("--url", required=True, help="URL de descarga del .exe")
    parser.add_argument("--notes", help="Notas de la release (opcional)")
    
    args = parser.parse_args()
    
    version = args.version.lstrip('v')
    
    print("=" * 60)
    print("ACTUALIZAR INFORMACIÓN DE RELEASE")
    print("=" * 60)
    print(f"Versión: {version}")
    print(f"URL: {args.url}")
    print("=" * 60)
    
    # Confirmar
    print(f"\n[?] Actualizar archivos de API? (y/n): ", end='')
    confirm = input().lower()
    
    if confirm != 'y':
        print("[*] Cancelado")
        sys.exit(0)
    
    # Actualizar archivos
    success1 = update_latest_js(version, args.url, args.notes or "")
    success2 = update_download_js(version, args.url)
    
    if success1 and success2:
        print("\n" + "=" * 60)
        print("[OK] ARCHIVOS ACTUALIZADOS")
        print("=" * 60)
        print("\nPróximos pasos:")
        print("  1. Revisa los cambios en api/updates/")
        print("  2. Haz commit y push:")
        print("     git add api/updates/")
        print("     git commit -m 'Update to version " + version + "'")
        print("     git push")
        print("  3. Vercel auto-desplegará los cambios")
        print("  4. Los usuarios verán la actualización automáticamente")
    else:
        print("\n[ERROR] Falló la actualización")
        sys.exit(1)


if __name__ == "__main__":
    main()

