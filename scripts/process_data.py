"""
Procesa datos de scraping de MakerWorld.
Extrae nombres de URLs, usa thumbnails del CDN, infiere categorías.
No requiere acceso a páginas individuales.
"""

import json
import re
from pathlib import Path
from datetime import datetime


DATA_DIR = Path(__file__).parent.parent / "data"
PROGRESS_FILE = DATA_DIR / "scraping_progress.json"
PROCESSED_FILE = DATA_DIR / "scraping_processed.json"


def slug_to_name(slug_url):
    parts = slug_url.rstrip("/").split("/")
    last = parts[-1] if parts else ""
    match = re.match(r'\d+-(.+)', last)
    if match:
        raw = match.group(1)
    else:
        raw = last
    raw = re.sub(r'[-_]+', ' ', raw)
    raw = re.sub(r'\b(no|ams|v\d+|mm|cm|pc)\b', '', raw, flags=re.IGNORECASE)
    raw = re.sub(r'\s+', ' ', raw).strip()
    return raw.title()


def get_model_id(url):
    parts = url.rstrip("/").split("/")
    last = parts[-1] if parts else ""
    match = re.match(r'(\d+)-', last)
    return match.group(1) if match else None


def get_thumbnail_hd(thumbnail_url):
    if not thumbnail_url:
        return None
    url = re.sub(r'x-oss-process=image/resize,w_\d+', 'x-oss-process=image/resize,w_1200', thumbnail_url)
    url = re.sub(r'format,webp', 'format,jpg', url)
    return url


def infer_category(name, url):
    text = f"{name} {url}".lower()
    
    rules = [
        ("Joyería & Accesorios", ["earring", "arete", "pendiente", "necklace", "collar", "pendant", "dije", "bracelet", "pulsera", "ring", "anillo", "brooch", "broche", "jewelry", "joyería", "jewel"]),
        ("Hogar & Decoración", ["pot", "maceta", "planter", "vase", "jarrón", "figure", "figura", "decorat", "sculptur", "sculptural", "home", "hogar", "lamp", "lámpara", "light", "luz", "candle", "vela", "tealight", "fossil", "petal", "veil"]),
        ("Organización", ["organizer", "organizador", "holder", "soporte", "storage", "almacen", "box", "caja", "tray", "bandeja", "jewelry box", "joyero", "toothbrush", "koozie"]),
        ("Regalos & Coleccionables", ["keychain", "llavero", "key chain", "figurine", "figurita", "collectible", "coleccionable", "gift", "regalo", "charm", "dije", "ornament", "skull", "calavera", "clock", "reloj"]),
        ("Entretenimiento", ["fidget", "toy", "juguete", "game", "juego", "puzzle", "rompecabezas", "spinner", "clicker", "toggle", "baseball", "bat", "glove"]),
    ]
    
    for cat, keywords in rules:
        for kw in keywords:
            if kw in text:
                return cat
    
    return "Regalos & Coleccionables"


def infer_subcategoria(name, categoria):
    text = name.lower()
    
    if categoria == "Joyería & Accesorios":
        if any(k in text for k in ["earring", "arete"]):
            return "Aretes"
        if any(k in text for k in ["necklace", "collar", "pendant"]):
            return "Collares"
        if any(k in text for k in ["bracelet", "pulsera"]):
            return "Pulseras"
        if any(k in text for k in ["ring", "anillo"]):
            return "Anillos"
        return "Aretes"
    
    if categoria == "Hogar & Decoración":
        if any(k in text for k in ["pot", "maceta", "planter"]):
            return "Macetas"
        if any(k in text for k in ["lamp", "lámpara", "light", "tealight"]):
            return "Iluminación"
        if any(k in text for k in ["fossil", "sculptur", "figure"]):
            return "Figuras Decorativas"
        return "Decoración"
    
    if categoria == "Organización":
        if any(k in text for k in ["jewelry", "joyero", "earring"]):
            return "Joyeros"
        if any(k in text for k in ["holder", "soporte"]):
            return "Porta-Objetos"
        return "Organizadores"
    
    if categoria == "Entretenimiento":
        if "fidget" in text:
            return "Fidgets"
        return "Juguetes"
    
    if categoria == "Regalos & Coleccionables":
        if any(k in text for k in ["keychain", "llavero"]):
            return "Llaveros"
        if any(k in text for k in ["skull", "calavera", "ornament"]):
            return "Figuras Temáticas"
        if any(k in text for k in ["clock", "reloj"]):
            return "Relojes"
        return "Coleccionables"
    
    return ""


