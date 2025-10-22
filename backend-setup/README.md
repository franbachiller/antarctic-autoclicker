# Antarctic Backend API

## 🚀 Deploy en Vercel

1. **Crear nuevo proyecto en Vercel** desde este directorio
2. **Configurar variables de entorno**:
   - `ADMIN_KEY` = `ADMIN_KEY_REMOVED`
3. **Conectar Vercel Postgres** en Storage tab
4. **Ejecutar SQL** para crear tabla:

```sql
CREATE TABLE licenses (
  id SERIAL PRIMARY KEY,
  license_key VARCHAR(255) UNIQUE NOT NULL,
  license_type VARCHAR(50) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP NOT NULL,
  last_used TIMESTAMP,
  usage_count INTEGER DEFAULT 0,
  is_banned BOOLEAN DEFAULT false,
  notes TEXT
);
```

## 📋 Endpoints

- POST /api/verify - Verificar licencia
- GET /api/admin/stats - Estadísticas (requiere X-Admin-Key header)
- GET /api/admin/licenses - Listar licencias (requiere X-Admin-Key header)
- POST /api/admin/create-license - Crear licencias (requiere X-Admin-Key header)
- POST /api/admin/ban-license - Banear licencia (requiere X-Admin-Key header)
- POST /api/admin/delete-license - Eliminar licencia (requiere X-Admin-Key header)

## 🔐 Autenticación

Todas las rutas admin requieren el header: `X-Admin-Key: ADMIN_KEY_REMOVED`

## 🧪 Test

```bash
# Test con autenticación
curl -H "X-Admin-Key: ADMIN_KEY_REMOVED" https://tu-backend.vercel.app/api/admin/stats

# Test sin autenticación (debería dar 401)
curl https://tu-backend.vercel.app/api/admin/stats
