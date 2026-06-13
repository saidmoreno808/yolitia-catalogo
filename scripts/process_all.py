"""
Procesa TODAS las URLs de la colección en base de datos estructurada.
Usa collection_urls.json (158 modelos) con thumbnails del CDN.
"""

import json
import re
from pathlib import Path
from datetime import datetime


DATA_DIR = Path(__file__).parent.parent / "data"
URLS_FILE = DATA_DIR / "collection_urls.json"
PROCESSED_FILE = DATA_DIR / "scraping_processed.json"


def slug_to_name(url):
    slug = url.rstrip("/").split("/")[-1]
    match = re.match(r'\d+-(.+)', slug)
    raw = match.group(1) if match else slug
    raw = re.sub(r'[-_]+', ' ', raw)
    raw = re.sub(r'\b(no|ams|v\d+|mm|cm|pc|hueforge)\b', '', raw, flags=re.IGNORECASE)
    raw = re.sub(r'\s+', ' ', raw).strip()
    return raw.title()


def get_model_id(url):
    slug = url.rstrip("/").split("/")[-1]
    match = re.match(r'(\d+)-', slug)
    return match.group(1) if match else None


def get_thumbnail_for_model(model_id, thumbnails_dict):
    for key, url in thumbnails_dict.items():
        if model_id in key or key in model_id:
            hd_url = re.sub(r'x-oss-process=image/resize,w_\d+', 'x-oss-process=image/resize,w_1200', url)
            hd_url = re.sub(r'format,webp', 'format,jpg', hd_url)
            return hd_url
    return None


def infer_category(name, url):
    text = f"{name} {url}".lower()
    
    rules = [
        ("Joyería & Accesorios", ["earring", "arete", "pendiente", "necklace", "collar", "pendant", "dije", "bracelet", "pulsera", "ring", "anillo", "brooch", "broche", "jewelry", "joyería"]),
        ("Hogar & Decoración", ["pot", "maceta", "planter", "vase", "jarrón", "figure", "figura", "decorat", "sculptur", "sculptural", "home", "hogar", "lamp", "lámpara", "light", "luz", "candle", "vela", "tealight", "fossil", "petal", "veil", "clock", "reloj", "lithophane", "feeder", "statue", "sculpture"]),
        ("Organización", ["organizer", "organizador", "holder", "soporte", "storage", "almacen", "box", "caja", "tray", "bandeja", "jewelry box", "joyero", "toothbrush", "koozie", "plyometric"]),
        ("Entretenimiento", ["fidget", "toy", "juguete", "game", "juego", "puzzle", "rompecabezas", "spinner", "clicker", "toggle", "baseball", "bat", "glove", "spray paint can", "fraction learning"]),
        ("Regalos & Coleccionables", ["keychain", "llavero", "key chain", "figurine", "figurita", "collectible", "coleccionable", "gift", "regalo", "charm", "dije", "ornament", "skull", "calavera", "graduate", "kettlebell"]),
    ]
    
    for cat, keywords in rules:
        for kw in keywords:
            if kw in text:
                return cat
    
    return "Regalos & Coleccionables"


def infer_subcategoria(name, categoria):
    text = name.lower()
    
    if categoria == "Joyería & Accesorios":
        if any(k in text for k in ["earring", "arete"]): return "Aretes"
        if any(k in text for k in ["necklace", "collar", "pendant"]): return "Collares"
        if any(k in text for k in ["bracelet", "pulsera"]): return "Pulseras"
        if any(k in text for k in ["ring", "anillo"]): return "Anillos"
        return "Aretes"
    
    if categoria == "Hogar & Decoración":
        if any(k in text for k in ["pot", "maceta", "planter"]): return "Macetas"
        if any(k in text for k in ["lamp", "lámpara", "light", "tealight", "lithophane"]): return "Iluminación"
        if any(k in text for k in ["clock", "reloj"]): return "Relojes"
        if any(k in text for k in ["fossil", "sculptur", "figure", "statue"]): return "Figuras Decorativas"
        return "Decoración"
    
    if categoria == "Organización":
        if any(k in text for k in ["jewelry", "joyero", "earring"]): return "Joyeros"
        if any(k in text for k in ["holder", "soporte"]): return "Porta-Objetos"
        return "Organizadores"
    
    if categoria == "Entretenimiento":
        if "fidget" in text: return "Fidgets"
        if "puzzle" in text: return "Rompecabezas"
        return "Juguetes"
    
    if categoria == "Regalos & Coleccionables":
        if any(k in text for k in ["keychain", "llavero"]): return "Llaveros"
        if any(k in text for k in ["skull", "calavera", "ornament"]): return "Figuras Temáticas"
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
        "naturaleza": ["mushroom", "flower", "plant", "tree", "leaf", "sakura", "cherry", "forest", "bosque", "bird"],
        "animal": ["cat", "dog", "paw", "butterfly", "serpent", "medusa", "jelly", "dinosaur", "giganoto", "ammonite", "unicorn", "deer", "bird"],
        "geometrico": ["spiral", "mandala", "eclipse", "moon", "sun", "star", "infinite", "node", "minimalist"],
        "origami": ["origami", "paper", "boat", "plane"],
        "comida": ["coffee", "mushroom", "koozie"],
        "deporte": ["baseball", "bat", "glove", "fender", "guitar", "kettlebell", "crossfit", "gym"],
        "regalo": ["keychain", "llavero", "earring", "gift"],
        "arte": ["sculptur", "sculptural", "art", "wave", "kanagawa", "dali", "prayer"],
        "espacial": ["solar", "planet", "moon", "mars", "saturn"],
        "educativo": ["puzzle", "fraction", "learning", "numbers", "toddler"],
        "valentines": ["valentine", "heart", "love"],
    }
    
    for tag, keywords in tag_words.items():
        for kw in keywords:
            if kw in text:
                tags.add(tag)
                break
    
    return sorted(list(tags))


