# 🎯 Antarctic Autoclicker

Sistema profesional de autoclicker con sistema de licencias y actualizaciones automáticas.

## 📁 Estructura del Proyecto

```
Antarctic/
├── src/                          # 💻 Código fuente principal
│   ├── antarctic.py             # Aplicación principal con GUI
│   ├── auth_client.py           # Cliente de autenticación de licencias
│   ├── latency_compensator.py   # Sistema de compensación de latencia
│   ├── security.py              # Módulo de seguridad
│   ├── updater.py               # Sistema de actualizaciones automáticas
│   └── version.txt              # Versión actual
│
├── api/                          # 🌐 Backend de validación (Vercel)
│   ├── activate.js              # Endpoint de activación
│   ├── validate.js              # Endpoint de validación
│   ├── admin/                   # Panel de administración
│   │   ├── licenses.js          # Lista de licencias
│   │   ├── create-license.js    # Crear licencia
│   │   ├── delete-license.js    # Eliminar licencia
│   │   ├── ban-license.js       # Banear licencia
│   │   └── stats.js             # Estadísticas
│   ├── middleware/
│   │   └── rate-limit.js        # Rate limiting
│   └── updates/
│       ├── latest.js            # Info de última versión
│       └── download.js          # Descarga de actualizaciones
│
├── admin-panel/                  # 🔐 Panel web de administración
│   ├── admin.html
│   ├── admin-script.js
│   └── admin-styles.css
│
├── website/                      # 🌍 Sitio web público
│   ├── index.html
│   ├── script.js
│   └── styles.css
│
├── tools/                        # 🛠️ Scripts de utilidad
│   ├── create_licenses.py       # Crear licencias masivamente
│   ├── key_generator.py         # Generar claves
│   ├── release.py               # Script de release automatizado
│   ├── create_logo.py           # Generar logos
│   └── migrate_to_github_releases.py
│
├── assets/                       # 🎨 Recursos gráficos
│   ├── icon.ico
│   ├── logo.png
│   └── logo_compact.png
│
├── dist/                         # 📦 Ejecutable compilado
│   └── Antarctic.exe
│
├── compile_antarctic.bat         # Compilar el proyecto
├── clean_project.bat             # Limpiar archivos temporales
├── auto_release.bat              # Release automatizado
├── release.bat                   # Release manual
├── config_updater.py             # Configuración de URLs
├── package.json                  # Dependencias de Node.js
├── vercel.json                   # Configuración de Vercel
└── set_env.bat                   # Variables de entorno (no en git)
```

## 🚀 Uso Rápido

### Ejecutar en modo desarrollo
```bash
python src/antarctic.py
```

### Compilar ejecutable
```bash
compile_antarctic.bat
```

### Limpiar archivos temporales
```bash
clean_project.bat
```

### Crear un release
```bash
auto_release.bat
```

## 🔧 Desarrollo

### Requisitos
- Python 3.8+
- PyInstaller
- customtkinter
- Pillow
- requests
- cryptography
- websocket-client

### Instalar dependencias de Python
```bash
pip install customtkinter pillow requests cryptography websocket-client pyinstaller pyarmor
```

### Instalar dependencias de Node.js (para API)
```bash
npm install
```

## 📝 Sistema de Licencias

El sistema usa Supabase para validación de licencias en tiempo real:
- **Activación**: Valida la clave contra la base de datos
- **Validación**: Verifica licencia activa periódicamente
- **Offline mode**: Modo de gracia de 1 hora sin conexión
- **Tipos de licencia**: 1 día, 7 días, 30 días, lifetime

## 🔄 Sistema de Actualizaciones

- Verificación automática en startup
- Descarga y instalación automática
- Backup automático antes de actualizar
- GitHub Releases como fuente

## 🎮 Características

- ✅ Sistema de clics configurable (single/double/triple)
- ✅ Compensación de latencia avanzada
- ✅ Perfiles de configuración
- ✅ Timing avanzado (Markov, Gaussian, Acceleration)
- ✅ Hotkeys (F2, F3, F5)
- ✅ Auto-burst con clic izquierdo
- ✅ GUI moderna con customtkinter

## 📦 Compilación

El script `compile_antarctic.bat` hace:
1. Ofusca el código con PyArmor
2. Compila con PyInstaller
3. Genera `dist/Antarctic.exe`

## 🌐 Deploy

### Vercel (API y Website)
```bash
vercel deploy
```

La API y el sitio web se despliegan automáticamente en Vercel.

## 📄 Licencia

Proyecto privado - Todos los derechos reservados

