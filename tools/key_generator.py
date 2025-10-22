#!/usr/bin/env python3
"""
ANTARCTIC LICENSE KEY GENERATOR - ADVANCED
==========================================
Generador mejorado que automáticamente actualiza antarctic.py
con las nuevas keys generadas.

Características de seguridad:
- Keys hasheadas con SHA256
- Doble verificación con salt
- Auto-inserción en el código fuente
- Backup automático antes de modificar

Uso:
    python tools/key_generator.py
"""

import hashlib
import random
import string
import os
import shutil
from datetime import datetime


# CONFIGURACIÓN
ANTARCTIC_FILE = os.path.join(os.path.dirname(__file__), "..", "antarctic.py")
BACKUP_DIR = os.path.join(os.path.dirname(__file__), "..", "backup")
SALT = "SALT_REMOVED"  # Salt para mayor seguridad


def generate_key():
    """Genera una key de licencia aleatoria"""
    parts = ["ANTARCTIC"]

    for _ in range(3):
        part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        parts.append(part)

    return '-'.join(parts)


def hash_key(key):
    """Hashea una key con SHA256 + salt para mayor seguridad"""
    salted_key = key + SALT
    return hashlib.sha256(salted_key.encode()).hexdigest()


def create_backup():
    """Crea un backup del archivo antarctic.py"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"antarctic_backup_{timestamp}.py"
    backup_path = os.path.join(BACKUP_DIR, backup_name)

    shutil.copy2(ANTARCTIC_FILE, backup_path)
    return backup_path


def update_antarctic_file(new_hashes):
    """Actualiza antarctic.py con los nuevos hashes"""
    if not os.path.exists(ANTARCTIC_FILE):
        print(f"❌ ERROR: No se encontró {ANTARCTIC_FILE}")
        return False

    # Crear backup
    backup_path = create_backup()
    print(f"✓ Backup creado: {backup_path}")

    # Leer archivo
    with open(ANTARCTIC_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Buscar la sección de valid_keys_hashed
    start_marker = "self.valid_keys_hashed = ["
    end_marker = "]"

    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("❌ ERROR: No se encontró la sección de valid_keys_hashed")
        return False

    # Encontrar el final del array
    start_idx += len(start_marker)
    end_idx = content.find(end_marker, start_idx)

    # Extraer las keys existentes
    existing_section = content[start_idx:end_idx].strip()
    existing_hashes = []

    for line in existing_section.split('\n'):
        line = line.strip()
        if line.startswith('"') and line.endswith('",') or line.endswith('"'):
            hash_value = line.strip('",').strip()
            if hash_value:
                existing_hashes.append(hash_value)

    # Combinar con nuevas keys
    all_hashes = existing_hashes + new_hashes

    # Construir nueva sección
    new_section = "self.valid_keys_hashed = [\n"
    for h in all_hashes:
        new_section += f'            "{h}",\n'
    new_section += "        ]"

    # Reemplazar en el contenido
    before = content[:content.find(start_marker)]
    after = content[end_idx + 1:]
    new_content = before + new_section + after

    # Actualizar también el SALT
    salt_marker = 'SALT = "'
    salt_start = new_content.find(salt_marker)
    if salt_start != -1:
        salt_start += len(salt_marker)
        salt_end = new_content.find('"', salt_start)
        new_content = new_content[:salt_start] + SALT + new_content[salt_end:]

    # Guardar archivo
    with open(ANTARCTIC_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✓ Archivo {ANTARCTIC_FILE} actualizado exitosamente")
    print(f"✓ Total de keys válidas: {len(all_hashes)}")
    return True


def generate_keys_interactive():
    """Genera keys de forma interactiva"""
    print("\n" + "=" * 70)
    print("     ANTARCTIC LICENSE KEY GENERATOR - ADVANCED")
    print("=" * 70)
    print()

    try:
        num_keys = int(input("¿Cuántas keys deseas generar? (1-50): "))
        num_keys = max(1, min(50, num_keys))
    except:
        num_keys = 1

    print()
    print("Generando keys...")
    print("-" * 70)

    keys_data = []

    for i in range(num_keys):
        key = generate_key()
        key_hash = hash_key(key)
        keys_data.append({
            'number': i + 1,
            'key': key,
            'hash': key_hash
        })

    # Mostrar keys generadas
    print()
    print("=" * 70)
    print("KEYS GENERADAS:")
    print("=" * 70)
    print()

    for data in keys_data:
        print(f"KEY #{data['number']}")
        print("-" * 70)
        print(f"License Key (dar al cliente): {data['key']}")
        print(f"Hash (SHA256):                {data['hash']}")
        print()

    # Preguntar si desea auto-actualizar
    print("=" * 70)
    auto_update = input("¿Deseas actualizar automáticamente antarctic.py? (s/n): ").lower()

    if auto_update == 's' or auto_update == 'y':
        print()
        print("Actualizando archivo...")
        new_hashes = [d['hash'] for d in keys_data]

        if update_antarctic_file(new_hashes):
            print()
            print("=" * 70)
            print("✓ ÉXITO: Keys añadidas automáticamente")
            print("=" * 70)
            print()
            print("PRÓXIMOS PASOS:")
            print("1. Verifica que antarctic.py se haya actualizado correctamente")
            print("2. Recompila el ejecutable con: pyinstaller Antarctic.spec")
            print("3. Distribuye las License Keys a tus clientes")
            print()
        else:
            print()
            print("=" * 70)
            print("❌ ERROR: No se pudo actualizar el archivo")
            print("=" * 70)
            print()
            print("SOLUCIÓN MANUAL:")
            print("Agrega estos hashes manualmente a antarctic.py:")
            print()
            for data in keys_data:
                print(f'    "{data["hash"]}",')
    else:
        print()
        print("=" * 70)
        print("INSTRUCCIONES MANUALES:")
        print("=" * 70)
        print()
        print("1. Abre antarctic.py")
        print("2. Busca la clase KeyManager y la variable valid_keys_hashed")
        print("3. Agrega estos hashes:")
        print()
        for data in keys_data:
            print(f'    "{data["hash"]}",')
        print()

    # Guardar keys en archivo de texto
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    keys_file = f"generated_keys_{timestamp}.txt"

    with open(keys_file, 'w', encoding='utf-8') as f:
        f.write("ANTARCTIC - LICENSE KEYS GENERATED\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        for data in keys_data:
            f.write(f"KEY #{data['number']}\n")
            f.write("-" * 70 + "\n")
            f.write(f"License Key: {data['key']}\n")
            f.write(f"Hash:        {data['hash']}\n\n")

    print()
    print(f"✓ Keys guardadas en: {keys_file}")
    print()
    print("=" * 70)


if __name__ == "__main__":
    try:
        generate_keys_interactive()
    except KeyboardInterrupt:
        print("\n\nOperación cancelada por el usuario.")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

    input("\nPresiona Enter para salir...")