def generate_name_es(nombre_en):
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
        "earrings cat": "Aretes Silueta Gato",
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
        "cute valentines statue": "Estatua San Valentín",
        "deco pot isabella valentine s day": "Maceta Isabella",
        "modern bird feeder": "Comedero Moderno para Aves",
        "spray paint can fidget": "Fidget Lata de Spray",
        "fraction learning puzzle": "Rompecabezas Fracciones",
        "graduate": "Graduado",
        "wall clock two tone minimalist satisfying clock": "Reloj Minimalista Bicolor",
        "nobody prayer sculpture of contemplation": "Escultura Oración",
        "dali wall clock": "Reloj Dalí de Pared",
        "jewelry deer box": "Joyero Ciervo",
        "plyometric box storage crossfit": "Caja Plyométrica Crossfit",
        "solar system lithophane planet lamps 150mm": "Lámparas Sistema Solar",
        "moon planter with base": "Maceta Luna",
        "gym bro kettlebell keychain": "Llavero Kettlebell",
    }
    
    if name in translations:
        return translations[name]
    
    return nombre_en


def main():
    print("=" * 60)
    print("PROCESAMIENTO COMPLETO - 158 MODELOS YOLITIA")
    print("=" * 60)
    
    with open(URLS_FILE, 'r', encoding='utf-8') as f:
        collection = json.load(f)
    
    if "models" in collection:
        models_list = collection["models"]
        urls = [m["url"] for m in models_list]
        thumb_map = {m["model_id"]: m["thumbnail"] for m in models_list if m.get("thumbnail") and m.get("model_id")}
    else:
        urls = collection["urls"]
        thumb_map = {}
    
    print(f"\nURLs: {len(urls)}")
    print(f"Thumbnails mapeados: {len(thumb_map)}")
    
    processed = []
    
    for i, url in enumerate(urls):
        model_id_num = get_model_id(url)
        nombre_en = slug_to_name(url)
        nombre_es = generate_name_es(nombre_en)
        categoria = infer_category(nombre_en, url)
        subcategoria = infer_subcategoria(nombre_en, categoria)
        tags = infer_tags(nombre_en, categoria, subcategoria)
        
        thumbnail_hd = None
        if model_id_num and model_id_num in thumb_map:
            raw_thumb = thumb_map[model_id_num]
            thumbnail_hd = re.sub(r'x-oss-process=image/resize,w_\d+', 'x-oss-process=image/resize,w_1200', raw_thumb)
            thumbnail_hd = re.sub(r'format,webp', 'format,jpg', thumbnail_hd)
            thumbnail_hd = re.sub(r'\.gif\?', '.jpg?', thumbnail_hd)
        
        yol_id = f"YOL-{i+1:03d}"
        sku_prefix = categoria[:3].upper().replace(" ", "").replace("&", "X")
        sku = f"YOL-{sku_prefix}-{i+1:03d}"
        handle = nombre_es.lower().replace(" ", "-").replace(".", "").replace(",", "").replace("'", "")
        
        producto = {
            "id": yol_id,
            "sku": sku,
            "barcode": None,
            "gtin": None,
            "mpn": None,
            "nombre_original": nombre_en,
            "nombre_yolitia": nombre_es,
            "handle": handle,
            "slug": handle,
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
                "filename": f"{yol_id}_principal_01.jpg",
                "tipo": "principal",
                "alt_text": f"{nombre_es} - Impreso en 3D con PLA",
                "titulo": nombre_es,
                "posicion": 1,
                "es_principal": True,
                "ruta_local": None,
                "drive_url": None
            })
            producto["imagen_principal"] = f"{yol_id}_principal_01.jpg"
        
        processed.append(producto)
    
    output = {
        "coleccion_url": collection["collection_url"],
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
    
    subcats = {}
    for p in processed:
        sc = p["subcategoria"]
        if sc:
            subcats[sc] = subcats.get(sc, 0) + 1
    
    print(f"\n  SUBCATEGORIAS:")
    for sc, count in sorted(subcats.items(), key=lambda x: -x[1]):
        print(f"    {sc}: {count}")
    
    imgs = sum(len(p["imagenes"]) for p in processed)
    print(f"\n  Imágenes disponibles: {imgs}/{len(processed)}")
    print(f"\n  Archivo: {PROCESSED_FILE}")
    print(f"{'=' * 60}")
    
    print(f"\nMUESTRA DE 15 PRODUCTOS:")
    print("-" * 80)
    for p in processed[:15]:
        print(f"  {p['id']} | {p['nombre_yolitia'][:35]:<35} | {p['subcategoria'][:20]:<20} | {p['categoria'][:25]}")
    
    print(f"\n  ... y {len(processed) - 15} productos más")


if __name__ == "__main__":
    main()
