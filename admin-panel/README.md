# ANTARCTIC Admin Panel - Frutiger Aero Style

## Descripción

Panel de administración completamente rediseñado con el mismo estilo Frutiger Aero del autoclicker Antarctic.

### Características del Diseño

- **Paleta de colores muted blues** idéntica al autoclicker
- **Tipografía profesional** con Segoe UI
- **Diseño compacto y moderno** con bordes redondeados
- **Animaciones suaves** y transiciones profesionales
- **Responsive** - funciona en desktop, tablet y móvil

### Colores Principales

```css
--bg-primary: #090C14       (Deep blue-black)
--bg-secondary: #0F1419     (Lighter blue-black)
--bg-card: #161B26          (Card background)
--accent-blue: #4A7BA7      (Muted professional blue)
--accent-cyan: #6B9FCC      (Soft blue)
--accent-green: #5A8AB0     (Muted blue-green)
--text-primary: #E0EBF5     (Soft blue-white)
--text-secondary: #7A92AB   (Muted blue-gray)
--border: #2D3F54           (Subtle border)
```

## Archivos Incluidos

1. **admin.html** - Estructura HTML del panel
2. **admin-styles.css** - Estilos Frutiger Aero
3. **admin-script.js** - Lógica de la aplicación
4. **README.md** - Este archivo

## Funcionalidades

### Login
- Pantalla de login con estilo Frutiger Aero
- Validación de admin key con el servidor
- Sesión guardada en localStorage
- Enter key support

### Dashboard
- 4 tarjetas de estadísticas (Total, Active, Expired, Banned)
- Colores distintivos por estado
- Hover effects y animaciones

### Crear Licencias
- Selector de tipo de licencia
- Campo de cantidad (1-100)
- Campo de notas opcional
- Botón con estados de carga
- Sección de licencias generadas con botón de copiar
- Exportar a archivo de texto

### Gestión de Licencias
- Tabla con todas las licencias
- Búsqueda en tiempo real
- Click en license key para copiar
- Botones de acción (Ban/Delete)
- Estados visuales con badges de color

### Notificaciones
- Sistema de alertas en la esquina inferior derecha
- 3 tipos: success (verde), error (rojo), info (azul)
- Auto-hide después de 5 segundos
- Animación slide-in

## Cómo Deployar en Vercel

### Método 1: Desde la carpeta admin-panel

```bash
cd admin-panel
vercel --prod
```

### Método 2: Copiar archivos al proyecto auth-server existente

Si ya tienes un proyecto en Vercel:

1. Copia los 3 archivos a la carpeta `public` de tu proyecto:
   ```
   auth-server/
   └── public/
       ├── admin.html
       ├── admin-styles.css
       └── admin-script.js
   ```

2. Redeploy:
   ```bash
   cd auth-server
   vercel --prod
   ```

### Método 3: Subir directamente desde Vercel Dashboard

1. Ve a tu proyecto en [vercel.com/dashboard](https://vercel.com/dashboard)
2. Settings → Deployments
3. Sube los 3 archivos en la carpeta raíz o `public`
4. Redeploy

## Configuración

### Cambiar la URL del servidor

Edita `admin-script.js` línea 1:

```javascript
const API_BASE_URL = 'https://tu-servidor.vercel.app';
```

### Cambiar el admin key

El admin key se configura en las variables de entorno de Vercel:

1. Vercel Dashboard → Tu proyecto → Settings → Environment Variables
2. Edita `ADMIN_KEY`
3. Redeploy

## Acceso al Panel

Una vez deployado, accede en:

```
https://tu-proyecto.vercel.app/admin.html
```

## Estructura del Código

### HTML (admin.html)
- Login screen
- Admin panel con navbar
- Stats grid (4 tarjetas)
- Create license section
- Generated licenses section
- All licenses table
- Notification system

### CSS (admin-styles.css)
- Variables CSS para colores
- Estilos del login
- Estilos del panel principal
- Componentes (cards, tables, forms, buttons)
- Responsive design
- Animaciones y transiciones

### JavaScript (admin-script.js)
- Autenticación y sesión
- Llamadas a la API
- Renderizado dinámico
- Búsqueda en tiempo real
- Sistema de notificaciones
- Copiar al portapapeles
- Exportar a archivo

## API Endpoints Utilizados

```javascript
GET  /api/admin/stats           // Obtener estadísticas
GET  /api/admin/licenses        // Obtener todas las licencias
POST /api/admin/create-license  // Crear nuevas licencias
POST /api/admin/ban-license     // Banear una licencia
POST /api/admin/delete-license  // Eliminar una licencia
```

Todos los endpoints requieren el header:
```
X-Admin-Key: tu_admin_key
```

## Mejoras vs Panel Anterior

✅ Diseño completamente nuevo Frutiger Aero  
✅ Colores muted blues profesionales  
✅ Tipografía mejorada (Segoe UI)  
✅ Bordes redondeados consistentes (10-12px)  
✅ Hover effects en todos los elementos  
✅ Stats cards con iconos y colores distintivos  
✅ Tabla más legible con mejor spacing  
✅ Notificaciones con mejor UX  
✅ Búsqueda con estilo mejorado  
✅ Botones con estados visuales claros  
✅ Sección de licencias generadas mejorada  
✅ Responsive design optimizado  
✅ Animaciones suaves y profesionales  

## Compatibilidad

- **Navegadores**: Chrome, Firefox, Safari, Edge (últimas versiones)
- **Móviles**: iOS Safari, Chrome Android
- **Resoluciones**: Desde 320px hasta 4K

## Solución de Problemas

### No puedo hacer login
- Verifica que el admin key sea correcto
- Abre la consola del navegador (F12) y revisa errores
- Verifica que la URL del servidor sea correcta

### Las licencias no se cargan
- Verifica la conexión al servidor
- Revisa la consola para errores de CORS
- Asegúrate que el servidor tenga CORS habilitado para tu dominio

### No puedo copiar al portapapeles
- Asegúrate de estar usando HTTPS
- Algunos navegadores antiguos no soportan la API
- Usa el fallback manual (selecciona y Ctrl+C)

### El diseño se ve roto
- Limpia la caché del navegador (Ctrl+Shift+R)
- Verifica que los 3 archivos estén en la misma carpeta
- Asegúrate que no haya errores de carga en la consola

## Mantenimiento

### Actualizar colores

Edita las variables CSS en `admin-styles.css`:

```css
:root {
    --bg-primary: #090C14;
    --accent-blue: #4A7BA7;
    /* etc... */
}
```

### Agregar nuevos endpoints

1. Crea la función en `admin-script.js`
2. Llama a la API con el admin key
3. Actualiza la UI con los resultados

### Modificar la tabla

Edita la función `renderLicenses()` en `admin-script.js` para cambiar las columnas o el formato.

## Seguridad

- ✅ Admin key requerido para todas las operaciones
- ✅ Validación de sesión con el servidor
- ✅ HTTPS obligatorio en producción
- ✅ Confirmación antes de acciones destructivas
- ✅ Sanitización de inputs

### Recomendaciones

1. Cambia el admin key regularmente
2. No compartas el admin key
3. Accede solo desde redes seguras
4. Usa un admin key fuerte (32+ caracteres)
5. Habilita 2FA en Vercel

## Créditos

**Diseño**: Frutiger Aero Style  
**Desarrollado para**: Antarctic License Management System  
**Versión**: 2.0 (Completamente rediseñado)  
**Fecha**: Octubre 2025  

---

**¡Disfruta tu nuevo panel de administración con estilo Frutiger Aero!** 🐧
