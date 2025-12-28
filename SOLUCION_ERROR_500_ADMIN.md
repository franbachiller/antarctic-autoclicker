# SOLUCIÓN: Error 500 en Panel de Admin

## El Problema

El panel de admin muestra error 500 porque faltan las variables de entorno de Supabase en Vercel.

**Error:**
```
Failed to load resource: the server responded with a status of 500 ()
```

## Causa

El código del panel intenta conectarse a Supabase, pero las variables `SUPABASE_URL` y `SUPABASE_ANON_KEY` no están configuradas en Vercel.

## Solución Rápida

### Paso 1: Configurar Variables de Entorno en Vercel

1. Ve a tu proyecto en Vercel: https://vercel.com/dashboard
2. Selecciona `antarctic-autoclicker`
3. Ve a **Settings** → **Environment Variables**
4. Agrega estas variables:

**Variables necesarias:**

```
ADMIN_KEY = G4e3U0r9
SUPABASE_URL = tu_url_de_supabase
SUPABASE_ANON_KEY = tu_clave_anonima_de_supabase
```

### Paso 2: Obtener Credenciales de Supabase

Si no tienes un proyecto de Supabase:

1. Ve a https://supabase.com/
2. Crea una cuenta / inicia sesión
3. Crea un nuevo proyecto
4. Ve a **Settings** → **API**
5. Copia:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** key → `SUPABASE_ANON_KEY`

### Paso 3: Crear Tabla de Licencias

En Supabase, ejecuta este SQL:

```sql
-- Crear tabla de licencias
CREATE TABLE licenses (
  id SERIAL PRIMARY KEY,
  license_key VARCHAR(19) UNIQUE NOT NULL,
  license_type VARCHAR(20) NOT NULL,
  hwid VARCHAR(64),
  status VARCHAR(20) DEFAULT 'inactive',
  is_banned BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  activated_at TIMESTAMP,
  expires_at TIMESTAMP,
  last_used TIMESTAMP,
  usage_count INTEGER DEFAULT 0,
  notes TEXT
);

-- Crear índices
CREATE INDEX idx_license_key ON licenses(license_key);
CREATE INDEX idx_hwid ON licenses(hwid);
CREATE INDEX idx_status ON licenses(status);
CREATE INDEX idx_is_banned ON licenses(is_banned);

-- Habilitar Row Level Security (RLS)
ALTER TABLE licenses ENABLE ROW LEVEL SECURITY;

-- Política para permitir todas las operaciones (ajustar según necesites)
CREATE POLICY "Allow all operations" ON licenses
  FOR ALL
  USING (true)
  WITH CHECK (true);
```

### Paso 4: Redeploy en Vercel

Después de configurar las variables:

1. Ve a **Deployments** en Vercel
2. Haz click en los tres puntos (⋯) del último deployment
3. Selecciona **Redeploy**
4. Espera a que termine el deployment

### Paso 5: Verificar

1. Abre el panel de admin: https://antarctic-autoclicker.vercel.app/admin-panel/admin.html
2. Ingresa la contraseña: `G4e3U0r9`
3. Debería funcionar correctamente

## Alternativa: Modo Sin Base de Datos

Si no quieres usar Supabase ahora mismo, puedo modificar el código para que funcione sin base de datos (solo para testing).

¿Quieres que:
1. Te ayude a configurar Supabase completo?
2. Modifique el código para que funcione sin base de datos temporalmente?
