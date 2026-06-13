"""
Genera el catalogo PDF de Yolitia usando reportlab.
Sigue el plan de layout definido en catalog_layout_plan.json.
"""

import json
import math
from pathlib import Path
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from PIL import Image as PILImage
from PyPDF2 import PdfReader


BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = BASE_DIR / "assets" / "images" / "productos"
OUTPUT_DIR = BASE_DIR / "output"
LAYOUT_FILE = DATA_DIR / "catalog_layout_plan.json"
JSON_FILE = DATA_DIR / "yolitia_products_database.json"
OUTPUT_PDF = OUTPUT_DIR / "catalogo_yolitia_v1.pdf"


# Colores de la paleta Yolitia
COLOR_MARFIL = colors.HexColor("#F8F6F0")
COLOR_NEGRO = colors.HexColor("#1A1A1A")
COLOR_AZUL = colors.HexColor("#B8CCE4")
COLOR_OLIVA = colors.HexColor("#7A8C6E")
COLOR_PIEDRA = colors.HexColor("#D6D0C8")
COLOR_CREMA = colors.HexColor("#EDE8DF")
COLOR_GRIS_TEXTO = colors.HexColor("#555555")


# Dimensiones A4
PAGE_WIDTH, PAGE_HEIGHT = A4  # 595.27 x 841.89 pt
MARGIN = 56.7  # 20mm
CONTENT_WIDTH = PAGE_WIDTH - (2 * MARGIN)
CONTENT_HEIGHT = PAGE_HEIGHT - (2 * MARGIN)


def load_data():
    with open(LAYOUT_FILE, "r", encoding="utf-8") as f:
        layout = json.load(f)
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    productos = {p["id"]: p for p in data["productos"]}
    return layout, productos


def draw_spiral(c, x, y, size, color, opacity=1.0, turns=3):
    """Dibuja una espiral geometrica organica (elemento signature)."""
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(1.5)
    
    if opacity < 1.0:
        c.setFillAlpha(opacity)
        c.setStrokeAlpha(opacity)
    
    points = []
    for i in range(turns * 360):
        angle = math.radians(i)
        radius = size * (i / (turns * 360))
        px = x + radius * math.cos(angle)
        py = y + radius * math.sin(angle)
        points.append((px, py))
    
    if len(points) > 1:
        p = c.beginPath()
        p.moveTo(points[0][0], points[0][1])
        for px, py in points[1:]:
            p.lineTo(px, py)
        c.drawPath(p, stroke=1, fill=0)
    
    c.restoreState()


def draw_gradient_background(c, color1, color2, steps=50):
    """Dibuja un degradado vertical de fondo."""
    step_height = PAGE_HEIGHT / steps
    for i in range(steps):
        ratio = i / steps
        r = color1.red + (color2.red - color1.red) * ratio
        g = color1.green + (color2.green - color1.green) * ratio
        b = color1.blue + (color2.blue - color1.blue) * ratio
        c.setFillColor(colors.Color(r, g, b))
        c.rect(0, PAGE_HEIGHT - (i + 1) * step_height, PAGE_WIDTH, step_height, stroke=0, fill=1)


def draw_page_number(c, page_num):
    """Dibuja el numero de pagina centrado en el pie."""
    c.saveState()
    c.setFont("Courier", 8)
    c.setFillColor(COLOR_PIEDRA)
    text = f"-- {page_num} --"
    c.drawCentredString(PAGE_WIDTH / 2, 30, text)
    c.restoreState()


def build_cover_page(c):
    """Pagina 1: Portada."""
    print("  Generando portada...")
    
    draw_gradient_background(c, COLOR_MARFIL, COLOR_AZUL)
    
    draw_spiral(c, PAGE_WIDTH / 2, PAGE_HEIGHT / 2 + 50, 180, COLOR_AZUL, opacity=0.3, turns=4)
    
    c.saveState()
    c.setFont("Helvetica-Bold", 72)
    c.setFillColor(COLOR_NEGRO)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 + 20, "Yolitia")
    
    c.setFont("Helvetica", 16)
    c.setFillColor(COLOR_NEGRO)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 - 20, "Diseno impreso. Hecho para durar.")
    
    c.setFont("Helvetica", 10)
    c.setFillColor(COLOR_OLIVA)
    c.drawCentredString(PAGE_WIDTH / 2, 80, "Catalogo de Productos 2026")
    c.drawCentredString(PAGE_WIDTH / 2, 65, "Impresion 3D en PLA Biodegradable")
    
    c.restoreState()
    c.showPage()


