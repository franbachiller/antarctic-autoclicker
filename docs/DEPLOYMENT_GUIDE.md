# Guía de Despliegue Rápido - Antarctic Auth Server

## 🎯 Guía paso a paso para desplegar en 10 minutos

### 1️⃣ Preparar Cuenta de Vercel (2 min)

1. Ve a [vercel.com](https://vercel.com)
2. Regístrate con GitHub (gratis)
3. Verifica tu email

### 2️⃣ Instalar Vercel CLI (1 min)

Abre terminal en la carpeta `auth-server`:

```bash
cd auth-server
npm install -g vercel
```

### 3️⃣ Login en Vercel (1 min)

```bash
vercel login
```

Sigue las instrucciones para autenticarte.

### 4️⃣ Crear Base de Datos PostgreSQL (2 min)

1. Ve a [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "Storage" en el menú
3. Click "Create Database"
4. Selecciona "Postgres"
5. Ponle un nombre: `antarctic-db`
6. Click "Create"
7. **¡IMPORTANTE!** Copia el `POSTGRES_URL` que aparece

### 5️⃣ Desplegar Proyecto (2 min)

```bash
# Inicializar proyecto
vercel

# Responde a las preguntas:
# - Set up and deploy? Y
# - Which scope? (selecciona tu cuenta)
# - Link to existing project? N
# - Project name? antarctic-auth
# - Directory? ./
# - Override settings? N
```

### 6️⃣ Configurar Variables de Entorno (2 min)

En el Dashboard de Vercel:

1. Ve a tu proyecto → Settings → Environment Variables
2. Agrega estas 3 variables:

```
POSTGRES_URL = (pega la URL que copiaste antes)
JWT_SECRET = antarctic_super_secret_key_2025_change_this_in_production
ADMIN_KEY = admin_key_cambiala_por_algo_seguro
```

3. Click "Save" para cada una

### 7️⃣ Inicializar Base de Datos (1 min)

1. En Vercel Dashboard → Storage → Tu base de datos
2. Click en "Query" o "Data"
3. Copia y pega el contenido de `schema.sql`
4. Click "Run Query"

### 8️⃣ Redesplegar con Variables (1 min)

```bash
vercel --prod
```

### 9️⃣ ¡Listo! Tu servidor está online

Tu URL será algo como: `https://antarctic-auth.vercel.app`

## 🧪 Probar que Funciona

### Probar Panel de Admin

1. Abre: `https://tu-proyecto.vercel.app/admin.html`
2. Ingresa tu ADMIN_KEY
3. Crea una licencia de prueba

### Probar API

```bash
# Crear licencia (reemplaza ADMIN_KEY y URL)
curl -X POST https://tu-proyecto.vercel.app/api/admin/create-license \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: tu_admin_key" \
  -d '{"licenseType":"month","count":1}'
```

## 🔧 Actualizar Antarctic.py

Edita `antarctic.py` línea ~1143:

```python
SERVER_URL = "https://tu-proyecto.vercel.app"
```

## 📦 Compilar Ejecutable

```bash
# Instalar dependencias adicionales
pip install requests

# Compilar
pyinstaller --onefile --noconsole --icon=icon.ico antarctic.py
```

El ejecutable estará en `dist/Antarctic.exe`

## ✅ Checklist Final

- [ ] Servidor desplegado en Vercel
- [ ] Base de datos PostgreSQL creada e inicializada
- [ ] Variables de entorno configuradas
- [ ] Panel de admin funciona
- [ ] Licencia de prueba creada exitosamente
- [ ] `antarctic.py` actualizado con URL correcta
- [ ] Aplicación compilada

## 🎉 ¡A Distribuir!

Ahora puedes:
1. Crear licencias desde el panel de admin
2. Distribuir tu aplicación
3. Los usuarios activarán con las licencias que generes
4. Las licencias expiran automáticamente según el tipo

## 📞 Soporte Común

### ❌ Error: "Cannot connect to server"
**Solución:** Verifica que la URL en `antarctic.py` sea correcta (sin / al final)

### ❌ Error: "Database connection failed"
**Solución:** Verifica que ejecutaste `schema.sql` en la base de datos

### ❌ Error: "Invalid admin key"
**Solución:** Verifica que `ADMIN_KEY` en Vercel coincida con lo que usas

### ❌ Error: "Module 'requests' not found"
**Solución:** `pip install requests` antes de compilar

## 🔐 Seguridad

**IMPORTANTE:** Cambia estos valores AHORA:

```
JWT_SECRET = (genera uno aleatorio de 32+ caracteres)
ADMIN_KEY = (genera una clave fuerte, guárdala segura)
```

Para generar claves seguras:
```bash
# En terminal
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 💰 Costos

**Plan Gratuito de Vercel:**
- ✅ Hosting: GRATIS
- ✅ PostgreSQL: GRATIS (256MB, suficiente para miles de licencias)
- ✅ Bandwidth: 100GB/mes GRATIS
- ✅ Funciones: Ilimitadas GRATIS

**Escalabilidad:** El plan gratuito soporta fácilmente 1000-5000 usuarios activos.

---

**¿Necesitas ayuda?** Revisa el `README.md` completo para más detalles.
