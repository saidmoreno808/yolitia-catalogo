"""
Catálogo Yolitia v3 - Diseño editorial premium
Todo en español, paleta elegante, más iconos y detalles
"""

import json
import math
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics

from PIL import Image as PILImage
from PyPDF2 import PdfReader


BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = BASE_DIR / "assets" / "images" / "productos"
OUTPUT_DIR = BASE_DIR / "output"
LAYOUT_FILE = DATA_DIR / "catalog_layout_plan.json"
JSON_FILE = DATA_DIR / "yolitia_products_database.json"
OUTPUT_PDF = OUTPUT_DIR / "catalogo_yolitia_v3.pdf"


# Paleta Yolitia v3 - elegante y sustentable
COLOR_BLANCO = colors.HexColor("#FFFFFF")
COLOR_NEGRO = colors.HexColor("#1A1A1A")
COLOR_OLIVA = colors.HexColor("#7A8C6E")
COLOR_AZUL_CLARO = colors.HexColor("#B8CCE4")
COLOR_ROSA_PASTEL = colors.HexColor("#E8D5D5")
COLOR_ARENA = colors.HexColor("#E8E0D5")
COLOR_GRIS = colors.HexColor("#555555")
COLOR_GRIS_CLARO = colors.HexColor("#D6D0C8")


# Dimensiones A4
PAGE_W, PAGE_H = A4
MARGIN = 45
CONTENT_W = PAGE_W - (2 * MARGIN)


def load_data():
    with open(LAYOUT_FILE, "r", encoding="utf-8") as f:
        layout = json.load(f)
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    productos = {p["id"]: p for p in data["productos"]}
    return layout, productos


def draw_leaf_icon(c, x, y, size, color):
    """Icono de hoja minimalista."""
    c.saveState()
    c.setFillColor(color)
    c.setStrokeColor(color)
    c.setLineWidth(1)
    
    p = c.beginPath()
    p.moveTo(x, y)
    p.curveTo(x + size*0.3, y + size*0.5, x + size*0.5, y + size*0.7, x + size*0.5, y + size)
    p.curveTo(x + size*0.5, y + size*0.7, x + size*0.7, y + size*0.5, x + size, y)
    p.curveTo(x + size*0.7, y + size*0.2, x + size*0.3, y + size*0.2, x, y)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    
    c.setStrokeColor(COLOR_BLANCO)
    c.setLineWidth(0.5)
    c.line(x + size*0.5, y + size*0.1, x + size*0.5, y + size*0.9)
    
    c.restoreState()


def draw_recycle_icon(c, x, y, size, color):
    """Icono de reciclaje con tres flechas."""
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(1.5)
    c.setFillColor(colors.Color(color.red, color.green, color.blue, alpha=0.1))
    
    cx, cy = x + size/2, y + size/2
    r = size * 0.4
    
    for i in range(3):
        angle = i * 120
        rad = math.radians(angle)
        px = cx + r * math.cos(rad)
        py = cy + r * math.sin(rad)
        c.circle(px, py, size*0.08, stroke=1, fill=1)
    
    c.restoreState()


def draw_heart_icon(c, x, y, size, color):
    """Icono de corazón (hecho a mano)."""
    c.saveState()
    c.setFillColor(color)
    c.setStrokeColor(color)
    c.setLineWidth(1)
    
    p = c.beginPath()
    p.moveTo(x + size/2, y + size*0.3)
    p.curveTo(x + size*0.2, y, x, y + size*0.3, x + size/2, y + size)
    p.curveTo(x + size, y + size*0.3, x + size*0.8, y, x + size/2, y + size*0.3)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    
    c.restoreState()


def draw_star_icon(c, x, y, size, color):
    """Icono de estrella (calidad)."""
    c.saveState()
    c.setFillColor(color)
    c.setStrokeColor(color)
    c.setLineWidth(1)
    
    cx, cy = x + size/2, y + size/2
    r_outer = size/2
    r_inner = size/4
    
    p = c.beginPath()
    for i in range(5):
        angle_outer = math.radians(i * 72 - 90)
        angle_inner = math.radians(i * 72 - 90 + 36)
        
        px_outer = cx + r_outer * math.cos(angle_outer)
        py_outer = cy + r_outer * math.sin(angle_outer)
        px_inner = cx + r_inner * math.cos(angle_inner)
        py_inner = cy + r_inner * math.sin(angle_inner)
        
        if i == 0:
            p.moveTo(px_outer, py_outer)
        else:
            p.lineTo(px_outer, py_outer)
        p.lineTo(px_inner, py_inner)
    
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    
    c.restoreState()


