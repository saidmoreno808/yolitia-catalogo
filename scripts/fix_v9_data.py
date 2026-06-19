"""
Corrige TODOS los problemas de datos en el catálogo v9:

1. Genera imagenes placeholder para productos sin imagen real
   (los 8 que fallaron descarga y quedaron con imagen incorrecta).
2. Genera descripciones automaticas para productos sin descripcion_corta/larga,
   basadas en categoria + nombre.
3. Re-traductor de los 2 productos faltantes (YOL-061, YOL-141).
4. Asigna precios por defecto segun la categoria (cuando precio es null).
5. Genera imagenes placeholder con el NOMBRE del producto (no solo "modelo blanco").

Las imagenes placeholder se generan con un diseno limpio y elegante:
fondo crema (#F5F0E6), tipografia display, isotopo decorativo, y nombre del producto
en color verde yolitia.  Esto da una apariencia profesional al catalogo en lugar
de mostrar polaroids vacios.
"""
from __future__ import annotations

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = BASE_DIR / "assets" / "images" / "productos"
JSON_FILE = DATA_DIR / "yolitia_products_database.json"


# Traducciones faltantes (productos que quedaron sin traducir)
TRADUCCIONES_FALTANTES = {
    "Popocatepetl Mexico City Volcano Topographic Map": "Popocatépetl CDMX - Mapa Topográfico Volcánico",
    "Kpop Demon Hunters Coloring Panel 2 Craft Diy": "Panel para Colorear Kpop Demon Hunters",
}


# Descripciones automaticas por categoria (cuando el producto no tiene descripcion)
DESCRIPCIONES_POR_CATEGORIA = {
    "Organización": "Organiza tus objetos cotidianos con un diseño único, impreso en PLA biodegradable. Pieza funcional y decorativa hecha bajo pedido.",
    "Decoración": "Figura decorativa impresa en 3D con PLA biodegradable. Líneas limpias y acabados mate que se adaptan a cualquier espacio.",
    "Iluminación": "Lámpara impresa en 3D con PLA biodegradable. Difunde luz cálida con un diseño único hecho a la medida de tu espacio.",
    "Joyería": "Pieza de joyería impresa en 3D con PLA biodegradable. Liviana, resistente y con un diseño exclusivo hecho bajo pedido.",
    "Fidget": "Fidget impreso en 3D con PLA biodegradable. Mecanismo de impresión en sitio (print-in-place), sin ensamblaje, listo para usar.",
    "Llaveros": "Llavero impreso en 3D con PLA biodegradable. Diseño único, resistente y ligero, hecho bajo pedido.",
    "Relojes": "Reloj impreso en 3D con PLA biodegradable. Mecanismo estándar y diseño minimalista hecho a la medida.",
    "Toppers": "Topper decorativo impreso en 3D con PLA biodegradable. Personalizado para tu evento y hecho bajo pedido.",
    "Hogar": "Objeto para el hogar impreso en 3D con PLA biodegradable. Diseño funcional y decorativo hecho bajo pedido.",
    "Lugares": "Miniatura arquitectónica de un lugar icónico, impresa en 3D con PLA biodegradable. Edición limitada, hecha bajo pedido.",
    "Niños": "Objeto imprimible para niños, fabricado en PLA biodegradable. Diseño seguro, ligero y colorido, hecho bajo pedido.",
    "Tarjetas": "Tarjeta decorativa impresa en 3D con PLA biodegradable. Grabado fino y acabados mate, ideal como regalo o detalle personal.",
    "Estaciones": "Pieza decorativa de temporada impresa en 3D con PLA biodegradable. Diseño único hecho bajo pedido.",
}


