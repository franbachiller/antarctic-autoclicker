# 🚀 Inicio Rápido - Desplegar Sistema de Licencias

## ¿Qué vamos a hacer?

Desplegar tu servidor de licencias en Vercel (gratis) en **10 minutos**.

## Requisitos

- Cuenta de GitHub/Google/Email (para Vercel)
- ¡Eso es todo!

---

## 📍 Paso a Paso

### 1️⃣ Login en Vercel (2 min)

```bash
cd auth-server
vercel login
```

Se abre tu navegador → Acepta → ✅ Listo

### 2️⃣ Desplegar Proyecto (1 min)

```bash
vercel
```

Preguntas:
- `Set up and deploy?` → **Y**
- `Which scope?` → Selecciona tu cuenta
- `Link to existing project?` → **N**
- `Project name?` → **antarctic-auth** (o el que quieras)
- `Directory?` → Enter (deja `.`)
- `Override settings?` → **N**

✅ Te dará una URL tipo: `https://antarctic-auth-abc123.vercel.app`

### 3️⃣ Crear Base de Datos (3 min)

1. Abre [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click en tu proyecto "antarctic-auth"
3. Click **Storage** → **Create Database**
4. Selecciona **Postgres**
5. Nombre: `antarctic-db`
6. Click **Create**

**📋 COPIA LA URL** que aparece: `postgres://...`

### 4️⃣ Configurar Claves (2 min)

En Vercel Dashboard → **Settings** → **Environment Variables**

Agrega estas 3 variables:

**Variable 1:**
```
Name: POSTGRES_URL
Value: [pega aquí el postgres://... que copiaste]
```

**Variable 2:**
```
Name: JWT_SECRET
Value: antarctic_jwt_secret_2025_change_this_later
```

**Variable 3:**
```
Name: ADMIN_KEY
Value: admin_antarctic_2025
```

Para cada una: Marca las 3 opciones (Production, Preview, Development) → Save

### 5️⃣ Redesplegar (1 min)

```bash
vercel --prod
```

✅ Tu servidor está ONLINE: `https://tu-proyecto.vercel.app`

### 6️⃣ Inicializar Database (2 min)

1. Vercel Dashboard → **Storage** → tu database
2. Click **`.sql`** o **Query**
3. Abre el archivo `schema.sql` en tu editor
4. Copia TODO el contenido
5. Pégalo en el editor de Vercel
6. Click **Run Query**

✅ Tablas creadas!

### 7️⃣ Probar Panel Admin (1 min)

Abre: `https://tu-proyecto.vercel.app/admin.html`

- Ingresa tu ADMIN_KEY: `admin_antarctic_2025`
- Crea una licencia:
  - Type: **month**
  - Count: **1**
  - Click **GENERATE**

✅ Verás tu primera licencia: `ANTARCTIC-XXXX-XXXX-XXXX`

---

## ✅ ¡LISTO!

Tu sistema está funcionando. Ahora:

### Siguiente paso: Actualizar Antarctic

Edita `antarctic.py` línea ~1143:

```python
SERVER_URL = "https://tu-proyecto.vercel.app"  # ← Pon tu URL aquí
```

Guarda y compila:

```bash
compile.bat
```

### Probar todo funciona:

```bash
python test_auth.py
```

Ingresa:
- URL: `https://tu-proyecto.vercel.app`
- Licencia: La que creaste en el paso 7

Deberías ver:
```
✅ Activación: License activated successfully
✅ Validación: Session is valid
✅ Estado: ACTIVADO
```

---

## 🎉 ¡Felicidades!

Ya puedes:
- ✅ Crear licencias desde el panel
- ✅ Distribuir tu aplicación
- ✅ Controlar todo desde `tu-proyecto.vercel.app/admin.html`

---

## 📞 ¿Problemas?

**No se conecta al servidor:**
- Verifica que la URL en `antarctic.py` sea correcta (sin `/` al final)

**"Invalid admin key":**
- Verifica que uses la misma que pusiste en Vercel

**"Database connection failed":**
- Verifica que ejecutaste el `schema.sql`

**Más ayuda:** Ver `auth-server/SETUP.md` para guía detallada