def build_index_page(c, layout):
    """Pagina 2: Indice de categorias."""
    print("  Generando indice...")
    
    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    
    c.saveState()
    c.setFont("Helvetica-Bold", 36)
    c.setFillColor(COLOR_NEGRO)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 100, "Contenido")
    
    c.setStrokeColor(COLOR_AZUL)
    c.setLineWidth(2)
    c.line(MARGIN, PAGE_HEIGHT - 120, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 120)
    
    y = PAGE_HEIGHT - 180
    
    categorias_vistas = set()
    for pagina in layout["paginas"]:
        if pagina["tipo"] == "separador_categoria":
            cat = pagina["categoria"]
            if cat not in categorias_vistas:
                categorias_vistas.add(cat)
                page_num = pagina["pagina_numero"]
                
                c.setFont("Helvetica-Bold", 14)
                c.setFillColor(COLOR_NEGRO)
                c.drawString(MARGIN + 20, y, cat)
                
                c.setFont("Courier", 12)
                c.setFillColor(COLOR_PIEDRA)
                c.drawRightString(PAGE_WIDTH - MARGIN - 20, y, str(page_num))
                
                c.setStrokeColor(COLOR_PIEDRA)
                c.setLineWidth(0.5)
                c.setDash(2, 2)
                dots_start = MARGIN + 20 + pdfmetrics.stringWidth(cat, "Helvetica-Bold", 14) + 10
                dots_end = PAGE_WIDTH - MARGIN - 20 - pdfmetrics.stringWidth(str(page_num), "Courier", 12) - 10
                c.line(dots_start, y + 4, dots_end, y + 4)
                c.setDash()
                
                y -= 40
    
    c.setFont("Helvetica", 10)
    c.setFillColor(COLOR_OLIVA)
    c.drawCentredString(PAGE_WIDTH / 2, 80, "150 productos | 5 categorias | Impreso en PLA")
    
    c.restoreState()
    c.showPage()


def build_category_separator(c, pagina_data, layout):
    """Pagina separadora de categoria."""
    cat = pagina_data["categoria"]
    orden = pagina_data.get("orden_categoria", 1)
    total = pagina_data.get("total_categorias", 5)
    page_num = pagina_data["pagina_numero"]
    
    print(f"  Separador: {cat} (pag {page_num})")
    
    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    
    c.saveState()
    c.setFillColor(COLOR_AZUL)
    c.setFillAlpha(0.3)
    c.rect(0, PAGE_HEIGHT / 2, PAGE_WIDTH, PAGE_HEIGHT / 2, stroke=0, fill=1)
    c.restoreState()
    
    draw_spiral(c, PAGE_WIDTH / 2, PAGE_HEIGHT * 0.65, 120, COLOR_AZUL, opacity=0.15, turns=3)
    
    c.saveState()
    c.setFont("Helvetica", 12)
    c.setFillColor(COLOR_OLIVA)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 80, f"Categoria {orden} de {total}")
    
    c.setFont("Helvetica-Bold", 36)
    c.setFillColor(COLOR_NEGRO)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 + 40, cat)
    
    c.setStrokeColor(COLOR_AZUL)
    c.setLineWidth(2)
    line_width = 200
    c.line((PAGE_WIDTH - line_width) / 2, PAGE_HEIGHT / 2 + 20, 
           (PAGE_WIDTH + line_width) / 2, PAGE_HEIGHT / 2 + 20)
    
    prods_en_cat = [p for p in layout["paginas"] 
                    if p["tipo"] == "productos" and p.get("categoria") == cat]
    total_prods = sum(p.get("num_productos", 0) for p in prods_en_cat)
    
    c.setFont("Helvetica", 12)
    c.setFillColor(COLOR_GRIS_TEXTO)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 - 10, 
                        f"{total_prods} productos")
    
    c.restoreState()
    
    draw_page_number(c, page_num)
    c.showPage()