# Precios por defecto segun subcategoria
PRECIOS_POR_SUBCATEGORIA = {
    "Aretes": 80,
    "Pulseras": 100,
    "Collares": 120,
    "Llaveros": 50,
    "Fidget": 100,
    "Toppers": 100,
    "Topper": 100,
    "Lámpara": 350,
    "Lampara": 350,
    "Reloj": 200,
    "Maceta": 150,
    "Organizador": 150,
    "Joyero": 200,
    "Calavera": 150,
    "Figura": 200,
    "Miniatura": 250,
    "Pirámide": 250,
    "Rompecabezas": 150,
    "Trofeo": 250,
    "Tarjeta": 100,
    "Estante": 150,
    "Globo": 150,
    "Soporte": 100,
    "Llavero": 50,
    "Popocatépetl": 250,
    "Volcán": 250,
    "Torre": 250,
    "Castillo": 250,
    "Catedral": 250,
}


def obtener_precio(subcategoria: str, nombre: str) -> int:
    """Devuelve un precio por defecto basado en subcategoria o nombre."""
    texto = f"{subcategoria or ''} {nombre or ''}".lower()
    for key, val in PRECIOS_POR_SUBCATEGORIA.items():
        if key.lower() in texto:
            return val
    return 100  # default


def obtener_descripcion(categoria: str, subcategoria: str, nombre: str) -> str:
    """Genera una descripcion a partir de la categoria."""
    texto = f"{categoria or ''} {subcategoria or ''} {nombre or ''}".lower()

    # Primero intenta por subcategoria
    if subcategoria:
        for key, val in DESCRIPCIONES_POR_CATEGORIA.items():
            if key.lower() in subcategoria.lower():
                return val

    # Luego por categoria
    if categoria:
        for key, val in DESCRIPCIONES_POR_CATEGORIA.items():
            if key.lower() in categoria.lower():
                return val

    # Fallback por palabras clave en el nombre
    if "llavero" in texto:
        return DESCRIPCIONES_POR_CATEGORIA["Llaveros"]
    if "arete" in texto or "pendiente" in texto:
        return DESCRIPCIONES_POR_CATEGORIA["Joyería"]
    if "fidget" in texto:
        return DESCRIPCIONES_POR_CATEGORIA["Fidget"]
    if "lámpara" in texto or "lampara" in texto or "vela" in texto:
        return DESCRIPCIONES_POR_CATEGORIA["Iluminación"]
    if "reloj" in texto:
        return DESCRIPCIONES_POR_CATEGORIA["Relojes"]
    if "topper" in texto:
        return DESCRIPCIONES_POR_CATEGORIA["Toppers"]
    if "pirámide" in texto or "templo" in texto or "catedral" in texto or "castillo" in texto or "volcán" in texto or "mapa" in texto:
        return DESCRIPCIONES_POR_CATEGORIA["Lugares"]
    if "tarjeta" in texto:
        return DESCRIPCIONES_POR_CATEGORIA["Tarjetas"]

    return "Pieza única impresa en 3D con PLA biodegradable, hecha bajo pedido con acabados mate y un diseño cuidado en cada detalle."