def infer_tags(name, categoria, subcategoria):
    text = name.lower()
    tags = set()
    
    tags.add(categoria.split(" & ")[0].lower().strip())
    if subcategoria:
        tags.add(subcategoria.lower())
    
    tag_words = {
        "halloween": ["halloween", "scream", "jason", "skull", "calavera", "spider", "deadly"],
        "nature": ["mushroom", "flower", "plant", "tree", "leaf", "sakura", "cherry", "forest", "bosque"],
        "animal": ["cat", "dog", "paw", "butterfly", "serpent", "medusa", "jelly", "dinosaur", "giganoto", "ammonite", "unicorn"],
        "geometric": ["spiral", "mandala", "eclipse", "moon", "sun", "star", "infinite", "node"],
        "origami": ["origami", "paper", "boat", "plane"],
        "food": ["coffee", "mushroom", "koozie"],
        "sport": ["baseball", "bat", "glove", "fender", "guitar"],
        "regalo": ["gift", "regalo", "keychain", "llavero", "earring"],
        "sustentable": ["pla", "biodegradable", "eco"],
        "arte": ["sculptur", "sculptural", "art", "wave", "kanagawa"],
    }
    
    for tag, keywords in tag_words.items():
        for kw in keywords:
            if kw in text:
                tags.add(tag)
                break
    
    return sorted(list(tags))


def generate_names_es(nombre_en):
    name = nombre_en.lower()
    
    translations = {
        "mushroom earrings": "Aretes Hongo del Bosque",
        "serpent of silk vows earrings": "Aretes Serpiente de Seda",
        "infinite node of love earrings": "Aretes Nodo Infinito",
        "fidget clicker": "Pulsador Zen",
        "turning fidget death star keychain": "Llavero Estrella Mortal",
        "indoor plant pot the arcadia with hidden drip tray": "Maceta Arcadia",
        "veil petal sculptural decor": "Velo de Pétalos",
        "jewelry organizer for earrings rings necklaces": "Joyero Organizador",
        "cat skeleton earrings": "Aretes Esqueleto de Gato",
        "calavera skull ornament with heart pattern": "Calavera del Corazón",
        "medusa earrings": "Aretes Medusa",
        "earrings halloween": "Aretes Noche de Brujas",
        "heart web earring halloween": "Aretes Telaraña de Amor",
        "scream earrings halloween": "Aretes Grito",
        "halloween jason earring": "Aretes Jason",
        "deadly jelly dangling earrings": "Aretes Medusa Mortal",
        "paper boat origami earrings": "Aretes Barco de Papel",
        "cute cat earring": "Aretes Gatito",
        "earrings tree of life": "Aretes Árbol de la Vida",
        "eclipse earrings": "Aretes Eclipse",
        "heart of eternal motion": "Corazón de Movimiento Eterno",
        "earrings butterfly": "Aretes Mariposa",
        "paw earrings": "Aretes Patita",
        "3d balloon dog earrings": "Aretes Perro Globo",
        "earrings cat": "Aretes Silueto Gato",
        "spider dangle earrings": "Aretes Araña Colgante",
        "moon cat earring halloween": "Aretes Luna y Gato",
        "coffee cup earrings": "Aretes Taza de Café",
        "sun earrings": "Aretes Sol",
        "woven heart earrings": "Aretes Corazón Tejido",
        "mandala maze earrings": "Aretes Mandala Laberinto",
        "paper plane origami earrings": "Aretes Avión de Papel",
        "sakura cherry blossom earring keychain": "Llavero Flor de Sakura",
        "the great wave off kanagawa hueforge earrings": "Aretes Gran Ola de Kanagawa",
        "print in place fidget toggle switch": "Interruptor Fidget",
        "ultimate koozie v2": "Funda Térmica Ultimate",
        "customizable baseball bat": "Bat de Béisbol Personalizable",
        "mini baseball glove keychain": "Llavero Guante de Béisbol",
        "origami spiral of life clock": "Reloj Espiral de la Vida",
        "table tealight lamp set 2": "Lámparas Vela para Mesa",
        "ammonite fossil": "Fósil de Ammonite",
        "giganotosaurus fossil": "Fósil de Giganotosaurio",
        "unicorn skull fossil": "Fósil Cráneo de Unicornio",
        "spiral an ammonite fossil sculpture": "Espiral Ammonite",
        "angled toothbrush holder moonwalk michael jackson": "Soporte Cepillos Moonwalk",
        "fender stratocaster key hanger guitar key holder": "Llavero Guitarra Stratocaster",
    }
    
    if name in translations:
        return translations[name]
    
    return nombre_en


