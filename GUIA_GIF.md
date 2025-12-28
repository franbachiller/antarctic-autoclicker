# Guía Rápida: Crear GIF Demo para GitHub

## Opción Más Fácil: ScreenToGif (RECOMENDADO)

### Paso 1: Descargar ScreenToGif
1. Ve a: https://www.screentogif.com/
2. Descarga e instala (es gratis y portable)

### Paso 2: Grabar tu aplicación
1. Abre Antarctic
2. Abre ScreenToGif
3. Selecciona "Recorder"
4. Posiciona el área de grabación sobre la ventana de Antarctic
5. Click en "Record" (F7)
6. Muestra las funcionalidades principales (10-15 segundos):
   - Pantalla de licencia
   - Configuración de clics
   - Modos de timing
   - Compensación de latencia
   - Perfiles
7. Click en "Stop" (F8)

### Paso 3: Editar y optimizar
1. ScreenToGif abrirá el editor automáticamente
2. Elimina frames innecesarios
3. Ajusta la velocidad si es necesario
4. Ve a "File" → "Save as..."
5. Guarda en: `Antarctic\assets\demo\antarctic_demo.gif`

### Paso 4: Activar en README
1. Abre `README.md`
2. Busca estas líneas:
```markdown
<!-- Uncomment when demo GIF is ready
![Antarctic Demo](assets/demo/antarctic_demo.gif)
-->
```
3. Cámbialo a:
```markdown
![Antarctic Demo](assets/demo/antarctic_demo.gif)
```

### Paso 5: Subir a GitHub
```bash
git add assets/demo/antarctic_demo.gif
git add README.md
git commit -m "Add demo GIF to showcase application"
git push origin main
```

---

## Opción 2: Script Automático

### Requisitos
```bash
pip install pyautogui pywin32
```

### Uso
```bash
python tools/create_demo_gif.py
```

El script:
- Abre Antarctic automáticamente
- Captura screenshots
- Crea el GIF optimizado
- Te dice dónde está guardado

---

## Opción 3: Screenshots Manuales

### Paso 1: Tomar screenshots
1. Abre Antarctic
2. Presiona `Win + Shift + S` para capturar
3. Guarda cada screenshot en una carpeta (ej: `screenshots/`)
4. Nómbralas en orden: `01.png`, `02.png`, etc.

### Paso 2: Crear GIF
```bash
python tools/create_manual_gif.py screenshots/ assets/demo/antarctic_demo.gif 1000
```

---

## Tips para un GIF Profesional

### Qué Mostrar (en orden)
1. **Pantalla principal** (2 segundos)
2. **Activación de licencia** (2 segundos)
3. **Configuración de clics** (2 segundos)
4. **Selección de modo de timing** (2 segundos)
5. **Compensación de latencia** (2 segundos)
6. **Gestión de perfiles** (2 segundos)
7. **Estadísticas en tiempo real** (2 segundos)

### Preparación
- Cierra otras ventanas
- Limpia datos personales
- Usa la interfaz en modo oscuro (se ve mejor)
- Asegúrate de que la ventana esté completa

### Optimización
- Mantén el GIF bajo 5MB
- Usa 800px de ancho máximo
- 10-15 segundos de duración total
- Frame rate: 10-15 FPS

### Errores Comunes a Evitar
❌ GIF muy pesado (>10MB)
❌ Muy rápido (difícil de seguir)
❌ Muy lento (aburrido)
❌ Resolución muy alta (carga lenta)
❌ Mostrar información personal

✅ 3-5 MB
✅ Velocidad moderada
✅ 10-15 segundos
✅ 800px ancho
✅ Interfaz limpia

---

## Verificar Antes de Publicar

1. **Tamaño del archivo**
```bash
ls -lh assets/demo/antarctic_demo.gif
```
Debe ser < 5MB

2. **Previsualizar**
Abre el GIF en tu navegador para verificar que se vea bien

3. **Test en GitHub**
Puedes crear un Pull Request draft para ver cómo se ve antes de publicar

---

## Resultado Final

Tu README se verá así:

```
# Antarctic Autoclicker

[GIF ANIMADO AQUÍ]

Advanced autoclicker system with license management...
```

Esto impresionará a cualquier reclutador que visite tu GitHub!
