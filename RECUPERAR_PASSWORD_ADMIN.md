# Cómo Recuperar/Cambiar la Contraseña del Panel de Admin

## El Problema

El panel de admin usa la variable de entorno `ADMIN_KEY` que está configurada en Vercel.

## Solución 1: Ver la Contraseña Actual en Vercel

1. Ve a tu proyecto en Vercel: https://vercel.com/dashboard
2. Selecciona el proyecto `antarctic-autoclicker`
3. Ve a **Settings** → **Environment Variables**
4. Busca la variable `ADMIN_KEY`
5. Haz click en el ícono de ojo para ver el valor

## Solución 2: Cambiar la Contraseña

### Opción A: Desde Vercel Dashboard

1. Ve a **Settings** → **Environment Variables**
2. Encuentra `ADMIN_KEY`
3. Haz click en los tres puntos (⋯) → **Edit**
4. Cambia el valor a la nueva contraseña que quieras
5. Guarda los cambios
6. **IMPORTANTE**: Ve a **Deployments** y haz un **Redeploy** para que tome efecto

### Opción B: Desde la Terminal (Vercel CLI)

```bash
# Instalar Vercel CLI si no lo tienes
npm install -g vercel

# Login
vercel login

# Ver variables de entorno actuales
vercel env ls

# Agregar/actualizar ADMIN_KEY
vercel env add ADMIN_KEY

# Te pedirá:
# - El valor de la variable (tu nueva contraseña)
# - Para qué entornos (selecciona Production, Preview, Development)

# Redeploy para aplicar cambios
vercel --prod
```

## Solución 3: Crear Nueva Contraseña Segura

Si quieres generar una contraseña segura nueva:

```bash
# En PowerShell
python -c "import secrets; print(secrets.token_urlsafe(16))"
```

Esto generará algo como: `xK9mP2nQ7vL4wR8t`

## Verificar que Funciona

1. Abre el panel de admin: https://antarctic-autoclicker.vercel.app/admin-panel/admin.html
2. Ingresa la contraseña (el valor de `ADMIN_KEY`)
3. Haz click en LOGIN

## Notas Importantes

- La contraseña NO es `G4e3U0r9` (esa era una sugerencia de ejemplo)
- La contraseña real está en Vercel como variable de entorno
- Después de cambiarla, DEBES hacer redeploy
- Guarda la nueva contraseña en un lugar seguro

## Contraseña Temporal

Si no puedes acceder a Vercel ahora mismo, puedo ayudarte a:

1. Configurar una contraseña temporal
2. Actualizar el deployment
3. Darte acceso inmediato

¿Quieres que configure una contraseña temporal ahora?