def build_product_page(c, pagina_data, productos):
    """Pagina de productos."""
    page_num = pagina_data["pagina_numero"]
    grid = pagina_data.get("grid", "1x2")
    elementos = pagina_data.get("elementos", [])
    
    print(f"  Productos pag {page_num}: grid {grid}, {len(elementos)} productos")
    
    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    
    if grid == "1x1":
        build_1x1_layout(c, elementos, productos)
    elif grid == "2x2":
        build_2x2_layout(c, elementos, productos)
    elif grid == "1x2":
        build_1x2_layout(c, elementos, productos)
    elif grid == "1x3":
        build_1x3_layout(c, elementos, productos)
    
    draw_page_number(c, page_num)
    c.showPage()


def build_1x1_layout(c, elementos, productos):
    """Layout 1 producto por pagina (hero)."""
    if not elementos:
        return
    
    elem = elementos[0]
    prod = productos.get(elem["producto_id"])
    if not prod:
        return
    
    img_path = get_image_path(elem)
    
    card_x = MARGIN
    card_y = MARGIN + 50
    card_w = CONTENT_WIDTH
    card_h = CONTENT_HEIGHT - 100
    
    c.setFillColor(COLOR_CREMA)
    c.roundRect(card_x, card_y, card_w, card_h, 8, stroke=0, fill=1)
    
    if img_path and Path(img_path).exists():
        try:
            img_display_w = card_w - 40
            img_display_h = card_h - 180
            img_x = card_x + 20
            img_y = card_y + 160
            
            c.drawImage(img_path, img_x, img_y, 
                       width=img_display_w, height=img_display_h,
                       preserveAspectRatio=True, anchor='c')
        except Exception as e:
            print(f"    Error imagen: {e}")
    
    text_y = card_y + 20
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(COLOR_NEGRO)
    c.drawString(card_x + 20, text_y + 80, prod["nombre_yolitia"])
    
    c.setFont("Helvetica", 10)
    c.setFillColor(COLOR_GRIS_TEXTO)
    desc = prod.get("descripcion_corta") or prod.get("descripcion_larga") or prod["nombre_yolitia"]
    c.drawString(card_x + 20, text_y + 55, desc[:70])
    
    c.setStrokeColor(COLOR_PIEDRA)
    c.setLineWidth(0.5)
    c.line(card_x + 20, text_y + 45, card_x + card_w - 20, text_y + 45)
    
    c.setFont("Helvetica", 9)
    c.setFillColor(COLOR_OLIVA)
    c.drawString(card_x + 20, text_y + 25, f"Material: {prod.get('material', 'PLA')}")
    
    c.setFont("Helvetica", 11)
    c.setFillColor(COLOR_NEGRO)
    c.drawString(card_x + 20, text_y, "Precio: $ ___________")


def build_2x2_layout(c, elementos, productos):
    """Layout 2x2 (4 productos por pagina, tipicamente aretes)."""
    card_w = (CONTENT_WIDTH - 20) / 2
    card_h = (CONTENT_HEIGHT - 80) / 2
    
    positions = [
        (MARGIN, MARGIN + card_h + 60),
        (MARGIN + card_w + 20, MARGIN + card_h + 60),
        (MARGIN, MARGIN),
        (MARGIN + card_w + 20, MARGIN),
    ]
    
    for i, elem in enumerate(elementos[:4]):
        prod = productos.get(elem["producto_id"])
        if not prod:
            continue
        
        x, y = positions[i]
        img_path = get_image_path(elem)
        
        c.setFillColor(COLOR_CREMA)
        c.roundRect(x, y, card_w, card_h, 6, stroke=0, fill=1)
        
        if img_path and Path(img_path).exists():
            try:
                img_w = card_w - 20
                img_h = card_h - 80
                c.drawImage(img_path, x + 10, y + 60,
                           width=img_w, height=img_h,
                           preserveAspectRatio=True, anchor='c')
            except Exception:
                pass
        
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(COLOR_NEGRO)
        c.drawString(x + 10, y + 35, prod["nombre_yolitia"][:30])
        
        c.setFont("Helvetica", 7)
        c.setFillColor(COLOR_GRIS_TEXTO)
        desc = prod.get("descripcion_corta") or prod["nombre_yolitia"]
        c.drawString(x + 10, y + 20, desc[:45])
        
        c.setFont("Helvetica", 7)
        c.setFillColor(COLOR_OLIVA)
        c.drawString(x + 10, y + 8, f"PLA | $ ___")


