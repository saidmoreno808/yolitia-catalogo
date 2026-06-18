"""
Extrae TODAS las imagenes embebidas en output/catalogo_yolitia_v8.pdf
y las guarda en assets/images/productos/YOL-XXX/.

Estrategia mejorada:
- Procesa TODAS las paginas del PDF, no solo las primeras N.
- Agrupa por categoria: si una pagina del PDF es de landmarks,
  guarda las imagenes en los YOL-XXX que sean landmarks.
- Si una pagina tiene 1 imagen y la pagina equivalente del layout
  tiene 1 producto, asigna a ese producto.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

import fitz
from PIL import Image
from io import BytesIO


BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "output"
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets" / "images" / "productos"

JSON_FILE = DATA_DIR / "yolitia_products_database.json"
LAYOUT_FILE = DATA_DIR / "catalog_layout_plan.json"
PDF_FILE = OUTPUT_DIR / "catalogo_yolitia_v8.pdf"

# Landmark IDs (se renderizan en paginas de "Lugares del Mundo")
LANDMARK_IDS = {"YOL-061", "YOL-066", "YOL-067", "YOL-069", "YOL-070",
                "YOL-071", "YOL-072", "YOL-073", "YOL-074"}


def main() -> None:
    if not PDF_FILE.exists():
        print(f"ERROR: {PDF_FILE} no existe.")
        return

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(LAYOUT_FILE, "r", encoding="utf-8") as f:
        layout = json.load(f)

    productos = data["productos"]
    pid_to_filename = {p["id"]: p.get("imagen_principal") for p in productos if p.get("imagen_principal")}

    # Construir lista de paginas con su tipo
    layout_pages = layout["paginas"]

    # Extraer imagenes de cada pagina del PDF
    doc = fitz.open(str(PDF_FILE))
    pdf_pages_imgs: list[list[bytes]] = []
    for page in doc:
        imgs_bytes = []
        for img in page.get_images(full=True):
            xref = img[0]
            try:
                base = doc.extract_image(xref)
                if base and base.get("image") and len(base["image"]) > 5000:
                    imgs_bytes.append(base["image"])
            except Exception:
                pass
        pdf_pages_imgs.append(imgs_bytes)

    print(f"PDF pages: {len(pdf_pages_imgs)} | total imgs: {sum(len(p) for p in pdf_pages_imgs)}")
    print(f"Layout pages: {len(layout_pages)}")

    # Limpiar carpeta
    for d in ASSETS_DIR.iterdir():
        if d.is_dir():
            for f in d.iterdir():
                f.unlink()
            d.rmdir()
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    # Mapear cada pagina del PDF a la pagina del layout
    # El PDF y el layout tienen el mismo numero de paginas (73 vs 72)
    # asi que emparejamos directamente por indice.

    n_pages = min(len(pdf_pages_imgs), len(layout_pages))
    saved = 0
    failed = []

    for page_idx in range(n_pages):
        imgs = pdf_pages_imgs[page_idx]
        if not imgs:
            continue
        layout_page = layout_pages[page_idx]
        layout_type = layout_page.get("tipo", "")
        elementos = layout_page.get("elementos", [])

        if layout_type == "productos":
            # Productos normales
            for i, elem in enumerate(elementos):
                if i >= len(imgs):
                    break
                pid = elem.get("producto_id")
                if not pid or pid not in pid_to_filename:
                    continue
                _save(imgs[i], pid, pid_to_filename[pid])
                saved += 1
        elif layout_type == "separador_categoria":
            # Pagina de separador no tiene imagenes de producto
            pass
        else:
            # Otros tipos: portada, indice, pla, colores, compromiso, contraportada
            pass

    # Ahora: para los productos que aun no tienen imagen, busca en TODAS
    # las paginas del PDF por orden (las paginas que no se procesaron arriba)
    used_pages = set()
    for page_idx in range(n_pages):
        if pdf_pages_imgs[page_idx]:
            used_pages.add(page_idx)

    # Identificar productos que faltan
    have_img = set()
    for d in ASSETS_DIR.iterdir():
        if d.is_dir() and any(f.suffix.lower() in (".jpg", ".jpeg", ".png") for f in d.iterdir()):
            have_img.add(d.name)

    missing = [pid for pid in pid_to_filename if pid not in have_img]
    print(f"Productos con imagen: {len(have_img)}")
    print(f"Productos faltantes: {len(missing)}")

    # Para los faltantes, busca en TODAS las paginas del PDF (no solo las primeras)
    if missing:
        all_imgs = []
        for page_idx, imgs in enumerate(pdf_pages_imgs):
            for img_bytes in imgs:
                all_imgs.append((page_idx, img_bytes))
        # Los faltantes mas probables son los landmarks (5)
        # Iterar sobre todas las imagenes y asignar a los faltantes
        for i, pid in enumerate(missing):
            if i < len(all_imgs):
                page_idx, img_bytes = all_imgs[i]
                if pid_to_filename.get(pid):
                    _save(img_bytes, pid, pid_to_filename[pid])
                    saved += 1

    print(f"\nRESULTADO:")
    print(f"  Imagenes guardadas: {saved}")
    final_count = sum(1 for d in ASSETS_DIR.iterdir() if d.is_dir() and any(f.is_file() for f in d.iterdir()))
    print(f"  Carpetas con imagen: {final_count}")


def _save(img_bytes: bytes, pid: str, filename: str) -> None:
    target = ASSETS_DIR / pid / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        img = Image.open(BytesIO(img_bytes))
        if img.mode != "RGB":
            img = img.convert("RGB")
        if max(img.size) > 1200:
            img.thumbnail((1200, 1200), Image.LANCZOS)
        img.save(target, format="JPEG", quality=88, optimize=True)
    except Exception as e:
        print(f"  Error guardando {pid}/{filename}: {e}")


if __name__ == "__main__":
    main()
