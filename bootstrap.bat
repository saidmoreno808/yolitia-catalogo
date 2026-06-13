@echo off
REM ============================================================================
REM YOLITIA — Bootstrap y publicacion del catalogo
REM Ejecuta este script desde C:\Users\djzai\Documents\Said Moreno\PDM\IA\yolitia\yolitia_catalog
REM ============================================================================

setlocal
cd /d "%~dp0"

echo.
echo [1/5] Preparando logo...
python scripts\prepare_logo.py
if errorlevel 1 goto :err

echo.
echo [2/5] Publicando PDF en dist/...
python scripts\publish_catalog.py
if errorlevel 1 goto :err

echo.
echo [3/5] Regenerando tarjeta con QR...
python scripts\generate_qr_card.py
if errorlevel 1 goto :err

echo.
echo [4/5] Verificando si es repo git...
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo     Inicializando repo...
    git init
    git checkout -b main 2>nul
    git config user.email "bot@yolitia.bio" 2>nul
    git config user.name "YOLITIA Bot" 2>nul
)

echo.
echo [5/5] Preparando commit...
git add .gitignore public\.github scripts assets\images\logo.png public\assets\logo.png 2>nul
git add .gitignore public .github scripts 2>nul
git add scripts assets\images\logo.png public\assets\logo.png 2>nul
git add .gitignore
git add public
git add .github
git add scripts
git add assets\images\logo.png public\assets\logo.png

git status --short
echo.
echo =============================================================================
echo  SIGUIENTE PASO MANUAL (solo la primera vez):
echo    1. Crear repo en https://github.com/new  (ej: yolitia/catalogo)
echo    2. git remote add origin https://github.com/TU-USUARIO/TU-REPO.git
echo    3. git push -u origin main
echo    4. Crear primera release arrastando dist\catalogo-yolitia.pdf a:
echo         https://github.com/TU-USUARIO/TU-REPO/releases/new
echo    5. En GitHub - Settings - Pages: activar Pages desde main / root
echo    6. Custom domain: catalogo.yolitia.bio  (configurar CNAME en tu DNS)
echo.
echo  PARA ACTUALIZAR EL CATALOGO DESPUES:
echo    1. Regenera el PDF (v9, v10, etc.) en output\
echo    2. Ejecuta este script de nuevo
echo    3. Sube la nueva release con: gh release create vFECHA dist\catalogo-yolitia.pdf
echo =============================================================================
goto :eof

:err
echo.
echo ERROR durante el bootstrap. Revisa los mensajes arriba.
exit /b 1