def draw_spiral_signature(c, x, y, size, color, opacity=0.15):
    """Espiral geométrica orgánica - elemento signature."""
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(1.2)
    c.setStrokeAlpha(opacity)
    
    points = []
    turns = 3
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


def draw_sustainability_badges(c, x, y, badges, size=10):
    """Dibuja iconos de sostenibilidad con etiquetas."""
    badge_icons = {
        "reciclable": ("♻", "Reciclable"),
        "biodegradable": ("🌱", "Biodegradable"),
        "larga_vida": ("", "Larga Vida"),
        "regenerado": ("↻", "Regenerado"),
        "sin_bpa": ("✓", "Sin BPA"),
        "absorbente": ("", "Absorbente"),
        "hecho_a_mano": ("✋", "Hecho a Mano"),
        "local": ("📍", "Producción Local"),
    }
    
    spacing = size + 12
    for i, badge in enumerate(badges):
        bx = x + i * spacing
        icon, label = badge_icons.get(badge, ("•", badge))
        
        c.saveState()
        c.setFillColor(COLOR_OLIVA)
        c.setFont("Helvetica", size + 2)
        c.drawString(bx, y, icon)
        
        c.setFont("Helvetica", 6)
        c.setFillColor(COLOR_GRIS)
        c.drawString(bx, y - 10, label)
        c.restoreState()


def draw_header_brand(c, page_num=None):
    """Header con marca Yolitia."""
    c.saveState()
    
    # Logo/texto marca
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(COLOR_NEGRO)
    c.drawString(MARGIN, PAGE_H - 35, "YOLITIA")
    
    # Subtítulo
    c.setFont("Helvetica", 7)
    c.setFillColor(COLOR_OLIVA)
    c.drawString(MARGIN + 70, PAGE_H - 30, "HACIA UNA ECONOMÍA CIRCULAR")
    
    # Iconos decorativos
    draw_leaf_icon(c, PAGE_W - MARGIN - 50, PAGE_H - 40, 12, COLOR_OLIVA)
    draw_recycle_icon(c, PAGE_W - MARGIN - 30, PAGE_H - 40, 12, COLOR_OLIVA)
    
    # Línea separadora
    c.setStrokeColor(COLOR_GRIS_CLARO)
    c.setLineWidth(0.5)
    c.line(MARGIN, PAGE_H - 45, PAGE_W - MARGIN, PAGE_H - 45)
    
    c.restoreState()


def draw_footer(c, page_num):
    """Footer con website y número de página."""
    c.saveState()
    
    # Línea superior
    c.setStrokeColor(COLOR_GRIS_CLARO)
    c.setLineWidth(0.5)
    c.line(MARGIN, 35, PAGE_W - MARGIN, 35)
    
    # Website
    c.setFont("Helvetica", 7)
    c.setFillColor(COLOR_GRIS)
    c.drawString(MARGIN, 20, "www.yolitia.bio")
    c.drawRightString(PAGE_W - MARGIN, 20, "Colección Regenerativa 2026")
    
    # Número de página
    c.setFont("Courier", 8)
    c.setFillColor(COLOR_GRIS_CLARO)
    c.drawCentredString(PAGE_W / 2, 20, f"{page_num:02d}")
    
    c.restoreState()


