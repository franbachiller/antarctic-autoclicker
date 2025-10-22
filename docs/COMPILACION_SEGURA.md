# Guía de Compilación Segura - Antarctic

## Prerrequisitos

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

**Dependencias necesarias:**
- customtkinter >= 5.2.0
- Pillow >= 10.0.0
- requests >= 2.31.0
- psutil >= 5.9.0
- pyinstaller >= 6.0.0

---

## Compilación Básica (Segura)

### Usar el Script Automático
```batch
compile_secure.bat
```

Este script:
✅ Incluye módulo de seguridad (`security.py`)
✅ Activa anti-debugging
✅ Activa validación periódica de licencia
✅ Elimina símbolos de debug (`--strip`)
✅ Empaqueta todo en un solo .exe

### Resultado
- **Archivo**: `dist\Antarctic.exe`
- **Tamaño**: ~30 MB
- **Protección**: Media-Alta ⭐⭐⭐⭐

---

## Compilación Avanzada (Máxima Seguridad)

### Opción 1: PyArmor (Recomendado)

#### Paso 1: Instalar PyArmor
```bash
pip install pyarmor
```

#### Paso 2: Ofuscar el código
```bash
pyarmor gen --obf-code 2 --obf-module 1 --restrict 0 antarctic.py
pyarmor gen --obf-code 2 --obf-module 1 --restrict 0 auth_client.py
pyarmor gen --obf-code 2 --obf-module 1 --restrict 0 security.py
```

Esto crea carpeta `dist/` con código ofuscado.

#### Paso 3: Compilar código ofuscado
```bash
cd dist
pyinstaller --onefile --windowed --icon=../icon.ico ^
    --add-data "../icon.ico;." ^
    --add-data "../logo.png;." ^
    --add-data "../logo_compact.png;." ^
    antarctic.py
```

**Resultado**:
- Código Python ofuscado (imposible de descompilar)
- Strings encriptados
- Anti-tampering incluido
- **Protección**: Muy Alta ⭐⭐⭐⭐⭐

---

### Opción 2: UPX Compression

Después de compilar con `compile_secure.bat`:

```bash
# Descargar UPX: https://upx.github.io/
upx --best --ultra-brute dist\Antarctic.exe
```

**Beneficios**:
- Reduce tamaño 50-70%
- Dificulta análisis estático
- Compresión reversible (no es ofuscación real)

**Resultado**:
- Tamaño: ~15 MB (reducido de ~30 MB)
- **Protección adicional**: Baja ⭐

---

### Opción 3: Protectores Comerciales

#### VMProtect ($$$$)
```
1. Compila con compile_secure.bat
2. Abre dist\Antarctic.exe en VMProtect
3. Selecciona funciones críticas para virtualizar:
   - SecurityGuard.check_debugger
   - AuthClient.validate
   - KeyManager.activate
4. Protege y guarda
```

**Resultado**: Prácticamente imposible de crackear ⭐⭐⭐⭐⭐

#### Themida ($$$$)
Similar a VMProtect, con interfaz diferente.

#### Enigma Protector ($)
Opción más económica, protección decente.

---

## Comparación de Métodos

| Método | Dificultad | Tiempo Cracking | Costo | Protección |
|--------|-----------|-----------------|-------|------------|
| PyInstaller básico | Fácil | 1-2 horas | Gratis | ⭐⭐ |
| compile_secure.bat | Media | 1-2 días | Gratis | ⭐⭐⭐⭐ |
| PyArmor | Alta | 1-2 semanas | Gratis-$$ | ⭐⭐⭐⭐⭐ |
| UPX | Baja | +30 min | Gratis | ⭐ |
| VMProtect | Muy Alta | Meses | $$$$ | ⭐⭐⭐⭐⭐ |

---

## Archivos Incluidos en Compilación

### Archivos de Código
- ✅ `antarctic.py` - Aplicación principal
- ✅ `auth_client.py` - Cliente de autenticación
- ✅ `security.py` - Módulo de seguridad (NUEVO)

### Recursos
- ✅ `icon.ico` - Icono de la aplicación
- ✅ `logo.png` - Logo principal
- ✅ `logo_compact.png` - Logo compacto

### Dependencias Auto-Incluidas
- customtkinter
- Pillow
- requests (+ urllib3, certifi)
- psutil

---

## Verificación Post-Compilación

