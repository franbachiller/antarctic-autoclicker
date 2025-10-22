# 🛠️ Comandos Útiles - Antarctic License System

## 📦 Instalación Inicial

```bash
# Instalar dependencias Python
pip install -r requirements.txt

# Instalar Vercel CLI
npm install -g vercel

# Instalar dependencias del servidor
cd auth-server
npm install
cd ..
```

## 🚀 Despliegue

```bash
# Login en Vercel
vercel login

# Desplegar a producción
cd auth-server
vercel --prod

# Ver logs en tiempo real
vercel logs
```

## 🧪 Testing

```bash
# Test interactivo del sistema de auth
python test_auth.py

# Test rápido con una licencia
python test_auth.py quick https://tu-app.vercel.app ANTARCTIC-XXXX-XXXX-XXXX

# Test local del servidor (requiere .env configurado)
cd auth-server
vercel dev
# Servidor en http://localhost:3000
```

## 🔨 Compilación

```bash
# Compilar Antarctic.exe (versión básica)
pyinstaller --onefile --noconsole --icon=icon.ico antarctic.py

# Compilar con datos incluidos (logos, etc)
pyinstaller --onefile --noconsole ^
    --icon=icon.ico ^
    --add-data "logo.png;." ^
    --add-data "logo_compact.png;." ^
    --add-data "icon.ico;." ^
    --add-data "auth_client.py;." ^
    --name Antarctic ^
    antarctic.py

# Limpiar archivos de compilación
powershell -Command "Remove-Item -Recurse -Force build; Remove-Item Antarctic.spec; Write-Host 'Cleaned'"
```

## 🗄️ Base de Datos

```bash
# Conectar a PostgreSQL de Vercel
psql $POSTGRES_URL

# Queries útiles:

# Ver todas las licencias
SELECT license_key, license_type, status, created_at, expires_at
FROM licenses
ORDER BY created_at DESC;

# Ver licencias activas
SELECT * FROM licenses WHERE status = 'active';

# Contar licencias por tipo
SELECT license_type, COUNT(*) as count
FROM licenses
GROUP BY license_type;

# Ver últimas activaciones
SELECT license_key, action, created_at
FROM audit_log
WHERE action = 'ACTIVATION_SUCCESS'
ORDER BY created_at DESC
LIMIT 10;

# Resetear HWID de una licencia (permitir re-activación)
UPDATE licenses
SET hwid = NULL
WHERE license_key = 'ANTARCTIC-XXXX-XXXX-XXXX';

# Extender expiración de una licencia
UPDATE licenses
SET expires_at = expires_at + INTERVAL '30 days'
WHERE license_key = 'ANTARCTIC-XXXX-XXXX-XXXX';

# Marcar licencias expiradas (se hace automáticamente)
UPDATE licenses
SET status = 'expired'
WHERE expires_at < CURRENT_TIMESTAMP
AND status = 'active';

# Limpiar sesiones expiradas
DELETE FROM sessions
WHERE expires_at < CURRENT_TIMESTAMP;

# Ver estadísticas
SELECT
    COUNT(*) as total,
    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
    SUM(CASE WHEN status = 'expired' THEN 1 ELSE 0 END) as expired,
    SUM(CASE WHEN status = 'banned' THEN 1 ELSE 0 END) as banned
FROM licenses;
```

## 🌐 API Calls con curl

```bash
# Variables (reemplazar con tus valores)
SERVER_URL="https://tu-app.vercel.app"
ADMIN_KEY="tu-admin-key"
LICENSE_KEY="ANTARCTIC-XXXX-XXXX-XXXX"

# Crear licencia
curl -X POST $SERVER_URL/api/admin/create-license \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: $ADMIN_KEY" \
  -d '{"licenseType":"month","count":1,"notes":"Test license"}'

# Crear múltiples licencias
curl -X POST $SERVER_URL/api/admin/create-license \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: $ADMIN_KEY" \
  -d '{"licenseType":"month","count":10,"notes":"Batch 1"}'

# Listar todas las licencias
curl $SERVER_URL/api/admin/list-licenses \
  -H "X-Admin-Key: $ADMIN_KEY"

# Banear licencia
curl -X POST $SERVER_URL/api/admin/ban-license \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: $ADMIN_KEY" \
  -d "{\"licenseKey\":\"$LICENSE_KEY\"}"

# Activar licencia (como cliente)
curl -X POST $SERVER_URL/api/activate \
  -H "Content-Type: application/json" \
  -d "{\"licenseKey\":\"$LICENSE_KEY\",\"hwid\":\"test-hwid-12345\"}"

# Validar sesión
curl -X POST $SERVER_URL/api/validate \
  -H "Content-Type: application/json" \
  -d "{\"sessionToken\":\"tu-jwt-token\",\"hwid\":\"test-hwid-12345\"}"
```

## 🔐 Generar Claves Seguras