def generar_imagen_placeholder(producto_id: str, nombre: str) -> Path:
    """Genera un placeholder elegante con el nombre del producto."""
    size = 1000
    img = Image.new("RGB", (size, size), color=(245, 240, 230))  # crema
    draw = ImageDraw.Draw(img)

    # Borde exterior sutil
    draw.rectangle([12, 12, size - 12, size - 12], outline=(220, 210, 195), width=2)
    # Borde interno
    draw.rectangle([28, 28, size - 28, size - 28], outline=(220, 210, 195), width=1)

    # Cargar fuente (Windows / Linux / Mac)
    candidates = [
        r"C:\Windows\Fonts\georgia.ttf",
        r"C:\Windows\Fonts\Georgia.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        r"/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        r"/System/Library/Fonts/Georgia.ttf",
        r"/Library/Fonts/Georgia.ttf",
    ]
    font_path = next((p for p in candidates if Path(p).exists()), None)
    title_font = ImageFont.truetype(font_path, 56) if font_path else ImageFont.load_default()
    small_font = ImageFont.truetype(font_path, 28) if font_path else ImageFont.load_default()
    brand_font = ImageFont.truetype(font_path, 22) if font_path else ImageFont.load_default()

    # Isotopo decorativo (circulo + hojas) - simple
    cx, cy = size // 2, size // 2 - 80
    draw.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], outline=(112, 130, 90), width=2)
    draw.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], outline=(112, 130, 90), width=1)

    # Wrap del nombre en lineas de max ~22 chars
    palabras = nombre.split()
    lineas = []
    linea_actual = ""
    max_chars = 22
    for palabra in palabras:
        test = (linea_actual + " " + palabra).strip()
        if len(test) <= max_chars:
            linea_actual = test
        else:
            if linea_actual:
                lineas.append(linea_actual)
            linea_actual = palabra
    if linea_actual:
        lineas.append(linea_actual)

    # Limitar a 4 lineas
    if len(lineas) > 4:
        lineas = lineas[:3] + [lineas[3] + "..."]

    # Centrar verticalmente
    total_h = len(lineas) * 70
    start_y = cy + 100 - total_h // 2
    for i, linea in enumerate(lineas):
        bbox = draw.textbbox((0, 0), linea, font=title_font)
        tw = bbox[2] - bbox[0]
        x = (size - tw) // 2
        y = start_y + i * 70
        draw.text((x, y), linea, fill=(60, 60, 60), font=title_font)

    # ID del producto (esquina)
    draw.text((50, size - 80), f"YOL-{producto_id.split('-')[1]}", fill=(112, 130, 90), font=brand_font)
    # Brand
    bbox = draw.textbbox((0, 0), "YOLITIA", font=small_font)
    tw = bbox[2] - bbox[0]
    draw.text((size - tw - 50, size - 80), "YOLITIA", fill=(112, 130, 90), font=small_font)

    # Guardar
    out_path = IMAGES_DIR / producto_id / f"{producto_id}_principal_01.jpg"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out_path), "JPEG", quality=92, optimize=True)
    return out_path


def detectar_imagenes_duplicadas():
    """Detecta pares de productos con la misma imagen (md5)."""
    import hashlib
    from collections import defaultdict

    hashes = defaultdict(list)
    for d in IMAGES_DIR.iterdir():
        if d.is_dir():
            for f in d.iterdir():
                if f.suffix.lower() in (".jpg", ".jpeg", ".png"):
                    h = hashlib.md5(f.read_bytes()).hexdigest()
                    hashes[h].append((d.name, f))

    return {h: files for h, files in hashes.items() if len(files) > 1}


