"""
Genera el plan de layout del catalogo Yolitia.
Asigna productos a paginas segun reglas de diseño editorial.
"""

import json
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).parent.parent / "data"
JSON_FILE = DATA_DIR / "yolitia_products_database.json"
LAYOUT_FILE = DATA_DIR / "catalog_layout_plan.json"


ORDEN_CATEGORIAS = [
    "Joyería & Accesorios",
    "Hogar & Decoración",
    "Organización",
    "Entretenimiento",
    "Regalos & Coleccionables",
]


def cargar_productos():
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["productos"]


def agrupar_por_categoria(productos):
    grupos = defaultdict(list)
    for p in productos:
        cat = p.get("categoria", "Otros")
        if not p.get("imagenes") or not any(img.get("ruta_local") for img in p.get("imagenes", [])):
            continue
        grupos[cat].append(p)
    return dict(grupos)


def determinar_grid(categoria, es_hero=False, num_productos_grupo=1):
    """
    Reglas de layout:
    - Hero/primer producto de categoria: 1x1 (pagina completa)
    - Joyeria (aretes pequenos): hasta 4 por pagina (2x2)
    - Hogar (macetas, figuras): maximo 2 por pagina (1x2)
    - Organizacion/Entretenimiento: 2-3 por pagina
    - Regalos: 2-3 por pagina
    """
    if es_hero or num_productos_grupo == 1:
        return "1x1"
    
    if categoria == "Joyería & Accesorios":
        return "2x2"  # 4 aretes por pagina
    
    if categoria == "Hogar & Decoración":
        return "1x2"  # 2 macetas/figuras por pagina
    
    if categoria == "Organización":
        return "1x2"  # 2 organizadores por pagina
    
    if categoria == "Entretenimiento":
        return "1x3"  # 3 fidgets/juguetes por pagina
    
    return "1x2"  # Default: 2 por pagina


def productos_por_pagina(grid):
    grids = {
        "1x1": 1,
        "1x2": 2,
        "2x2": 4,
        "1x3": 3,
    }
    return grids.get(grid, 2)


def build_layout_plan(productos):
    grupos = agrupar_por_categoria(productos)
    
    paginas = []
    pagina_num = 1
    
    paginas.append({
        "tipo": "portada",
        "pagina_numero": None,
        "numero_pagina_display": None,
        "elementos": [],
        "notas": "Portada: Yolitia + subtitulo + espiral signature + degradado marfil->azul"
    })
    
    paginas.append({
        "tipo": "indice",
        "pagina_numero": None,
        "numero_pagina_display": None,
        "elementos": [],
        "categorias": [],
        "notas": "Indice de categorias con numeros de pagina"
    })
    
    total_categorias = len([c for c in ORDEN_CATEGORIAS if c in grupos])
    
    for idx_cat, categoria in enumerate(ORDEN_CATEGORIAS):
        if categoria not in grupos:
            continue
        
        prods_cat = grupos[categoria]
        
        paginas.append({
            "tipo": "separador_categoria",
            "pagina_numero": pagina_num,
            "numero_pagina_display": str(pagina_num),
            "categoria": categoria,
            "orden_categoria": idx_cat + 1,
            "total_categorias": total_categorias,
            "elementos": [],
            "notas": "Media pagina: nombre categoria en grande + franja azul niebla + icono"
        })
        pagina_num += 1
        
        first_in_cat = True
        i = 0
        while i < len(prods_cat):
            if first_in_cat:
                grid = "1x1"
                count = 1
                highlight = True
                first_in_cat = False
            else:
                grid = determinar_grid(categoria, es_hero=False, num_productos_grupo=len(prods_cat) - i)
                count = productos_por_pagina(grid)
                highlight = False
            
            elementos_pagina = []
            for j in range(count):
                if i + j < len(prods_cat):
                    p = prods_cat[i + j]
                    elementos_pagina.append({
                        "posicion": j + 1,
                        "producto_id": p["id"],
                        "sku": p["sku"],
                        "nombre_yolitia": p["nombre_yolitia"],
                        "subcategoria": p.get("subcategoria", ""),
                        "imagen_filename": p.get("imagen_principal", ""),
                        "imagen_ruta": next((img["ruta_local"] for img in p.get("imagenes", []) if img.get("ruta_local")), None),
                        "material": p.get("material", "PLA"),
                        "descripcion_corta": p.get("descripcion_corta", ""),
                        "es_hero": highlight and j == 0,
                        "destacado": p.get("catalogo", {}).get("destacado", False)
                    })
            
            paginas.append({
                "tipo": "productos",
                "pagina_numero": pagina_num,
                "numero_pagina_display": str(pagina_num),
                "categoria": categoria,
                "grid": grid,
                "num_productos": len(elementos_pagina),
                "elementos": elementos_pagina,
                "notas": f"Grid {grid}: {len(elementos_pagina)} producto(s)"
            })
            
            pagina_num += 1
            i += count
    
    paginas.append({
        "tipo": "material_pla",
        "pagina_numero": pagina_num,
        "numero_pagina_display": str(pagina_num),
        "elementos": [],
        "notas": "Seccion PLA: 'HECHO DE PLA — Bello por dentro y por fuera'"
    })
    pagina_num += 1
    
    paginas.append({
        "tipo": "colores",
        "pagina_numero": pagina_num,
        "numero_pagina_display": str(pagina_num),
        "elementos": [],
        "notas": "Colores disponibles para los modelos"
    })
    pagina_num += 1
    
    paginas.append({
        "tipo": "compromiso",
        "pagina_numero": pagina_num,
        "numero_pagina_display": str(pagina_num),
        "elementos": [],
        "notas": "Compromiso ambiental: 10% ganancias a conservacion + redes sociales"
    })
    pagina_num += 1
    
    paginas.append({
        "tipo": "contraportada",
        "pagina_numero": None,
        "numero_pagina_display": None,
        "elementos": [],
        "notas": "Manifiesto Yolitia: 'Un proyecto circular'"
    })
    
    return paginas


