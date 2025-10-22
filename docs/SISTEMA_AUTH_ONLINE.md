# ANTARCTIC - SISTEMA DE AUTENTICACION ONLINE

## RESUMEN EJECUTIVO

El sistema de autenticacion online de Antarctic esta **100% FUNCIONAL** y desplegado en produccion.

### Estado del Sistema
- ✅ Servidor desplegado en Vercel
- ✅ Base de datos Supabase configurada
- ✅ APIs de autenticacion funcionando
- ✅ Cliente Python integrado
- ✅ Ejecutable compilado con PyInstaller
- ✅ Herramientas de gestion de licencias

---

## CONFIGURACION ACTUAL

### URL del Servidor (Produccion)
```
https://antarctic-auth-ml5lf7xqr-frans-projects-593301de.vercel.app
```

### Credenciales de Administrador
```
Admin Key: admin_antarctic_2025
```

---

## COMPONENTES DEL SISTEMA

### 1. Servidor de Autenticacion (Vercel)
**Ubicacion:** `auth-server/`

**APIs Disponibles:**
- `POST /api/activate` - Activar una licencia
- `POST /api/validate` - Validar una sesion
- `POST /api/admin/create-license` - Crear licencias (requiere admin key)
- `GET /api/admin/list-licenses` - Listar todas las licencias (requiere admin key)
- `POST /api/admin/ban-license` - Banear una licencia (requiere admin key)
- `GET /api/test-db` - Test de conexion a la base de datos

**Despliegue:**
```bash
cd auth-server
vercel deploy --prod
```

### 2. Cliente de Autenticacion (Python)
**Archivo:** `auth_client.py`

**Funciones principales:**
- `activate(license_key)` - Activar licencia
- `validate()` - Validar sesion actual
- `is_activated()` - Verificar estado de activacion
- `deactivate()` - Desactivar sesion local
- `get_hwid()` - Obtener hardware ID unico del dispositivo

### 3. Aplicacion Principal
**Archivo:** `antarctic.py`

La aplicacion ya esta integrada con el sistema de autenticacion online. Al ejecutarse:
1. Verifica si hay una sesion activa
2. Si no hay sesion, muestra ventana de activacion
3. Solicita la licencia al usuario
4. Activa la licencia con el servidor
5. Guarda la sesion localmente
6. Valida periodicamente con el servidor

### 4. Herramientas

#### Crear Licencias
**Archivo:** `tools/create_licenses.py`

```bash
python tools/create_licenses.py
```

Permite:
- Crear licencias de diferentes tipos (semana, mes, 3 meses, 6 meses, año, lifetime)
- Listar todas las licencias
- Guardar licencias en archivo de texto

#### Probar Autenticacion
**Archivo:** `test_auth.py`

```bash
# Prueba interactiva
python test_auth.py

# Prueba rapida
python test_auth.py quick <SERVER_URL> <LICENSE_KEY>
```

---

## TIPOS DE LICENCIAS

| Tipo | Duracion | Codigo |
|------|----------|--------|
| Semana | 7 dias | `week` |
| Mes | 30 dias | `month` |
| 3 Meses | 90 dias | `3months` |
| 6 Meses | 180 dias | `6months` |
| Año | 365 dias | `year` |
| Lifetime | 100 años | `lifetime` |

---

## FLUJO DE AUTENTICACION

### Primera Activacion
1. Usuario ejecuta `Antarctic.exe`
2. Sistema detecta que no hay licencia
3. Muestra ventana de activacion
4. Usuario ingresa su clave de licencia (formato: `ANTARCTIC-XXXX-XXXX-XXXX`)
5. Sistema envia request a `/api/activate` con:
   - `licenseKey`: La clave ingresada
   - `hwid`: Hardware ID unico del dispositivo
6. Servidor valida:
   - Licencia existe
   - Licencia no esta baneada
   - Licencia no ha expirado
   - Licencia no esta activada en otro dispositivo (o coincide con el HWID actual)
7. Si todo OK:
   - Servidor genera token de sesion (JWT, valido 24h)
   - Servidor bindea la licencia al HWID del dispositivo
   - Cliente guarda el token localmente (encriptado con XOR)
   - Usuario puede usar la aplicacion

### Validaciones Posteriores
1. Al iniciar `Antarctic.exe`:
   - Sistema carga sesion guardada
   - Valida con servidor via `/api/validate`
   - Si token valido: Acceso permitido
   - Si token invalido: Solicita nueva activacion

2. Modo offline con periodo de gracia:
   - Si no hay conexion al servidor
   - Sistema permite 1 hora de uso antes de expirar el token
   - Cuando se recupere conexion, se vuelve a validar

---

## SEGURIDAD

### Hardware ID (HWID)
- Generado combinando:
  - Nombre de la maquina
  - Procesador
  - Sistema operativo
  - Direccion MAC
- Hasheado con SHA256
- Bindea una licencia a un dispositivo especifico
- Previene que una licencia se use en multiples dispositivos

### Token de Sesion
- JWT firmado con secret
- Expira en 24 horas
- Contiene: licenseKey, hwid, timestamp
- Almacenado localmente con encriptacion XOR

### Admin Key
- Requerida para crear, listar y banear licencias
- Configurada en variables de entorno de Vercel
- No accesible desde el cliente

---