```bash
# Generar JWT_SECRET
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generar ADMIN_KEY
python -c "import secrets; print(secrets.token_urlsafe(24))"

# Generar ambos
python -c "import secrets; print(f'JWT_SECRET={secrets.token_urlsafe(32)}'); print(f'ADMIN_KEY={secrets.token_urlsafe(24)}')"
```

## 📊 Vercel CLI

```bash
# Ver proyectos
vercel list

# Ver información del proyecto
vercel inspect

# Ver variables de entorno
vercel env ls

# Agregar variable de entorno
vercel env add VARIABLE_NAME

# Remover variable de entorno
vercel env rm VARIABLE_NAME

# Ver logs (últimas 100 líneas)
vercel logs

# Ver logs en tiempo real
vercel logs --follow

# Descargar código de producción
vercel pull

# Promover deployment a producción
vercel promote [deployment-url]

# Alias personalizado
vercel alias set deployment-url tu-dominio.com
```

## 🧹 Limpieza y Mantenimiento

```bash
# Limpiar archivos de compilación Python
Remove-Item -Recurse -Force build, dist, __pycache__
Remove-Item *.spec

# Limpiar sesiones locales de prueba
Remove-Item antarctic_session.dat

# Limpiar node_modules (para reinstalar)
cd auth-server
Remove-Item -Recurse -Force node_modules
npm install
cd ..

# Reset completo (cuidado!)
Remove-Item antarctic_profiles.json
Remove-Item antarctic.lic
Remove-Item antarctic_session.dat
```

## 📝 Git (si usas control de versiones)

```bash
# Inicializar repo
git init
git add .
git commit -m "Initial commit - Antarctic License System"

# NO subas estos archivos (ya están en .gitignore):
# - .env
# - node_modules/
# - *.log
# - antarctic_session.dat
# - antarctic.lic
```

## 🔄 Actualización del Sistema

```bash
# Actualizar servidor
cd auth-server
vercel --prod

# Actualizar cliente (recompilar)
pyinstaller --onefile --noconsole --icon=icon.ico antarctic.py

# Actualizar dependencias
pip install --upgrade -r requirements.txt
cd auth-server
npm update
```

## 📦 Distribución

```bash
# Crear carpeta de distribución
mkdir Release
copy dist\Antarctic.exe Release\
copy README.md Release\
copy LICENSE.txt Release\  # Si tienes uno

# Comprimir para distribución
# En PowerShell:
Compress-Archive -Path Release\* -DestinationPath Antarctic-v1.0.zip
```

## 🐛 Debugging

```bash
# Ver logs detallados de Python
python antarctic.py

# Ejecutar con debugging
python -v antarctic.py

# Test de conexión al servidor
python -c "import requests; print(requests.get('https://tu-app.vercel.app').status_code)"

# Ver HWID de tu máquina
python -c "from auth_client import AuthClient; print(AuthClient().get_hwid())"
```

## 📊 Monitoreo

```bash
# Vercel Analytics (navegador)
# https://vercel.com/dashboard → Tu proyecto → Analytics

# Ver uso de base de datos
# https://vercel.com/dashboard → Storage → Tu DB → Usage

# Health check de API
curl https://tu-app.vercel.app/api/admin/list-licenses -I
```

## 🎯 Scripts de Batch Útiles

### Crear múltiples licencias

```python
# create_bulk_licenses.py
import requests

SERVER_URL = "https://tu-app.vercel.app"
ADMIN_KEY = "tu-admin-key"

# Crear 50 licencias de 1 mes
response = requests.post(
    f"{SERVER_URL}/api/admin/create-license",
    headers={"X-Admin-Key": ADMIN_KEY},
    json={"licenseType": "month", "count": 50, "notes": "Batch sale"}
)

licenses = response.json()['data']['licenses']
with open('licenses.txt', 'w') as f:
    for lic in licenses:
        f.write(f"{lic['key']}\n")

print(f"✓ Creadas {len(licenses)} licencias → licenses.txt")
```

### Exportar todas las licencias

```python
# export_licenses.py
import requests
import csv

SERVER_URL = "https://tu-app.vercel.app"
ADMIN_KEY = "tu-admin-key"

response = requests.get(
    f"{SERVER_URL}/api/admin/list-licenses",
    headers={"X-Admin-Key": ADMIN_KEY}
)

licenses = response.json()['data']['licenses']

with open('licenses_export.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['key', 'type', 'status', 'createdAt', 'expiresAt', 'usageCount'])
    writer.writeheader()
    writer.writerows(licenses)

print(f"✓ Exportadas {len(licenses)} licencias → licenses_export.csv")
```

---

## 💡 Tips

1. **Guarda tu ADMIN_KEY seguro** - Necesario para todas las operaciones
2. **Backup regular** - Vercel hace automático, pero exporta licencias periódicamente
3. **Monitorea uso** - Revisa analytics para detectar abusos
4. **Rate limiting** - Vercel lo hace automático, pero puedes agregar más restricciones
5. **Logs** - Revisa audit_log en la DB para ver toda la actividad

---

**Cheat sheet guardado!** Marca este archivo para referencia rápida.