def main():
    print("=" * 60)
    print("PLAN DE LAYOUT - CATALOGO YOLITIA")
    print("=" * 60)
    
    productos = cargar_productos()
    print(f"\nProductos cargados: {len(productos)}")
    
    paginas = build_layout_plan(productos)
    
    total_paginas = len(paginas)
    paginas_portada = sum(1 for p in paginas if p["tipo"] == "portada")
    paginas_indice = sum(1 for p in paginas if p["tipo"] == "indice")
    paginas_separador = sum(1 for p in paginas if p["tipo"] == "separador_categoria")
    paginas_productos = sum(1 for p in paginas if p["tipo"] == "productos")
    paginas_pla = sum(1 for p in paginas if p["tipo"] == "material_pla")
    paginas_contraportada = sum(1 for p in paginas if p["tipo"] == "contraportada")
    
    total_productos_en_paginas = sum(p.get("num_productos", 0) for p in paginas if p["tipo"] == "productos")
    
    output = {
        "metadata": {
            "marca": "Yolitia",
            "version": "1.0",
            "fecha_creacion": __import__("datetime").datetime.now().isoformat(),
            "total_paginas": total_paginas,
            "total_productos_catalogados": total_productos_en_paginas,
        },
        "identidad_visual": {
            "paleta": {
                "marfil": "#F8F6F0",
                "negro_suave": "#1A1A1A",
                "azul_niebla": "#B8CCE4",
                "verde_oliva": "#7A8C6E",
                "gris_piedra": "#D6D0C8",
                "crema_calido": "#EDE8DF",
            },
            "tipografia": {
                "titulos": "Montserrat ExtraBold",
                "cuerpo": "Open Sans Light",
                "numeros": "Courier New Light",
                "fallback_titulos": "Helvetica-Bold",
            },
            "elemento_signature": {
                "descripcion": "Espiral geometrica organica — representa circularidad + raices mexicanas",
                "ubicacion": "Portada (fondo), separadores de categoria (marca de agua sutil)",
                "tecnica": "Vector SVG embebido como reporte en reportlab canvas",
                "color": "#B8CCE4 al 30% opacidad",
            },
            "dimensiones": {
                "formato": "A4 vertical",
                "ancho_pt": 595,
                "alto_pt": 842,
                "margen_pt": 56.7,
                "sangrado_pt": 8.5,
            }
        },
        "paginas": paginas,
    }
    
    with open(LAYOUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'=' * 60}")
    print(f"RESUMEN DEL PLAN:")
    print(f"{'=' * 60}")
    print(f"  Total paginas:         {total_paginas}")
    print(f"    Portada:             {paginas_portada}")
    print(f"    Indice:              {paginas_indice}")
    print(f"    Separadores categoria:{paginas_separador}")
    print(f"    Paginas productos:   {paginas_productos}")
    print(f"    Seccion PLA:         {paginas_pla}")
    print(f"    Contraportada:       {paginas_contraportada}")
    print(f"\n  Productos catalogados: {total_productos_en_paginas}/{len(productos)}")
    
    print(f"\nDESGLOSE POR CATEGORIA:")
    print("-" * 60)
    cats_vistas = set()
    for p in paginas:
        if p["tipo"] == "productos" and p.get("categoria") not in cats_vistas:
            cat = p["categoria"]
            cats_vistas.add(cat)
            prods_cat = [pp for pp in paginas if pp["tipo"] == "productos" and pp.get("categoria") == cat]
            total_prods = sum(pp.get("num_productos", 0) for pp in prods_cat)
            total_pags = len(prods_cat)
            print(f"  {cat:<30} {total_prods:>3} productos en {total_pags} paginas")
    
    print(f"\nESTRUCTURA VISUAL:")
    print("-" * 60)
    for i, p in enumerate(paginas[:15]):
        tipo = p["tipo"]
        num = p.get("numero_pagina_display") or "--"
        nota = p.get("notas", "")[:50]
        extra = ""
        if tipo == "productos":
            extra = f" [{p.get('grid','')} {p.get('num_productos','')}prods]"
        elif tipo == "separador_categoria":
            extra = f" {p.get('categoria','')}"
        print(f"  Pag {str(num):>3} | {tipo:<22}{extra:<30}")
    
    if len(paginas) > 15:
        print(f"  ... y {len(paginas) - 15} paginas mas")
    
    print(f"\nELEMENTO SIGNATURE:")
    print(f"  Espiral geometrica organica")
    print(f"  - Portada: fondo completo, color azul niebla (#B8CCE4)")
    print(f"  - Separadores: marca de agua sutil al 15% opacidad")
    print(f"  - Contraportada: version reducida junto al manifiesto")
    print(f"  - Simboliza: circularidad, economia circular, raices mexicanas")
    print(f"\nArchivo: {LAYOUT_FILE}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
