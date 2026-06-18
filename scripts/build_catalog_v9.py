"""
Catálogo Yolitia v9 — Vertical (portrait) · ESPAÑOL
Basado en v8 (landscape). Cambio de orientación: A4 vertical (210x297 mm).
Reorganización de grids: 1x1 hero, 1x2 vertical, 2x2 ahora 2x2 vertical.
"""

import json
import math
from pathlib import Path

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
OVERRIDES_FILE = DATA_DIR / "catalog_overrides_v8.json"
OUTPUT_PDF = OUTPUT_DIR / "catalogo_yolitia_v9.pdf"


# ============================================================================
# PALETA
# ============================================================================
COLOR_MARFIL       = colors.HexColor("#F5F0E6")
COLOR_MARFIL_CLARO = colors.HexColor("#FAF7EF")
COLOR_CREMA        = colors.HexColor("#E8DCC4")
COLOR_CREMA_OSC    = colors.HexColor("#D8C9A8")
COLOR_KRAFT        = colors.HexColor("#D9CBA8")
COLOR_NEGRO        = colors.HexColor("#1A1614")
COLOR_NEGRO_SUAVE  = colors.HexColor("#2D2620")
COLOR_MORADO       = colors.HexColor("#4A4458")
COLOR_VERDE        = colors.HexColor("#5C6E54")
COLOR_MARRON       = colors.HexColor("#5A4A3A")
COLOR_GRIS_LINEA   = colors.HexColor("#C9BFA9")


# ============================================================================
# TIPOGRAFÍAS
# ============================================================================
SCRIPT_REG  = "YolitiaScript"
SCRIPT_BOLD = "YolitiaScriptB"
SANS_REG    = "YolitiaSans"
SANS_BOLD   = "YolitiaSansB"
SANS_LIGHT  = "YolitiaSansL"
SERIF_REG   = "YolitiaSerif"
SERIF_ITAL  = "YolitiaSerifI"
SERIF_BOLD  = "YolitiaSerifB"

WIN_FONTS = Path("C:/Windows/Fonts")


def register_fonts():
    try:
        pdfmetrics.registerFont(TTFont(SCRIPT_REG, str(WIN_FONTS / "LCALLIG.TTF")))
    except Exception:
        pdfmetrics.registerFont(TTFont(SCRIPT_REG, str(WIN_FONTS / "PRISTINA.TTF")))
    pdfmetrics.registerFont(TTFont(SCRIPT_BOLD, str(WIN_FONTS / "PRISTINA.TTF")))
    pdfmetrics.registerFont(TTFont(SANS_REG, str(WIN_FONTS / "calibri.ttf")))
    pdfmetrics.registerFont(TTFont(SANS_BOLD, str(WIN_FONTS / "calibrib.ttf")))
    pdfmetrics.registerFont(TTFont(SANS_LIGHT, str(WIN_FONTS / "calibri.ttf")))
    pdfmetrics.registerFont(TTFont(SERIF_REG, str(WIN_FONTS / "BOD_R.TTF")))
    pdfmetrics.registerFont(TTFont(SERIF_ITAL, str(WIN_FONTS / "BOD_I.TTF")))
    pdfmetrics.registerFont(TTFont(SERIF_BOLD, str(WIN_FONTS / "BOD_B.TTF")))


# ============================================================================
# PÁGINA
# ============================================================================
PAGE_W, PAGE_H = A4  # 595 x 842 pt (210x297 mm portrait)
MARGIN = 36
CONTENT_W = PAGE_W - (2 * MARGIN)


# ============================================================================
# UTILIDADES DE TEXTO
# ============================================================================