def build_1x2_layout(c, elementos, productos):
    """Layout 1x2 (2 productos por pagina)."""
    card_w = CONTENT_WIDTH
    card_h = (CONTENT_HEIGHT - 60) / 2
    
    positions = [
        (MARGIN, MARGIN + card_h + 40),
        (MARGIN, MARGIN),
    ]
    
    for i, elem in enumerate(elementos[:2]):
        prod = productos.get(elem["producto_id"])
        if not prod:
            continue
        
        x, y = positions[i]
        img_path = get_image_path(elem)
        
        c.setFillColor(COLOR_CREMA)
        c.roundRect(x, y, card_w, card_h, 6, stroke=0, fill=1)
        
        if img_path and Path(img_path).exists():
            try:
                img_w = card_w * 0.45
                img_h = card_h - 30
                c.drawImage(img_path, x + 15, y + 15,
                           width=img_w, height=img_h,
                           preserveAspectRatio=True, anchor='w')
            except Exception:
                pass
        
        text_x = x + card_w * 0.5
        
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(COLOR_NEGRO)
        c.drawString(text_x, y + card_h - 40, prod["nombre_yolitia"][:35])
        
        c.setFont("Helvetica", 9)
        c.setFillColor(COLOR_GRIS_TEXTO)
        desc = prod.get("descripcion_corta") or prod.get("descripcion_larga") or prod["nombre_yolitia"]
        lines = wrap_text(desc[:80], 40)
        for j, line in enumerate(lines[:3]):
            c.drawString(text_x, y + card_h - 65 - j * 14, line)
        
        c.setStrokeColor(COLOR_PIEDRA)
        c.setLineWidth(0.5)
        c.line(text_x, y + 50, x + card_w - 20, y + 50)
        
        c.setFont("Helvetica", 8)
        c.setFillColor(COLOR_OLIVA)
        c.drawString(text_x, y + 30, f"Material: {prod.get('material', 'PLA')}")
        
        c.setFont("Helvetica", 10)
        c.setFillColor(COLOR_NEGRO)
        c.drawString(text_x, y + 10, "Precio: $ ___________")


def build_1x3_layout(c, elementos, productos):
    """Layout 1x3 (3 productos por pagina)."""
    card_w = CONTENT_WIDTH
    card_h = (CONTENT_HEIGHT - 50) / 3
    
    positions = [
        (MARGIN, MARGIN + card_h * 2 + 30),
        (MARGIN, MARGIN + card_h + 15),
        (MARGIN, MARGIN),
    ]
    
    for i, elem in enumerate(elementos[:3]):
        prod = productos.get(elem["producto_id"])
        if not prod:
            continue
        
        x, y = positions[i]
        img_path = get_image_path(elem)
        
        c.setFillColor(COLOR_CREMA)
        c.roundRect(x, y, card_w, card_h, 6, stroke=0, fill=1)
        
        if img_path and Path(img_path).exists():
            try:
                img_w = card_w * 0.35
                img_h = card_h - 20
                c.drawImage(img_path, x + 10, y + 10,
                           width=img_w, height=img_h,
                           preserveAspectRatio=True, anchor='w')
            except Exception:
                pass
        
        text_x = x + card_w * 0.4
        
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(COLOR_NEGRO)
        c.drawString(text_x, y + card_h - 30, prod["nombre_yolitia"][:30])
        
        c.setFont("Helvetica", 8)
        c.setFillColor(COLOR_GRIS_TEXTO)
        desc = prod.get("descripcion_corta") or prod["nombre_yolitia"]
        c.drawString(text_x, y + card_h - 50, desc[:40])
        
        c.setFont("Helvetica", 7)
        c.setFillColor(COLOR_OLIVA)
        c.drawString(text_x, y + 20, f"PLA | $ ___")


