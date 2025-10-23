# 🧪 Guía de Pruebas - Advanced Timing Systems

## ✅ Cómo Verificar que Todo Funciona

### 📊 **Monitor en Tiempo Real**
En la sección "⚡ Advanced Timing" verás una línea de monitor que muestra:
- **Delay:XX.Xms** - Delay actual de cada click en milisegundos
- **M:🟢/🟡/🔴** - Estado de Markov (verde=rápido, amarillo=medio, rojo=lento)
- **G:±X.X** - Variación Gaussiana aplicada
- **A:XX%** - Progreso de aceleración (0-100%)

---

## 🔬 **Pruebas Paso a Paso**

### **TEST 1: Markov Chain**
1. ✅ Activa solo el checkbox **"Markov"**
2. ✅ Presiona **F3** para capturar coordenadas
3. ✅ Presiona **F2** para hacer un burst
4. ✅ **Observa el monitor**: Deberías ver el icono cambiar entre 🟢🟡🔴
5. ✅ **Resultado esperado**: El delay cambia según el estado
   - 🟢 Fast = delay más corto (más rápido)
   - 🟡 Medium = delay normal
   - 🔴 Slow = delay más largo (más lento)

**Cómo ajustar:**
- Click en ⚙ → Ajusta "Fast/Medium/Slow Speed Multiplier"
- Valores menores = más rápido, valores mayores = más lento

---

### **TEST 2: Gaussian Distribution**
1. ✅ Desactiva Markov, activa solo **"Gaussian"**
2. ✅ Presiona **F2** para hacer un burst
3. ✅ **Observa el monitor**: El delay debería variar alrededor de un valor central
4. ✅ **Resultado esperado**: Delays varían pero se mantienen cerca del promedio
   - Ejemplo: Si Mean=10ms, verás delays como 8ms, 11ms, 9ms, 12ms, 10ms...

**Cómo ajustar:**
- Click en ⚙ → Ajusta "Mean Delay" (valor central)
- Ajusta "Std Deviation" (cuánto varía)
  - Std Dev bajo = poca variación
  - Std Dev alto = mucha variación

---

### **TEST 3: Acceleration Profile**
1. ✅ Desactiva Gaussian, activa solo **"Accel"**
2. ✅ Presiona **F2** para hacer un burst
3. ✅ **Observa el monitor**: A:0% → A:100% progresivamente
4. ✅ **Resultado esperado**: El delay cambia gradualmente
   - Si Start=1.0 y End=0.5: Empieza normal, termina más rápido
   - Si Start=0.5 y End=1.0: Empieza rápido, termina normal

**Cómo ajustar:**
- Click en ⚙ → Selecciona "Curve Type":
  - **Linear**: Cambio constante
  - **Exponential**: Cambio lento al inicio, rápido al final
  - **S_curve**: Cambio suave al inicio y final
- Ajusta "Start/End Speed Multiplier"
- Ajusta "Duration (clicks)" para controlar cuántos clicks dura la transición

---

### **TEST 4: Combinación de Sistemas**
1. ✅ Activa **Markov + Gaussian + Accel** todos juntos
2. ✅ Presiona **F2** para hacer un burst
3. ✅ **Observa el monitor**: Verás todos los indicadores
   - Ejemplo: `Delay:12.3ms | M:🟡 | G:±2.1 | A:45%`
4. ✅ **Resultado esperado**: Los tres sistemas se combinan
   - Markov cambia el estado base
   - Gaussian añade variación aleatoria
   - Acceleration modifica progresivamente

---

## 🎯 **Pruebas de Sliders en el Diálogo ⚙**

### **Markov Chain Sliders:**
- **Fast Speed Multiplier** (0.1-2.0)
  - Prueba: Pon en 0.3 → Los clicks en estado 🟢 serán muy rápidos
  - Prueba: Pon en 1.5 → Los clicks en estado 🟢 serán más lentos
  
- **Slow Speed Multiplier** (0.1-3.0)
  - Prueba: Pon en 3.0 → Los clicks en estado 🔴 serán muy lentos
  - Prueba: Pon en 1.0 → Los clicks en estado 🔴 serán normales

