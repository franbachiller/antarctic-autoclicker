#!/bin/bash
# Script para limpiar secretos del historial de Git

echo "============================================"
echo "LIMPIEZA DE SECRETOS DEL HISTORIAL DE GIT"
echo "============================================"
echo ""
echo "ADVERTENCIA: Este script reescribirá el historial de Git"
echo "Asegúrate de tener un backup antes de continuar"
echo ""
read -p "¿Continuar? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Cancelado"
    exit 1
fi

echo ""
echo "Instalando git-filter-repo si es necesario..."
pip install git-filter-repo

echo ""
echo "Creando backup del repositorio..."
cd ..
cp -r Antarctic Antarctic_backup_$(date +%Y%m%d_%H%M%S)
cd Antarctic

echo ""
echo "Limpiando secretos del historial..."

# Crear archivo de reemplazos
cat > /tmp/git-secrets-replace.txt << 'EOF'
GITHUB_TOKEN_REMOVED==>GITHUB_TOKEN_REMOVED
ADMIN_KEY_REMOVED==>ADMIN_KEY_REMOVED
SALT_REMOVED==>SALT_REMOVED
SALT_REMOVED==>SALT_REMOVED
EOF

# Aplicar reemplazos
git filter-repo --replace-text /tmp/git-secrets-replace.txt --force

echo ""
echo "============================================"
echo "LIMPIEZA COMPLETADA"
echo "============================================"
echo ""
echo "Próximos pasos:"
echo "1. Verifica que los cambios son correctos"
echo "2. Configura las variables de entorno:"
echo "   export GITHUB_TOKEN=tu_token_aqui"
echo "   export ADMIN_KEY=tu_admin_key_aqui"
echo "3. Force push al repositorio:"
echo "   git remote add origin https://github.com/Narfbach/antarctic-autoclicker.git"
echo "   git push origin --force --all"
echo "4. Haz el repositorio público en GitHub"
echo ""