### 1. Verificar Tamaño
```bash
dir dist\Antarctic.exe
```
**Esperado**: 25-35 MB (sin comprimir)

### 2. Probar Anti-Debugging
```bash
# Intenta ejecutar en x64dbg o OllyDbg
# Debería cerrarse con "Security Alert"
```

### 3. Probar Validación de Licencia
```bash
# Ejecuta Antarctic.exe
# Espera 5 minutos
# Revoca la licencia en el panel admin
# Espera otros 5 minutos
# Debería cerrarse con "License Expired"
```

### 4. Verificar Display de Tiempo
```bash
# Ejecuta Antarctic.exe
# Verifica que muestra:
#   - Tipo de licencia
#   - Tiempo restante
#   - Color correcto (verde/naranja/rojo)
```

---

## Distribución

### Archivos a Distribuir
```
Antarctic-v1.0/
├── Antarctic.exe          ← Solo esto
└── README.txt            ← Instrucciones para usuario
```

### ⚠️ NO Distribuir
- ❌ Código fuente (.py)
- ❌ Dependencias (ya incluidas en .exe)
- ❌ Icon/logos (ya incluidos en .exe)
- ❌ auth-server/ (backend)
- ❌ tools/ (generadores)

---

## Medidas de Seguridad Incluidas

### ✅ Al Inicio (Startup)
1. Check de debugger
2. Check de herramientas RE
3. Verificación de integridad
4. Validación de licencia con servidor

### ✅ Durante Ejecución (Runtime)
1. Monitor de seguridad cada 30 segundos
2. Re-validación de licencia cada 5 minutos
3. Display de tiempo restante
4. Cierre automático si detecta violaciones

### ✅ Protección de Datos
1. Sesión encriptada con XOR + HWID
2. HWID binding (no transferible)
3. Tokens con expiración (24h)
4. Comunicación HTTPS con servidor

---

## Troubleshooting

### Error: "Security violation detected (001)"
- **Causa**: Debugger detectado
- **Solución**: No ejecutar en debugger

### Error: "Security violation detected (002)"
- **Causa**: Integridad del .exe comprometida
- **Solución**: Re-compilar desde código fuente limpio

### Error: "Security violation detected (003)"
- **Causa**: Herramientas RE detectadas
- **Solución**: Cerrar Process Hacker, IDA, etc.

### Warning: "Running in VM"
- **Info**: Solo logging, no bloquea
- **Acción**: Ninguna, funciona normal

### Error: Falta "psutil"
```bash
pip install psutil
```

### Error: Antarctic.exe no se crea
```bash
# Verificar que todos los archivos existan:
dir antarctic.py auth_client.py security.py icon.ico
```

---

## Mejores Prácticas

### ✅ Hacer
1. **Siempre** usa `compile_secure.bat` (no compile.bat)
2. **Prueba** el .exe antes de distribuir
3. **Verifica** que security checks funcionan
4. **Mantén** el código fuente privado
5. **Usa** PyArmor para productos comerciales

### ❌ NO Hacer
1. **NO** distribuyas archivos .py
2. **NO** desactives security checks
3. **NO** hardcodees licencias en el código
4. **NO** subas el código a GitHub público
5. **NO** uses compile.bat básico para producción

---

## Niveles de Seguridad Recomendados

### Para Proyecto Personal
```
compile_secure.bat
```
**Suficiente para**: Amigos, comunidad pequeña

### Para Venta Pequeña (<100 usuarios)
```
PyArmor + compile_secure.bat
```
**Suficiente para**: Venta en foros, Discord

### Para Producto Comercial (>100 usuarios)
```
PyArmor + VMProtect/Themida + Code Signing
```
**Suficiente para**: Venta profesional, empresa

### Para Producto Premium (>$100)
```
PyArmor + VMProtect + Server-Side Validation + Code Signing
```
**Máxima protección**: Casi imposible de crackear

---

## Recursos Adicionales

### Herramientas
- **PyArmor**: https://pyarmor.readthedocs.io/
- **UPX**: https://upx.github.io/
- **VMProtect**: https://vmpsoft.com/
- **Themida**: https://www.oreans.com/

### Documentación
- [SEGURIDAD.md](SEGURIDAD.md) - Detalles técnicos completos
- [README.md](../README.md) - Información general
- [SISTEMA_LICENCIAS.md](SISTEMA_LICENCIAS.md) - Sistema de licencias

---

**Última actualización**: 2024-10-19
**Versión**: 1.0
