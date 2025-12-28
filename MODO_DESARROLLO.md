# Modo Desarrollo - Sin Licencia

## Cambio Implementado

He modificado `src/antarctic.py` para que **cuando ejecutes desde el código fuente, NO requiera licencia**.

## Cómo Funciona

El código detecta automáticamente si estás en:

### Modo Desarrollo (Sin Licencia)
- **Cuándo:** Ejecutas `python src/antarctic.py`
- **Comportamiento:** Salta la validación de licencia completamente
- **Mensaje:** Verás un mensaje en consola indicando "DEVELOPMENT MODE"

### Modo Producción (Con Licencia)
- **Cuándo:** Ejecutas el `.exe` compilado
- **Comportamiento:** Requiere licencia válida
- **Validación:** Sistema completo de licencias activo

## Uso

### Para Desarrollo (Sin Licencia)
```bash
python src/antarctic.py
```

Verás este mensaje:
```
============================================================
ANTARCTIC - DEVELOPMENT MODE
============================================================
Running without license validation (development mode)
License system is bypassed when running from source
============================================================
```

La aplicación se abrirá directamente sin pedir licencia.

### Para Producción (Con Licencia)
```bash
dist/Antarctic.exe
```

El ejecutable compilado seguirá requiriendo licencia normalmente.

## Detalles Técnicos

La detección se hace con:
```python
is_dev_mode = not getattr(sys, 'frozen', False)
```

- `sys.frozen` existe solo cuando el código está compilado con PyInstaller
- Si NO existe → Modo desarrollo → Sin licencia
- Si existe → Modo producción → Con licencia

## Ventajas

✅ **Desarrollo rápido:** No necesitas licencia para testear  
✅ **Producción segura:** El `.exe` sigue protegido  
✅ **Automático:** No necesitas cambiar nada manualmente  
✅ **Claro:** Mensaje en consola te indica el modo

## Nota Importante

Este cambio **NO afecta** al ejecutable compilado. Cuando compiles con `compile_antarctic.bat`, el `.exe` seguirá requiriendo licencia normalmente.

El bypass solo funciona cuando ejecutas directamente desde Python.
