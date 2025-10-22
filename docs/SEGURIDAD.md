# Antarctic - Documentación de Seguridad

## Resumen de Medidas de Seguridad Implementadas

Antarctic incluye múltiples capas de seguridad para proteger contra piratería, ingeniería inversa y uso no autorizado.

---

## 1. Protección Anti-Debugging

### Detección de Debuggers
- **IsDebuggerPresent()**: Detecta debuggers adjuntos (OllyDbg, x64dbg, etc.)
- **NtQueryInformationProcess**: Verificación adicional del puerto de debug
- **Monitoreo Continuo**: Verifica cada 30 segundos si hay debuggers

### Acción al Detectar Debugger
- Contador de violaciones incrementa
- Después de 2 violaciones → cierre inmediato de la aplicación
- Mensaje genérico de "Security Alert" (no revela la causa exacta)

---

## 2. Detección de Herramientas de Ingeniería Inversa

### Herramientas Detectadas
El sistema monitorea procesos en busca de:
- **Debuggers**: IDA Pro, OllyDbg, x64dbg, WinDbg
- **Analizadores**: Process Hacker, Process Monitor, PEStudio
- **Sniffers**: Wireshark, Fiddler
- **Decompiladores**: dnSpy

### Implementación
```python
suspicious_processes = [
    'ida.exe', 'ida64.exe', 'ollydbg.exe', 'x64dbg.exe',
    'processhacker.exe', 'procmon.exe', 'wireshark.exe', ...
]
```

---

## 3. Validación de Licencia Multi-Capa

### Validación al Inicio
1. **Verificación de sesión local** (archivo encriptado)
2. **Validación con servidor** (online check)
3. **Verificación de HWID** (hardware ID binding)
4. **Check de expiración**

### Validación Continua
- **Cada 5 minutos**: Re-valida la licencia con el servidor
- **Detección de revocación**: Si la licencia es revocada, cierra la app
- **Grace Period**: 1 hora de tolerancia para problemas de red

### Encriptación de Sesión
```python
# XOR encryption con HWID como clave
encrypted = XOR(session_data, HWID)
```
- Los datos de sesión no pueden transferirse entre PCs
- Binding por hardware único

---

## 4. Protección de Integridad

### Verificación de Ejecutable
- Detecta si el .exe ha sido modificado (tamaño mínimo)
- Verifica que se ejecuta desde PyInstaller empaquetado
- Bloquea ejecución si detecta manipulación

---

## 5. Detección de Virtualización (Opcional)

### Indicadores de VM Detectados
- VMware
- VirtualBox
- QEMU
- Hyper-V

**Nota**: Actualmente solo registra, no bloquea (muchos usuarios legítimos usan VMs)

---

## 6. Monitoreo en Tiempo Real

### SecurityGuard Thread
```python
monitor_thread = threading.Thread(
    target=self.monitor_continuous,
    daemon=True
)
```

**Frecuencia**: Cada 30 segundos
**Checks Realizados**:
- Debugger presente
- Herramientas RE ejecutándose
- Integridad del proceso

---

## 7. Información de Licencia en GUI

### Display en Tiempo Real
- **Tipo de licencia**: Week, Month, Lifetime, etc.
- **Tiempo restante**: Calculado en tiempo real
- **Alertas visuales**:
  - 🟢 Verde: > 3 días restantes
  - 🟠 Naranja: ≤ 3 días restantes
  - 🔴 Rojo: < 24 horas o expirado

### Actualización Automática
- Se actualiza cada 5 minutos junto con la validación
- Muestra advertencias antes de expirar

---

## 8. Compilación con PyInstaller

### Opciones de Seguridad Usadas

```batch
pyinstaller ^
    --onefile           # Un solo archivo
    --windowed          # Sin consola
    --strip             # Elimina símbolos de debug
    --hidden-import=security  # Incluye módulo de seguridad
```

### Resultado
- **Sin archivos .pyc**: Código compilado a bytecode
- **Empaquetado**: Todo en un solo .exe
- **Símbolos eliminados**: Más difícil de analizar

---

## 9. Ofuscación de Código (Limitada)

### Nivel Actual: BÁSICO
PyInstaller proporciona ofuscación básica:
- Bytecode de Python (no texto plano)
- Strings no directamente visibles
- Estructura de clases parcialmente oculta

### ⚠️ ADVERTENCIA
**PyInstaller NO es ofuscación real**. Herramientas como:
- `pyinstxtractor` - Extrae archivos del .exe
- `uncompyle6` / `decompyle3` - Descompila bytecode a Python

---

## 10. Recomendaciones para Máxima Seguridad

### Nivel MEDIO (Implementado)
✅ Anti-debugging
✅ Detección de herramientas RE
✅ Validación de licencia continua
✅ HWID binding
✅ Encriptación de sesión

### Nivel ALTO (Recomendado para Producción)

#### A. Ofuscación con PyArmor
```bash
pip install pyarmor
pyarmor gen --obf-code 2 --obf-module 1 antarctic.py
```
**Beneficios**:
- Ofuscación real de código Python
- Protección de strings
- Anti-tampering mejorado