def build_cover(c):
    """Portada elegante."""
    print("  Portada...")
    
    # Fondo blanco
    c.setFillColor(COLOR_BLANCO)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    
    # Franja superior arena
    c.setFillColor(COLOR_ARENA)
    c.rect(0, PAGE_H - 120, PAGE_W, 120, stroke=0, fill=1)
    
    # Espiral signature grande
    draw_spiral_signature(c, PAGE_W/2, PAGE_H/2 + 80, 220, COLOR_OLIVA, opacity=0.15)
    
    # Marca
    c.saveState()
    c.setFont("Helvetica-Bold", 60)
    c.setFillColor(COLOR_NEGRO)
    c.drawCentredString(PAGE_W/2, PAGE_H/2 + 50, "YOLITIA")
    
    c.setFont("Helvetica", 16)
    c.setFillColor(COLOR_OLIVA)
    c.drawCentredString(PAGE_W/2, PAGE_H/2 + 10, "Hacia una economía circular")
    
    # Línea decorativa
    c.setStrokeColor(COLOR_OLIVA)
    c.setLineWidth(1.5)
    c.line(PAGE_W/2 - 120, PAGE_H/2 - 10, PAGE_W/2 + 120, PAGE_H/2 - 10)
    
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(COLOR_NEGRO)
    c.drawCentredString(PAGE_W/2, PAGE_H/2 - 40, "COLECCIÓN REGENERATIVA")
    
    c.setFont("Helvetica", 11)
    c.setFillColor(COLOR_GRIS)
    c.drawCentredString(PAGE_W/2, PAGE_H/2 - 65, "Impresión 3D en PLA Biodegradable")
    c.drawCentredString(PAGE_W/2, PAGE_H/2 - 85, "Catálogo 2026")
    
    # Iconos en esquinas
    draw_leaf_icon(c, MARGIN + 20, PAGE_H - MARGIN - 40, 20, COLOR_OLIVA)
    draw_recycle_icon(c, PAGE_W - MARGIN - 40, PAGE_H - MARGIN - 40, 20, COLOR_OLIVA)
    
    # Franja inferior rosa pastel
    c.setFillColor(COLOR_ROSA_PASTEL)
    c.rect(0, 0, PAGE_W, 80, stroke=0, fill=1)
    
    c.setFont("Helvetica", 9)
    c.setFillColor(COLOR_NEGRO)
    c.drawCentredString(PAGE_W/2, 40, "Diseño consciente · Impreso aquí · Hecho para durar")
    
    c.restoreState()
    c.showPage()


def build_index(c, layout):
    """Índice de categorías."""
    print("  Índice...")
    
    c.setFillColor(COLOR_BLANCO)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    
    draw_header_brand(c)
    
    c.saveState()
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(COLOR_NEGRO)
    c.drawString(MARGIN, PAGE_H - 100, "Contenido")
    
    c.setStrokeColor(COLOR_OLIVA)
    c.setLineWidth(1.5)
    c.line(MARGIN, PAGE_H - 115, PAGE_W - MARGIN, PAGE_H - 115)
    
    y = PAGE_H - 160
    
    categorias_vistas = set()
    for pagina in layout["paginas"]:
        if pagina["tipo"] == "separador_categoria":
            cat = pagina["categoria"]
            if cat not in categorias_vistas:
                categorias_vistas.add(cat)
                page_num = pagina["pagina_numero"]
                
                # Icono de categoría
                draw_leaf_icon(c, MARGIN, y - 5, 14, COLOR_OLIVA)
                
                # Nombre categoría
                c.setFont("Helvetica-Bold", 14)
                c.setFillColor(COLOR_NEGRO)
                c.drawString(MARGIN + 30, y, cat)
                
                # Número de página
                c.setFont("Courier", 12)
                c.setFillColor(COLOR_GRIS_CLARO)
                c.drawRightString(PAGE_W - MARGIN, y, f"{page_num:02d}")
                
                # Línea punteada
                c.setStrokeColor(COLOR_GRIS_CLARO)
                c.setLineWidth(0.5)
                c.setDash(2, 2)
                text_w = pdfmetrics.stringWidth(cat, "Helvetica-Bold", 14)
                num_w = pdfmetrics.stringWidth(f"{page_num:02d}", "Courier", 12)
                c.line(MARGIN + 35 + text_w, y + 5, PAGE_W - MARGIN - 10 - num_w, y + 5)
                c.setDash()
                
                y -= 50
    
    c.restoreState()
    draw_footer(c, 0)
    c.showPage()


