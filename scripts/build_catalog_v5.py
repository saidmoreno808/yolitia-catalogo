"""
Catálogo Yolitia v5 - Estilo editorial caligráfico
Inspirado en el diseño de referencia: tipografía script, etiquetas de papel,
polaroid frames, cinta adhesiva decorativa, curvas orgánicas de fondo.

Solo cambia el estilo visual. NO se modifica información, nombres ni precios.
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
from reportlab.pdfbase.ttfonts import TTFont

from PyPDF2 import PdfReader


BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = BASE_DIR / "assets" / "images" / "productos"
OUTPUT_DIR = BASE_DIR / "output"
LAYOUT_FILE = DATA_DIR / "catalog_layout_plan.json"
JSON_FILE = DATA_DIR / "yolitia_products_database.json"
OUTPUT_PDF = OUTPUT_DIR / "catalogo_yolitia_v5.pdf"


# ============================================================================
# PALETA — Estilo editorial caligráfico (referencia: catálogo Yolitia de muestra)
# ============================================================================
COLOR_MARFIL      = colors.HexColor("#F5F0E6")  # fondo principal
COLOR_MARFIL_CLARO = colors.HexColor("#FAF7EF")
COLOR_CREMA       = colors.HexColor("#E8DCC4")  # etiquetas de papel
COLOR_CREMA_OSC   = colors.HexColor("#D8C9A8")
COLOR_KRAFT       = colors.HexColor("#D9CBA8")  # cinta adhesiva
COLOR_NEGRO       = colors.HexColor("#1A1614")  # texto principal
COLOR_NEGRO_SUAVE = colors.HexColor("#2D2620")
COLOR_MORADO      = colors.HexColor("#4A4458")  # color de la marca (gris-violáceo)
COLOR_VERDE       = colors.HexColor("#5C6E54")  # isotipo/acentos
COLOR_MARRON      = colors.HexColor("#5A4A3A")
COLOR_GRIS_LINEA  = colors.HexColor("#C9BFA9")


# ============================================================================
# TIPOGRAFÍAS — Emparejadas como en el diseño de referencia
# ============================================================================
SCRIPT_REG  = "YolitiaScript"   # LCALLIG — para "Yolitia" principal (caligráfica)
SCRIPT_BOLD = "YolitiaScriptB"  # PRISTINA — alternativa cursiva
SANS_REG    = "YolitiaSans"     # calibri light — cuerpo versalitas
SANS_BOLD   = "YolitiaSansB"    # calibri bold — énfasis
SANS_LIGHT  = "YolitiaSansL"    # calibri light
SERIF_REG   = "YolitiaSerif"    # BOD_R — precios y acentos serif
SERIF_ITAL  = "YolitiaSerifI"   # BOD_I — cursiva editorial
SERIF_BOLD  = "YolitiaSerifB"   # BOD_B — títulos serif

WIN_FONTS = Path("C:/Windows/Fonts")


def register_fonts():
    """Registra fuentes del sistema según el estilo del catálogo de referencia."""
    # Caligráfica para la marca "Yolitia" (script elegante)
    try:
        pdfmetrics.registerFont(TTFont(SCRIPT_REG, str(WIN_FONTS / "LCALLIG.TTF")))
    except Exception:
        pdfmetrics.registerFont(TTFont(SCRIPT_REG, str(WIN_FONTS / "PRISTINA.TTF")))

    # Cursiva alternativa
    pdfmetrics.registerFont(TTFont(SCRIPT_BOLD, str(WIN_FONTS / "PRISTINA.TTF")))

    # Sans-serif limpia para versalitas
    pdfmetrics.registerFont(TTFont(SANS_REG, str(WIN_FONTS / "calibri.ttf")))
    pdfmetrics.registerFont(TTFont(SANS_BOLD, str(WIN_FONTS / "calibrib.ttf")))
    pdfmetrics.registerFont(TTFont(SANS_LIGHT, str(WIN_FONTS / "calibri.ttf")))

    # Serif para precios y detalles editoriales
    pdfmetrics.registerFont(TTFont(SERIF_REG, str(WIN_FONTS / "BOD_R.TTF")))
    pdfmetrics.registerFont(TTFont(SERIF_ITAL, str(WIN_FONTS / "BOD_I.TTF")))
    pdfmetrics.registerFont(TTFont(SERIF_BOLD, str(WIN_FONTS / "BOD_B.TTF")))


# ============================================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================================
PAGE_W, PAGE_H = A4
MARGIN = 40
CONTENT_W = PAGE_W - (2 * MARGIN)


# ============================================================================
# UTILIDADES DE DIBUJO
# ============================================================================

def draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.45):
    """
    Curvas orgánicas grandes de fondo — el signature del diseño de referencia.
    Formas suaves tipo hojas/ondas en color gris cálido.
    """
    c.saveState()
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setStrokeAlpha(opacity)
    c.setFillAlpha(opacity)
    c.setLineWidth(0.8)

    # Curva grande inferior izquierda
    p = c.beginPath()
    p.moveTo(-50, 0)
    p.curveTo(60, 80, 140, 200, 80, 320)
    p.curveTo(20, 420, -40, 480, -50, 520)
    p.lineTo(-50, 0)
    p.close()
    c.drawPath(p, stroke=0, fill=1)

    # Curva grande superior derecha
    p = c.beginPath()
    p.moveTo(PAGE_W + 30, PAGE_H)
    p.curveTo(PAGE_W - 60, PAGE_H - 100, PAGE_W - 180, PAGE_H - 220, PAGE_W - 100, PAGE_H - 360)
    p.curveTo(PAGE_W - 40, PAGE_H - 480, PAGE_W + 10, PAGE_H - 560, PAGE_W + 30, PAGE_H - 600)
    p.lineTo(PAGE_W + 30, PAGE_H)
    p.close()
    c.drawPath(p, stroke=0, fill=1)

    # Curva media derecha
    p = c.beginPath()
    p.moveTo(PAGE_W, PAGE_H * 0.5)
    p.curveTo(PAGE_W - 80, PAGE_H * 0.5 + 30, PAGE_W - 40, PAGE_H * 0.5 - 60, PAGE_W - 100, PAGE_H * 0.5 - 140)
    p.curveTo(PAGE_W - 150, PAGE_H * 0.5 - 200, PAGE_W - 30, PAGE_H * 0.5 - 220, PAGE_W, PAGE_H * 0.5 - 240)
    p.lineTo(PAGE_W, PAGE_H * 0.5)
    p.close()
    c.drawPath(p, stroke=0, fill=1)

    c.restoreState()


def draw_washi_tape(c, x, y, w, h=14, angle=0, color=COLOR_KRAFT):
    """Cinta adhesiva decorativa (washi tape) sobre las fotos."""
    c.saveState()
    c.translate(x + w / 2, y + h / 2)
    c.rotate(angle)
    c.setFillColor(color)
    c.setFillAlpha(0.88)
    c.rect(-w / 2, -h / 2, w, h, stroke=0, fill=1)
    # Líneas tenues verticales
    c.setStrokeAlpha(0.18)
    c.setStrokeColor(colors.HexColor("#B8A988"))
    c.setLineWidth(0.4)
    for i in range(-int(w / 2) + 4, int(w / 2) - 4, 6):
        c.line(i, -h / 2 + 1, i, h / 2 - 1)
    c.restoreState()


def draw_polaroid_frame(c, x, y, w, h, rotation=0, shadow=True):
    """
    Marco polaroid blanco con sombra. Devuelve el rectángulo interno donde
    se debe colocar la imagen.
    """
    c.saveState()
    c.translate(x + w / 2, y + h / 2)
    c.rotate(rotation)

    border_top = 18
    border_bottom = 50
    border_lr = 16
    img_w = w - 2 * border_lr
    img_h = h - border_top - border_bottom

    # Sombra suave
    if shadow:
        c.setFillColor(colors.HexColor("#D8CFC0"))
        c.setFillAlpha(0.55)
        c.roundRect(-w / 2 + 2, -h / 2 - 2, w, h, 2, stroke=0, fill=1)

    # Marco blanco
    c.setFillColor(colors.HexColor("#FFFFFF"))
    c.setFillAlpha(1.0)
    c.roundRect(-w / 2, -h / 2, w, h, 2, stroke=0, fill=1)

    # Borde muy sutil
    c.setStrokeColor(colors.HexColor("#E8E0D2"))
    c.setLineWidth(0.4)
    c.roundRect(-w / 2, -h / 2, w, h, 2, stroke=1, fill=0)

    c.restoreState()

    return {
        "x": x + border_lr,
        "y": y + border_bottom,
        "w": img_w,
        "h": img_h,
        "cx": x + w / 2,
        "cy": y + h / 2,
    }


def draw_paper_label(c, x, y, w, h, rotation=0, color=COLOR_CREMA, has_tape=True, tape_pos="top"):
    """
    Etiqueta de papel rectangular con cinta adhesiva opcional encima.
    Estilo "papel pegado" del diseño de referencia.
    """
    c.saveState()
    c.translate(x + w / 2, y + h / 2)
    c.rotate(rotation)

    # Sombra
    c.setFillColor(colors.HexColor("#C8BBA0"))
    c.setFillAlpha(0.4)
    c.roundRect(-w / 2 + 1.5, -h / 2 - 1.5, w, h, 1, stroke=0, fill=1)

    # Papel
    c.setFillColor(color)
    c.setFillAlpha(1.0)
    c.rect(-w / 2, -h / 2, w, h, stroke=0, fill=1)

    # Borde muy sutil
    c.setStrokeColor(colors.HexColor("#C8B89C"))
    c.setLineWidth(0.3)
    c.rect(-w / 2, -h / 2, w, h, stroke=1, fill=0)

    # Cinta adhesiva
    if has_tape:
        if tape_pos == "top":
            tape_x, tape_y, tape_w, tape_h = -28, h / 2 - 4, 56, 10
        else:
            tape_x, tape_y, tape_w, tape_h = -22, -h / 2 - 3, 44, 8
        c.setFillColor(COLOR_KRAFT)
        c.setFillAlpha(0.85)
        c.rect(tape_x, tape_y, tape_w, tape_h, stroke=0, fill=1)
        c.setFillAlpha(1.0)

    c.restoreState()


def draw_isotipo_hoja(c, cx, cy, size, color=COLOR_VERDE):
    """
    Isotipo de hoja geométrica: cuatro pétalos tipo trébol/hoja en cruz diagonal,
    como el del catálogo de referencia.
    """
    c.saveState()
    c.translate(cx, cy)
    c.setFillColor(color)

    # Tamaño base de cada pétalo
    pw = size * 0.32  # ancho del pétalo
    pl = size * 0.48  # largo del pétalo

    # Pétalo: forma de hoja almendrada (curvas bezier simétricas)
    def petal():
        p = c.beginPath()
        p.moveTo(0, 0)
        p.curveTo(pw * 0.6, pl * 0.15, pw * 0.55, pl * 0.7, 0, pl)
        p.curveTo(-pw * 0.55, pl * 0.7, -pw * 0.6, pl * 0.15, 0, 0)
        p.close()
        c.drawPath(p, stroke=0, fill=1)

    # Pétalo central (norte)
    petal()
    # Pétalo sur (rotado 180°)
    c.saveState()
    c.rotate(180)
    petal()
    c.restoreState()
    # Pétalo este (rotado 90° horario)
    c.saveState()
    c.rotate(90)
    petal()
    c.restoreState()
    # Pétalo oeste (rotado 90° antihorario)
    c.saveState()
    c.rotate(-90)
    petal()
    c.restoreState()

    c.restoreState()


def draw_thin_line(c, x1, y1, x2, y2, color=COLOR_NEGRO, width=0.6):
    """Línea fina decorativa."""
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)
    c.restoreState()


def fit_image_in_box(c, img_path, box_x, box_y, box_w, box_h):
    """Dibuja una imagen centrada en el box preservando aspecto."""
    try:
        img = ImageReader(img_path)
        iw, ih = img.getSize()
        ratio = iw / ih
        box_ratio = box_w / box_h
        if ratio > box_ratio:
            w = box_w
            h = box_w / ratio
        else:
            h = box_h
            w = box_h * ratio
        x = box_x + (box_w - w) / 2
        y = box_y + (box_h - h) / 2
        c.drawImage(img_path, x, y, width=w, height=h,
                   preserveAspectRatio=True, mask='auto')
    except Exception as e:
        print(f"    Error imagen {img_path}: {e}")


# ============================================================================
# CARGA DE DATOS
# ============================================================================

def load_data():
    with open(LAYOUT_FILE, "r", encoding="utf-8") as f:
        layout = json.load(f)
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    productos = {p["id"]: p for p in data["productos"]}
    return layout, productos


def get_image_path(elem, productos):
    """Obtiene ruta de imagen principal."""
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
    # Fallback: primera imagen disponible
    folder = IMAGES_DIR / prod_id
    if folder.exists():
        for f in folder.iterdir():
            if "principal" in f.name.lower() and f.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                return str(f)
        for f in folder.iterdir():
            if f.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                return str(f)
    return None


# ============================================================================
# HEADER & FOOTER EDITORIAL
# ============================================================================

def draw_header_brand(c, subtitle=None):
    """Header: isotipo arriba + 'Yolitia' caligráfico + subtítulo versalitas."""
    c.saveState()

    # Isotipo centrado
    draw_isotipo_hoja(c, PAGE_W / 2, PAGE_H - 50, 32, color=COLOR_VERDE)

    # "Yolitia" caligráfico
    c.setFont(SCRIPT_REG, 42)
    c.setFillColor(COLOR_MORADO)
    text_w = pdfmetrics.stringWidth("Yolitia", SCRIPT_REG, 42)
    c.drawString((PAGE_W - text_w) / 2, PAGE_H - 88, "Yolitia")

    # Subtítulo
    if subtitle:
        c.setFont(SANS_REG, 11)
        c.setFillColor(COLOR_NEGRO_SUAVE)
        sub_w = pdfmetrics.stringWidth(subtitle, SANS_REG, 11)
        c.drawString((PAGE_W - sub_w) / 2, PAGE_H - 108, subtitle)
    else:
        c.setFont(SANS_REG, 11)
        c.setFillColor(COLOR_NEGRO_SUAVE)
        sub = "DECORACIÓN PARA EL HOGAR"
        sub_w = pdfmetrics.stringWidth(sub, SANS_REG, 11)
        c.drawString((PAGE_W - sub_w) / 2, PAGE_H - 108, sub)

    c.restoreState()


def draw_footer(c, page_num):
    """Footer editorial con website en itálica y línea fina."""
    c.saveState()
    # Línea fina
    c.setStrokeColor(COLOR_GRIS_LINEA)
    c.setLineWidth(0.4)
    c.line(MARGIN, 35, PAGE_W - MARGIN, 35)

    # Web izquierda
    c.setFont(SERIF_ITAL, 9)
    c.setFillColor(COLOR_MARRON)
    c.drawString(MARGIN, 20, "yolitia.bio")

    # Página centrada
    c.setFont(SERIF_REG, 9)
    c.setFillColor(COLOR_MARRON)
    c.drawCentredString(PAGE_W / 2, 20, f"{page_num:02d}")

    # Tagline derecha
    c.setFont(SANS_REG, 7)
    c.setFillColor(COLOR_MARRON)
    c.drawRightString(PAGE_W - MARGIN, 20, "COLECCIÓN REGENERATIVA  ·  2026")

    c.restoreState()


# ============================================================================
# PÁGINAS ESPECIALES
# ============================================================================

def build_cover(c):
    """Portada editorial caligráfica."""
    print("  Portada...")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

    # Curvas orgánicas de fondo
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.55)

    # Isotipo grande centrado arriba
    draw_isotipo_hoja(c, PAGE_W / 2, PAGE_H - 130, 56, color=COLOR_VERDE)

    # Marca caligráfica
    c.setFont(SCRIPT_REG, 78)
    c.setFillColor(COLOR_MORADO)
    text = "Yolitia"
    w = pdfmetrics.stringWidth(text, SCRIPT_REG, 78)
    c.drawString((PAGE_W - w) / 2, PAGE_H - 210, text)

    # Subtítulo
    c.setFont(SANS_REG, 12)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    sub = "COLECCIÓN  \"DÍA DE LA MADRE\""
    w = pdfmetrics.stringWidth(sub, SANS_REG, 12)
    c.drawString((PAGE_W - w) / 2, PAGE_H - 245, sub)

    # Línea decorativa
    draw_thin_line(c, PAGE_W / 2 - 60, PAGE_H - 265, PAGE_W / 2 + 60, PAGE_H - 265,
                   color=COLOR_NEGRO, width=0.7)

    # Tagline en itálica
    c.setFont(SERIF_ITAL, 14)
    c.setFillColor(COLOR_MARRON)
    line1 = "Diseño consciente"
    line2 = "Impreso aquí · Hecho para durar"
    w1 = pdfmetrics.stringWidth(line1, SERIF_ITAL, 14)
    w2 = pdfmetrics.stringWidth(line2, SERIF_ITAL, 14)
    c.drawString((PAGE_W - w1) / 2, 130, line1)
    c.drawString((PAGE_W - w2) / 2, 108, line2)

    # Cinta adhesiva con tagline
    draw_washi_tape(c, PAGE_W / 2 - 95, 70, 190, 18, angle=-3)

    c.showPage()


def build_index(c, layout):
    """Índice editorial."""
    print("  Índice...")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.3)

    draw_header_brand(c)

    # Título
    c.setFont(SCRIPT_REG, 30)
    c.setFillColor(COLOR_MORADO)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 165, "Contenido")

    # Línea decorativa
    draw_thin_line(c, PAGE_W / 2 - 50, PAGE_H - 178, PAGE_W / 2 + 50, PAGE_H - 178,
                   color=COLOR_NEGRO, width=0.6)

    y = PAGE_H - 215

    categorias_vistas = set()
    for pagina in layout["paginas"]:
        if pagina["tipo"] == "separador_categoria":
            cat = pagina["categoria"]
            if cat not in categorias_vistas:
                categorias_vistas.add(cat)
                page_num = pagina["pagina_numero"]

                # Viñeta
                c.setFillColor(COLOR_VERDE)
                c.circle(MARGIN + 8, y + 4, 2.5, stroke=0, fill=1)

                # Nombre categoría
                c.setFont(SANS_BOLD, 11)
                c.setFillColor(COLOR_NEGRO)
                c.drawString(MARGIN + 22, y, cat.upper())

                # Línea de puntos
                text_w = pdfmetrics.stringWidth(cat.upper(), SANS_BOLD, 11)
                num_str = f"{page_num:02d}"
                num_w = pdfmetrics.stringWidth(num_str, SERIF_REG, 11)
                c.setStrokeColor(COLOR_GRIS_LINEA)
                c.setLineWidth(0.4)
                c.setDash(2, 2)
                c.line(MARGIN + 26 + text_w, y + 4, PAGE_W - MARGIN - num_w - 8, y + 4)
                c.setDash()

                # Número
                c.setFont(SERIF_REG, 11)
                c.setFillColor(COLOR_MARRON)
                c.drawRightString(PAGE_W - MARGIN, y, num_str)

                y -= 32

    draw_footer(c, 0)
    c.showPage()


# ============================================================================
# PRODUCTO — Estilo polaroid + etiqueta de papel
# ============================================================================

def draw_product_card_scrapbook(c, x, y, w, h, prod, img_path, rot_photo=0, rot_label=0):
    """
    Tarjeta estilo scrapbook: polaroid rotada + etiqueta de papel pegada debajo
    (con solapamiento, como en el diseño de referencia).
    """
    # Polaroid rotada
    box = draw_polaroid_frame(c, x, y, w, h, rotation=rot_photo)

    # Coordenadas de la imagen
    if img_path:
        fit_image_in_box(c, img_path, box["x"], box["y"], box["w"], box["h"])

    # Cinta adhesiva ENCIMA de la polaroid (pegada al borde superior)
    tape_w = w * 0.42
    draw_washi_tape(c, x + (w - tape_w) / 2, y + h - 8, tape_w, 13,
                    angle=rot_photo * 0.4, color=COLOR_KRAFT)

    # Etiqueta de papel: solapa con el borde inferior de la polaroid
    label_w = w * 0.85
    label_h = 70
    label_x = x + (w - label_w) / 2
    label_y = y - label_h + 18   # solapa ~18pt sobre la polaroid

    draw_paper_label(c, label_x, label_y, label_w, label_h,
                     rotation=rot_label, color=COLOR_CREMA, has_tape=False)

    # Texto dentro de la etiqueta
    c.saveState()
    c.translate(label_x + label_w / 2, label_y + label_h / 2)
    c.rotate(rot_label)

    nombre = prod.get("nombre_yolitia", "")[:30]
    descripcion = prod.get("descripcion_corta") or prod.get("descripcion_larga") or prod.get("nombre_yolitia", "")
    descripcion = descripcion[:42]
    material = prod.get("material", "PLA")
    medidas = prod.get("medidas", "")
    precio = prod.get("precio")

    # Nombre con comillas tipográficas
    c.setFont(SANS_BOLD, 9.5)
    c.setFillColor(COLOR_NEGRO)
    c.drawCentredString(0, 22, f"\u201C{nombre.upper()}\u201D")

    # Descripción
    c.setFont(SANS_REG, 6.8)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    c.drawCentredString(0, 11, f"DESCRIPCIÓN: {descripcion.upper()}")

    # Material y medidas
    c.setFont(SANS_REG, 6.5)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    if medidas:
        c.drawCentredString(0, 2, f"MATERIAL: {material.upper()}    MEDIDAS: {medidas}")
    else:
        c.drawCentredString(0, 2, f"MATERIAL: {material.upper()}")

    # Precio serif grande a la derecha
    if precio:
        c.setFont(SERIF_BOLD, 17)
        c.setFillColor(COLOR_NEGRO)
        precio_txt = f"${precio:.0f}"
        c.drawRightString(label_w / 2 - 12, -18, precio_txt)

    c.restoreState()

    return label_y  # y de la parte inferior de la etiqueta


# ============================================================================
# LAYOUTS DE PRODUCTO
# ============================================================================

def build_cover_collection_page(c, categoria, page_num):
    """
    Portada de colección: isotipo, nombre de la colección grande caligráfico.
    Reemplaza al separador de categoría tradicional.
    """
    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.45)

    # Header
    draw_header_brand(c)

    # Bloque central
    cy = PAGE_H / 2 + 30

    # Etiqueta de papel grande
    label_w = 380
    label_h = 280
    label_x = (PAGE_W - label_w) / 2
    label_y = cy - label_h / 2

    draw_paper_label(c, label_x, label_y, label_w, label_h,
                     rotation=0, color=COLOR_CREMA, has_tape=True, tape_pos="top")

    # Cinta adicional más pequeña decorativa
    draw_washi_tape(c, label_x + 30, label_y - 8, 80, 12, angle=-8)

    # Texto
    c.saveState()
    c.setFont(SCRIPT_REG, 38)
    c.setFillColor(COLOR_MORADO)
    cat_text = categoria
    w = pdfmetrics.stringWidth(cat_text, SCRIPT_REG, 38)
    c.drawCentredString(PAGE_W / 2, cy + 60, cat_text)

    # Línea
    draw_thin_line(c, PAGE_W / 2 - 50, cy + 35, PAGE_W / 2 + 50, cy + 35,
                   color=COLOR_NEGRO, width=0.6)

    c.setFont(SANS_REG, 11)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    sub = "Colección regenerativa"
    w = pdfmetrics.stringWidth(sub, SANS_REG, 11)
    c.drawCentredString(PAGE_W / 2, cy + 15, sub)

    c.setFont(SERIF_ITAL, 12)
    c.setFillColor(COLOR_MARRON)
    txt = "Diseño consciente · Impreso aquí"
    w = pdfmetrics.stringWidth(txt, SERIF_ITAL, 12)
    c.drawCentredString(PAGE_W / 2, cy - 30, txt)

    # Pequeño isotipo al pie
    draw_isotipo_hoja(c, PAGE_W / 2, cy - 90, 22, color=COLOR_VERDE)

    c.restoreState()
    draw_footer(c, page_num)
    c.showPage()


def build_hero_product_page(c, elem, productos, page_num):
    """Producto hero a página completa, estilo editorial."""
    prod = productos.get(elem["producto_id"])
    if not prod:
        return
    print(f"  Hero: {prod['nombre_yolitia'][:35]} (pág {page_num})")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.35)

    draw_header_brand(c)

    img_path = get_image_path(elem, productos)

    # Polaroid grande centrada, con espacio arriba y abajo
    pw, ph = 270, 260
    px = (PAGE_W - pw) / 2
    # Dejamos buen margen bajo el header (que termina ~145)
    py = PAGE_H - 200 - ph  # py es el BOTTOM del polaroid

    draw_product_card_scrapbook(c, px, py, pw, ph, prod, img_path,
                                 rot_photo=0, rot_label=0)

    # Etiqueta adicional con detalles (en la parte de abajo)
    info_x = MARGIN + 20
    info_y = 100
    info_w = PAGE_W - 2 * (MARGIN + 20)
    info_h = 80

    draw_paper_label(c, info_x, info_y, info_w, info_h, rotation=0,
                     color=COLOR_CREMA_OSC, has_tape=False)

    c.saveState()
    text_x = info_x + 20
    text_y = info_y + info_h - 20

    c.setFont(SANS_BOLD, 9)
    c.setFillColor(COLOR_MORADO)
    c.drawString(text_x, text_y, "SOSTENIBILIDAD")

    c.setFont(SANS_REG, 8)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    badges = ["RECICLABLE", "BIODEGRADABLE", "LARGA VIDA"]
    bx = text_x
    for b in badges:
        c.setFont(SANS_REG, 7.5)
        c.setFillColor(COLOR_VERDE)
        c.circle(bx + 3, text_y - 16, 2.5, stroke=0, fill=1)
        c.setFillColor(COLOR_NEGRO_SUAVE)
        c.drawString(bx + 10, text_y - 19, b)
        bx += 110

    c.setFont(SERIF_ITAL, 8.5)
    c.setFillColor(COLOR_MARRON)
    sku = elem.get("sku", "")
    subcat = prod.get("subcategoria_yolitia", "") or elem.get("subcategoria", "")
    c.drawRightString(info_x + info_w - 20, text_y - 4, f"SKU: {sku}")
    if subcat:
        c.drawRightString(info_x + info_w - 20, text_y - 18, f"Categoría: {subcat}")

    c.restoreState()

    draw_footer(c, page_num)
    c.showPage()


def build_grid_2x2(c, elementos, productos, page_num):
    """Grid 2x2 estilo scrapbook: 4 productos con polaroid rotadas y etiquetas."""
    print(f"  Grid 2x2: {len(elementos)} productos (pág {page_num})")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.32)
    draw_header_brand(c)

    # Cada producto polaroid + etiqueta ocupa ~ altura total
    # (polaroid 200 + etiqueta solapada). A4 = 842pt, header termina ~130, footer ~70
    # Altura disponible: 842 - 130 - 70 = 642 / 2 filas = 321 por fila
    pw, ph = 220, 200
    label_h = 70   # etiqueta solapa
    # Fila 1 (arriba): el TOP del polaroid debe estar bajo el header (PAGE_H - 130)
    # y = PAGE_H - 130 - ph  →  y = 842 - 130 - 200 = 512
    # Fila 2 (abajo): separada por label_h
    row1_y = PAGE_H - 135 - ph
    row2_y = row1_y - label_h - 20 - ph

    positions = [
        (MARGIN + 10,  row1_y, pw, ph, -2.5, 1.5),
        (MARGIN + 270, row1_y + 10, pw, ph,  2.0, -1.5),
        (MARGIN + 30,  row2_y, pw, ph,  1.5, -1.0),
        (MARGIN + 290, row2_y - 10, pw, ph, -2.0, 1.5),
    ]

    for i, elem in enumerate(elementos[:4]):
        prod = productos.get(elem["producto_id"])
        if not prod:
            continue
        x, y, w, h, rot_p, rot_l = positions[i]
        img_path = get_image_path(elem, productos)
        draw_product_card_scrapbook(c, x, y, w, h, prod, img_path,
                                     rot_photo=rot_p, rot_label=rot_l)

    draw_footer(c, page_num)
    c.showPage()


def build_grid_1x2(c, elementos, productos, page_num):
    """Grid 1x2: 2 productos grandes a página completa."""
    print(f"  Grid 1x2: {len(elementos)} productos (pág {page_num})")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.3)
    draw_header_brand(c)

    # Dos productos: uno a la izquierda, otro a la derecha
    # A4 = 842pt, header termina ~120, footer ~70, área útil 652pt
    # Polaroid 380 + etiqueta 70 (solapa) = ~430 total, centrado vertical
    pw, ph = 230, 360
    top_y = PAGE_H - 140 - ph  # top del polaroid: 120 + 20 margen = debajo del header
    # y = bottom del polaroid
    polaroid_y = top_y

    positions = [
        (MARGIN + 10,  polaroid_y, pw, ph, -1.5, 1.0),
        (MARGIN + 280, polaroid_y, pw, ph,  1.5, -1.0),
    ]

    for i, elem in enumerate(elementos[:2]):
        prod = productos.get(elem["producto_id"])
        if not prod:
            continue
        x, y, w, h, rot_p, rot_l = positions[i]
        img_path = get_image_path(elem, productos)
        draw_product_card_scrapbook(c, x, y, w, h, prod, img_path,
                                     rot_photo=rot_p, rot_label=rot_l)

    draw_footer(c, page_num)
    c.showPage()


def build_grid_1x3(c, elementos, productos, page_num):
    """Grid 1x3: 3 productos verticales a la izquierda + paleta de colores a la derecha."""
    print(f"  Grid 1x3: {len(elementos)} productos (pág {page_num})")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.28)
    draw_header_brand(c)

    # Tres productos verticales, lado izquierdo
    # A4 alto = 842, header termina ~120, footer ~70, área útil = 652
    # 3 polaroids + 3 etiquetas solapadas. Polaroid 130 + label 60 = 190 por fila
    pw, ph = 210, 130
    row_h = ph + 60   # polaroid + label solapada + gap
    start_y_top = PAGE_H - 130 - ph  # bottom del primer polaroid

    positions = [
        (MARGIN + 5,  start_y_top,                     pw, ph, -1.2, 1.0),
        (MARGIN + 25, start_y_top - row_h - 10,        pw, ph,  0.8, -0.8),
        (MARGIN + 15, start_y_top - 2 * (row_h + 10),  pw, ph, -0.7, 0.6),
    ]

    for i, elem in enumerate(elementos[:3]):
        prod = productos.get(elem["producto_id"])
        if not prod:
            continue
        x, y, w, h, rot_p, rot_l = positions[i]
        img_path = get_image_path(elem, productos)
        draw_product_card_scrapbook(c, x, y, w, h, prod, img_path,
                                     rot_photo=rot_p, rot_label=rot_l)

    # Etiqueta de colores a la derecha
    label_x = MARGIN + 250
    label_w = 250
    label_h = 580
    label_y = start_y_top - label_h + ph   # alineado con el primer polaroid

    draw_paper_label(c, label_x, label_y, label_w, label_h, rotation=1.2,
                     color=COLOR_CREMA, has_tape=True, tape_pos="top")

    c.saveState()
    c.translate(label_x + label_w / 2, label_y + label_h / 2)
    c.rotate(1.2)

    c.setFont(SANS_BOLD, 11)
    c.setFillColor(COLOR_MORADO)
    c.drawCentredString(0, label_h / 2 - 30, "COLORES DISPONIBLES")

    draw_thin_line(c, -40, label_h / 2 - 40, 40, label_h / 2 - 40,
                   color=COLOR_NEGRO, width=0.5)

    colores = [
        ("Blanco Matte",      "#FFFFFF"),
        ("Negro Matte",       "#1A1A1A"),
        ("Verde Oliva Matte", "#7A8C6E"),
        ("Azul Claro Matte",  "#B8CCE4"),
        ("Rosa Pastel Matte", "#E8D5D5"),
        ("Gris",              "#9E9E9E"),
    ]

    start_y = label_h / 2 - 75
    for i, (nombre, hex_c) in enumerate(colores):
        row = i // 2
        col = i % 2
        x_off = -55 + col * 110
        y_off = start_y - row * 75

        # Swatch
        c.setFillColor(colors.HexColor(hex_c))
        c.setStrokeColor(colors.HexColor("#BFB59F"))
        c.setLineWidth(0.3)
        c.circle(x_off, y_off, 14, stroke=1, fill=1)

        c.setFont(SANS_BOLD, 7.5)
        c.setFillColor(COLOR_NEGRO)
        c.drawCentredString(x_off + 28, y_off + 4, nombre)

        c.setFont(SERIF_REG, 6.5)
        c.setFillColor(COLOR_MARRON)
        c.drawCentredString(x_off + 28, y_off - 6, hex_c)

    c.restoreState()

    draw_footer(c, page_num)
    c.showPage()


# ============================================================================
# PÁGINAS INSTITUCIONALES
# ============================================================================

def build_pla_page(c, page_num):
    """Página sobre PLA, estilo etiqueta de papel."""
    print(f"  PLA (pág {page_num})")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.32)
    draw_header_brand(c)

    # Etiqueta de papel grande central
    label_w = 460
    label_h = 620
    label_x = (PAGE_W - label_w) / 2
    label_y = 80

    draw_paper_label(c, label_x, label_y, label_w, label_h, rotation=0,
                     color=COLOR_CREMA, has_tape=True, tape_pos="top")

    c.saveState()

    # Título
    c.setFont(SCRIPT_REG, 32)
    c.setFillColor(COLOR_MORADO)
    c.drawCentredString(PAGE_W / 2, label_y + label_h - 60, "Hecho de PLA")

    c.setFont(SANS_REG, 11)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    c.drawCentredString(PAGE_W / 2, label_y + label_h - 82,
                        "BELLO POR DENTRO Y POR FUERA")

    # Línea
    draw_thin_line(c, PAGE_W / 2 - 50, label_y + label_h - 95,
                   PAGE_W / 2 + 50, label_y + label_h - 95,
                   color=COLOR_NEGRO, width=0.5)

    # Texto
    text_x = label_x + 35
    text_y = label_y + label_h - 125

    paragraphs = [
        (SANS_REG, COLOR_NEGRO, "El PLA (Ácido Poliláctico) es un polímero de origen"),
        (SANS_REG, COLOR_NEGRO, "vegetal, derivado principalmente de almidón de maíz o"),
        (SANS_REG, COLOR_NEGRO, "caña de azúcar. A diferencia de los plásticos"),
        (SANS_REG, COLOR_NEGRO, "convencionales, el PLA se obtiene de fuentes"),
        (SANS_REG, COLOR_NEGRO, "renovables y es compostable en condiciones"),
        (SANS_REG, COLOR_NEGRO, "industriales."),
        (SANS_REG, None, ""),
        (SANS_BOLD, COLOR_MORADO, "POR QUÉ IMPORTA"),
        (SANS_REG, None, ""),
        (SANS_REG, COLOR_NEGRO, "  ·  Reduce la dependencia de petroquímicos"),
        (SANS_REG, COLOR_NEGRO, "  ·  Menor huella de carbono en su producción"),
        (SANS_REG, COLOR_NEGRO, "  ·  Compostable: no se acumula por siglos"),
        (SANS_REG, COLOR_NEGRO, "  ·  Permite producción local y bajo demanda"),
        (SANS_REG, COLOR_NEGRO, "  ·  Cero inventario excedente = cero desperdicio"),
        (SANS_REG, None, ""),
        (SANS_BOLD, COLOR_NEGRO, "En Yolitia, cada pieza se imprime en 3D cuando tú la"),
        (SANS_BOLD, COLOR_NEGRO, "pides. No hay bodegas llenas. No hay sobreproducción."),
    ]

    for font, color, text in paragraphs:
        if font:
            c.setFont(font, 9.5)
        if color:
            c.setFillColor(color)
        c.drawString(text_x, text_y, text)
        text_y -= 15

    c.restoreState()
    draw_footer(c, page_num)
    c.showPage()


def build_colores_page(c, page_num):
    """Página de colores disponibles."""
    print(f"  Colores (pág {page_num})")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.32)
    draw_header_brand(c)

    # Título
    c.setFont(SCRIPT_REG, 28)
    c.setFillColor(COLOR_MORADO)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 175, "Colores disponibles")

    c.setFont(SANS_REG, 9.5)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 200,
                        "TODOS NUESTROS MODELOS ESTÁN DISPONIBLES EN")

    # Línea decorativa
    draw_thin_line(c, PAGE_W / 2 - 50, PAGE_H - 215, PAGE_W / 2 + 50, PAGE_H - 215,
                   color=COLOR_NEGRO, width=0.5)

    colores = [
        ("Blanco Matte",      "#FFFFFF"),
        ("Negro Matte",       "#1A1A1A"),
        ("Verde Oliva Matte", "#7A8C6E"),
        ("Azul Claro Matte",  "#B8CCE4"),
        ("Rosa Pastel Matte", "#E8D5D5"),
        ("Gris",              "#9E9E9E"),
    ]

    # Distribución 2 columnas x 3 filas
    col_w = 200
    row_h = 100
    start_x = (PAGE_W - 2 * col_w - 30) / 2
    start_y = PAGE_H - 350  # dejar más espacio bajo el header y el título

    for i, (nombre, hex_c) in enumerate(colores):
        col = i % 2
        row = i // 2
        x = start_x + col * (col_w + 30)
        y = start_y - row * (row_h + 15)

        # Etiqueta de papel por cada color
        draw_paper_label(c, x, y, col_w, row_h, rotation=0,
                         color=COLOR_CREMA, has_tape=False)

        c.saveState()

        # Swatch grande
        sw_size = 46
        sw_x = x + (col_w - sw_size) / 2
        sw_y = y + row_h - 35 - sw_size

        c.setFillColor(colors.HexColor(hex_c))
        c.setStrokeColor(colors.HexColor("#BFB59F"))
        c.setLineWidth(0.4)
        c.circle(sw_x + sw_size / 2, sw_y + sw_size / 2, sw_size / 2, stroke=1, fill=1)

        # Nombre
        c.setFont(SANS_BOLD, 10)
        c.setFillColor(COLOR_NEGRO)
        c.drawCentredString(x + col_w / 2, y + 30, nombre.upper())

        # Código hex
        c.setFont(SERIF_REG, 8)
        c.setFillColor(COLOR_MARRON)
        c.drawCentredString(x + col_w / 2, y + 15, hex_c)

        c.restoreState()

    # Nota al pie
    c.setFont(SERIF_ITAL, 9.5)
    c.setFillColor(COLOR_MARRON)
    c.drawCentredString(PAGE_W / 2, 80,
                        "Acabado matte en todos los colores")
    c.setFont(SANS_REG, 8)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    c.drawCentredString(PAGE_W / 2, 64,
                        "IMPRESIÓN 3D EN PLA BIODEGRADABLE")

    draw_footer(c, page_num)
    c.showPage()


def build_compromiso_page(c, page_num):
    """Página de compromiso ambiental."""
    print(f"  Compromiso (pág {page_num})")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.32)
    draw_header_brand(c)

    # Título
    c.setFont(SCRIPT_REG, 30)
    c.setFillColor(COLOR_MORADO)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 155, "Nuestro compromiso")

    c.setFont(SANS_REG, 11)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 180,
                        "CONTIGO Y CON EL PLANETA")

    draw_thin_line(c, PAGE_W / 2 - 50, PAGE_H - 195, PAGE_W / 2 + 50, PAGE_H - 195,
                   color=COLOR_NEGRO, width=0.5)

    # Bloque 1
    box1_x = MARGIN + 20
    box1_y = 380
    box1_w = PAGE_W - 2 * (MARGIN + 20)
    box1_h = 130

    draw_paper_label(c, box1_x, box1_y, box1_w, box1_h, rotation=-0.5,
                     color=COLOR_CREMA, has_tape=True, tape_pos="top")

    c.saveState()
    c.translate(box1_x + 20, box1_y + box1_h - 20)
    c.setFont(SCRIPT_REG, 20)
    c.setFillColor(COLOR_VERDE)
    c.drawString(0, 0, "10%")
    c.setFont(SANS_BOLD, 11)
    c.setFillColor(COLOR_MORADO)
    c.drawString(60, 5, "PARA LA CONSERVACIÓN")

    c.setFont(SANS_REG, 8.5)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    c.drawString(60, -8, "El 10% de nuestras ganancias se destina a proyectos")
    c.drawString(60, -19, "de conservación ambiental en México. Cada compra")
    c.drawString(60, -30, "que haces contribuye a preservar la biodiversidad.")

    c.restoreState()

    # Bloque 2
    box2_x = MARGIN + 30
    box2_y = 220
    box2_w = PAGE_W - 2 * (MARGIN + 30)
    box2_h = 130

    draw_paper_label(c, box2_x, box2_y, box2_w, box2_h, rotation=0.8,
                     color=COLOR_CREMA_OSC, has_tape=True, tape_pos="top")

    c.saveState()
    c.translate(box2_x + 20, box2_y + box2_h - 20)
    c.setFont(SCRIPT_REG, 20)
    c.setFillColor(COLOR_VERDE)
    c.drawString(0, 0, "@")
    c.setFont(SANS_BOLD, 11)
    c.setFillColor(COLOR_MORADO)
    c.drawString(60, 5, "DIFUNDIMOS EN REDES")

    c.setFont(SANS_REG, 8.5)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    c.drawString(60, -8, "Estamos activos compartiendo nuestro proceso y")
    c.drawString(60, -19, "valores. Síguenos y únete al movimiento:")
    c.setFont(SERIF_ITAL, 10)
    c.setFillColor(COLOR_MARRON)
    c.drawString(60, -36, "@yolitia   ·   www.yolitia.bio")

    c.restoreState()

    # Cierre
    c.setFont(SERIF_ITAL, 12)
    c.setFillColor(COLOR_MARRON)
    c.drawCentredString(PAGE_W / 2, 130,
                        "Cada pieza que creamos es un acto de amor")
    c.setFont(SERIF_ITAL, 12)
    c.drawCentredString(PAGE_W / 2, 110, "por el planeta que habitamos.")

    draw_footer(c, page_num)
    c.showPage()


def build_back_cover(c):
    """Contraportada con manifiesto."""
    print("  Contraportada...")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.45)

    # Isotipo arriba
    draw_isotipo_hoja(c, PAGE_W / 2, PAGE_H - 110, 50, color=COLOR_VERDE)

    # Marca
    c.setFont(SCRIPT_REG, 60)
    c.setFillColor(COLOR_MORADO)
    w = pdfmetrics.stringWidth("Yolitia", SCRIPT_REG, 60)
    c.drawString((PAGE_W - w) / 2, PAGE_H - 175, "Yolitia")

    c.setFont(SANS_REG, 11)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    sub = "UN PROYECTO CIRCULAR"
    w = pdfmetrics.stringWidth(sub, SANS_REG, 11)
    c.drawString((PAGE_W - w) / 2, PAGE_H - 200, sub)

    # Etiqueta de papel con manifiesto
    label_w = 440
    label_h = 460
    label_x = (PAGE_W - label_w) / 2
    label_y = 100

    draw_paper_label(c, label_x, label_y, label_w, label_h, rotation=0,
                     color=COLOR_CREMA, has_tape=True, tape_pos="top")

    c.saveState()

    text_x = label_x + 35
    text_y = label_y + label_h - 50

    manifesto = [
        (SANS_REG, COLOR_NEGRO, "Yolitia nace de una pregunta simple:"),
        (SANS_REG, None, ""),
        (SERIF_ITAL, COLOR_MORADO, "¿Y si los objetos que usamos cada día"),
        (SERIF_ITAL, COLOR_MORADO, "pudieran hacerse con menos y"),
        (SERIF_ITAL, COLOR_MORADO, "significar más?"),
        (SANS_REG, None, ""),
        (SANS_BOLD, COLOR_VERDE, "NUESTRO MODELO ES DIFERENTE"),
        (SANS_REG, None, ""),
        (SANS_REG, COLOR_NEGRO, "  →  Producimos bajo pedido, no en masa"),
        (SANS_REG, COLOR_NEGRO, "  →  Materiales de origen vegetal (PLA)"),
        (SANS_REG, COLOR_NEGRO, "  →  Diseñamos para durar"),
        (SANS_REG, COLOR_NEGRO, "  →  Cada compra apoya manufactura local"),
        (SANS_REG, None, ""),
        (SANS_REG, COLOR_NEGRO, "Somos parte del movimiento de economía"),
        (SANS_REG, COLOR_NEGRO, "circular: los materiales entran, se usan,"),
        (SANS_REG, COLOR_NEGRO, "se recuperan."),
        (SANS_REG, None, ""),
        (SANS_BOLD, COLOR_MORADO, "Nada se pierde. Todo vuelve."),
    ]

    for font, color, text in manifesto:
        if font:
            c.setFont(font, 10)
        if color:
            c.setFillColor(color)
        c.drawString(text_x, text_y, text)
        text_y -= 16

    c.restoreState()

    # Footer cinta
    draw_washi_tape(c, PAGE_W / 2 - 110, 45, 220, 16, angle=-2)

    c.setFont(SERIF_ITAL, 9)
    c.setFillColor(COLOR_NEGRO)
    c.drawCentredString(PAGE_W / 2, 52, "Diseño consciente · Impreso aquí")

    c.showPage()


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def build_catalog():
    """Genera catálogo PDF v5 — estilo editorial caligráfico."""
    print("=" * 70)
    print("GENERACIÓN CATÁLOGO YOLITIA v5 — ESTILO EDITORIAL CALIGRÁFICO")
    print("=" * 70)

    register_fonts()

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
            cat = pagina_data.get("categoria", "")
            page_num = pagina_data["pagina_numero"]
            build_cover_collection_page(c, cat, page_num)
            paginas_generadas += 1
            pagina_actual += 1

        elif tipo == "productos":
            grid = pagina_data.get("grid", "1x2")
            page_num = pagina_data.get("pagina_numero") or (pagina_actual + 1)

            if grid == "1x1":
                elem = pagina_data.get("elementos", [{}])[0]
                build_hero_product_page(c, elem, productos, page_num)
            elif grid == "2x2":
                build_grid_2x2(c, pagina_data.get("elementos", []), productos, page_num)
            elif grid == "1x2":
                build_grid_1x2(c, pagina_data.get("elementos", []), productos, page_num)
            elif grid == "1x3":
                build_grid_1x3(c, pagina_data.get("elementos", []), productos, page_num)
            else:
                build_grid_1x2(c, pagina_data.get("elementos", []), productos, page_num)

            paginas_generadas += 1
            pagina_actual += 1

        elif tipo == "material_pla":
            build_pla_page(c, pagina_actual + 1)
            paginas_generadas += 1
            pagina_actual += 1

        elif tipo == "colores":
            build_colores_page(c, pagina_actual + 1)
            paginas_generadas += 1
            pagina_actual += 1

        elif tipo == "compromiso":
            build_compromiso_page(c, pagina_actual + 1)
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