def main():
    print("=" * 70)
    print("FIX V9 - DATOS DEL CATALOGO")
    print("=" * 70)

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    productos = data["productos"]

    # 1. Re-traducir faltantes
    print("\n[1/5] Re-traduciendo faltantes...")
    for prod in productos:
        orig = prod.get("nombre_original", "")
        if orig in TRADUCCIONES_FALTANTES:
            nuevo = TRADUCCIONES_FALTANTES[orig]
            if prod.get("nombre_yolitia") != nuevo:
                prod["nombre_yolitia"] = nuevo
                print(f"  {orig[:50]} -> {nuevo}")

    # 2. Generar descripciones
    print("\n[2/5] Generando descripciones...")
    desc_added = 0
    for prod in productos:
        cat = prod.get("categoria", "")
        sub = prod.get("subcategoria", "")
        nombre = prod.get("nombre_yolitia") or prod.get("nombre_original", "")
        if not prod.get("descripcion_corta") and not prod.get("descripcion_larga"):
            desc = obtener_descripcion(cat, sub, nombre)
            prod["descripcion_corta"] = desc
            desc_added += 1
    print(f"  Descripciones generadas: {desc_added}")

    # 3. Asignar precios por defecto
    print("\n[3/5] Asignando precios faltantes...")
    price_added = 0
    for prod in productos:
        if not prod.get("precio"):
            sub = prod.get("subcategoria", "")
            nombre = prod.get("nombre_yolitia", "")
            nuevo_precio = obtener_precio(sub, nombre)
            prod["precio"] = nuevo_precio
            price_added += 1
    print(f"  Precios asignados: {price_added}")

    # 4. Detectar y corregir imagenes duplicadas
    print("\n[4/5] Detectando imagenes duplicadas...")
    dups = detectar_imagenes_duplicadas()
    # Estrategia: por cada grupo de duplicados, conservar solo el primero
    # y generar placeholders para los demas.
    # Excepcion: si el grupo contiene un landmark (YOL-061, 066, 067, 069, 070, 071, 072, 073, 074),
    # conservar el landmark y regenerar el resto.
    # Excepcion: si el grupo es producto de asignacion automatica (no real),
    # regenerar TODAS las imagenes con placeholder.
    LANDMARKS = {"YOL-061", "YOL-066", "YOL-067", "YOL-069", "YOL-070",
                 "YOL-071", "YOL-072", "YOL-073", "YOL-074"}

    # Productos que perdieron su imagen original por fallos 403 de makerworld.
    # Sus duplicados no representan al producto. Regenerar TODAS sus imagenes.
    PRODUCTOS_FALLBACK = set()
    try:
        with open(DATA_DIR / "download_failures.json", "r", encoding="utf-8") as f:
            fallos = json.load(f)
        for x in fallos:
            fname = x.get("filename", "")
            if fname.startswith("YOL-"):
                pid = fname.split("_")[0]
                PRODUCTOS_FALLBACK.add(pid)
    except Exception:
        pass

    imgs_regen = 0
    for h, files in dups.items():
        pids = [pid for pid, _ in files]
        nombres_productos = {p["id"]: (p.get("nombre_yolitia") or p.get("nombre_original") or p["id"])
                              for p in productos}

        # Si todo el grupo es de productos con download_failed, regenerar TODOS
        if all(pid in PRODUCTOS_FALLBACK for pid in pids):
            for pid, fpath in files:
                nombre = nombres_productos.get(pid, pid)
                generar_imagen_placeholder(pid, nombre)
                imgs_regen += 1
                print(f"  Regenerada imagen para {pid} (grupo entero era fallback)")
            continue

        # Si el grupo incluye un landmark, conservar el landmark
        landmark_in_group = [pid for pid in pids if pid in LANDMARKS]
        if landmark_in_group:
            keep = landmark_in_group[0]
        else:
            keep = pids[0]

        # Regenerar imagen para los demas
        for pid, fpath in files:
            if pid == keep:
                continue
            # Generar placeholder
            nombre = nombres_productos.get(pid, pid)
            generar_imagen_placeholder(pid, nombre)
            imgs_regen += 1
            print(f"  Regenerada imagen para {pid} (duplicaba con {keep})")
    print(f"  Imagenes regeneradas: {imgs_regen}")

    # 5. Generar imagenes para productos que no tienen ninguna
    print("\n[5/5] Verificando que todos los productos tengan imagen...")
    sin_img = 0
    nombres_productos = {p["id"]: (p.get("nombre_yolitia") or p.get("nombre_original") or p["id"])
                          for p in productos}
    for prod in productos:
        pid = prod["id"]
        folder = IMAGES_DIR / pid
        if not folder.exists() or not any(f.suffix.lower() in (".jpg", ".jpeg", ".png") for f in folder.iterdir()):
            nombre = nombres_productos.get(pid, pid)
            generar_imagen_placeholder(pid, nombre)
            sin_img += 1
            print(f"  Imagen creada para {pid} (no tenia ninguna)")
    print(f"  Imagenes creadas desde cero: {sin_img}")

    # Guardar cambios
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print("RESUMEN")
    print(f"  Descripciones generadas: {desc_added}")
    print(f"  Precios asignados:       {price_added}")
    print(f"  Imagenes regeneradas:    {imgs_regen}")
    print(f"  Imagenes desde cero:     {sin_img}")
    print("=" * 70)


if __name__ == "__main__":
    main()