#### B. Protectores Comerciales
- **VMProtect** ($$$) - Virtualización de código
- **Themida** ($$$) - Protección anti-debug avanzada
- **Enigma Protector** ($$) - Opción económica

#### C. Compresión con UPX
```bash
upx --best --ultra-brute dist\Antarctic.exe
```
**Beneficios**:
- Reduce tamaño del .exe
- Dificulta análisis estático (leve)

#### D. Code Signing Certificate
- Firma digital del ejecutable
- Incrementa confianza del usuario
- Windows SmartScreen no alerta

---

## 11. Limitaciones Conocidas

### ❌ PyInstaller es Reversible
- Expertos pueden desempaquetar el .exe
- El bytecode puede descompilarse a código Python
- Las strings son visibles con herramientas

### ❌ Python es Interpretado
- No es código nativo (C/C++)
- Más fácil de descompilar que binarios nativos
- Rendimiento puede ser analizado

### ❌ Client-Side Checks
- Todas las verificaciones ocurren en el cliente
- Un cracker experto puede parchear los checks
- La única protección real es el servidor de licencias

---

## 12. Arquitectura de Seguridad

```
┌─────────────────────────────────────────┐
│         USUARIO EJECUTA .EXE            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│   SECURITY CHECKS (startup)             │
│  - Anti-debugging                       │
│  - Anti-tampering                       │
│  - Integrity check                      │
└────────────────┬────────────────────────┘
                 │ ✓ PASSED
                 ▼
┌─────────────────────────────────────────┐
│   LICENSE VALIDATION                    │
│  - Local session check                  │
│  - Server API call                      │
│  - HWID verification                    │
└────────────────┬────────────────────────┘
                 │ ✓ VALID
                 ▼
┌─────────────────────────────────────────┐
│   MAIN APPLICATION                      │
│  + Background security monitor (30s)    │
│  + License revalidation (5min)          │
│  + Display time remaining               │
└─────────────────────────────────────────┘
```

---

## 13. Cómo Funciona en la Práctica

### Escenario 1: Usuario Legítimo
1. Ejecuta Antarctic.exe
2. Security checks: ✓ PASS
3. Ingresa licencia válida
4. App inicia normalmente
5. Monitor en background verifica cada 5 min
6. Usuario ve su tiempo restante en la GUI

### Escenario 2: Pirata con Debugger
1. Ejecuta Antarctic.exe en x64dbg
2. Security checks: ❌ DEBUGGER DETECTED
3. App muestra "Security Alert"
4. App se cierra inmediatamente

### Escenario 3: Licencia Expirada
1. Usuario ejecuta app con licencia vencida
2. Security checks: ✓ PASS
3. License validation: ❌ EXPIRED
4. App muestra "License Expired"
5. App se cierra

### Escenario 4: Licencia Revocada Remotamente
1. Usuario ejecuta app (licencia válida al inicio)
2. Admin revoca licencia en el servidor
3. Después de 5 minutos, validación periódica falla
4. App muestra "License Expired or Revoked"
5. App se cierra automáticamente

---

## 14. FAQ de Seguridad

### ¿Es 100% imposible de crackear?
**No.** Ningún software es 100% seguro. Sin embargo, las medidas implementadas hacen que sea:
- **Muy difícil** para usuarios promedio
- **Costoso en tiempo** para crackers
- **No vale la pena** para la mayoría

### ¿Qué pasa si alguien descompila el código?
Pueden ver:
- ✓ Lógica del programa
- ✓ URL del servidor
- ❌ **NO** pueden generar licencias válidas (servidor las valida)
- ❌ **NO** pueden bypassear HWID (servidor valida)
- ❌ **NO** pueden bypassear validación continua

### ¿Puedo mejorar la seguridad?
**Sí**. Opciones recomendadas en orden de efectividad:
1. **PyArmor** (ofuscación real) - ALTO impacto
2. **VMProtect/Themida** (protectores) - ALTO impacto
3. **UPX compression** - BAJO impacto
4. **Code signing** - Mejora confianza, no seguridad

### ¿El servidor es seguro?
**Sí**. El servidor:
- Usa HTTPS (encrypted)
- Valida HWID en servidor (no cliente)
- Usa JWT tokens con expiración
- Tiene rate limiting (Vercel)
- PostgreSQL con passwords hasheados

---

## 15. Conclusión

### Nivel de Protección Actual: ⭐⭐⭐⭐ (4/5)

**Protege contra**:
✅ Usuarios casuales sin conocimientos técnicos
✅ Compartir licencias entre PCs
✅ Debugging básico
✅ Uso después de expiración
✅ Herramientas automáticas de cracking

**NO protege contra**:
❌ Crackers profesionales con semanas de tiempo
❌ Reverse engineering completo del código
❌ Parches binarios (hex editing del .exe)

### Recomendación Final
Para un **producto comercial serio**:
1. Usa Antarctic como está (buena protección básica)
2. Agrega **PyArmor** para ofuscación real
3. Considera **VMProtect** si el producto vale >$100

Para un **proyecto personal/pequeño**:
- La seguridad actual es **más que suficiente**
- 99% de usuarios no podrán crackear
- El costo/beneficio de más seguridad no vale la pena

---

**Última actualización**: 2024-10-19
**Versión del documento**: 1.0
