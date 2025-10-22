# PANEL DE ADMINISTRACIÓN WEB - ANTARCTIC

## URL DE ACCESO

```
https://antarctic-auth-5da4jpcgh-frans-projects-593301de.vercel.app/admin.html
```

**Admin Key:** `admin_antarctic_2025`

---

## CARACTERÍSTICAS DEL PANEL

### 🎨 Interfaz Moderna y Profesional
- Diseño dark/red theme acorde con Antarctic
- Interfaz responsive y adaptable a cualquier dispositivo
- Animaciones suaves y efectos visuales
- Auto-refresh cada 30 segundos

### 🔐 Sistema de Autenticación
- Login con admin key
- Guarda la sesión en localStorage
- Botón de logout visible
- Validación automática de credenciales
- Soporte para Enter key en el campo de password

### 📊 Dashboard de Estadísticas
Tarjetas visuales que muestran en tiempo real:
- **Total Licenses**: Todas las licencias en el sistema
- **Active**: Licencias activas y válidas
- **Expired**: Licencias expiradas
- **Banned**: Licencias baneadas

### ⚙️ Creación de Licencias

**Formulario Mejorado:**
- Selector de tipo de licencia (week, month, 3months, 6months, year, lifetime)
- Campo de cantidad (1-100 licencias)
- Campo de notas opcional para identificar clientes/pedidos
- Botón con estado de carga ("Generating...")
- Limpia automáticamente el campo de notas después de crear

**Visualización de Licencias Generadas:**
- Muestra las licencias recién creadas en una sección destacada
- Cada licencia tiene:
  - Clave completa
  - Tipo de licencia
  - Fecha de expiración
  - Botón "Copy Key" para copiar al portapapeles
- Botón "Export to Text File" para descargar todas las licencias generadas

### 📋 Gestión de Licencias

**Tabla Completa con:**
- License Key (clickable para copiar)
- Tipo de licencia
- Estado (active/expired/banned con colores)
- Fecha de creación
- Fecha de expiración
- Último uso
- Contador de usos
- Notas asociadas
- Botón de acción (Ban)

**Funcionalidades:**
- **Buscar**: Campo de búsqueda en tiempo real por key, tipo, estado o notas
- **Copiar**: Click en cualquier license key para copiar al portapapeles
- **Banear**: Botón para banear licencias con confirmación
- **Refresh**: Botón manual para actualizar la lista
- **Tooltips**: Indicadores visuales al pasar el mouse

### 🔔 Sistema de Alertas

Notificaciones visuales para:
- ✅ **Success** (verde): Operaciones exitosas
- ❌ **Error** (rojo): Errores y problemas
- ℹ️ **Info** (azul): Información general (ej: copiado al portapapeles)

Todas las alertas se ocultan automáticamente después de 5 segundos.

### 📥 Exportación de Licencias

Al generar licencias, puedes exportarlas a un archivo de texto con formato:
```
======================================================================
ANTARCTIC - GENERATED LICENSES
======================================================================

Generated: 18/10/2025 12:00:00
Total: 5 license(s)

LICENSE #1
----------------------------------------------------------------------
Key:     ANTARCTIC-XXXX-XXXX-XXXX
Type:    month
Expires: 17/11/2025
Status:  active

...
```

Nombre del archivo: `antarctic-licenses-YYYY-MM-DD-HHMMSS.txt`

---

## CÓMO USAR EL PANEL

### 1. Acceder al Panel
1. Abre tu navegador
2. Ve a: `https://antarctic-auth-5da4jpcgh-frans-projects-593301de.vercel.app/admin.html`
3. Ingresa el admin key: `admin_antarctic_2025`
4. Click en "Login" o presiona Enter

### 2. Crear Licencias
1. Selecciona el tipo de licencia
2. Ingresa la cantidad deseada (1-100)
3. Opcionalmente, agrega notas (ej: "Cliente: Juan Pérez")
4. Click en "Generate License(s)"
5. Las licencias aparecerán en una sección verde debajo
6. Click en "Copy Key" para copiar cada licencia
7. O click en "Export to Text File" para descargar todas

### 3. Buscar Licencias
1. En la sección "All Licenses"
2. Usa el campo de búsqueda superior
3. Escribe: clave, tipo, estado o notas
4. Los resultados se filtran automáticamente

### 4. Copiar una License Key
- **Opción 1**: Click en la license key en la tabla
- **Opción 2**: Usa el botón "Copy Key" en licencias generadas
- Verás una notificación azul confirmando la copia

### 5. Banear una Licencia
1. Busca la licencia en la tabla
2. Click en el botón "Ban" (rojo)
3. Confirma la acción en el diálogo
4. La licencia se marcará como "banned" inmediatamente
5. El cliente no podrá usar esa licencia más

