"""
Extrae las imagenes embebidas en output/catalogo_yolitia_v8.pdf
y las guarda en assets/images/productos/YOL-XXX/.

El PDF v8 se genero cuando las imagenes SI estaban en disco, asi que
contiene todas las imagenes. Las extraemos y las reescribimos al disco
para que el catalogo v9 (vertical) pueda reutilizarlas.

Estrategia: iterar el PDF pagina por pagina. Cada pagina tiene N imagenes
que corresponden a los productos listados. Emparejamos por orden con el
JSON de productos.
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
PDF_FILE = OUTPUT_DIR / "catalogo_yolitia_v8.pdf"


def main() -> None:
    if not PDF_FILE.exists():
        print(f"ERROR: {PDF_FILE} no existe. No se puede extraer.")
        return

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Construir lista de productos en el orden en que aparecen en el JSON
    productos = data["productos"]
    product_ids = [p["id"] for p in productos]
    print(f"Productos en JSON: {len(product_ids)}")

    # Mapear pid -> imagen_principal filename esperado
    pid_to_filename: dict[str, str] = {}
    for p in productos:
        # Cada producto tiene imagen_principal apuntando al filename
        ip = p.get("imagen_principal")
        if ip:
            pid_to_filename[p["id"]] = ip
    print(f"Productos con imagen_principal: {len(pid_to_filename)}")

    # Extraer todas las imagenes del PDF
    doc = fitz.open(str(PDF_FILE))
    all_extracted: list[bytes] = []
    for page in doc:
        for img in page.get_images(full=True):
            xref = img[0]
            try:
                base = doc.extract_image(xref)
                if base and base.get("image"):
                    all_extracted.append(base["image"])
            except Exception:
                pass
    print(f"Imagenes extraidas del PDF: {len(all_extracted)}")

    # Emparejar: las primeras imagenes del PDF corresponden al primer
    # producto de cada pagina. Como el orden de insercion del script v8
    # es: portada, indice, separador, productos por categoria...
    # necesitamos una heuristica mejor: agrupar por tamano o hash,
    # o usar la posicion de la imagen en la pagina.

    # Mejor estrategia: extraer por pagina y mapear segun los productos
    # que el layout_plan dice que estan en esa pagina.
    layout_file = DATA_DIR / "catalog_layout_plan.json"
    if not layout_file.exists():
        print(f"ERROR: {layout_file} no existe.")
        return

    with open(layout_file, "r", encoding="utf-8") as f:
        layout = json.load(f)

    # Por cada pagina, anotar que productos tiene
    page_products: list[list[str]] = []  # page index -> [pids]
    for p in layout["paginas"]:
        if p["tipo"] == "productos":
            page_products.append([e["producto_id"] for e in p.get("elementos", [])])
        else:
            page_products.append([])

    print(f"Paginas en layout: {len(page_products)}")

    # Iterar el PDF pagina por pagina, extraer imagenes, asignar a productos
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    # Limpiar carpetas existentes
    for d in ASSETS_DIR.iterdir():
        if d.is_dir():
            for f in d.iterdir():
                f.unlink()
            d.rmdir()

    extracted_per_page: list[list[bytes]] = []
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
        extracted_per_page.append(imgs_bytes)

    print(f"Imagenes por pagina (primeras 5): {[len(p) for p in extracted_per_page[:5]]}")

    # Emparejar: si la pagina N del layout dice [P1, P2] y la pagina
    # correspondiente del PDF tiene 2 imagenes, asignamos.
    # El PDF tiene menos paginas que el layout (algunas son sin imagenes
    # como portada, indice, separador, pla, colores, compromiso, contraportada)
    # asi que tenemos que mapear inteligentemente.

    # Forma mas simple: para cada pagina del PDF con imagenes, mirar el
    # orden de productos en el layout. El PDF v8 sigue el mismo orden
    # que el layout.

    # Vamos a iterar el PDF en orden y consumir productos del layout segun
    # el orden del layout.

    # Crear un iterador sobre las paginas del PDF con imagenes
    pdf_page_iter = iter(range(len(doc)))
    products_to_assign: list[str] = []  # cola de productos que necesitan imagen
    saved = 0
    failed = []

    for page_idx, page in enumerate(doc):
        if page_idx >= len(page_products):
            break
        pids = page_products[page_idx]
        if not pids:
            continue
        # Extraer imagenes de esta pagina del PDF
        imgs_bytes = []
        for img in page.get_images(full=True):
            xref = img[0]
            try:
                base = doc.extract_image(xref)
                if base and base.get("image") and len(base["image"]) > 5000:
                    imgs_bytes.append(base["image"])
            except Exception:
                pass
        # Asignar las primeras len(pids) imagenes a los productos
        for i, pid in enumerate(pids):
            if i >= len(imgs_bytes):
                failed.append(pid)
                continue
            filename = pid_to_filename.get(pid, f"{pid}_principal_01.jpg")
            target = ASSETS_DIR / pid / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                img = Image.open(BytesIO(imgs_bytes[i]))
                if img.mode != "RGB":
                    img = img.convert("RGB")
                # Normalizar tamano max 1200px
                if max(img.size) > 1200:
                    img.thumbnail((1200, 1200), Image.LANCZOS)
                img.save(target, format="JPEG", quality=88, optimize=True)
                saved += 1
            except Exception as e:
                failed.append(pid)
                print(f"  Error guardando {pid}: {e}")

    print(f"\nRESULTADO:")
    print(f"  Imagenes guardadas: {saved}")
    print(f"  Productos sin imagen: {len(failed)}")
    if failed:
        print(f"  Primeros fallidos: {failed[:10]}")


if __name__ == "__main__":
    main()
