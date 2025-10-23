# 🔧 Agregar Campo session_token a la Base de Datos

## ⚠️ IMPORTANTE: Ejecuta esto en Supabase

Para que el programa funcione correctamente, necesitas agregar el campo `session_token` a la tabla de licencias.

## 📝 Pasos:

### 1. Ir a Supabase
1. Abre [https://supabase.com](https://supabase.com)
2. Selecciona tu proyecto
3. En el menú lateral, click en **"SQL Editor"**

### 2. Ejecutar este SQL

Copia y pega este código en el editor SQL:

```sql
-- Agregar columna session_token a la tabla licenses
ALTER TABLE licenses 
ADD COLUMN IF NOT EXISTS session_token VARCHAR(255);

-- Crear índice para búsquedas rápidas por session_token
CREATE INDEX IF NOT EXISTS idx_session_token ON licenses(session_token);

-- Verificar que se agregó correctamente
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'licenses' 
AND column_name = 'session_token';
```

### 3. Click en "Run" o presiona `Ctrl+Enter`

Deberías ver un mensaje de éxito.

## ✅ Verificación

Después de ejecutar el SQL, verifica que todo esté correcto:

```sql
-- Ver estructura completa de la tabla
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'licenses'
ORDER BY ordinal_position;
```

Deberías ver estos campos:
- `id`
- `license_key`
- `license_type`
- `status`
- `hwid`
- `created_at`
- `expires_at`
- `last_used`
- `usage_count`
- `is_banned`
- `notes`
- **`session_token`** ← NUEVO

## 🎯 ¿Qué hace este campo?

El `session_token` es un token único que se genera cuando un usuario activa su licencia. Este token:
- Se guarda en el dispositivo del usuario
- Se usa para validar la sesión sin necesidad de re-ingresar la licencia
- Permite que el programa funcione sin pedir la licencia cada vez que se abre
- Se invalida si la licencia es baneada o expira

## 🚀 Después de esto

Una vez agregado el campo, el flujo completo funcionará:

1. **Usuario activa licencia** → Se genera `session_token`
2. **Programa valida sesión** → Usa `session_token` para verificar
3. **Admin banea licencia** → `session_token` se invalida automáticamente
4. **Licencia expira** → `session_token` deja de funcionar

---

**¡Listo!** Después de ejecutar este SQL, todo estará conectado y funcionando. 🎉