def main():
    print("=" * 60)
    print("PROCESAMIENTO DE DATOS - YOLITIA")
    print("=" * 60)
    
    with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
        progress = json.load(f)
    
    models_raw = progress["models_data"]
    print(f"\nModelos en progreso: {len(models_raw)}")
    
    processed = []
    
    for i, model in enumerate(models_raw):
        url = model["url"]
        model_id_num = get_model_id(url)
        nombre_en = slug_to_name(url)
        nombre_es = generate_names_es(nombre_en)
        categoria = infer_category(nombre_en, url)
        subcategoria = infer_subcategoria(nombre_en, categoria)
        tags = infer_tags(nombre_en, categoria, subcategoria)
        
        thumbnail_hd = get_thumbnail_hd(model.get("thumbnail"))
        
        producto = {
            "id": f"YOL-{model_id_num}" if model_id_num else f"YOL-{i+1:03d}",
            "sku": None,
            "nombre_original": nombre_en,
            "nombre_yolitia": nombre_es,
            "handle": None,
            "categoria": categoria,
            "subcategoria": subcategoria,
            "tipo_producto": "simple",
            "descripcion_corta": None,
            "descripcion_larga": None,
            "descripcion_html": None,
            "material": "PLA",
            "beneficios_material": ["ligero", "resistente", "biodegradable", "impreso en 3D"],
            "peso_gramos": None,
            "dimensiones_cm": None,
            "precio": None,
            "precio_comparacion": None,
            "precio_costo": None,
            "moneda": "MXN",
            "impuesto_porcentaje": 16,
            "impuesto_incluido": False,
            "inventario": {
                "tracking": False,
                "cantidad": None,
                "ubicacion": None,
                "politica_agotado": "deny",
                "backorders": False,
                "min_compra": 1,
                "max_compra": None
            },
            "envio": {
                "requiere_envio": True,
                "clase_envio": "estandar",
                "peso_envio_kg": None,
                "dimensiones_envio_cm": None,
                "origen_cp": None,
                "gravable": True
            },
            "variantes": [],
            "seo": {
                "meta_title": None,
                "meta_description": None,
                "meta_keywords": tags,
                "canonical_url": None,
                "google_product_category": None,
                "condition": "new"
            },
            "imagenes": [],
            "imagen_principal": None,
            "catalogo": {
                "destacado": False,
                "pagina": None,
                "posicion_pagina": None,
                "coleccion": categoria,
                "colecciones_adicionales": [],
                "orden_coleccion": i + 1
            },
            "relacionados": {
                "upsells": [],
                "cross_sells": [],
                "agrupados": []
            },
            "url_makerworld": url,
            "url_externa": None,
            "activo": True,
            "estado": "borrador",
            "visibilidad": "visible",
            "metadata": {
                "url_makerworld": url,
                "autor_modelo": None,
                "licencia": None,
                "notas_internas": None
            },
            "timestamps": {
                "creado": datetime.now().isoformat(),
                "actualizado": datetime.now().isoformat(),
                "publicado": None
            },
            "platform_data": {
                "woocommerce": {},
                "prestashop": {},
                "medusa": {},
                "magento": {}
            }
        }
        
        if thumbnail_hd:
            producto["imagenes"].append({
                "url": thumbnail_hd,
                "filename": f"YOL-{model_id_num}_principal_01.jpg" if model_id_num else f"YOL-{i+1:03d}_principal_01.jpg",
                "tipo": "principal",
                "alt_text": f"{nombre_es} - Impreso en 3D con PLA",
                "titulo": nombre_es,
                "posicion": 1,
                "es_principal": True,
                "ruta_local": None,
                "drive_url": None
            })
            producto["imagen_principal"] = producto["imagenes"][0]["filename"]
        
        processed.append(producto)
    
    for i, p in enumerate(processed):
        p["id"] = f"YOL-{i+1:03d}"
        sku_parts = p["categoria"][:3].upper().replace(" ", "")
        p["sku"] = f"YOL-{sku_parts}-{i+1:03d}"
        p["handle"] = p["nombre_yolitia"].lower().replace(" ", "-").replace(".", "").replace(",", "")
        if p["imagenes"]:
            p["imagenes"][0]["filename"] = f"YOL-{i+1:03d}_principal_01.jpg"
            p["imagen_principal"] = p["imagenes"][0]["filename"]
    
    output = {
        "coleccion_url": "https://makerworld.com/es/collections/10205491-yolitia-iniciousa",
        "total_modelos": len(processed),
        "fecha_procesamiento": datetime.now().isoformat(),
        "productos": processed
    }
    
    with open(PROCESSED_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'=' * 60}")
    print(f"RESULTADO:")
    print(f"  Productos procesados: {len(processed)}")
    
    cats = {}
    for p in processed:
        cat = p["categoria"]
        cats[cat] = cats.get(cat, 0) + 1
    
    print(f"\n  CATEGORIAS:")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"    {cat}: {count}")
    
    imgs = sum(len(p["imagenes"]) for p in processed)
    print(f"\n  Imágenes disponibles: {imgs}")
    print(f"\n  Archivo: {PROCESSED_FILE}")
    print(f"{'=' * 60}")
    
    print(f"\nMUESTRA DE 10 PRODUCTOS:")
    print("-" * 60)
    for p in processed[:10]:
        print(f"  {p['id']} | {p['nombre_yolitia'][:40]:<40} | {p['categoria'][:25]}")
    
    print(f"\n  ... y {len(processed) - 10} productos más")


if __name__ == "__main__":
    main()