def build_category_spread(c, pagina_data, layout, productos, is_left=True):
    """Página de separador de categoría o producto hero."""
    cat = pagina_data.get("categoria", "")
    page_num = pagina_data["pagina_numero"]
    
    if pagina_data["tipo"] == "separador_categoria":
        print(f"  Separador: {cat} (pág {page_num})")
        
        c.setFillColor(COLOR_BLANCO)
        c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
        
        draw_header_brand(c, page_num)
        
        # Franja azul claro suave
        c.saveState()
        c.setFillColor(COLOR_AZUL_CLARO)
        c.setFillAlpha(0.2)
        c.rect(0, PAGE_H/2 - 60, PAGE_W, 120, stroke=0, fill=1)
        c.restoreState()
        
        # Espiral signature
        draw_spiral_signature(c, PAGE_W/2, PAGE_H/2, 180, COLOR_OLIVA, opacity=0.12)
        
        # Título categoría
        c.saveState()
        c.setFont("Helvetica-Bold", 36)
        c.setFillColor(COLOR_NEGRO)
        c.drawCentredString(PAGE_W/2, PAGE_H/2 + 30, cat)
        
        c.setFont("Helvetica", 12)
        c.setFillColor(COLOR_OLIVA)
        c.drawCentredString(PAGE_W/2, PAGE_H/2 - 10, "Colección Regenerativa")
        
        # Línea decorativa
        c.setStrokeColor(COLOR_OLIVA)
        c.setLineWidth(1.5)
        c.line(PAGE_W/2 - 100, PAGE_H/2 - 30, PAGE_W/2 + 100, PAGE_H/2 - 30)
        
        # Contador de productos
        prods_en_cat = [p for p in layout["paginas"] 
                        if p["tipo"] == "productos" and p.get("categoria") == cat]
        total_prods = sum(p.get("num_productos", 0) for p in prods_en_cat)
        
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(COLOR_NEGRO)
        c.drawCentredString(PAGE_W/2, PAGE_H/2 - 60, f"{total_prods} productos")
        
        c.restoreState()
        
        draw_footer(c, page_num)
        c.showPage()
    
    elif pagina_data["tipo"] == "productos" and is_left:
        build_hero_product(c, pagina_data, productos, page_num)


def build_hero_product(c, pagina_data, productos, page_num):
    """Producto hero en página izquierda."""
    elementos = pagina_data.get("elementos", [])
    if not elementos:
        return
    
    elem = elementos[0]
    prod = productos.get(elem["producto_id"])
    if not prod:
        return
    
    print(f"  Hero: {prod['nombre_yolitia'][:30]} (pág {page_num})")
    
    c.setFillColor(COLOR_BLANCO)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    
    draw_header_brand(c, page_num)
    
    img_path = get_image_path(elem)
    
    # Imagen grande del producto
    if img_path and Path(img_path).exists():
        try:
            img_w = CONTENT_W - 40
            img_h = (PAGE_H - 200) * 0.65
            c.drawImage(img_path, MARGIN + 20, PAGE_H/2 - 20,
                       width=img_w, height=img_h,
                       preserveAspectRatio=True, anchor='c')
        except Exception as e:
            print(f"    Error imagen: {e}")
    
    # Información del producto
    text_y = 180
    
    c.saveState()
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(COLOR_NEGRO)
    c.drawString(MARGIN + 20, text_y, prod["nombre_yolitia"][:40])
    
    # Descripción
    c.setFont("Helvetica", 10)
    c.setFillColor(COLOR_GRIS)
    desc = prod.get("descripcion_corta") or prod.get("descripcion_larga") or prod["nombre_yolitia"]
    c.drawString(MARGIN + 20, text_y - 25, desc[:70])
    
    # Material
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(COLOR_OLIVA)
    c.drawString(MARGIN + 20, text_y - 55, "MATERIAL:")
    c.setFont("Helvetica", 9)
    c.setFillColor(COLOR_NEGRO)
    c.drawString(MARGIN + 80, text_y - 55, prod.get("material", "PLA"))
    
    # Iconos de sostenibilidad
    badges = ["reciclable", "biodegradable", "larga_vida"]
    draw_sustainability_badges(c, MARGIN + 20, text_y - 90, badges, size=10)
    
    # Precio
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(COLOR_NEGRO)
    c.drawString(MARGIN + 20, text_y - 130, "$ ___________")
    
    c.restoreState()
    
    draw_footer(c, page_num)
    c.showPage()