## COMO CREAR Y DISTRIBUIR LICENCIAS

### Paso 1: Crear Licencias
```bash
python tools/create_licenses.py
```

Selecciona:
- Tipo de licencia (week, month, etc.)
- Cantidad (1-100)
- Notas opcionales

Las licencias se guardan automaticamente en un archivo `licenses_YYYYMMDD_HHMMSS.txt`

### Paso 2: Distribuir a Clientes
Envia al cliente SOLO la clave de licencia:
```
ANTARCTIC-A418-12BF-634D
```

### Paso 3: Cliente Activa
1. Cliente ejecuta `Antarctic.exe`
2. Ingresa la clave
3. Sistema se activa automaticamente
4. Cliente puede usar la aplicacion

---

## COMPILACION DEL EJECUTABLE

### Requisitos
- Python 3.13
- PyInstaller
- Todas las dependencias instaladas (`pip install -r requirements.txt`)

### Compilar
```bash
compile.bat
```

o

```bash
pyinstaller --onefile --windowed --icon=icon.ico \
  --add-data "icon.ico;." \
  --add-data "logo.png;." \
  --add-data "logo_compact.png;." \
  --hidden-import=requests \
  --hidden-import=urllib3 \
  --hidden-import=certifi \
  --hidden-import=charset_normalizer \
  --name Antarctic antarctic.py
```

### Resultado
- Ejecutable: `dist/Antarctic.exe`
- Tamaño: ~29.5 MB
- No requiere Python instalado
- Todo autocontenido

---

## PRUEBAS REALIZADAS

### Test de Base de Datos
```bash
curl https://antarctic-auth-ml5lf7xqr-frans-projects-593301de.vercel.app/api/test-db
```
✅ Resultado: Conexion exitosa

### Test de Creacion de Licencia
```bash
curl -X POST https://antarctic-auth-ml5lf7xqr-frans-projects-593301de.vercel.app/api/admin/create-license \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: admin_antarctic_2025" \
  -d '{"licenseType":"month","count":1,"notes":"Test"}'
```
✅ Resultado: Licencia creada exitosamente

### Test de Activacion
```bash
python test_auth.py quick \
  "https://antarctic-auth-ml5lf7xqr-frans-projects-593301de.vercel.app" \
  "ANTARCTIC-E8A1-669D-4D68"
```
✅ Resultado: Activacion exitosa, validacion OK, estado ACTIVADO

---

## TROUBLESHOOTING

### Problema: Licencia ya activada en otro dispositivo
**Causa:** La licencia esta bindeada a otro HWID

**Solucion:**
1. Acceder a la base de datos Supabase
2. Buscar la licencia por `license_key`
3. Limpiar el campo `hwid` (ponerlo en NULL)
4. Intentar activar nuevamente

### Problema: Error de conexion al servidor
**Causa:** No hay internet o servidor caido

**Solucion:**
- Verificar conexion a internet
- Verificar que el servidor este activo: `curl https://antarctic-auth-ml5lf7xqr-frans-projects-593301de.vercel.app/api/test-db`
- Modo offline: El sistema permite 1 hora de uso sin conexion

### Problema: Token expirado
**Causa:** Han pasado mas de 24 horas desde la ultima validacion

**Solucion:**
- Sistema automaticamente valida al iniciar
- Si hay internet, se renueva el token
- Si no hay internet, se usa periodo de gracia

---

## VARIABLES DE ENTORNO (VERCEL)

Para configurar el servidor, necesitas estas variables en Vercel:

```
SUPABASE_URL=<tu-supabase-url>
SUPABASE_ANON_KEY=<tu-supabase-anon-key>
JWT_SECRET=<secret-para-firmar-tokens>
ADMIN_KEY=admin_antarctic_2025
```

---

## PROXIMOS PASOS RECOMENDADOS

### Mejoras de Seguridad
- [ ] Cambiar ADMIN_KEY por una clave mas segura
- [ ] Implementar rate limiting en las APIs
- [ ] Agregar logs de auditoria mas detallados

### Mejoras de Funcionalidad
- [ ] Panel web de administracion (admin.html)
- [ ] Notificaciones cuando una licencia esta por expirar
- [ ] Sistema de renovacion automatica
- [ ] API para transferir licencias entre dispositivos

### Optimizaciones
- [ ] Cache de validaciones para reducir requests
- [ ] Compresion del token guardado
- [ ] Limpieza automatica de sesiones expiradas

---

## CONTACTO Y SOPORTE

Para cualquier problema o pregunta sobre el sistema de autenticacion:
1. Revisar este documento primero
2. Verificar los logs del servidor en Vercel
3. Probar con `test_auth.py` para diagnostico
4. Revisar la base de datos en Supabase

---

## LICENCIAS DE PRUEBA GENERADAS

Durante el desarrollo se crearon estas licencias de prueba:

1. `ANTARCTIC-A418-12BF-634D` - Activada en HWID de prueba
2. `ANTARCTIC-E8A1-669D-4D68` - Activada en HWID local

**Nota:** Estas son licencias de prueba. Para produccion, generar nuevas con `tools/create_licenses.py`

---

**Fecha de este documento:** 18 de octubre de 2025
**Version del sistema:** 1.0.0
**Estado:** PRODUCCION - COMPLETAMENTE FUNCIONAL
