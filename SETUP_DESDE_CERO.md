# 🚀 ANTARCTIC - SETUP DESDE CERO (GUÍA DEFINITIVA)

## ⏱️ Tiempo estimado: 15 minutos

---

## 📋 PASO 1: LIMPIAR TODO (5 min)

### 1.1 Eliminar proyecto de Vercel
1. Ve a https://vercel.com/dashboard
2. Encuentra tu proyecto `antarctic-autoclicker`
3. Settings → General → Delete Project
4. Confirma la eliminación

### 1.2 Eliminar proyecto de Supabase
1. Ve a https://supabase.com/dashboard
2. Encuentra tu proyecto
3. Settings → General → Delete Project
4. Confirma la eliminación

### 1.3 Limpiar repositorio local
```bash
# Eliminar carpeta .vercel si existe
rm -rf .vercel

# Verificar que node_modules NO esté en git
git status
# Si aparece node_modules, ejecuta:
git rm -r --cached node_modules
git commit -m "Remove node_modules from git"
```

---

## 🗄️ PASO 2: CREAR SUPABASE NUEVO (3 min)

### 2.1 Crear proyecto
1. Ve a https://supabase.com/dashboard
2. Click "New Project"
3. Completa:
   - **Name:** `antarctic-licenses`
   - **Database Password:** Crea una contraseña fuerte (guárdala)
   - **Region:** Selecciona la más cercana
   - **Plan:** Free
4. Click "Create new project" (espera 1-2 min)

### 2.2 Crear tabla de licencias
1. En el menú lateral, click "SQL Editor"
2. Click "New query"
3. Pega este SQL:

```sql
CREATE TABLE licenses (
  id BIGSERIAL PRIMARY KEY,
  license_key VARCHAR(255) UNIQUE NOT NULL,
  license_type VARCHAR(50) NOT NULL DEFAULT 'standard',
  status VARCHAR(20) NOT NULL DEFAULT 'active',
  hwid VARCHAR(255),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMPTZ,
  last_used TIMESTAMPTZ,
  usage_count INTEGER NOT NULL DEFAULT 0,
  is_banned BOOLEAN NOT NULL DEFAULT false,
  notes TEXT
);

-- Índices para performance
CREATE INDEX idx_license_key ON licenses(license_key);
CREATE INDEX idx_status ON licenses(status);
CREATE INDEX idx_hwid ON licenses(hwid);

-- Insertar una licencia de prueba
INSERT INTO licenses (license_key, license_type, expires_at, notes)
VALUES (
  'TEST-' || substring(md5(random()::text) from 1 for 8) || '-' || substring(md5(random()::text) from 1 for 8),
  'trial',
  NOW() + INTERVAL '30 days',
  'Licencia de prueba creada automáticamente'
);
```

4. Click "Run" o presiona `Ctrl+Enter`
5. Deberías ver "Success. No rows returned"

### 2.3 Obtener credenciales
1. En el menú lateral, click "Settings" → "API"
2. Copia y guarda:
   - **Project URL** (ejemplo: `https://xxxxx.supabase.co`)
   - **anon public key** (empieza con `eyJhbGc...`)

---

## ☁️ PASO 3: DESPLEGAR EN VERCEL (5 min)

### 3.1 Crear nuevo proyecto en Vercel
1. Ve a https://vercel.com/dashboard
2. Click "Add New..." → "Project"
3. Importa tu repositorio de GitHub `antarctic-autoclicker`
4. **NO HAGAS DEPLOY TODAVÍA**

### 3.2 Configurar variables de entorno
1. En la pantalla de configuración, busca "Environment Variables"
2. Agrega estas 3 variables:

```
ADMIN_KEY = MiPasswordSuperSegura123
SUPABASE_URL = https://xxxxx.supabase.co
SUPABASE_ANON_KEY = eyJhbGc...tu-key-aqui...
```