### 6. Actualizar Datos
- **Automático**: El panel se actualiza cada 30 segundos
- **Manual**: Click en el botón "Refresh" (azul)

---

## MEJORAS IMPLEMENTADAS

### Nuevas Funcionalidades
✅ Auto-login con localStorage (mantiene sesión)
✅ Botón de logout visible en el header
✅ Validación de admin key antes de mostrar el panel
✅ Campo de búsqueda en tiempo real
✅ Click en license key para copiar
✅ Tooltips informativos
✅ Exportación a archivo de texto
✅ Botón "Copy Key" en licencias generadas
✅ Indicador de estado de carga en botones
✅ Soporte para Enter key en login
✅ Columna de "Notes" en la tabla
✅ Auto-refresh cada 30 segundos
✅ Contador visual de auto-refresh

### Mejoras de UX/UI
✅ Alertas con auto-hide (5 segundos)
✅ Alertas de tipo "info" para notificaciones
✅ Limpieza automática del campo de notas
✅ Confirmación mejorada al banear licencias
✅ Estados visuales en botones (hover, disabled)
✅ Scroll horizontal en tabla responsive
✅ Diseño de 3 columnas en formulario de creación
✅ Checkmark (✓) en mensajes de éxito
✅ Colores distintivos por tipo de alerta

### Mejoras Técnicas
✅ Almacenamiento de todas las licencias para búsqueda
✅ Filtrado eficiente en cliente
✅ Fallback para browsers sin clipboard API
✅ Manejo robusto de errores
✅ Validación de admin key con el servidor
✅ Generación de timestamps en nombres de archivo
✅ Export con formato legible

---

## TROUBLESHOOTING

### Problema: No puedo acceder al panel
**Solución:** Verifica que la URL sea correcta: `https://antarctic-auth-5da4jpcgh-frans-projects-593301de.vercel.app/admin.html`

### Problema: Admin key inválido
**Solución:** Asegúrate de usar: `admin_antarctic_2025`

### Problema: Las licencias no se cargan
**Solución:**
1. Click en "Refresh"
2. Abre la consola del navegador (F12) y verifica errores
3. Verifica que el servidor esté activo

### Problema: No puedo copiar al portapapeles
**Solución:**
- Asegúrate de estar usando HTTPS
- Algunos browsers antiguos pueden no soportar la API
- Usa el fallback manual (seleccionar y Ctrl+C)

### Problema: El panel no se actualiza automáticamente
**Solución:**
- El auto-refresh funciona cada 30 segundos
- Usa el botón "Refresh" para actualización manual

---

## ATAJOS DE TECLADO

- **Enter** en campo de admin key: Login
- **Ctrl+F** (luego click en búsqueda): Buscar licencias
- **Ctrl+C**: Copiar (después de seleccionar)

---

## SEGURIDAD

### Medidas Implementadas
- ✅ Admin key requerido para acceso
- ✅ Validación de admin key con el servidor
- ✅ CORS habilitado solo para origen correcto
- ✅ Admin key guardado en localStorage (solo local, no servidor)
- ✅ Confirmación antes de acciones destructivas (ban)
- ✅ HTTPS obligatorio en producción

### Recomendaciones
- 🔒 Cambia el admin key regularmente
- 🔒 No compartas el admin key
- 🔒 Accede al panel solo desde redes seguras
- 🔒 Cierra sesión (logout) cuando termines
- 🔒 Usa un admin key fuerte en producción

---

## PRÓXIMAS MEJORAS RECOMENDADAS

### Funcionalidades
- [ ] Editar notas de licencias existentes
- [ ] Filtros por estado (active/expired/banned)
- [ ] Ordenar tabla por columnas
- [ ] Paginación para grandes cantidades de licencias
- [ ] Ver historial de uso de una licencia
- [ ] Transferir licencia entre HWIDs
- [ ] Dashboard de gráficos (charts)

### Seguridad
- [ ] Autenticación de dos factores
- [ ] Roles de usuario (admin, viewer)
- [ ] Log de actividad del admin
- [ ] Sesiones con expiración

### UX
- [ ] Modo light/dark toggle
- [ ] Personalización de colores
- [ ] Atajos de teclado avanzados
- [ ] Drag & drop para importar licencias

---

## CAPTURAS DE PANTALLA

### Panel Principal
- Header con logo y botón de logout
- 4 tarjetas de estadísticas
- Formulario de creación de licencias
- Tabla de gestión de licencias

### Funcionalidades Destacadas
- Búsqueda en tiempo real
- Tooltips al pasar el mouse
- Copiar al portapapeles con un click
- Exportar licencias a archivo

---

**Fecha de actualización:** 18 de octubre de 2025
**Versión del Panel:** 1.0 (Mejorado)
**Estado:** PRODUCCIÓN - COMPLETAMENTE FUNCIONAL

**Desarrollado para ANTARCTIC License Management System**
