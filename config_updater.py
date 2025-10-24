# ============================================
# CONFIGURACIÓN DEL AUTO-UPDATER
# ============================================
#
# 1. URL de la API de updates (tu servidor Vercel)
UPDATE_API_URL = "https://antarctic-autoclicker.vercel.app/api/updates"
#
# 2. Repositorio de GitHub (para releases internas)
GITHUB_REPO = "Narfbach/antarctic-autoclicker"
#
# 3. Para crear una release:
#    - Actualiza api/updates/latest.js con la nueva versión
#    - Sube el .exe a tu storage (Dropbox, Google Drive, etc.)
#    - Actualiza la URL en api/updates/latest.js
#    - Compila: compile_antarctic.bat
#    - Deploy: git push (Vercel auto-deploys)
#
# Los clientes verán la actualización automáticamente!

