"""
Sincroniza el último PDF generado en output/ con el directorio public/
para que el subdominio (catalogo.yolitia.bio) lo sirva con nombre estable.

Uso:
    python scripts/publish_catalog.py
    python scripts/publish_catalog.py --pdf output/catalogo_yolitia_v9.pdf
    python scripts/publish_catalog.py --url https://catalogo.yolitia.bio --regen-card

El nombre del PDF publicado SIEMPRE es 'catalogo-yolitia.pdf' para que la
URL/QR no cambien. Solo se reemplaza el archivo.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "output"
DIST_DIR = BASE_DIR / "dist"
PUBLIC_DIR = BASE_DIR / "public"
ASSETS_DIR = BASE_DIR / "assets" / "images"

DEFAULT_URL = "https://catalogo.yolitia.bio"
DIST_PDF = DIST_DIR / "catalogo-yolitia.pdf"


def find_latest_pdf() -> Path:
    pdfs = sorted(OUTPUT_DIR.glob("catalogo_yolitia_v*.pdf"))
    if not pdfs:
        raise SystemExit(f"No se encontraron PDFs en {OUTPUT_DIR}")
    return pdfs[-1]


def stage_pdf(src: Path, dst: Path) -> int:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst.stat().st_size


def ensure_logo_in_public() -> None:
    target = PUBLIC_DIR / "assets" / "logo.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    src = ASSETS_DIR / "logo.png"
    if src.exists():
        shutil.copy2(src, target)


def regen_card(url: str) -> None:
    script = BASE_DIR / "scripts" / "generate_qr_card.py"
    subprocess.check_call([sys.executable, str(script), "--url", url])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", type=Path, default=None, help="PDF fuente (por defecto: el más reciente en output/)")
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--regen-card", action="store_true", help="Regenera la tarjeta con QR")
    args = ap.parse_args()

    src = args.pdf or find_latest_pdf()
    if not src.exists():
        raise SystemExit(f"No existe el PDF fuente: {src}")

    size = stage_pdf(src, DIST_PDF)
    ensure_logo_in_public()
    print(f"OK staged PDF: {DIST_PDF}  ({size/1024/1024:.2f} MB)  source={src.name}")
    print("   Subir a GitHub como release para que el sitio lo sirva:")
    print("     gh release create v<fecha> dist/catalogo-yolitia.pdf --title 'Catalogo Yolitia'")
    print("   O arrastrar el archivo a https://github.com/<owner>/<repo>/releases/new")

    if args.regen_card:
        regen_card(args.url)


if __name__ == "__main__":
    main()