def build_product_grid(c, pagina_data, productos, page_num):
    """Grid de productos en página derecha."""
    elementos = pagina_data.get("elementos", [])
    grid = pagina_data.get("grid", "1x2")
    
    print(f"  Grid {grid}: {len(elementos)} productos (pág {page_num})")
    
    c.setFillColor(COLOR_BLANCO)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    
    draw_header_brand(c, page_num)
    
    if grid == "2x2":
        build_2x2_grid(c, elementos, productos)
    elif grid == "1x2":
        build_1x2_grid(c, elementos, productos)
    elif grid == "1x3":
        build_1x3_grid(c, elementos, productos)
    
    draw_footer(c, page_num)
    c.showPage()


def build_2x2_grid(c, elementos, productos):
    """Grid 2x2 para aretes y productos pequeños."""
    card_w = (CONTENT_W - 30) / 2
    card_h = (PAGE_H - 180) / 2
    
    positions = [
        (MARGIN + 15, PAGE_H - 100 - card_h),
        (MARGIN + 15 + card_w + 15, PAGE_H - 100 - card_h),
        (MARGIN + 15, PAGE_H - 100 - card_h * 2 - 20),
        (MARGIN + 15 + card_w + 15, PAGE_H - 100 - card_h * 2 - 20),
    ]
    
    for i, elem in enumerate(elementos[:4]):
        prod = productos.get(elem["producto_id"])
        if not prod:
            continue
        
        x, y = positions[i]
        img_path = get_image_path(elem)
        
        # Fondo tarjeta arena
        c.setFillColor(COLOR_ARENA)
        c.roundRect(x, y, card_w, card_h, 4, stroke=0, fill=1)
        
        # Imagen
        if img_path and Path(img_path).exists():
            try:
                img_w = card_w - 20
                img_h = card_h - 80
                c.drawImage(img_path, x + 10, y + 60,
                           width=img_w, height=img_h,
                           preserveAspectRatio=True, anchor='c')
            except Exception:
                pass
        
        # Nombre
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(COLOR_NEGRO)
        c.drawString(x + 10, y + 40, prod["nombre_yolitia"][:25])
        
        # Material
        c.setFont("Helvetica", 7)
        c.setFillColor(COLOR_OLIVA)
        c.drawString(x + 10, y + 28, prod.get("material", "PLA"))
        
        # Iconos pequeños
        c.setFont("Helvetica", 7)
        c.setFillColor(COLOR_GRIS)
        c.drawString(x + 10, y + 15, "♻ Reciclable")
        
        # Precio
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(COLOR_NEGRO)
        c.drawString(x + 10, y + 5, "$ ___")


def build_1x2_grid(c, elementos, productos):
    """Grid 1x2 para productos medianos."""
    card_w = CONTENT_W - 20
    card_h = (PAGE_H - 180) / 2
    
    positions = [
        (MARGIN + 10, PAGE_H - 100 - card_h),
        (MARGIN + 10, PAGE_H - 100 - card_h * 2 - 30),
    ]
    
    for i, elem in enumerate(elementos[:2]):
        prod = productos.get(elem["producto_id"])
        if not prod:
            continue
        
        x, y = positions[i]
        img_path = get_image_path(elem)
        
        # Fondo tarjeta arena
        c.setFillColor(COLOR_ARENA)
        c.roundRect(x, y, card_w, card_h, 6, stroke=0, fill=1)
        
        # Imagen (lado izquierdo)
        if img_path and Path(img_path).exists():
            try:
                img_w = card_w * 0.4
                img_h = card_h - 20
                c.drawImage(img_path, x + 10, y + 10,
                           width=img_w, height=img_h,
                           preserveAspectRatio=True, anchor='w')
            except Exception:
                pass
        
        # Texto (lado derecho)
        text_x = x + card_w * 0.45
        
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(COLOR_NEGRO)
        c.drawString(text_x, y + card_h - 30, prod["nombre_yolitia"][:30])
        
        c.setFont("Helvetica", 9)
        c.setFillColor(COLOR_GRIS)
        desc = prod.get("descripcion_corta") or prod["nombre_yolitia"]
        c.drawString(text_x, y + card_h - 50, desc[:40])
        
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(COLOR_OLIVA)
        c.drawString(text_x, y + card_h - 70, "MATERIAL:")
        c.setFont("Helvetica", 8)
        c.setFillColor(COLOR_NEGRO)
        c.drawString(text_x + 50, y + card_h - 70, prod.get("material", "PLA"))
        
        # Iconos
        c.setFont("Helvetica", 8)
        c.setFillColor(COLOR_GRIS)
        c.drawString(text_x, y + 25, "♻ Reciclable  ∞ Larga Vida  🌱 Biodegradable")
        
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(COLOR_NEGRO)
        c.drawString(text_x, y + 5, "$ ___")