### **Gaussian Sliders:**
- **Mean Delay** (1-100ms)
  - Prueba: Pon en 5ms → Delays muy rápidos alrededor de 5ms
  - Prueba: Pon en 50ms → Delays lentos alrededor de 50ms
  
- **Std Deviation** (0.5-20ms)
  - Prueba: Pon en 1ms → Poca variación (delays muy consistentes)
  - Prueba: Pon en 10ms → Mucha variación (delays muy aleatorios)

- **Min Delay** (0.1-10ms)
  - Prueba: Pon en 5ms → Ningún delay será menor a 5ms

### **Acceleration Sliders:**
- **Start Speed Multiplier** (0.1-3.0)
  - Prueba: Pon en 2.0 → Empieza lento (doble delay)
  
- **End Speed Multiplier** (0.1-3.0)
  - Prueba: Pon en 0.3 → Termina muy rápido
  
- **Duration (clicks)** (10-200)
  - Prueba: Pon en 20 → La aceleración dura 20 clicks
  - Prueba: Pon en 100 → La aceleración dura 100 clicks

---

## 📈 **Ejemplos de Configuraciones**

### **Configuración 1: "Humano Realista"**
```
✓ Markov: ON
  - Fast: 0.8
  - Medium: 1.0
  - Slow: 1.3

✓ Gaussian: ON
  - Mean: 15ms
  - Std Dev: 4ms
  - Min: 8ms

✗ Accel: OFF
```
**Resultado**: Clicks con timing variable y realista, como un humano

---

### **Configuración 2: "Aceleración Agresiva"**
```
✗ Markov: OFF

✗ Gaussian: OFF

✓ Accel: ON
  - Curve: Exponential
  - Start: 2.0 (lento)
  - End: 0.3 (muy rápido)
  - Duration: 30 clicks
```
**Resultado**: Empieza lento y acelera dramáticamente

---

### **Configuración 3: "Caos Controlado"**
```
✓ Markov: ON
  - Fast: 0.4
  - Medium: 1.0
  - Slow: 2.5

✓ Gaussian: ON
  - Mean: 10ms
  - Std Dev: 8ms
  - Min: 2ms

✓ Accel: ON
  - Curve: S_curve
  - Start: 1.5
  - End: 0.5
  - Duration: 50 clicks
```
**Resultado**: Timing muy impredecible pero controlado

---

## ✅ **Checklist de Verificación**

- [ ] El monitor muestra valores cuando hago clicks (F2)
- [ ] Markov checkbox cambia el icono 🟢🟡🔴 en el monitor
- [ ] Gaussian checkbox hace que el delay varíe aleatoriamente
- [ ] Accel checkbox muestra progreso A:0% → A:100%
- [ ] El botón ⚙ abre el diálogo de configuración
- [ ] Los sliders en el diálogo cambian los valores
- [ ] Los perfiles guardan/cargan las configuraciones
- [ ] Puedo combinar los 3 sistemas a la vez
- [ ] El delay mostrado en el monitor cambia según mis ajustes

---

## 🐛 **Si algo no funciona:**

1. **No veo el monitor**: Asegúrate de estar haciendo clicks (F2)
2. **El monitor no cambia**: Verifica que los checkboxes estén activados
3. **Los sliders no hacen nada**: Cierra y abre el diálogo ⚙ de nuevo
4. **Los valores son extraños**: Resetea poniendo valores por defecto

---

## 🎓 **Entendiendo los Valores**

**Speed Multiplier:**
- 0.5 = Mitad del delay = 2x más rápido
- 1.0 = Delay normal = velocidad normal
- 2.0 = Doble delay = 2x más lento

**Delay en ms:**
- 1ms = Muy rápido (1000 clicks por segundo teórico)
- 10ms = Rápido (100 clicks por segundo)
- 50ms = Medio (20 clicks por segundo)
- 100ms = Lento (10 clicks por segundo)

---

¡Ahora tienes todo para verificar que cada sistema funciona correctamente! 🚀