def build_pla_page(c, page_num):
    """Pagina sobre material PLA."""
    print(f"  Seccion PLA (pag {page_num})")
    
    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    
    c.saveState()
    c.setFillColor(COLOR_OLIVA)
    c.setFillAlpha(0.1)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    c.restoreState()
    
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(COLOR_OLIVA)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 100, "HECHO DE PLA")
    
    c.setFont("Helvetica", 14)
    c.setFillColor(COLOR_NEGRO)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 130, "Bello por dentro y por fuera")
    
    c.setStrokeColor(COLOR_OLIVA)
    c.setLineWidth(1)
    c.line(MARGIN + 50, PAGE_HEIGHT - 150, PAGE_WIDTH - MARGIN - 50, PAGE_HEIGHT - 150)
    
    text_x = MARGIN + 30
    text_y = PAGE_HEIGHT - 200
    line_height = 16
    
    paragraphs = [
        "El PLA (Acido Polilactico) es un polimero de origen vegetal,",
        "derivado principalmente de almidon de maiz o cana de azucar.",
        "A diferencia de los plasticos convencionales, el PLA se obtiene",
        "de fuentes renovables y es compostable en condiciones industriales.",
        "",
        "Por que importa:",
        "",
        "  - Reduce la dependencia de petroquimicos",
        "  - Menor huella de carbono en su produccion",
        "  - Compostable: no se acumula en oceanos por siglos",
        "  - Permite produccion local y bajo demanda",
        "  - Cero inventario excedente = cero desperdicio",
        "",
        "En Yolitia, cada pieza se imprime en 3D cuando tu la pides.",
        "No hay bodegas llenas. No hay sobreproduccion.",
    ]
    
    c.setFont("Helvetica", 11)
    c.setFillColor(COLOR_NEGRO)
    
    for line in paragraphs:
        if line.startswith("Por que") or line.startswith("En Yolitia"):
            c.setFont("Helvetica-Bold", 11)
        else:
            c.setFont("Helvetica", 11)
        c.drawString(text_x, text_y, line)
        text_y -= line_height
    
    draw_spiral(c, PAGE_WIDTH - 100, 150, 60, COLOR_OLIVA, opacity=0.2, turns=2)
    
    draw_page_number(c, page_num)
    c.showPage()


def build_back_cover(c):
    """Contraportada: Manifiesto Yolitia."""
    print("  Generando contraportada...")
    
    draw_gradient_background(c, COLOR_MARFIL, COLOR_CREMA)
    
    draw_spiral(c, PAGE_WIDTH / 2, PAGE_HEIGHT / 2 + 100, 150, COLOR_OLIVA, opacity=0.15, turns=3)
    
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(COLOR_NEGRO)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 120, "YOLITIA")
    
    c.setFont("Helvetica", 14)
    c.setFillColor(COLOR_OLIVA)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 150, "Un proyecto circular")
    
    c.setStrokeColor(COLOR_OLIVA)
    c.setLineWidth(1)
    c.line(MARGIN + 100, PAGE_HEIGHT - 170, PAGE_WIDTH - MARGIN - 100, PAGE_HEIGHT - 170)
    
    text_x = MARGIN + 40
    text_y = PAGE_HEIGHT - 220
    line_height = 18
    
    manifesto = [
        "Yolitia nace de una pregunta simple:",
        "Y si los objetos que usamos cada dia pudieran",
        "hacerse con menos y significar mas?",
        "",
        "Nuestro modelo es diferente:",
        "",
        "  > Producimos bajo pedido, no en masa",
        "  > Usamos materiales de origen vegetal (PLA)",
        "  > Disenamos para durar, no para desechar",
        "  > Cada compra apoya la manufactura local",
        "",
        "Somos parte del movimiento de economia circular:",
        "los materiales entran, se usan, se recuperan.",
        "Nada se pierde. Todo vuelve.",
        "",
        "",
        "Yolitia",
        "Diseno consciente. Impreso aqui.",
    ]
    
    c.setFont("Helvetica", 11)
    c.setFillColor(COLOR_NEGRO)
    
    for line in manifesto:
        if line == "Yolitia" or line.startswith("Diseno consciente"):
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(COLOR_OLIVA)
        elif line.startswith("Nuestro modelo") or line.startswith("Somos parte"):
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(COLOR_NEGRO)
        else:
            c.setFont("Helvetica", 11)
            c.setFillColor(COLOR_NEGRO)
        
        c.drawString(text_x, text_y, line)
        text_y -= line_height
    
    c.setFont("Helvetica", 8)
    c.setFillColor(COLOR_PIEDRA)
    c.drawCentredString(PAGE_WIDTH / 2, 50, "www.yolitia.com | @yolitia")
    
    c.showPage()