def build_1x3_grid(c, elementos, productos):
    """Grid 1x3 para productos pequeños."""
    card_w = CONTENT_W - 20
    card_h = (PAGE_H - 180) / 3
    
    positions = [
        (MARGIN + 10, PAGE_H - 100 - card_h),
        (MARGIN + 10, PAGE_H - 100 - card_h * 2 - 15),
        (MARGIN + 10, PAGE_H - 100 - card_h * 3 - 30),
    ]
    
    for i, elem in enumerate(elementos[:3]):
        prod = productos.get(elem["producto_id"])
        if not prod:
            continue
        
        x, y = positions[i]
        img_path = get_image_path(elem)
        
        # Fondo tarjeta arena
        c.setFillColor(COLOR_ARENA)
        c.roundRect(x, y, card_w, card_h, 4, stroke=0, fill=1)
        
        # Imagen
        if img_path and Path(img_path).exists():
            try:
                img_w = card_w * 0.3
                img_h = card_h - 15
                c.drawImage(img_path, x + 8, y + 8,
                           width=img_w, height=img_h,
                           preserveAspectRatio=True, anchor='w')
            except Exception:
                pass
        
        # Texto
        text_x = x + card_w * 0.35
        
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(COLOR_NEGRO)
        c.drawString(text_x, y + card_h - 25, prod["nombre_yolitia"][:25])
        
        c.setFont("Helvetica", 8)
        c.setFillColor(COLOR_GRIS)
        c.drawString(text_x, y + card_h - 40, prod.get("material", "PLA"))
        
        c.setFont("Helvetica", 7)
        c.setFillColor(COLOR_GRIS)
        c.drawString(text_x, y + 15, "♻ Reciclable")
        
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(COLOR_NEGRO)
        c.drawString(text_x, y + 5, "$ ___")


