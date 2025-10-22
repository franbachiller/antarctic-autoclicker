# 🎚️ GUÍA DE SLIDERS - ANTARCTIC AUTOCLICKER

## Problema Resuelto ✅

Los sliders ahora funcionan correctamente. El problema era que el modo "Burst Variations" estaba sobrescribiendo completamente la configuración de Interval.

---

## 📊 Explicación de Cada Slider

### 1. **Clicks/Batch** (1-100)
- **Qué hace:** Controla cuántos clics se envían en cada lote/ráfaga
- **Efecto:** Con valor 24, envía 24 clics, luego pausa, luego otros 24
- **Notas:** 
  - Si "Humanization" está activado, este valor varía aleatoriamente (5-15)
  - Si "Burst Variations" está activado, usa patrones predefinidos del perfil

### 2. **Interval (ms)** (1-200 ms)
- **Qué hace:** Controla el tiempo de espera ENTRE CADA CLIC
- **Efecto:** Con valor 10ms, espera 10 milisegundos entre cada clic individual
- **Notas:**
  - Este slider SIEMPRE funciona (es la base del timing)
  - "Humanization" SUMA variación aleatoria encima de este valor
  - "Burst Variations" SUMA micro-jitter encima de este valor
  - ULTRA MODE ignora este slider (0 delay)

### 3. **Duration (s)** (0.01-2.0 segundos)
- **Qué hace:** Controla cuánto tiempo dura la RÁFAGA completa
- **Efecto:** Con valor 0.30s, la ráfaga dura 300 milisegundos
- **Notas:**
  - Durante este tiempo, envía tantos clics como pueda
  - Ejemplo: 0.30s con 10ms interval = ~30 clics por ráfaga

### 4. **Auto-Burst Delay** (0.0-1.0 segundos)
- **Qué hace:** Controla cuánto espera ANTES de iniciar una ráfaga en modo Auto-Burst
- **Efecto:** Con valor 0.0s, no hay delay. Con 0.5s, espera medio segundo
- **Notas:**
  - Solo funciona cuando Auto-Burst [F5] está activado
  - Se activa al hacer clic izquierdo (si está conectado a BoomBang)
  - Útil para sincronizar con eventos del juego

---

## 🎮 Modos de Operación

### Modo Normal (Sin checkboxes)
```
Clics: 24 por batch
Interval: 10ms entre cada clic
Duration: 0.30s por ráfaga
Resultado: ~30 clics cada vez que presionas F2
```

### Con Humanization ✓
```
Clics: Variable (5-15 aleatorio) - IGNORA el slider
Interval: 10ms BASE + variación aleatoria (2-25ms extra)
Duration: 0.30s (igual)
Resultado: Patrón más "humano", menos detectable
```

### Con Burst Variations ✓
```
Clics: Usa patrón [1,1,2,1,1,3] del perfil - IGNORA el slider
Interval: 10ms BASE + micro-jitter (0.1-0.3ms)
Duration: 0.30s (igual)
Resultado: Patrón complejo para race conditions
```

### ULTRA MODE
```
Clics: 24 por batch (respetado)
Interval: 0ms - IGNORA el slider completamente
Duration: 0.30s (igual)
Resultado: Máxima velocidad, sin delays
```

---

## 🔍 Ejemplos Prácticos

### Configuración 1: Clicker Lento y Preciso
```
Clicks/Batch: 10
Interval: 50ms
Duration: 1.0s
Delay: 0.0s
Humanization: ✗
Burst Variations: ✗

Resultado: 20 clics por segundo, muy preciso
```

### Configuración 2: Spam Rápido
```
Clicks/Batch: 50
Interval: 5ms
Duration: 0.50s
Delay: 0.0s
Humanization: ✗
Burst Variations: ✗

Resultado: ~100 clics en medio segundo
```

### Configuración 3: Modo Humano
```
Clicks/Batch: 20 (pero varía 5-15)
Interval: 15ms (pero añade 2-25ms aleatorio)
Duration: 0.80s
Delay: 0.0s
Humanization: ✓
Burst Variations: ✗

Resultado: Patrón irregular, difícil de detectar
```

### Configuración 4: Race Condition Master
```
Clicks/Batch: 24 (pero usa patrón del perfil)
Interval: 1ms (mínimo + micro-jitter)
Duration: 0.20s
Delay: 0.0s
Humanization: ✗
Burst Variations: ✓

Resultado: Patrón complejo optimizado para condiciones de carrera
```

---

## 🐛 Debugging

Si los sliders parecen no funcionar:

1. **Verifica el modo actual:**
   - ¿ULTRA MODE está activado? → Ignora Interval
   - ¿Humanization está activado? → Clicks es aleatorio
   - ¿Burst Variations está activado? → Clicks usa patrón del perfil

2. **Verifica la conexión:**
   - Debe decir "● ONLINE" en verde
   - Debe estar conectado a la ventana BoomBang

3. **Captura coordenadas:**
   - Presiona F3 sobre el objetivo
   - Debe mostrar "TARGET: [ X , Y ]" en verde

4. **Ejecuta la ráfaga:**
   - Presiona F2 para burst manual
   - O activa Auto-Burst [F5] y haz clic izquierdo

---

## 💡 Recomendaciones

### Para PvP Normal
```
Clicks: 20-30
Interval: 10-20ms
Duration: 0.30-0.50s
Humanization: ✓ (más seguro)
```

### Para Eventos/Boss
```
Clicks: 40-60
Interval: 5-10ms
Duration: 0.50-1.0s
Burst Variations: ✓ (más efectivo)
```

### Para Testing
```
ULTRA MODE activado
Duration: 0.10s (corto)
Observa cuántos clics envía
```

---

## ⚠️ Advertencias

1. **No uses ULTRA MODE en producción** - Es muy obvio y detectable
2. **Interval < 5ms** puede ser detectado como "superhuman"
3. **Duration muy largo** (>1.5s) puede ser obvio
4. **Sin humanization** en PvP es arriesgado

---

## 🎯 Cambios Realizados en el Código

### Antes (Problemático):
```python
# Advanced timing tenía precedencia total
if self.config.advanced_timing_enabled:
    base_delay = profile.base_delay  # Ignoraba el slider
    return base_delay
```

### Ahora (Correcto):
```python
# Siempre usa el slider Interval como base
base_delay = self.config.interval / 1000.0

# Humanization y Burst Variations SUMAN encima
if self.config.humanize_enabled:
    base_delay += random_variation()

if self.config.advanced_timing_enabled:
    base_delay += micro_jitter()
```

---

## 📈 Monitoreo en Tiempo Real

Observa la esquina superior derecha:
```
CLICKS: 1250 / 28
        ^^^^   ^^
        Total  Último burst
```

- **Total:** Clics enviados desde que iniciaste la app
- **Burst:** Clics enviados en la ráfaga actual (se resetea al terminar)

---

¡Ahora todos los sliders funcionan correctamente! 🎉
