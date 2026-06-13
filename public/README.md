# YOLITIA — Subdominio del catálogo

Este directorio (`public/`) contiene el sitio estático que se sirve en
**https://catalogo.yolitia.bio** vía GitHub Pages.

## Qué hace

Cuando alguien escanea el QR (impreso en la tarjeta) o entra a la URL:

1. Ve una mini-página con el logo YOLITIA, el botón "Descargar catálogo"
   y la URL.
2. La página intenta disparar la descarga automáticamente del PDF
   `catalogo-yolitia.pdf` (el nombre del archivo es **estable**, nunca
   cambia).
3. Si la auto-descarga falla, el usuario hace clic en el botón y listo.

## Estructura

```
public/
├── index.html             # Landing con auto-descarga
├── catalogo-yolitia.pdf   # PDF del catálogo (se reemplaza al actualizar)
├── assets/
│   └── logo.png           # Logo YOLITIA
├── CNAME                  # catalogo.yolitia.bio
└── _redirects             # Reglas de redirección (Netlify-style, ignorado por GH Pages pero útil si migras)
```

## Actualizar el catálogo (sin que cambie la URL ni el QR)

```bash
# 1. Genera el nuevo PDF (ej. v9) en output/
python scripts/build_catalog_v9.py

# 2. Publica el PDF más reciente en public/ y regenera la tarjeta QR
python scripts/publish_catalog.py --regen-card
```

Sube los cambios a la rama `main` y GitHub Pages se actualiza solo
(vía el workflow en `.github/workflows/deploy.yml`).

## Generar solo la tarjeta con QR

```bash
python scripts/generate_qr_card.py --url https://catalogo.yolitia.bio
```

Salidas en `output/`:
- `yolitia_qr_card.pdf` — Tarjeta A6 lista para imprimir
- `yolitia_qr_card.png` — Vista previa
- `yolitia_qr.png`      — Solo el QR (alta resolución)

## Cambiar la URL del QR

Si en algún momento migras a otro subdominio o hosting, regenera todo:

```bash
python scripts/generate_qr_card.py --url https://otro-dominio.com
python scripts/publish_catalog.py --url https://otro-dominio.com --regen-card
```

## Dominio personalizado (catalogo.yolitia.bio)

En tu proveedor de DNS para `yolitia.bio`, crea un CNAME:

```
catalogo  CNAME  <usuario>.github.io
```

Y en GitHub → Settings → Pages → Custom domain escribe
`catalogo.yolitia.bio`. El archivo `public/CNAME` ya contiene ese valor.