def build_pla_page(c, page_num):
    """Página sobre material PLA."""
    print(f"  PLA (pág {page_num})")
    
    c.setFillColor(COLOR_BLANCO)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    
    draw_header_brand(c, page_num)
    
    # Franja oliva suave
    c.saveState()
    c.setFillColor(COLOR_OLIVA)
    c.setFillAlpha(0.1)
    c.rect(0, PAGE_H - 150, PAGE_W, 80, stroke=0, fill=1)
    c.restoreState()
    
    c.saveState()
    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(COLOR_OLIVA)
    c.drawCentredString(PAGE_W/2, PAGE_H - 110, "HECHO DE PLA")
    
    c.setFont("Helvetica", 13)
    c.setFillColor(COLOR_NEGRO)
    c.drawCentredString(PAGE_W/2, PAGE_H - 135, "Bello por dentro y por fuera")
    
    c.setStrokeColor(COLOR_OLIVA)
    c.setLineWidth(1.5)
    c.line(MARGIN + 100, PAGE_H - 150, PAGE_W - MARGIN - 100, PAGE_H - 150)
    
    # Contenido
    text_x = MARGIN + 40
    text_y = PAGE_H - 200
    line_height = 16
    
    paragraphs = [
        ("Helvetica-Bold", COLOR_NEGRO, "El PLA (Ácido Poliláctico) es un polímero de origen vegetal,"),
        ("Helvetica", COLOR_NEGRO, "derivado principalmente de almidón de maíz o caña de azúcar."),
        ("Helvetica", COLOR_NEGRO, "A diferencia de los plásticos convencionales, el PLA se obtiene"),
        ("Helvetica", COLOR_NEGRO, "de fuentes renovables y es compostable en condiciones industriales."),
        ("Helvetica", None, ""),
        ("Helvetica-Bold", COLOR_OLIVA, "Por qué importa:"),
        ("Helvetica", None, ""),
        ("Helvetica", COLOR_NEGRO, "  • Reduce la dependencia de petroquímicos"),
        ("Helvetica", COLOR_NEGRO, "  • Menor huella de carbono en su producción"),
        ("Helvetica", COLOR_NEGRO, "  • Compostable: no se acumula en océanos por siglos"),
        ("Helvetica", COLOR_NEGRO, "  • Permite producción local y bajo demanda"),
        ("Helvetica", COLOR_NEGRO, "  • Cero inventario excedente = cero desperdicio"),
        ("Helvetica", None, ""),
        ("Helvetica-Bold", COLOR_NEGRO, "En Yolitia, cada pieza se imprime en 3D cuando tú la pides."),
        ("Helvetica", COLOR_NEGRO, "No hay bodegas llenas. No hay sobreproducción."),
    ]
    
    for font, color, text in paragraphs:
        if font:
            c.setFont(font, 10)
        if color:
            c.setFillColor(color)
        c.drawString(text_x, text_y, text)
        text_y -= line_height
    
    # Espiral decorativa
    draw_spiral_signature(c, PAGE_W - 120, 150, 80, COLOR_OLIVA, opacity=0.15)
    
    c.restoreState()
    draw_footer(c, page_num)
    c.showPage()


def build_back_cover(c):
    """Contraportada con manifiesto."""
    print("  Contraportada...")
    
    c.setFillColor(COLOR_BLANCO)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    
    # Espiral signature
    draw_spiral_signature(c, PAGE_W/2, PAGE_H/2 + 80, 180, COLOR_OLIVA, opacity=0.12)
    
    # Franja superior arena
    c.setFillColor(COLOR_ARENA)
    c.rect(0, PAGE_H - 80, PAGE_W, 80, stroke=0, fill=1)
    
    c.saveState()
    c.setFont("Helvetica-Bold", 30)
    c.setFillColor(COLOR_NEGRO)
    c.drawCentredString(PAGE_W/2, PAGE_H - 100, "YOLITIA")
    
    c.setFont("Helvetica", 13)
    c.setFillColor(COLOR_OLIVA)
    c.drawCentredString(PAGE_W/2, PAGE_H - 125, "Un proyecto circular")
    
    c.setStrokeColor(COLOR_OLIVA)
    c.setLineWidth(1.5)
    c.line(MARGIN + 100, PAGE_H - 145, PAGE_W - MARGIN - 100, PAGE_H - 145)
    
    text_x = MARGIN + 50
    text_y = PAGE_H - 200
    line_height = 18
    
    manifesto = [
        ("Helvetica", COLOR_NEGRO, "Yolitia nace de una pregunta simple:"),
        ("Helvetica-Oblique", COLOR_NEGRO, "¿Y si los objetos que usamos cada día pudieran"),
        ("Helvetica-Oblique", COLOR_NEGRO, "hacerse con menos y significar más?"),
        ("Helvetica", None, ""),
        ("Helvetica-Bold", COLOR_OLIVA, "Nuestro modelo es diferente:"),
        ("Helvetica", None, ""),
        ("Helvetica", COLOR_NEGRO, "  → Producimos bajo pedido, no en masa"),
        ("Helvetica", COLOR_NEGRO, "  → Usamos materiales de origen vegetal (PLA)"),
        ("Helvetica", COLOR_NEGRO, "  → Diseñamos para durar, no para desechar"),
        ("Helvetica", COLOR_NEGRO, "  → Cada compra apoya la manufactura local"),
        ("Helvetica", None, ""),
        ("Helvetica", COLOR_NEGRO, "Somos parte del movimiento de economía circular:"),
        ("Helvetica", COLOR_NEGRO, "los materiales entran, se usan, se recuperan."),
        ("Helvetica-Bold", COLOR_OLIVA, "Nada se pierde. Todo vuelve."),
        ("Helvetica", None, ""),
        ("Helvetica", None, ""),
        ("Helvetica-Bold", COLOR_OLIVA, "Yolitia"),
        ("Helvetica", COLOR_NEGRO, "Diseño consciente. Impreso aquí."),
    ]
    
    for font, color, text in manifesto:
        if font:
            c.setFont(font, 11)
        if color:
            c.setFillColor(color)
        c.drawString(text_x, text_y, text)
        text_y -= line_height
    
    # Iconos en esquinas
    draw_leaf_icon(c, MARGIN + 20, MARGIN + 20, 15, COLOR_OLIVA)
    draw_recycle_icon(c, PAGE_W - MARGIN - 35, MARGIN + 20, 15, COLOR_OLIVA)
    
    # Franja inferior rosa pastel
    c.setFillColor(COLOR_ROSA_PASTEL)
    c.rect(0, 0, PAGE_W, 60, stroke=0, fill=1)
    
    c.setFont("Helvetica", 9)
    c.setFillColor(COLOR_NEGRO)
    c.drawCentredString(PAGE_W/2, 30, "www.yolitia.bio | @yolitia")
    
    c.restoreState()
    c.showPage()