def wrap_text(text, font, font_size, max_width):
    """Envuelve el texto en múltiples líneas según max_width."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if pdfmetrics.stringWidth(test_line, font, font_size) < max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines


def wrap_text_with_breaks(text, font, font_size, max_width, max_lines=None):
    """
    Envuelve texto. Si max_lines es None, devuelve todas las líneas.
    Si max_lines está definido y hay overflow, la última línea termina con '...'
    """
    lines = wrap_text(text, font, font_size, max_width)
    if max_lines and len(lines) > max_lines:
        kept = lines[:max_lines]
        last = kept[-1]
        while pdfmetrics.stringWidth(last + "...", font, font_size) > max_width and len(last) > 1:
            last = last[:-1].rstrip(",.;:")
        kept[-1] = last + "..."
        return kept
    return lines


# ============================================================================
# UTILIDADES DE DIBUJO
# ============================================================================

def draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.45):
    """Manchas decorativas en las esquinas (orientacion portrait)."""
    c.saveState()
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setStrokeAlpha(opacity)
    c.setFillAlpha(opacity)
    c.setLineWidth(0.8)

    # Esquina superior izquierda
    p = c.beginPath()
    p.moveTo(-50, PAGE_H + 30)
    p.curveTo(40, PAGE_H - 80, 130, PAGE_H - 240, 80, PAGE_H - 380)
    p.curveTo(30, PAGE_H - 480, -30, PAGE_H - 560, -50, PAGE_H - 620)
    p.lineTo(-50, PAGE_H + 30)
    p.close()
    c.drawPath(p, stroke=0, fill=1)

    # Esquina inferior derecha
    p = c.beginPath()
    p.moveTo(PAGE_W + 30, -30)
    p.curveTo(PAGE_W - 60, 80, PAGE_W - 180, 220, PAGE_W - 100, 360)
    p.curveTo(PAGE_W - 40, 480, PAGE_W + 10, 560, PAGE_W + 30, 620)
    p.lineTo(PAGE_W + 30, -30)
    p.close()
    c.drawPath(p, stroke=0, fill=1)

    c.restoreState()


def draw_washi_tape(c, x, y, w, h=14, angle=0, color=COLOR_KRAFT):
    c.saveState()
    c.translate(x + w / 2, y + h / 2)
    c.rotate(angle)
    c.setFillColor(color)
    c.setFillAlpha(0.88)
    c.rect(-w / 2, -h / 2, w, h, stroke=0, fill=1)
    c.setStrokeAlpha(0.18)
    c.setStrokeColor(colors.HexColor("#B8A988"))
    c.setLineWidth(0.4)
    for i in range(-int(w / 2) + 4, int(w / 2) - 4, 6):
        c.line(i, -h / 2 + 1, i, h / 2 - 1)
    c.restoreState()


def draw_polaroid_frame(c, x, y, w, h, rotation=0, shadow=True):
    c.saveState()
    c.translate(x + w / 2, y + h / 2)
    c.rotate(rotation)

    border_top = 18
    border_bottom = 50
    border_lr = 16
    img_w = w - 2 * border_lr
    img_h = h - border_top - border_bottom

    if shadow:
        c.setFillColor(colors.HexColor("#D8CFC0"))
        c.setFillAlpha(0.55)
        c.roundRect(-w / 2 + 2, -h / 2 - 2, w, h, 2, stroke=0, fill=1)

    c.setFillColor(colors.HexColor("#FFFFFF"))
    c.setFillAlpha(1.0)
    c.roundRect(-w / 2, -h / 2, w, h, 2, stroke=0, fill=1)

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


def draw_paper_label(c, x, y, w, h, rotation=0, color=COLOR_CREMA, has_tape=False, tape_pos="top"):
    c.saveState()
    c.translate(x + w / 2, y + h / 2)
    c.rotate(rotation)

    c.setFillColor(colors.HexColor("#C8BBA0"))
    c.setFillAlpha(0.4)
    c.roundRect(-w / 2 + 1.5, -h / 2 - 1.5, w, h, 1, stroke=0, fill=1)

    c.setFillColor(color)
    c.setFillAlpha(1.0)
    c.rect(-w / 2, -h / 2, w, h, stroke=0, fill=1)

    c.setStrokeColor(colors.HexColor("#C8B89C"))
    c.setLineWidth(0.3)
    c.rect(-w / 2, -h / 2, w, h, stroke=1, fill=0)

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
    c.saveState()
    c.translate(cx, cy)
    c.setFillColor(color)

    pw = size * 0.32
    pl = size * 0.48

    def petal():
        p = c.beginPath()
        p.moveTo(0, 0)
        p.curveTo(pw * 0.6, pl * 0.15, pw * 0.55, pl * 0.7, 0, pl)
        p.curveTo(-pw * 0.55, pl * 0.7, -pw * 0.6, pl * 0.15, 0, 0)
        p.close()
        c.drawPath(p, stroke=0, fill=1)

    petal()
    c.saveState()
    c.rotate(180)
    petal()
    c.restoreState()
    c.saveState()
    c.rotate(90)
    petal()
    c.restoreState()
    c.saveState()
    c.rotate(-90)
    petal()
    c.restoreState()

    c.restoreState()


def draw_thin_line(c, x1, y1, x2, y2, color=COLOR_NEGRO, width=0.6):
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)
    c.restoreState()


def fit_image_in_box(c, img_path, box_x, box_y, box_w, box_h):
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
# OVERRIDES
# ============================================================================

def load_overrides():
    if OVERRIDES_FILE.exists():
        with open(OVERRIDES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # Fallback: buscar el overrides mas reciente disponible
    for cand in sorted(DATA_DIR.glob("catalog_overrides_*.json"), reverse=True):
        try:
            with open(cand, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            continue
    return {}


def apply_overrides(productos, overrides):
    renames = overrides.get("renames", {})
    descriptions = overrides.get("descriptions", {})
    prices = overrides.get("prices", {})
    dimensions = overrides.get("dimensions", {})

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

        if pid in dimensions:
            prod["_display_dims"] = dimensions[pid]
        else:
            prod["_display_dims"] = prod.get("dimensiones_cm") or prod.get("medidas", "")

        prod["_landscape_color"] = None


# ============================================================================
# HEADER & FOOTER
# ============================================================================

def draw_minimal_header(c, subtitle="CATÁLOGO DE PRODUCTOS"):
    """Header minimalista en español (portrait)."""
    # Header mas compacto y con mas margen superior
    draw_isotipo_hoja(c, PAGE_W / 2, PAGE_H - 40, 18, color=COLOR_VERDE)
    c.setFont(SCRIPT_REG, 26)
    c.setFillColor(COLOR_MORADO)
    text_w = pdfmetrics.stringWidth("Yolitia", SCRIPT_REG, 26)
    c.drawString((PAGE_W - text_w) / 2, PAGE_H - 68, "Yolitia")
    # Linea fina debajo del header
    c.setStrokeColor(COLOR_KRAFT)
    c.setLineWidth(0.3)
    c.line(MARGIN + 40, PAGE_H - 88, PAGE_W - MARGIN - 40, PAGE_H - 88)


def draw_footer(c, page_num):
    c.saveState()
    c.setStrokeColor(COLOR_GRIS_LINEA)
    c.setLineWidth(0.4)
    c.line(MARGIN, 32, PAGE_W - MARGIN, 32)

    c.setFont(SERIF_ITAL, 8)
    c.setFillColor(COLOR_MARRON)
    c.drawString(MARGIN, 18, "yolitia.bio")

    c.setFont(SERIF_REG, 8)
    c.setFillColor(COLOR_MARRON)
    c.drawCentredString(PAGE_W / 2, 18, f"{page_num:02d}")

    c.setFont(SANS_REG, 6.5)
    c.setFillColor(COLOR_MARRON)
    c.drawRightString(PAGE_W - MARGIN, 18, "COLECCIÓN VERANO  ·  2026")

    c.restoreState()


# ============================================================================
# PÁGINAS ESPECIALES
# ============================================================================

def build_cover(c):
    print("  Portada...")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.55)

    # Logo arriba centrado
    draw_isotipo_hoja(c, PAGE_W / 2, PAGE_H - 150, 64, color=COLOR_VERDE)

    # Nombre de marca (más grande porque tenemos más alto)
    c.setFont(SCRIPT_REG, 96)
    c.setFillColor(COLOR_MORADO)
    text = "Yolitia"
    w = pdfmetrics.stringWidth(text, SCRIPT_REG, 96)
    c.drawString((PAGE_W - w) / 2, PAGE_H - 240, text)

    # Subtítulo
    c.setFont(SANS_REG, 14)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    sub = "COLECCIÓN  ·  VERANO  ·  2026"
    w = pdfmetrics.stringWidth(sub, SANS_REG, 14)
    c.drawString((PAGE_W - w) / 2, PAGE_H - 280, sub)

    # Línea divisoria
    draw_thin_line(c, PAGE_W / 2 - 70, PAGE_H - 305, PAGE_W / 2 + 70, PAGE_H - 305,
                   color=COLOR_NEGRO, width=0.7)

    # "CATÁLOGO"
    c.setFont(SCRIPT_REG, 26)
    c.setFillColor(COLOR_NEGRO)
    cat = "CATÁLOGO"
    w = pdfmetrics.stringWidth(cat, SCRIPT_REG, 26)
    c.drawString((PAGE_W - w) / 2, PAGE_H - 345, cat)

    # Tagline italic
    c.setFont(SERIF_ITAL, 15)
    c.setFillColor(COLOR_MARRON)
    line1 = "Diseño consciente"
    line2 = "Impreso aquí · Hecho para durar"
    w1 = pdfmetrics.stringWidth(line1, SERIF_ITAL, 15)
    w2 = pdfmetrics.stringWidth(line2, SERIF_ITAL, 15)
    c.drawString((PAGE_W - w1) / 2, 150, line1)
    c.drawString((PAGE_W - w2) / 2, 128, line2)

    # Washtape al pie
    draw_washi_tape(c, PAGE_W / 2 - 110, 80, 220, 18, angle=-3)

    c.showPage()


def build_index(c, layout):
    print("  Índice...")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.3)

    draw_minimal_header(c)

    c.setFont(SCRIPT_REG, 30)
    c.setFillColor(COLOR_MORADO)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 145, "Contenido")

    draw_thin_line(c, PAGE_W / 2 - 50, PAGE_H - 158, PAGE_W / 2 + 50, PAGE_H - 158,
                   color=COLOR_NEGRO, width=0.6)

    y = PAGE_H - 195

    categorias_vistas = set()
    for pagina in layout["paginas"]:
        if pagina["tipo"] == "separador_categoria":
            cat = pagina["categoria"]
            if cat not in categorias_vistas:
                categorias_vistas.add(cat)
                page_num = pagina["pagina_numero"]
                cat_es = cat.upper()

                c.setFillColor(COLOR_VERDE)
                c.circle(MARGIN + 8, y + 4, 2.5, stroke=0, fill=1)

                c.setFont(SANS_BOLD, 11)
                c.setFillColor(COLOR_NEGRO)
                c.drawString(MARGIN + 22, y, cat_es)

                text_w = pdfmetrics.stringWidth(cat_es, SANS_BOLD, 11)
                num_str = f"{page_num:02d}"
                num_w = pdfmetrics.stringWidth(num_str, SERIF_REG, 11)
                c.setStrokeColor(COLOR_GRIS_LINEA)
                c.setLineWidth(0.4)
                c.setDash(2, 2)
                c.line(MARGIN + 26 + text_w, y + 4, PAGE_W - MARGIN - num_w - 8, y + 4)
                c.setDash()

                c.setFont(SERIF_REG, 11)
                c.setFillColor(COLOR_MARRON)
                c.drawRightString(PAGE_W - MARGIN, y, num_str)

                y -= 30

    draw_footer(c, 0)
    c.showPage()


# ============================================================================
# PRODUCTO — Versión mejorada con wrap de texto y paleta arriba
# ============================================================================

def draw_color_palette_strip(c, x, y, w, custom_palette):
    """
    Dibuja la paleta de colores en una franja ARRIBA de la imagen
    (no encima de la descripción).
    """
    if not custom_palette:
        return 0

    h = 14
    draw_paper_label(c, x, y, w, h, rotation=0, color=COLOR_CREMA, has_tape=False)

    c.saveState()
    c.translate(x + w / 2, y + h / 2)

    c.setFont(SANS_BOLD, 6.5)
    c.setFillColor(COLOR_MORADO)
    c.drawString(-w / 2 + 8, 0, "ACABADO:")

    chip_x = -w / 2 + 50
    c.setFillColor(colors.HexColor(custom_palette["hex"]))
    c.setStrokeColor(colors.HexColor("#BFB59F"))
    c.setLineWidth(0.3)
    c.circle(chip_x, 0, 4, stroke=1, fill=1)

    c.setFont(SANS_REG, 6.5)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    c.drawString(chip_x + 7, -2, custom_palette["primary"].upper())

    c.restoreState()
    return h


def draw_product_card_scrapbook(c, x, y, w, h, prod, img_path, rot_photo=0, rot_label=0,
                                 show_color_palette=False, custom_palette=None,
                                 horizontal_drift=0, max_desc_lines=None):
    """
    Tarjeta scrapbook v8:
    - Paleta de colores ARRIBA de la imagen (no encima de la descripción)
    - Descripción con wrap de texto (no se corta a mitad de frase)
    - Margen extra entre líneas para mejor lectura
    """
    x = x + horizontal_drift

    # Polaroid
    box = draw_polaroid_frame(c, x, y, w, h, rotation=rot_photo)
    if img_path:
        fit_image_in_box(c, img_path, box["x"], box["y"], box["w"], box["h"])

    tape_w = w * 0.4
    draw_washi_tape(c, x + (w - tape_w) / 2, y + h - 8, tape_w, 12,
                    angle=rot_photo * 0.3, color=COLOR_KRAFT)

    # === Paleta ARRIBA de la imagen (entre la cinta y la imagen) ===
    palette_h = 0
    if show_color_palette and custom_palette:
        palette_h = 14
        palette_y = y + h - 8 - 12 - palette_h - 2  # debajo de la cinta
        palette_w = w * 0.7
        palette_x = x + (w - palette_w) / 2
        draw_color_palette_strip(c, palette_x, palette_y, palette_w, custom_palette)

    # === Etiqueta (debajo del polaroid) ===
    label_w = w * 0.95
    label_h = 80  # Más alto para portrait (descripción con más espacio)
    label_x = x + (w - label_w) / 2
    label_y = y - label_h + 14

    draw_paper_label(c, label_x, label_y, label_w, label_h,
                     rotation=rot_label, color=COLOR_CREMA, has_tape=False)

    c.saveState()
    c.translate(label_x + label_w / 2, label_y + label_h / 2)
    c.rotate(rot_label)

    nombre = prod["_display_name"]
    descripcion = prod["_display_desc"]
    material = prod.get("material", "PLA")
    medidas = prod.get("_display_dims", "")
    precio = prod["_display_price"]

    # Nombre del producto
    c.setFont(SANS_BOLD, 8.5)
    c.setFillColor(COLOR_NEGRO)
    nombre_corto = nombre
    if pdfmetrics.stringWidth(nombre_corto, SANS_BOLD, 8.5) > label_w * 0.85:
        while len(nombre_corto) > 1 and pdfmetrics.stringWidth(nombre_corto + "...", SANS_BOLD, 8.5) > label_w * 0.85:
            nombre_corto = nombre_corto[:-1]
        nombre_corto = nombre_corto + "..."
    c.drawCentredString(0, label_h / 2 - 14, f"\u201C{nombre_corto.upper()}\u201D")

    # Descripción con wrap (no se corta a mitad de frase)
    c.setFont(SANS_REG, 6.2)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    desc_lines = wrap_text(f"DESCRIPCIÓN: {descripcion.upper()}",
                           SANS_REG, 6.2, label_w * 0.88)
    if max_desc_lines and len(desc_lines) > max_desc_lines:
        desc_lines = desc_lines[:max_desc_lines]
        # Asegurar que la última línea no termine en mitad de palabra
        last = desc_lines[-1]
        last = last.rstrip(",.;: ")
        if " " in last:
            # Quitar la última palabra incompleta
            words = last.split(" ")
            if len(words) > 1:
                last = " ".join(words[:-1]) + "..."
            else:
                last = last + "..."
        else:
            last = last + "..."
        desc_lines[-1] = last

    ly = label_h / 2 - 26
    line_height = 8.5  # Más espacio entre renglones
    for line in desc_lines:
        c.drawCentredString(0, ly, line)
        ly -= line_height

    # Material y medidas
    mat_y = ly - 4
    c.setFont(SANS_REG, 6)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    if medidas:
        c.drawCentredString(0, mat_y, f"MATERIAL: {material.upper()}    MEDIDAS: {medidas}")
    else:
        c.drawCentredString(0, mat_y, f"MATERIAL: {material.upper()}")

    # Precio (grande, en la esquina)
    if precio:
        c.setFont(SERIF_BOLD, 15)
        c.setFillColor(COLOR_NEGRO)
        precio_txt = f"${precio:.0f}"
        c.drawRightString(label_w / 2 - 10, -label_h / 2 + 14, precio_txt)

    c.restoreState()

    return label_y


# ============================================================================
# LANDMARKS — 1 a 2 lugares por página
# ============================================================================

def build_landmarks_page(c, productos_map, page_num, landmark_ids):
    """Pagina de landmarks en portrait: 1 o 2 lugares apilados."""
    print(f"  Lugares del Mundo (pág {page_num}) — {len(landmark_ids)} lugares")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.32)

    draw_minimal_header(c)

    # Subtitulo mas abajo del header (header termina en y=765)
    c.setFont(SCRIPT_REG, 22)
    c.setFillColor(COLOR_MORADO)
    c.drawCentredString(PAGE_W / 2, 720, "Lugares del Mundo")

    c.setFont(SANS_REG, 8.5)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    c.drawCentredString(PAGE_W / 2, 700, "MINIATURAS ARQUITECTONICAS  ·  EDICION LIMITADA")

    draw_thin_line(c, PAGE_W / 2 - 80, 685, PAGE_W / 2 + 80, 685,
                   color=COLOR_NEGRO, width=0.5)

    overrides = load_overrides()
    landscape_colors = overrides.get("landmarks_terrain_only", {})

    n = len(landmark_ids)
    # Layout: 1 landmark grande centrado, o 2 apilados
    if n == 1:
        col_w = 280
        polaroid_h = 260
        # Polaroid top en y=580, bot en y=320 (etiqueta 60pt debajo: 260-320)
        positions = [(PAGE_W / 2 - col_w / 2, 320)]
    elif n == 2:
        col_w = 280
        polaroid_h = 200
        # 2 apilados: top y=540 bot y=340; bot y=160 bot y=-40 (etiqueta)
        # Mejor: polaroid 1 top=440 bot=240 (etiqueta 180-240)
        #        polaroid 2 top=160 bot=-40 (etiqueta -100 a -40 -> fuera!)
        # Hay que hacer el polaroid mas pequeno
        # polaroid_h=160, total con etiqueta = 220
        # polaroid 1: y=440, bot=600, etiqueta 380-440
        # polaroid 2: y=160, bot=320, etiqueta 100-160
        # 60pt de gap entre etiqueta1 bot (440) y polaroid2 top (160) -> mucho
        # Compacto: polaroid_h=140
        # polaroid 1: y=400, bot=540, etiqueta 340-400
        # polaroid 2: y=140, bot=280, etiqueta 80-140
        # Gap = 60 entre etiqueta1 bot y polaroid2 top
        col_w = 280
        polaroid_h = 150
        positions = [
            (PAGE_W / 2 - col_w / 2, 400),
            (PAGE_W / 2 - col_w / 2, 130),
        ]
    else:
        col_w = 180
        polaroid_h = 130
        positions = []
        for i in range(n):
            gap = 15
            total_w = n * col_w + (n - 1) * gap
            start_x = (PAGE_W - total_w) / 2
            positions.append((start_x + i * (col_w + gap), 400))

    for i, pid in enumerate(landmark_ids):
        if pid not in productos_map:
            continue
        prod = productos_map[pid]
        px, py = positions[i]
        img_path = get_image_path({"producto_id": pid, "imagen_filename": prod.get("imagen_principal")},
                                  productos_map)
        custom_color = landscape_colors.get(pid)

        box = draw_polaroid_frame(c, px, py, col_w, polaroid_h, rotation=0, shadow=False)
        if img_path:
            fit_image_in_box(c, img_path, box["x"], box["y"], box["w"], box["h"])

        # Etiqueta DEBAJO del polaroid (no encima)
        label_h = 50
        label_w = col_w
        label_x = px
        label_y = py - label_h - 4  # 4pt de gap entre polaroid bot y label top

        draw_paper_label(c, label_x, label_y, label_w, label_h, rotation=0,
                         color=COLOR_CREMA, has_tape=False)

        c.saveState()
        c.translate(label_x + label_w / 2, label_y + label_h / 2)

        c.setFont(SANS_BOLD, 9)
        c.setFillColor(COLOR_NEGRO)
        c.drawCentredString(0, 8, f"\u201C{prod['_display_name'].upper()}\u201D")

        if prod.get("_display_price"):
            c.setFont(SERIF_BOLD, 14)
            c.setFillColor(COLOR_NEGRO)
            c.drawCentredString(0, -10, f"${prod['_display_price']:.0f}")

        if custom_color:
            c.setFillColor(colors.HexColor(custom_color["hex"]))
            c.setStrokeColor(colors.HexColor("#BFB59F"))
            c.setLineWidth(0.3)
            c.circle(-label_w / 2 + 16, 0, 5, stroke=1, fill=1)
            c.setFont(SANS_REG, 6)
            c.setFillColor(COLOR_NEGRO_SUAVE)
            c.drawString(-label_w / 2 + 24, -2, custom_color["primary"].upper())

        c.restoreState()

    # Nota al pie
    c.setFont(SERIF_ITAL, 8.5)
    c.setFillColor(COLOR_MARRON)
    c.drawCentredString(PAGE_W / 2, 55,
                        "Cada lugar se imprime en su propio color de terreno especial")
    c.setFont(SANS_REG, 7)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    c.drawCentredString(PAGE_W / 2, 42,
                        "ACABADO MATE QUE RESALTA LOS DETALLES ARQUITECTONICOS")

    draw_footer(c, page_num)
    c.showPage()


# ============================================================================
# PALETA DE COLORES
# ============================================================================

def build_colors_swatch_palette(c, page_num):
    print(f"  Colores disponibles (pág {page_num})")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.32)

    draw_minimal_header(c)

    c.setFont(SCRIPT_REG, 24)
    c.setFillColor(COLOR_MORADO)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 130, "Colores Disponibles")

    c.setFont(SANS_REG, 8.5)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 150, "TODOS NUESTROS MODELOS ESTAN DISPONIBLES EN LOS SIGUIENTES ACABADOS")

    draw_thin_line(c, PAGE_W / 2 - 80, PAGE_H - 165, PAGE_W / 2 + 80, PAGE_H - 165,
                   color=COLOR_NEGRO, width=0.5)

    colores = [
        ("Blanco Matte",      "#FFFFFF"),
        ("Negro Matte",       "#1A1A1A"),
        ("Verde Oliva Matte", "#7A8C6E"),
        ("Azul Claro Matte",  "#B8CCE4"),
        ("Rosa Pastel Matte", "#E8D5D5"),
        ("Gris",              "#9E9E9E"),
    ]

    # 2 filas x 3 columnas
    col_w = 150
    row_h = 130
    gap_x = 25
    gap_y = 25
    cols = 3
    rows = 2
    total_w = cols * col_w + (cols - 1) * gap_x
    start_x = (PAGE_W - total_w) / 2
    start_y = 440

    for i, (nombre, hex_c) in enumerate(colores):
        col = i % cols
        row = i // cols
        x = start_x + col * (col_w + gap_x)
        y = start_y - row * (row_h + gap_y)

        draw_paper_label(c, x, y, col_w, row_h, rotation=0,
                         color=COLOR_CREMA, has_tape=False)

        c.saveState()

        c.setFillColor(colors.HexColor(hex_c))
        c.setStrokeColor(colors.HexColor("#BFB59F"))
        c.setLineWidth(0.4)
        c.circle(x + col_w / 2, y + row_h - 45, 28, stroke=1, fill=1)

        c.setFont(SANS_BOLD, 9.5)
        c.setFillColor(COLOR_NEGRO)
        c.drawCentredString(x + col_w / 2, y + 38, nombre.upper())

        c.setFont(SERIF_REG, 7.5)
        c.setFillColor(COLOR_MARRON)
        c.drawCentredString(x + col_w / 2, y + 22, hex_c)

        c.restoreState()

    c.setFont(SERIF_ITAL, 10)
    c.setFillColor(COLOR_MARRON)
    c.drawCentredString(PAGE_W / 2, 130, "Acabado mate en todos los colores")
    c.setFont(SANS_REG, 8.5)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    c.drawCentredString(PAGE_W / 2, 110, "IMPRESION 3D EN PLA BIODEGRADABLE")

    draw_footer(c, page_num)
    c.showPage()


# ============================================================================
# PÁGINAS DE PRODUCTO
# ============================================================================

def build_cover_collection_page(c, categoria, page_num):
    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.45)

    draw_minimal_header(c)

    cy = PAGE_H / 2 - 30

    label_w = 420
    label_h = 360
    label_x = (PAGE_W - label_w) / 2
    label_y = cy - label_h / 2

    draw_paper_label(c, label_x, label_y, label_w, label_h,
                     rotation=0, color=COLOR_CREMA, has_tape=True, tape_pos="top")

    draw_washi_tape(c, label_x + 30, label_y - 8, 80, 12, angle=-8)

    c.saveState()
    c.setFont(SCRIPT_REG, 42)
    c.setFillColor(COLOR_NEGRO)
    cat_text = categoria
    if pdfmetrics.stringWidth(cat_text, SCRIPT_REG, 42) > label_w - 40:
        c.setFont(SCRIPT_REG, 34)
    c.drawCentredString(PAGE_W / 2, cy + 90, cat_text)

    draw_thin_line(c, PAGE_W / 2 - 50, cy + 60, PAGE_W / 2 + 50, cy + 60,
                   color=COLOR_NEGRO, width=0.6)

    c.setFont(SANS_REG, 12)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    sub = "Coleccion Regenerativa"
    c.drawCentredString(PAGE_W / 2, cy + 35, sub)

    c.setFont(SERIF_ITAL, 13)
    c.setFillColor(COLOR_MARRON)
    c.drawCentredString(PAGE_W / 2, cy - 10, "Diseno consciente · Impreso aqui")

    draw_isotipo_hoja(c, PAGE_W / 2, cy - 80, 26, color=COLOR_VERDE)

    c.restoreState()
    draw_footer(c, page_num)
    c.showPage()


def build_hero_product_page(c, elem, productos, page_num):
    prod = productos.get(elem["producto_id"])
    if not prod:
        return
    print(f"  Hero: {prod['_display_name'][:35]} (pág {page_num})")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.35)

    draw_minimal_header(c)

    img_path = get_image_path(elem, productos)

    # Polaroid centrado. Header termina en y~785. Necesito gap de 30pt.
    # Polaroid bot = 755, top = 755 - ph. ph=320 -> top=435. Demasiado alto.
    # Mejor: ph=280, top=475, bot=755.
    pw, ph = 300, 280
    px = (PAGE_W - pw) / 2
    py = 470

    draw_product_card_scrapbook(c, px, py, pw, ph, prod, img_path,
                                 rot_photo=0, rot_label=0, max_desc_lines=4)

    # Info label centrado abajo (ancho completo)
    info_w = PAGE_W - 2 * MARGIN
    info_h = 220
    info_x = MARGIN
    info_y = 70

    draw_paper_label(c, info_x, info_y, info_w, info_h, rotation=0,
                     color=COLOR_CREMA_OSC, has_tape=True, tape_pos="top")

    c.saveState()

    # Layout horizontal: 3 columnas
    col1_x = info_x + 30
    col2_x = info_x + info_w / 2
    col3_x = info_x + info_w - 30
    text_y = info_y + info_h - 35

    # Columna 1: Sostenibilidad
    c.setFont(SANS_BOLD, 10)
    c.setFillColor(COLOR_MORADO)
    c.drawString(col1_x, text_y, "SOSTENIBILIDAD")
    c.setFont(SANS_REG, 8.5)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    badges = ["RECICLABLE", "BIODEGRADABLE", "LARGA VIDA"]
    by = text_y - 25
    for b in badges:
        c.setFillColor(COLOR_VERDE)
        c.circle(col1_x + 3, by, 3, stroke=0, fill=1)
        c.setFillColor(COLOR_NEGRO_SUAVE)
        c.drawString(col1_x + 11, by - 3, b)
        by -= 20

    # Columna 2: Detalles
    c.setFont(SANS_BOLD, 10)
    c.setFillColor(COLOR_MORADO)
    c.drawString(col2_x, text_y, "DETALLES")
    c.setFont(SERIF_ITAL, 9)
    c.setFillColor(COLOR_MARRON)
    sku = elem.get("sku", "")
    cat_es = prod.get('categoria', '')
    dy = text_y - 25
    c.drawString(col2_x, dy, f"SKU: {sku}")
    c.drawString(col2_x, dy - 15, f"Categoria: {cat_es}")
    c.drawString(col2_x, dy - 30, f"Material: {prod.get('material', 'PLA')}")

    # Columna 3: Descripcion corta
    c.setFont(SANS_BOLD, 10)
    c.setFillColor(COLOR_MORADO)
    c.drawRightString(col3_x, text_y, "NOTAS")
    c.setFont(SERIF_ITAL, 8.5)
    c.setFillColor(COLOR_MARRON)
    desc = prod["_display_desc"]
    # Wrap simple
    words = desc.split()
    lines = []
    current_line = ""
    max_w = (col3_x - col2_x) - 30
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if pdfmetrics.stringWidth(test_line, SERIF_ITAL, 8.5) < max_w:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    ly = text_y - 25
    for line in lines[:6]:
        c.drawRightString(col3_x, ly, line)
        ly -= 12

    c.restoreState()

    draw_footer(c, page_num)
    c.showPage()


def build_grid_2x2(c, elementos, productos, page_num, custom_palette_map=None):
    """Portrait: 2 productos lado a lado."""
    print(f"  Grid 2x2: {len(elementos)} productos (pág {page_num})")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.32)

    draw_minimal_header(c)

    pw, ph = 200, 290
    n = min(len(elementos), 2)

    gap = (PAGE_W - n * pw) / (n + 1)
    top_y = PAGE_H - 145 - ph

    rot_photos = [-0.4, 0.4]
    rot_labels = [0.3, -0.3]
    drifts = [3, -2]

    for i, elem in enumerate(elementos[:n]):
        prod = productos.get(elem["producto_id"])
        if not prod:
            continue
        x = gap + i * (pw + gap)
        rot_p = rot_photos[i]
        rot_l = rot_labels[i]
        drift = drifts[i]
        img_path = get_image_path(elem, productos)
        custom_color = (custom_palette_map or {}).get(prod["id"])
        draw_product_card_scrapbook(c, x, top_y, pw, ph, prod, img_path,
                                     rot_photo=rot_p, rot_label=rot_l,
                                     show_color_palette=bool(custom_color),
                                     custom_palette=custom_color,
                                     horizontal_drift=drift,
                                     max_desc_lines=3)

    draw_footer(c, page_num)
    c.showPage()


def build_grid_1x2(c, elementos, productos, page_num, custom_palette_map=None):
    """Portrait: 2 productos apilados verticalmente."""
    print(f"  Grid 1x2: {len(elementos)} productos (pág {page_num})")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.3)

    draw_minimal_header(c)

    pw, ph = 340, 240
    # 2 productos apilados. Margen desde header (y~85) y footer (y~40).
    # Top polaroid y=540, bottom polaroid y=215
    # Espacio disponible: 540-215 = 325 (incluye polaroid+etiqueta)
    # Etiqueta va 80pt debajo del polaroid. Polaroid top->bottom: 240
    # polaroid 1: y=540 a 780, etiqueta y=460 a 540
    # polaroid 2: y=215 a 455, etiqueta y=135 a 215
    polaroid_y_top = PAGE_H - 302
    polaroid_y_bot = 215

    positions = [
        ((PAGE_W - pw) / 2, polaroid_y_top, -0.3, 0.2, 3),
        ((PAGE_W - pw) / 2, polaroid_y_bot, 0.3, -0.2, -3),
    ]

    for i, elem in enumerate(elementos[:2]):
        prod = productos.get(elem["producto_id"])
        if not prod:
            continue
        x, y, rot_p, rot_l, drift = positions[i]
        img_path = get_image_path(elem, productos)
        custom_color = (custom_palette_map or {}).get(prod["id"])
        draw_product_card_scrapbook(c, x, y, pw, ph, prod, img_path,
                                     rot_photo=rot_p, rot_label=rot_l,
                                     show_color_palette=bool(custom_color),
                                     custom_palette=custom_color,
                                     horizontal_drift=drift,
                                     max_desc_lines=3)

    draw_footer(c, page_num)
    c.showPage()


def build_grid_1x3(c, elementos, productos, page_num, custom_palette_map=None):
    """Portrait: 1 producto centrado por pagina (3 elementos = 3 paginas las crea el caller)."""
    print(f"  Grid 1x3: {len(elementos)} productos (pág {page_num})")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.28)

    draw_minimal_header(c)

    pw, ph = 340, 400
    n = min(len(elementos), 1)  # Solo 1 por pagina en portrait

    polaroid_x = (PAGE_W - pw) / 2
    polaroid_y = PAGE_H - 145 - ph

    for i, elem in enumerate(elementos[:n]):
        prod = productos.get(elem["producto_id"])
        if not prod:
            continue
        img_path = get_image_path(elem, productos)
        custom_color = (custom_palette_map or {}).get(prod["id"])
        draw_product_card_scrapbook(c, polaroid_x, polaroid_y, pw, ph, prod, img_path,
                                     rot_photo=-0.3, rot_label=0.2,
                                     show_color_palette=bool(custom_color),
                                     custom_palette=custom_color,
                                     horizontal_drift=2,
                                     max_desc_lines=5)

    # Mini strip de colores al pie
    strip_y = 75
    strip_x = MARGIN + 50
    strip_w = PAGE_W - 2 * (MARGIN + 50)

    c.setFont(SANS_BOLD, 7.5)
    c.setFillColor(COLOR_MORADO)
    c.drawString(strip_x, strip_y + 14, "COLORES DISPONIBLES:")

    colores = [
        ("BLANCO", "#FFFFFF"),
        ("NEGRO", "#1A1A1A"),
        ("OLIVA", "#7A8C6E"),
        ("AZUL CLARO", "#B8CCE4"),
        ("ROSA", "#E8D5D5"),
        ("GRIS", "#9E9E9E"),
    ]

    sw_size = 9
    sw_gap = 50
    sw_x_start = strip_x + 145
    for i, (nombre, hex_c) in enumerate(colores):
        sx = sw_x_start + i * sw_gap
        c.setFillColor(colors.HexColor(hex_c))
        c.setStrokeColor(colors.HexColor("#BFB59F"))
        c.setLineWidth(0.3)
        c.circle(sx, strip_y + 14, 6, stroke=1, fill=1)
        c.setFont(SANS_REG, 6)
        c.setFillColor(COLOR_NEGRO_SUAVE)
        c.drawCentredString(sx, strip_y, nombre)

    draw_footer(c, page_num)
    c.showPage()


# ============================================================================
# PÁGINAS INSTITUCIONALES
# ============================================================================

def build_pla_page(c, page_num):
    print(f"  PLA (pág {page_num})")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.32)

    draw_minimal_header(c)

    # Etiqueta principal ocupa casi toda la pagina en portrait
    label_w = PAGE_W - 2 * MARGIN
    label_h = 600
    label_x = MARGIN
    label_y = 80

    draw_paper_label(c, label_x, label_y, label_w, label_h, rotation=0,
                     color=COLOR_CREMA, has_tape=True, tape_pos="top")

    c.saveState()

    c.setFont(SCRIPT_REG, 34)
    c.setFillColor(COLOR_MORADO)
    c.drawCentredString(PAGE_W / 2, label_y + label_h - 55, "Hecho de PLA")

    c.setFont(SANS_REG, 11)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    c.drawCentredString(PAGE_W / 2, label_y + label_h - 80, "BELLO POR DENTRO Y POR FUERA")

    draw_thin_line(c, PAGE_W / 2 - 50, label_y + label_h - 95, PAGE_W / 2 + 50, label_y + label_h - 95,
                   color=COLOR_NEGRO, width=0.5)

    text_x = label_x + 40
    text_y = label_y + label_h - 130

    paragraphs = [
        (SANS_REG, COLOR_NEGRO, "El PLA (Acido Polilactico) es un polimero de origen vegetal,"),
        (SANS_REG, COLOR_NEGRO, "derivado principalmente de almidon de maiz o cana de azucar."),
        (SANS_REG, COLOR_NEGRO, "A diferencia de los plasticos convencionales, el PLA se obtiene"),
        (SANS_REG, COLOR_NEGRO, "de fuentes renovables y es compostable en condiciones"),
        (SANS_REG, COLOR_NEGRO, "industriales."),
        (SANS_REG, None, ""),
        (SANS_BOLD, COLOR_MORADO, "POR QUE IMPORTA"),
        (SANS_REG, None, ""),
        (SANS_REG, COLOR_NEGRO, "  -  Reduce la dependencia de petroquimicos"),
        (SANS_REG, COLOR_NEGRO, "  -  Menor huella de carbono en su produccion"),
        (SANS_REG, COLOR_NEGRO, "  -  Compostable: no se acumula por siglos"),
        (SANS_REG, COLOR_NEGRO, "  -  Permite produccion local y bajo demanda"),
        (SANS_REG, COLOR_NEGRO, "  -  Cero inventario excedente = cero desperdicio"),
        (SANS_REG, None, ""),
        (SANS_BOLD, COLOR_NEGRO, "En Yolitia, cada pieza se imprime en 3D cuando tu la pides."),
        (SANS_BOLD, COLOR_NEGRO, "No hay bodegas llenas. No hay sobreproduccion."),
    ]

    for font, color, text in paragraphs:
        if font:
            c.setFont(font, 10)
        if color:
            c.setFillColor(color)
        c.drawString(text_x, text_y, text)
        text_y -= 16

    c.restoreState()
    draw_footer(c, page_num)
    c.showPage()


def build_compromiso_page(c, page_num):
    print(f"  Compromiso (pág {page_num})")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.32)

    draw_minimal_header(c)

    c.setFont(SCRIPT_REG, 30)
    c.setFillColor(COLOR_MORADO)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 130, "Nuestro Compromiso")

    c.setFont(SANS_REG, 11)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 150, "CONTIGO Y CON EL PLANETA")

    draw_thin_line(c, PAGE_W / 2 - 50, PAGE_H - 165, PAGE_W / 2 + 50, PAGE_H - 165,
                   color=COLOR_NEGRO, width=0.5)

    # Box 1 - 10% conservacion
    box1_x = MARGIN + 10
    box1_y = 350
    box1_w = PAGE_W - 2 * (MARGIN + 10)
    box1_h = 180

    draw_paper_label(c, box1_x, box1_y, box1_w, box1_h, rotation=-0.3,
                     color=COLOR_CREMA, has_tape=True, tape_pos="top")

    c.saveState()
    c.translate(box1_x + 25, box1_y + box1_h - 40)
    c.setFont(SCRIPT_REG, 30)
    c.setFillColor(COLOR_VERDE)
    c.drawString(0, 0, "10%")
    c.setFont(SANS_BOLD, 13)
    c.setFillColor(COLOR_MORADO)
    c.drawString(110, 8, "PARA LA CONSERVACION")

    c.setFont(SANS_REG, 10)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    c.drawString(110, -10, "El 10% de nuestras ganancias se destina directamente a proyectos")
    c.drawString(110, -25, "de conservacion ambiental en Mexico.")
    c.drawString(110, -50, "Cada compra tuya apoya esa causa.")

    c.restoreState()

    # Box 2 - redes
    box2_x = MARGIN + 20
    box2_y = 110
    box2_w = PAGE_W - 2 * (MARGIN + 20)
    box2_h = 180

    draw_paper_label(c, box2_x, box2_y, box2_w, box2_h, rotation=0.4,
                     color=COLOR_CREMA_OSC, has_tape=True, tape_pos="top")

    c.saveState()
    c.translate(box2_x + 25, box2_y + box2_h - 40)
    c.setFont(SCRIPT_REG, 30)
    c.setFillColor(COLOR_VERDE)
    c.drawString(0, 0, "@")
    c.setFont(SANS_BOLD, 13)
    c.setFillColor(COLOR_MORADO)
    c.drawString(70, 8, "DIFUNDIMOS EN REDES")

    c.setFont(SANS_REG, 10)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    c.drawString(70, -10, "Estamos activos en redes sociales compartiendo nuestro proceso y")
    c.drawString(70, -25, "valores. Siguenos y unete al movimiento:")
    c.setFont(SERIF_ITAL, 12)
    c.setFillColor(COLOR_MARRON)
    c.drawString(70, -55, "@yolitia   ·   www.yolitia.bio")

    c.restoreState()

    draw_footer(c, page_num)
    c.showPage()


def build_back_cover(c):
    print("  Contraportada...")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.45)

    # Logo y nombre arriba
    draw_isotipo_hoja(c, PAGE_W / 2, PAGE_H - 130, 54, color=COLOR_VERDE)

    c.setFont(SCRIPT_REG, 68)
    c.setFillColor(COLOR_MORADO)
    w = pdfmetrics.stringWidth("Yolitia", SCRIPT_REG, 68)
    c.drawString((PAGE_W - w) / 2, PAGE_H - 200, "Yolitia")

    c.setFont(SANS_REG, 12)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    sub = "UN PROYECTO CIRCULAR"
    w = pdfmetrics.stringWidth(sub, SANS_REG, 12)
    c.drawString((PAGE_W - w) / 2, PAGE_H - 230, sub)

    # Manifesto ocupa casi toda la pagina
    label_w = PAGE_W - 2 * MARGIN
    label_h = 480
    label_x = MARGIN
    label_y = 100

    draw_paper_label(c, label_x, label_y, label_w, label_h, rotation=0,
                     color=COLOR_CREMA, has_tape=True, tape_pos="top")

    c.saveState()

    text_x = label_x + 35
    text_y = label_y + label_h - 50

    manifesto = [
        (SANS_REG, COLOR_NEGRO, "Yolitia nace de una pregunta simple:"),
        (SANS_REG, None, ""),
        (SERIF_ITAL, COLOR_MORADO, "Y si los objetos que usamos cada dia pudieran"),
        (SERIF_ITAL, COLOR_MORADO, "hacerse con menos y significar mas?"),
        (SANS_REG, None, ""),
        (SANS_BOLD, COLOR_VERDE, "NUESTRO MODELO ES DIFERENTE"),
        (SANS_REG, None, ""),
        (SANS_REG, COLOR_NEGRO, "  -  Producimos bajo pedido, no en masa"),
        (SANS_REG, COLOR_NEGRO, "  -  Materiales de origen vegetal (PLA)"),
        (SANS_REG, COLOR_NEGRO, "  -  Disenamos para durar"),
        (SANS_REG, COLOR_NEGRO, "  -  Cada compra apoya manufactura local"),
        (SANS_REG, None, ""),
        (SANS_REG, COLOR_NEGRO, "Somos parte del movimiento de economia circular:"),
        (SANS_REG, COLOR_NEGRO, "los materiales entran, se usan, se recuperan."),
        (SANS_BOLD, COLOR_MORADO, "Nada se pierde. Todo vuelve."),
    ]

    for font, color, text in manifesto:
        if font:
            c.setFont(font, 11)
        if color:
            c.setFillColor(color)
        c.drawString(text_x, text_y, text)
        text_y -= 17

    c.restoreState()

    draw_washi_tape(c, PAGE_W / 2 - 110, 50, 220, 16, angle=-2)

    c.setFont(SERIF_ITAL, 9)
    c.setFillColor(COLOR_NEGRO)
    c.drawCentredString(PAGE_W / 2, 60, "Diseno consciente · Impreso aqui")

    c.showPage()


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
# FUNCIÓN PRINCIPAL
# ============================================================================

def build_catalog():
    print("=" * 70)
    print("GENERACION CATALOGO YOLITIA v9 - VERTICAL (PORTRAIT) - ESPANOL")
    print("=" * 70)

    register_fonts()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    layout, productos = load_data()
    overrides = load_overrides()
    apply_overrides(productos, overrides)

    print(f"\nLayout: {len(layout['paginas'])} paginas")
    print(f"Productos: {len(productos)}")

    c = canvas.Canvas(str(OUTPUT_PDF), pagesize=A4)
    c.setTitle("Catalogo Yolitia 2026 - Coleccion Verano (Vertical)")
    c.setAuthor("Yolitia")
    c.setSubject("Catalogo de productos impresos en 3D en PLA biodegradable")

    paginas_generadas = 0
    pagina_actual = 0
    landmarks_inserted = False

    LANDMARK_IDS = ["YOL-061", "YOL-066", "YOL-067", "YOL-069", "YOL-070",
                    "YOL-071", "YOL-072", "YOL-073", "YOL-074"]

    # Distribución de landmarks: 2 + 2 + 2 + 2 + 1 (cinco páginas)
    LANDMARK_BATCHES = [
        ["YOL-061", "YOL-066"],
        ["YOL-067", "YOL-069"],
        ["YOL-070", "YOL-071"],
        ["YOL-072", "YOL-073"],
        ["YOL-074"],
    ]
    batch_idx = 0

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

            if not landmarks_inserted and ("Regalos" in cat or "Coleccionables" in cat):
                # Insertar todas las páginas de landmarks ANTES del separador
                for batch in LANDMARK_BATCHES:
                    build_landmarks_page(c, productos, pagina_actual + 1, batch)
                    paginas_generadas += 1
                    pagina_actual += 1
                landmarks_inserted = True

            build_cover_collection_page(c, cat, page_num)
            paginas_generadas += 1
            pagina_actual += 1

        elif tipo == "productos":
            grid = pagina_data.get("grid", "1x2")
            page_num = pagina_data.get("pagina_numero") or (pagina_actual + 1)

            elementos_filtrados = [
                e for e in pagina_data.get("elementos", [])
                if e.get("producto_id") not in LANDMARK_IDS
            ]

            if not elementos_filtrados:
                continue

            custom_palette = overrides.get("landmarks_terrain_only", {})

            if grid == "1x1":
                elem = elementos_filtrados[0]
                build_hero_product_page(c, elem, productos, page_num)
                paginas_generadas += 1
                pagina_actual += 1
            elif grid == "2x2":
                # Portrait: 2 productos lado a lado (no 4)
                build_grid_2x2(c, elementos_filtrados, productos, page_num, custom_palette)
                paginas_generadas += 1
                pagina_actual += 1
            elif grid == "1x2":
                build_grid_1x2(c, elementos_filtrados, productos, page_num, custom_palette)
                paginas_generadas += 1
                pagina_actual += 1
            elif grid == "1x3":
                # Portrait: cada producto en su propia pagina
                for i, elem in enumerate(elementos_filtrados):
                    build_grid_1x3(c, [elem], productos, page_num + i, custom_palette)
                    paginas_generadas += 1
                    pagina_actual += 1
            else:
                build_grid_1x2(c, elementos_filtrados, productos, page_num, custom_palette)
                paginas_generadas += 1
                pagina_actual += 1

        elif tipo == "material_pla":
            build_pla_page(c, pagina_actual + 1)
            paginas_generadas += 1
            pagina_actual += 1

        elif tipo == "colores":
            build_colors_swatch_palette(c, pagina_actual + 1)
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