def get_image_path(elem):
    """Obtiene la ruta de la imagen del producto."""
    ruta = elem.get("imagen_ruta")
    if ruta:
        full_path = BASE_DIR / ruta
        if full_path.exists():
            return str(full_path)
    
    prod_id = elem.get("producto_id", "")
    filename = elem.get("imagen_filename", "")
    if filename:
        path = IMAGES_DIR / prod_id / filename
        if path.exists():
            return str(path)
    
    return None


def wrap_text(text, max_chars):
    """Divide texto en lineas de max_chars caracteres."""
    words = text.split()
    lines = []
    current_line = []
    current_len = 0
    
    for word in words:
        if current_len + len(word) + 1 <= max_chars:
            current_line.append(word)
            current_len += len(word) + 1
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_len = len(word)
    
    if current_line:
        lines.append(" ".join(current_line))
    
    return lines


def build_catalog():
    """Genera el catalogo PDF completo."""
    print("=" * 60)
    print("GENERACION DE CATALOGO PDF - YOLITIA")
    print("=" * 60)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    layout, productos = load_data()
    print(f"\nLayout cargado: {len(layout['paginas'])} paginas planificadas")
    print(f"Productos cargados: {len(productos)}")
    
    c = canvas.Canvas(str(OUTPUT_PDF), pagesize=A4)
    c.setTitle("Catalogo Yolitia 2026")
    c.setAuthor("Yolitia")
    c.setSubject("Catalogo de productos impresos en 3D")
    
    paginas_generadas = 0
    
    for pagina_data in layout["paginas"]:
        tipo = pagina_data["tipo"]
        
        if tipo == "portada":
            build_cover_page(c)
            paginas_generadas += 1
        
        elif tipo == "indice":
            build_index_page(c, layout)
            paginas_generadas += 1
        
        elif tipo == "separador_categoria":
            build_category_separator(c, pagina_data, layout)
            paginas_generadas += 1
        
        elif tipo == "productos":
            build_product_page(c, pagina_data, productos)
            paginas_generadas += 1
        
        elif tipo == "material_pla":
            build_pla_page(c, pagina_data["pagina_numero"])
            paginas_generadas += 1
        
        elif tipo == "contraportada":
            build_back_cover(c)
            paginas_generadas += 1
    
    c.save()
    
    print(f"\n{'=' * 60}")
    print(f"PDF GENERADO:")
    print(f"  Archivo: {OUTPUT_PDF}")
    print(f"  Paginas: {paginas_generadas}")
    
    file_size = OUTPUT_PDF.stat().st_size
    print(f"  Tamano: {file_size / (1024*1024):.2f} MB")
    
    try:
        reader = PdfReader(str(OUTPUT_PDF))
        pdf_pages = len(reader.pages)
        print(f"  Validacion PDF: OK ({pdf_pages} paginas)")
        
        if pdf_pages != paginas_generadas:
            print(f"  ADVERTENCIA: Paginas generadas ({paginas_generadas}) != paginas PDF ({pdf_pages})")
    except Exception as e:
        print(f"  ERROR validacion: {e}")
    
    print(f"{'=' * 60}")
    
    return paginas_generadas


if __name__ == "__main__":
    build_catalog()