def get_image_path(elem):
    """Obtiene ruta de imagen."""
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


def build_catalog():
    """Genera catálogo PDF v3."""
    print("=" * 70)
    print("GENERACIÓN CATÁLOGO YOLITIA v3 - DISEÑO EDITORIAL PREMIUM")
    print("=" * 70)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    layout, productos = load_data()
    print(f"\nLayout: {len(layout['paginas'])} páginas")
    print(f"Productos: {len(productos)}")
    
    c = canvas.Canvas(str(OUTPUT_PDF), pagesize=A4)
    c.setTitle("Catálogo Yolitia 2026 - Colección Regenerativa")
    c.setAuthor("Yolitia")
    c.setSubject("Catálogo de productos impresos en 3D en PLA biodegradable")
    
    paginas_generadas = 0
    pagina_actual = 0
    
    for pagina_data in layout["paginas"]:
        tipo = pagina_data["tipo"]
        
        if tipo == "portada":
            build_cover(c)
            paginas_generadas += 1
        
        elif tipo == "indice":
            build_index(c, layout)
            paginas_generadas += 1
            pagina_actual += 1
        
        elif tipo == "separador_categoria":
            build_category_spread(c, pagina_data, layout, productos, is_left=True)
            paginas_generadas += 1
            pagina_actual += 1
        
        elif tipo == "productos":
            es_hero = pagina_data.get("grid") == "1x1"
            
            if es_hero:
                build_hero_product(c, pagina_data, productos, pagina_actual + 1)
                paginas_generadas += 1
                pagina_actual += 1
            else:
                build_product_grid(c, pagina_data, productos, pagina_actual + 1)
                paginas_generadas += 1
                pagina_actual += 1
        
        elif tipo == "material_pla":
            build_pla_page(c, pagina_actual + 1)
            paginas_generadas += 1
            pagina_actual += 1
        
        elif tipo == "contraportada":
            build_back_cover(c)
            paginas_generadas += 1
    
    c.save()
    
    print(f"\n{'=' * 70}")
    print(f"PDF GENERADO:")
    print(f"  Archivo: {OUTPUT_PDF}")
    print(f"  Páginas: {paginas_generadas}")
    
    file_size = OUTPUT_PDF.stat().st_size
    print(f"  Tamaño: {file_size / (1024*1024):.2f} MB")
    
    try:
        reader = PdfReader(str(OUTPUT_PDF))
        pdf_pages = len(reader.pages)
        print(f"  Validación: OK ({pdf_pages} páginas)")
    except Exception as e:
        print(f"  Error validación: {e}")
    
    print(f"{'=' * 70}")
    
    return paginas_generadas


if __name__ == "__main__":
    build_catalog()
