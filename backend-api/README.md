# Antarctic Backend API

## Deploy en Vercel

1. Pushea el código a GitHub
2. En Vercel dashboard, crea nuevo proyecto desde backend-api
3. Configura variables de entorno:
   - `ADMIN_KEY` = admin_antarctic_2025
4. Conecta Vercel Postgres en Storage tab
5. Ejecuta SQL para crear tabla:

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

## Endpoints

- POST /api/verify - Verificar licencia
- GET /api/admin/stats - Estadísticas
- GET /api/admin/licenses - Listar licencias
- POST /api/admin/create-license - Crear licencias
- POST /api/admin/ban-license - Banear licencia
- POST /api/admin/delete-license - Eliminar licencia
