#!/usr/bin/env bash
# ============================================================================
# YOLITIA — Bootstrap y publicacion del catalogo
# Ejecuta desde la carpeta yolitia_catalog
# ============================================================================
set -euo pipefail
cd "$(dirname "$0")"

echo
echo "[1/5] Preparando logo..."
python scripts/prepare_logo.py

echo
echo "[2/5] Publicando PDF en dist/..."
python scripts/publish_catalog.py

echo
echo "[3/5] Regenerando tarjeta con QR..."
python scripts/generate_qr_card.py

echo
echo "[4/5] Verificando si es repo git..."
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "    Inicializando repo..."
    git init
    git checkout -b main 2>/dev/null || true
    git config user.email "bot@yolitia.bio" 2>/dev/null || true
    git config user.name  "YOLITIA Bot" 2>/dev/null || true
fi

echo
echo "[5/5] Preparando commit..."
git add .gitignore public .github scripts
git add assets/images/logo.png public/assets/logo.png 2>/dev/null || true
git status --short

cat <<'EOF'

==============================================================================
 SIGUIENTE PASO MANUAL (solo la primera vez):
   1. Crear repo en https://github.com/new  (ej: yolitia/catalogo)
   2. git remote add origin https://github.com/TU-USUARIO/TU-REPO.git
   3. git push -u origin main
   4. Crear primera release arrastrando dist/catalogo-yolitia.pdf a:
        https://github.com/TU-USUARIO/TU-REPO/releases/new
   5. En GitHub -> Settings -> Pages: activar Pages desde main / root
   6. Custom domain: catalogo.yolitia.bio  (configurar CNAME en tu DNS)

 PARA ACTUALIZAR EL CATALOGO DESPUES:
   1. Regenera el PDF (v9, v10, etc.) en output/
   2. Ejecuta este script de nuevo
   3. Sube la nueva release con:
        gh release create vFECHA dist/catalogo-yolitia.pdf
==============================================================================
EOF