**IMPORTANTE:** 
- Cambia `MiPasswordSuperSegura123` por una contraseña que TÚ elijas
- Pega tu `SUPABASE_URL` real
- Pega tu `SUPABASE_ANON_KEY` real

3. Click "Deploy"
4. Espera 2-3 minutos

### 3.3 Obtener URL de producción
1. Una vez desplegado, verás tu URL (ejemplo: `https://antarctic-autoclicker.vercel.app`)
2. Cópiala y guárdala

---

## ✅ PASO 4: PROBAR QUE FUNCIONA (2 min)

### 4.1 Acceder al panel
1. Ve a tu URL: `https://antarctic-autoclicker.vercel.app`
2. Deberías ver la pantalla de login

### 4.2 Login
1. Ingresa la contraseña que configuraste en `ADMIN_KEY`
2. Click "LOGIN"
3. **¡Deberías entrar al panel!** 🎉

### 4.3 Verificar datos
Deberías ver:
- **Total licenses:** 1
- **Active:** 1
- **Expired:** 0
- **Banned:** 0
- Una licencia de prueba en la tabla

---

## 🎯 PASO 5: CREAR LICENCIAS (OPCIONAL)

### 5.1 Desde el panel admin
1. En el panel, ve a la sección "Generate Licenses"
2. Selecciona:
   - **Type:** standard o trial
   - **Count:** 1-100
   - **Notes:** (opcional)
3. Click "GENERATE LICENSE(S)"
4. Las licencias aparecerán en la lista

### 5.2 Exportar licencias
1. Click "EXPORT TO FILE"
2. Se descargará un archivo `.txt` con todas las licencias generadas

---

## 🔧 TROUBLESHOOTING

### Problema: "Invalid admin key"
**Solución:**
1. Ve a Vercel Dashboard → Tu proyecto → Settings → Environment Variables
2. Verifica que `ADMIN_KEY` esté configurada correctamente
3. Si la cambias, haz un Redeploy:
   - Deployments → Click en los 3 puntos del último → Redeploy

### Problema: "Connection error"
**Solución:**
1. Abre la consola del navegador (F12)
2. Mira los errores
3. Verifica que la URL de Vercel sea correcta

### Problema: No aparecen licencias
**Solución:**
1. Ve a Supabase → SQL Editor
2. Ejecuta: `SELECT * FROM licenses;`
3. Verifica que haya datos
4. Si no hay, ejecuta el INSERT del paso 2.2 nuevamente

### Problema: Error 500 en las APIs
**Solución:**
1. Ve a Vercel → Tu proyecto → Deployments
2. Click en el último deployment
3. Click en "Functions" → Click en la función que falla
4. Mira los logs para ver el error exacto
5. Verifica que las variables de entorno estén configuradas

---

## 📝 RESUMEN DE CREDENCIALES

Guarda esto en un lugar seguro:

```
=== ANTARCTIC LICENSE SYSTEM ===

ADMIN PANEL:
URL: https://antarctic-autoclicker.vercel.app
Admin Key: [TU_PASSWORD_AQUI]

SUPABASE:
URL: https://xxxxx.supabase.co
Anon Key: eyJhbGc...
Database Password: [TU_PASSWORD_DB_AQUI]

VERCEL:
Project: antarctic-autoclicker
GitHub Repo: Narfbach/antarctic-autoclicker
```

---

## 🎉 ¡LISTO!

Tu sistema de licencias está funcionando. Ahora puedes:
- ✅ Crear licencias desde el panel
- ✅ Ver estadísticas en tiempo real
- ✅ Banear/eliminar licencias
- ✅ Exportar licencias a archivo
- ✅ Buscar licencias específicas

---

## 📞 SOPORTE

Si algo no funciona:
1. Revisa la sección de Troubleshooting
2. Verifica los logs en Vercel
3. Verifica la consola del navegador (F12)
4. Asegúrate de que todas las variables de entorno estén configuradas

---

**Creado:** 2025-10-23
**Versión:** 1.0
**Sistema:** Antarctic License Management

