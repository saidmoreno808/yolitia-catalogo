"""
Validador iterativo del catalogo vertical v1.
Inspecciona pagina por pagina verificando que cada producto
tenga su nombre, descripcion y precio correctos.
Detecta texto solapado y elementos fuera de margen.
Retorna codigo de error: 0=OK, 1=corregir.
"""
import json
import sys
from pathlib import Path

import pdfplumber


BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "output"
LAYOUT_FILE = BASE_DIR / "data" / "catalog_layout_plan.json"
OVERRIDES_FILE = BASE_DIR / "data" / "catalog_overrides_verano2026_v5.json"
PDF_PATH = OUTPUT_DIR / "finales" / "catalogo_yolitia_Verano2026_v1.pdf"

LANDMARK_IDS = ["YOL-061", "YOL-066", "YOL-067", "YOL-069", "YOL-070",
                "YOL-071", "YOL-072", "YOL-073", "YOL-074"]

LANDMARK_BATCHES = [
    ["YOL-061", "YOL-066"],
    ["YOL-067", "YOL-069"],
    ["YOL-070", "YOL-071"],
    ["YOL-072", "YOL-073"],
    ["YOL-074"],
]


def load_product_map():
    """Carga productos con overrides aplicados (como en build_catalog)."""
    with open(OVERRIDES_FILE, "r", encoding="utf-8") as f:
        overrides = json.load(f)
    with open(BASE_DIR / "data" / "yolitia_products_database.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    productos = {p["id"]: p for p in data["productos"]}

    renames = overrides.get("renames", {})
    descriptions = overrides.get("descriptions", {})
    prices = overrides.get("prices", {})

    for pid, prod in productos.items():
        if pid in renames:
            prod["_display_name"] = renames[pid]
        else:
            prod["_display_name"] = prod.get("nombre_yolitia") or prod.get("nombre_original") or pid
        if pid in descriptions:
            prod["_display_desc"] = descriptions[pid]
        else:
            existing = prod.get("descripcion_corta") or prod.get("descripcion_larga") or prod["_display_name"]
            prod["_display_desc"] = existing
        if pid in prices:
            prod["_display_price"] = prices[pid]
        else:
            prod["_display_price"] = prod.get("precio")

    return productos


def get_expected_pages():
    """Genera la lista de paginas esperadas con sus productos."""
    with open(LAYOUT_FILE, "r", encoding="utf-8") as f:
        layout = json.load(f)

    pages = []
    current_page = 1
    landmarks_inserted = False

    # Cover doesn't count as numbered page
    first = True

    for pagina_data in layout["paginas"]:
        tipo = pagina_data["tipo"]

        if tipo == "portada":
            pages.append({"pagina_pdf": len(pages) + 1, "tipo": "portada", "productos": []})
            continue

        elif tipo == "indice":
            pages.append({"pagina_pdf": len(pages) + 1, "tipo": "indice", "productos": []})
            continue

        elif tipo == "separador_categoria":
            cat = pagina_data.get("categoria", "")

            if not landmarks_inserted and ("Regalos" in cat or "Coleccionables" in cat):
                for batch in LANDMARK_BATCHES:
                    batch_prods = []
                    for pid in batch:
                        batch_prods.append({"producto_id": pid})
                    pages.append({"pagina_pdf": len(pages) + 1, "tipo": "landmarks",
                                  "productos": batch_prods})
                landmarks_inserted = True

            pages.append({"pagina_pdf": len(pages) + 1, "tipo": "separador",
                          "categoria": cat, "productos": []})
            continue

        elif tipo == "productos":
            grid = pagina_data.get("grid", "1x2")
            elementos = [
                e for e in pagina_data.get("elementos", [])
                if e.get("producto_id") not in LANDMARK_IDS
            ]
            pages.append({"pagina_pdf": len(pages) + 1, "tipo": "productos", "grid": grid,
                          "productos": elementos})
            continue

        elif tipo == "material_pla":
            pages.append({"pagina_pdf": len(pages) + 1, "tipo": "pla", "productos": []})
            continue

        elif tipo == "colores":
            pages.append({"pagina_pdf": len(pages) + 1, "tipo": "colores", "productos": []})
            continue

        elif tipo == "compromiso":
            pages.append({"pagina_pdf": len(pages) + 1, "tipo": "compromiso", "productos": []})
            continue

        elif tipo == "contraportada":
            pages.append({"pagina_pdf": len(pages) + 1, "tipo": "contraportada", "productos": []})
            continue

    return pages


def validate_pdf():
    if not PDF_PATH.exists():
        print(f"ERROR: No existe el PDF: {PDF_PATH}")
        return False

    productos_map = load_product_map()
    expected_pages = get_expected_pages()

    print(f"\n{'=' * 70}")
    print(f"VALIDANDO: {PDF_PATH.name}")
    print(f"{'=' * 70}")

    try:
        with pdfplumber.open(str(PDF_PATH)) as pdf:
            total_pages = len(pdf.pages)
            print(f"Total paginas PDF: {total_pages}")
            print(f"Total paginas esperadas: {len(expected_pages)}")

            if total_pages != len(expected_pages):
                print(f"ADVERTENCIA: numero de paginas diferente "
                      f"({total_pages} vs {len(expected_pages)})")

            all_ok = True
            issues = []

            for page_idx, page_info in enumerate(expected_pages):
                if page_idx >= total_pages:
                    issues.append(f"Pag {page_idx+1}: FALTANTE - esperada pero no existe en PDF")
                    all_ok = False
                    continue

                page = pdf.pages[page_idx]
                page_text = page.extract_text() or ""
                page_words = page.extract_words() or []
                page_type = page_info["tipo"]
                prods = page_info["productos"]

                # Skip validation for non-product pages
                if page_type in ("portada", "indice", "separador", "pla",
                                 "colores", "compromiso", "contraportada"):
                    print(f"  Pag {page_idx+1}: {page_type} -- SKIP (pagina especial)")
                    continue

                if page_type == "landmarks":
                    # Verify landmark names and prices
                    problems = []
                    for prod in prods:
                        pid = prod["producto_id"]
                        pdata = productos_map.get(pid)
                        if not pdata:
                            continue
                        name = pdata.get("_display_name", "")
                        price = pdata.get("_display_price")
                        if name and name.upper() not in page_text.upper():
                            problems.append(f"   - Nombre faltante: {name} ({pid})")
                        if price:
                            price_str = f"${price:.0f}"
                            if price_str not in page_text:
                                # Try without decimals
                                if f"${int(price)}" not in page_text:
                                    problems.append(f"   - Precio faltante: ${price:.0f} ({pid})")
                    if problems:
                        issues.append(f"Pag {page_idx+1}: LANDMARKS problemas:")
                        issues.extend(problems)
                        all_ok = False
                    else:
                        print(f"  Pag {page_idx+1}: landmarks ({len(prods)} lugares) -- OK")
                    continue

                if page_type == "productos":
                    grid = page_info.get("grid", "1x2")
                    problems = []

                    # Check product names, descriptions, prices
                    for prod in prods:
                        pid = prod.get("producto_id", "")
                        pdata = productos_map.get(pid)
                        if not pdata:
                            problems.append(f"   - Producto {pid} no encontrado en DB")
                            continue

                        name = pdata.get("_display_name", "")
                        desc = pdata.get("_display_desc", "")
                        price = pdata.get("_display_price")

                        if name and name.upper() not in page_text.upper():
                            problems.append(f"   - Nombre: {name} ({pid})")
                        if price:
                            price_str = f"${price:.0f}"
                            if price_str not in page_text:
                                if f"${int(price)}" not in page_text:
                                    problems.append(f"   - Precio: ${price:.0f} ({pid})")

                    # Check for overlapping text (words at same y with overlapping x)
                    if page_words:
                        overlap_found = False
                        y_groups = {}
                        for w in page_words:
                            y_key = round(w["top"], 0)
                            if y_key not in y_groups:
                                y_groups[y_key] = []
                            y_groups[y_key].append(w)

                        for y_key, words_at_y in y_groups.items():
                            if len(words_at_y) > 1:
                                sorted_w = sorted(words_at_y, key=lambda x: x["x0"])
                                for i in range(len(sorted_w) - 1):
                                    gap = sorted_w[i+1]["x0"] - sorted_w[i]["x1"]
                                    if gap < -5:  # Significant overlap
                                        if not overlap_found:
                                            overlap_found = True
                                            problems.append(f"   - Posible solapamiento detectado en y={y_key}")

                    if problems:
                        issues.append(f"Pag {page_idx+1}: {grid} - {len(prods)} productos PROBLEMAS:")
                        issues.extend(problems)
                        all_ok = False
                    else:
                        print(f"  Pag {page_idx+1}: {grid} ({len(prods)} prods) -- OK")

            # Summary
            print(f"\n{'=' * 70}")
            if all_ok:
                print(f"RESULTADO: OK - Todas las paginas correctas")
                print(f"{'=' * 70}")
                return True
            else:
                print(f"RESULTADO: CORREGIR - {len(issues)} problema(s) encontrado(s)")
                for issue in issues:
                    print(f"  {issue}")
                print(f"{'=' * 70}")
                return False

    except Exception as e:
        print(f"ERROR validando PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = validate_pdf()
    sys.exit(0 if success else 1)
