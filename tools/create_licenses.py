#!/usr/bin/env python3
"""
ANTARCTIC LICENSE MANAGER - ONLINE
===================================
Herramienta para crear y gestionar licencias en el servidor Vercel.

Uso:
    python tools/create_licenses.py
"""

import requests
import sys
import os
from datetime import datetime

# Configuración
SERVER_URL = "https://antarctic-autoclicker.vercel.app"
ADMIN_KEY = "ADMIN_KEY_REMOVED"

def create_licenses(license_type, count=1, notes=""):
    """Crear licencias en el servidor"""
    try:
        response = requests.post(
            f"{SERVER_URL}/api/admin/create-license",
            headers={
                "Content-Type": "application/json",
                "X-Admin-Key": ADMIN_KEY
            },
            json={
                "licenseType": license_type,
                "count": count,
                "notes": notes
            },
            timeout=15
        )

        result = response.json()

        if response.status_code == 200 and result.get('success'):
            return True, result['data']['licenses']
        else:
            return False, result.get('error', 'Error desconocido')

    except requests.RequestException as e:
        return False, f"Error de conexión: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def list_licenses():
    """Listar todas las licencias"""
    try:
        response = requests.get(
            f"{SERVER_URL}/api/admin/list-licenses",
            headers={
                "X-Admin-Key": ADMIN_KEY
            },
            timeout=15
        )

        result = response.json()

        if response.status_code == 200 and result.get('success'):
            return True, result['data']['licenses']
        else:
            return False, result.get('error', 'Error desconocido')

    except requests.RequestException as e:
        return False, f"Error de conexión: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def save_licenses_to_file(licenses):
    """Guardar licencias en un archivo"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"licenses_{timestamp}.txt"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("ANTARCTIC - LICENCIAS GENERADAS\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total: {len(licenses)} licencias\n\n")

        for i, lic in enumerate(licenses, 1):
            f.write(f"LICENCIA #{i}\n")
            f.write("-" * 70 + "\n")
            f.write(f"Key:     {lic['key']}\n")
            f.write(f"Tipo:    {lic['type']}\n")
            f.write(f"Expira:  {lic['expiresAt']}\n")
            f.write(f"Estado:  {lic['status']}\n\n")

    return filename

def main():
    """Menú principal"""
    print("\n" + "=" * 70)
    print("     ANTARCTIC LICENSE MANAGER - ONLINE")
    print("=" * 70)
    print()
    print(f"Servidor: {SERVER_URL}")
    print()

    while True:
        print("-" * 70)
        print("MENÚ:")
        print("-" * 70)
        print("1. Crear licencias")
        print("2. Listar todas las licencias")
        print("3. Salir")
        print("-" * 70)

        choice = input("\nSelecciona opción (1-3): ").strip()

        if choice == "1":
            print("\n--- CREAR LICENCIAS ---")
            print("\nTipos disponibles:")
            print("  1. week      - 1 semana")
            print("  2. month     - 1 mes")
            print("  3. 3months   - 3 meses")
            print("  4. 6months   - 6 meses")
            print("  5. year      - 1 año")
            print("  6. lifetime  - Permanente")

            type_choice = input("\nSelecciona tipo (1-6): ").strip()
            type_map = {
                "1": "week",
                "2": "month",
                "3": "3months",
                "4": "6months",
                "5": "year",
                "6": "lifetime"
            }

            license_type = type_map.get(type_choice)
            if not license_type:
                print("[ERROR] Opción inválida")
                continue

            try:
                count = int(input("¿Cuántas licencias? (1-100): "))
                count = max(1, min(100, count))
            except:
                count = 1

            notes = input("Notas (opcional): ").strip()

            print("\n[*] Creando licencias...")
            success, result = create_licenses(license_type, count, notes)

            if success:
                print(f"[OK] {len(result)} licencias creadas exitosamente\n")

                for i, lic in enumerate(result, 1):
                    print(f"LICENCIA #{i}")
                    print("-" * 70)
                    print(f"Key:     {lic['key']}")
                    print(f"Tipo:    {lic['type']}")
                    print(f"Expira:  {lic['expiresAt']}")
                    print(f"Estado:  {lic['status']}")
                    print()

                filename = save_licenses_to_file(result)
                print(f"[OK] Licencias guardadas en: {filename}\n")
            else:
                print(f"[ERROR] {result}\n")

        elif choice == "2":
            print("\n--- LISTAR LICENCIAS ---\n")
            print("[*] Obteniendo licencias...")
            success, result = list_licenses()

            if success:
                print(f"\n[OK] Total: {len(result)} licencias\n")

                # Agrupar por estado
                active = [l for l in result if l['status'] == 'active']
                expired = [l for l in result if l['status'] == 'expired']
                banned = [l for l in result if l['status'] == 'banned']

                print(f"Activas:  {len(active)}")
                print(f"Expiradas: {len(expired)}")
                print(f"Baneadas:  {len(banned)}")
                print()

                show = input("¿Mostrar detalles? (s/n): ").strip().lower()
                if show == 's':
                    for lic in result[:20]:  # Mostrar solo las primeras 20
                        print("-" * 70)
                        print(f"Key:     {lic['license_key']}")
                        print(f"Tipo:    {lic['license_type']}")
                        print(f"Estado:  {lic['status']}")
                        print(f"Expira:  {lic.get('expires_at', 'N/A')}")
                        print(f"HWID:    {lic.get('hwid', 'No activada')[:16] if lic.get('hwid') else 'No activada'}...")
                        print(f"Creada:  {lic['created_at']}")

                    if len(result) > 20:
                        print(f"\n... y {len(result) - 20} más")
                print()
            else:
                print(f"[ERROR] {result}\n")

        elif choice == "3":
            print("\n[*] Saliendo...\n")
            break

        else:
            print("[ERROR] Opción inválida\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[*] Operación cancelada por el usuario.\n")
    except Exception as e:
        print(f"\n[ERROR] {e}\n")
