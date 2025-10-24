# PROCESO DE RELEASE - ANTARCTIC

## Sistema de Updates Privado

Dado que el repositorio es privado, usamos nuestra propia API para distribuir actualizaciones.

## Opciones para Alojar el .exe

### Opción 1: Google Drive (Recomendado - Gratis)

1. Sube el .exe a Google Drive
2. Click derecho → Compartir → Cambiar a "Cualquiera con el enlace"
3. Copia el ID del archivo (está en la URL)
4. La URL de descarga directa es:
   ```
   https://drive.google.com/uc?export=download&id=FILE_ID
   ```

### Opción 2: Dropbox (Gratis)

1. Sube el .exe a Dropbox
2. Click derecho → Compartir → Crear enlace
3. Cambia `www.dropbox.com` por `dl.dropboxusercontent.com` en la URL
4. Cambia `?dl=0` por `?dl=1` al final

### Opción 3: GitHub Releases (Privado con Token)

1. Crea una release en GitHub (puede ser privada)
2. Sube el .exe como asset
3. Usa la URL directa del asset (requiere autenticación)

### Opción 4: Tu Propio Servidor

Si tienes un servidor web, simplemente sube el .exe allí.

## Proceso Completo de Release

### Paso 1: Compilar

```bash
compile_antarctic.bat
```

Esto genera `dist/Antarctic.exe`

### Paso 2: Subir el .exe

Sube `dist/Antarctic.exe` a uno de los servicios mencionados arriba y obtén la URL de descarga directa.

Ejemplo de URL válida:
```
https://drive.google.com/uc?export=download&id=1ABC123XYZ
```

### Paso 3: Actualizar la API

```bash
python tools/update_release_info.py --version 1.0.3 --url "https://tu-url-aqui.com/Antarctic.exe" --notes "- Fix bug X
- Add feature Y"
```

Esto actualiza automáticamente:
- `api/updates/latest.js` - Info de la última versión
- `api/updates/download.js` - Mapeo de versiones a URLs

### Paso 4: Deploy

```bash
git add api/updates/
git commit -m "Release v1.0.3"
git push
```

Vercel auto-desplegará los cambios en ~30 segundos.

### Paso 5: Verificar

Los usuarios verán la actualización automáticamente al abrir el autoclicker.

## Proceso Rápido (Resumen)

```bash
# 1. Compilar
compile_antarctic.bat

# 2. Subir dist/Antarctic.exe a Google Drive y obtener URL

# 3. Actualizar API
python tools/update_release_info.py --version 1.0.3 --url "https://drive.google.com/uc?export=download&id=TU_FILE_ID"

# 4. Deploy
git add api/updates/
git commit -m "Release v1.0.3"
git push
```

## Variables de Entorno (Opcional)

Puedes configurar la URL del .exe como variable de entorno en Vercel:

1. Ve a tu proyecto en Vercel
2. Settings → Environment Variables
3. Agrega: `LATEST_EXE_URL` = `https://tu-url.com/Antarctic.exe`
4. Redeploy

Esto te permite cambiar la URL sin modificar el código.

## Troubleshooting

### "No updates available" cuando debería haber update

1. Verifica que la API esté desplegada: `https://antarctic-autoclicker.vercel.app/api/updates/latest`
2. Verifica que la versión en `api/updates/latest.js` sea mayor que la actual
3. Verifica que la URL de descarga sea accesible públicamente

### Error al descargar

1. Verifica que la URL sea de descarga DIRECTA (no una página de vista previa)
2. Para Google Drive, usa el formato: `https://drive.google.com/uc?export=download&id=FILE_ID`
3. Para Dropbox, usa `dl.dropboxusercontent.com` y `?dl=1`

### Los usuarios no ven la actualización

1. Verifica que tengan conexión a internet
2. Verifica que la API esté respondiendo correctamente
3. Pídeles que hagan click en "Check for Updates" manualmente

