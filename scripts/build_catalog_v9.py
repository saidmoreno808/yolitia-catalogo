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
# reportlab usa coordenadas cartesianas con origen en la esquina INFERIOR-IZQUIERDA.
# PAGE_H = 842 (A4 portrait vertical).
# Para evitar confusion, definimos zonas en terminos de "y desde el FONDO":
PAGE_W, PAGE_H = A4  # 595 x 842 pt (210x297 mm portrait)
MARGIN = 36
CONTENT_W = PAGE_W - (2 * MARGIN)

# Zonas verticales (todas en coords "y desde el FONDO"):
# En reportlab y crece hacia arriba. PAGE_H=842.
# Header: isotopo y=820, script baseline y=786, linea y=762. El header ocupa hasta y~755.
# Contenido: y entre 750 (debajo del header) y 60 (arriba del footer).
PAGE_BOTTOM = 0
PAGE_TOP = PAGE_H
FOOTER_TOP = 60   # el footer arranca en y=60 (todo lo de abajo esta reservado)
HEADER_BOTTOM = 750  # el header termina en y=750 (todo lo de abajo esta disponible)
CONTENT_AREA_BOTTOM = FOOTER_TOP + 8  # 68: margen antes del footer
CONTENT_AREA_TOP = HEADER_BOTTOM  # 750
CONTENT_AREA_HEIGHT = CONTENT_AREA_TOP - CONTENT_AREA_BOTTOM  # ~682pt


# Helper: convierte "y desde el top" a "y desde el fondo" (coords reportlab)
def y_from_top(y_top: float) -> float:
    """y_top = 0 en el borde superior; retorna y en coords reportlab."""
    return PAGE_H - y_top


# Helper: convierte "y desde el fondo" a "y desde el top" (visual)
def y_from_bottom(y_bot: float) -> float:
    return PAGE_H - y_bot


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


def fit_image_in_box_cover(c, img_path, box_x, box_y, box_w, box_h):
    """Como fit_image_in_box pero la imagen LLENA el area (puede recortarse).
    Util para landmarks con imagenes pequenas que deben verse grandes.
    """
    try:
        img = ImageReader(img_path)
        iw, ih = img.getSize()
        ratio = iw / ih
        box_ratio = box_w / box_h
        if ratio > box_ratio:
            # imagen mas ancha: limitamos por alto
            h = box_h
            w = box_h * ratio
        else:
            # imagen mas alta: limitamos por ancho
            w = box_w
            h = box_w / ratio
        x = box_x + (box_w - w) / 2
        y = box_y + (box_h - h) / 2
        # Fondo blanco para areas vacias del box
        c.setFillColorRGB(0.95, 0.94, 0.91)
        c.rect(box_x, box_y, box_w, box_h, fill=1, stroke=0)
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
    """Header minimalista en español (portrait).
    Header ocupa y=820 (isotopo) hasta y=755 (linea). Contenido debe estar
    debajo de HEADER_BOTTOM=750.
    """
    # Isotopo
    draw_isotipo_hoja(c, PAGE_W / 2, 822, 16, color=COLOR_VERDE)
    # Script "Yolitia" centrado, baseline en y=790
    c.setFont(SCRIPT_REG, 24)
    c.setFillColor(COLOR_MORADO)
    text_w = pdfmetrics.stringWidth("Yolitia", SCRIPT_REG, 24)
    c.drawString((PAGE_W - text_w) / 2, 790, "Yolitia")
    # Linea fina debajo del header
    c.setStrokeColor(COLOR_KRAFT)
    c.setLineWidth(0.3)
    c.line(MARGIN + 40, 768, PAGE_W - MARGIN - 40, 768)


def draw_footer(c, page_num):
    """Footer en y=0..50. Contenido debe estar arriba de FOOTER_TOP=60."""
    c.saveState()
    c.setStrokeColor(COLOR_GRIS_LINEA)
    c.setLineWidth(0.4)
    c.line(MARGIN, 52, PAGE_W - MARGIN, 52)

    c.setFont(SERIF_ITAL, 8)
    c.setFillColor(COLOR_MARRON)
    c.drawString(MARGIN, 36, "yolitia.bio")

    c.setFont(SERIF_REG, 8)
    c.setFillColor(COLOR_MARRON)
    c.drawCentredString(PAGE_W / 2, 36, f"{page_num:02d}")

    c.setFont(SANS_REG, 6.5)
    c.setFillColor(COLOR_MARRON)
    c.drawRightString(PAGE_W - MARGIN, 36, "COLECCIÓN VERANO  ·  2026")

    c.restoreState()


# ============================================================================
# PÁGINAS ESPECIALES
# ============================================================================

def build_cover(c):
    print("  Portada...")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.55)

    # Logo arriba centrado (cerca del top)
    draw_isotipo_hoja(c, PAGE_W / 2, 730, 60, color=COLOR_VERDE)

    # Nombre de marca
    c.setFont(SCRIPT_REG, 90)
    c.setFillColor(COLOR_MORADO)
    text = "Yolitia"
    w = pdfmetrics.stringWidth(text, SCRIPT_REG, 90)
    c.drawString((PAGE_W - w) / 2, 650, text)

    # Subtítulo
    c.setFont(SANS_REG, 13)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    sub = "COLECCIÓN  ·  VERANO  ·  2026"
    w = pdfmetrics.stringWidth(sub, SANS_REG, 13)
    c.drawString((PAGE_W - w) / 2, 612, sub)

    # Línea divisoria
    draw_thin_line(c, PAGE_W / 2 - 70, 590, PAGE_W / 2 + 70, 590,
                   color=COLOR_NEGRO, width=0.7)

    # "CATÁLOGO"
    c.setFont(SCRIPT_REG, 26)
    c.setFillColor(COLOR_NEGRO)
    cat = "CATÁLOGO"
    w = pdfmetrics.stringWidth(cat, SCRIPT_REG, 26)
    c.drawString((PAGE_W - w) / 2, 555, cat)

    # Tagline italic
    c.setFont(SERIF_ITAL, 14)
    c.setFillColor(COLOR_MARRON)
    line1 = "Diseño consciente"
    line2 = "Impreso aquí · Hecho para durar"
    w1 = pdfmetrics.stringWidth(line1, SERIF_ITAL, 14)
    w2 = pdfmetrics.stringWidth(line2, SERIF_ITAL, 14)
    c.drawString((PAGE_W - w1) / 2, 200, line1)
    c.drawString((PAGE_W - w2) / 2, 180, line2)

    # Washtape al pie
    draw_washi_tape(c, PAGE_W / 2 - 110, 130, 220, 18, angle=-3)

    c.showPage()


def build_index(c, layout):
    print("  Índice...")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.3)

    draw_minimal_header(c)

    # "Contenido" debajo del header
    c.setFont(SCRIPT_REG, 28)
    c.setFillColor(COLOR_MORADO)
    c.drawCentredString(PAGE_W / 2, 705, "Contenido")

    draw_thin_line(c, PAGE_W / 2 - 50, 692, PAGE_W / 2 + 50, 692,
                   color=COLOR_NEGRO, width=0.6)

    y = 655
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
    # Bug fix: en coords reportlab (y crece hacia arriba), el polaroid va de y a y+ph.
    # La etiqueta debe estar DEBAJO del polaroid: su top debe ser MENOR que polaroid bot.
    # Formula correcta: label_y = y - 8 - label_h (8pt de gap entre polaroid bot y etiqueta top).
    label_w = w * 0.95
    label_h = 80
    label_x = x + (w - label_w) / 2
    label_y = y - 8 - label_h

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
    """Pagina de landmarks en portrait: 1 o 2 lugares apilados.
    HEADER_BOTTOM=750, FOOTER_TOP=60. Area util: 690pt.
    """
    print(f"  Lugares del Mundo (pág {page_num}) — {len(landmark_ids)} lugares")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.32)

    draw_minimal_header(c)

    # Subtitulo debajo del header
    # Header termina en y=750 (linea). Dejamos 20pt de gap, subtitulo en y=730.
    c.setFont(SCRIPT_REG, 22)
    c.setFillColor(COLOR_MORADO)
    c.drawCentredString(PAGE_W / 2, 715, "Lugares del Mundo")

    c.setFont(SANS_REG, 8.5)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    c.drawCentredString(PAGE_W / 2, 695, "MINIATURAS ARQUITECTONICAS  ·  EDICION LIMITADA")

    draw_thin_line(c, PAGE_W / 2 - 80, 680, PAGE_W / 2 + 80, 680,
                   color=COLOR_NEGRO, width=0.5)

    overrides = load_overrides()
    landscape_colors = overrides.get("landmarks_terrain_only", {})

    n = len(landmark_ids)
    col_w = 280
    label_h = 50
    gap_polaroid_label = 8
    inter_landmark_gap = 30

    if n == 1:
        # 1 landmark centrado. polaroid + etiqueta = polaroid_h + label_h + gap
        # Disponible: 680 (linea) - 60 (footer) = 620pt
        # polaroid_h = 400, label_h = 50, gap = 8 -> 458. Margen 81+81.
        polaroid_h = 400
        # polaroid top y = 670 - polaroid_h = 270. Etiqueta bot = 270 - 8 - 50 = 212.
        # polaroid bot y = 270. Etiqueta top y = 212, bot = 262.
        # Margen arriba: 670-270 = 400... no, polaroid bot = 270.
        # polaroid top = 270+400=670, bot = 270. Header termino 750. Gap polaroid-header = 750-670=80.
        p1_y = 270
        l1_y = p1_y - gap_polaroid_label - label_h
        positions = [(PAGE_W / 2 - col_w / 2, p1_y)]
        label_positions = [l1_y]
    elif n == 2:
        # 2 landmarks apilados. Cada uno = polaroid + etiqueta + 2 gaps.
        # Area util: 680 (linea) - 60 (footer) = 620pt
        # 2 bloques * (polaroid + label) + 1 gap entre bloques = 620
        # 2 * (polaroid_h + 50) + 30 = 620
        # 2*polaroid_h + 130 = 620
        # polaroid_h = 245
        polaroid_h = 220
        # Layout de arriba a abajo (coords reportlab, mayor y = mas arriba):
        # Polaroid 1 top = 670 (debajo de la linea 680 con margen 10)
        # Polaroid 1 bot = 670 - 220 = 450
        p1_y = 670 - polaroid_h  # 450
        # Etiqueta 1: 8pt debajo de polaroid 1 bot
        l1_y = p1_y - gap_polaroid_label - label_h  # 450-8-50 = 392
        # Gap entre etiqueta 1 bot y polaroid 2 top = 30pt
        # etiqueta 1 bot = 392+50 = 442
        # polaroid 2 top = 442 - 30 = 412
        # polaroid 2 bot = 412 - 220 = 192
        p2_y = (l1_y + label_h) - inter_landmark_gap - polaroid_h  # (392+50)-30-220 = 192
        l2_y = p2_y - gap_polaroid_label - label_h  # 192-8-50 = 134
        positions = [
            (PAGE_W / 2 - col_w / 2, p1_y),
            (PAGE_W / 2 - col_w / 2, p2_y),
        ]
        label_positions = [l1_y, l2_y]
    else:
        polaroid_h = 130
        positions = []
        label_positions = []
        gap = 15
        total_w = n * col_w + (n - 1) * gap
        start_x = (PAGE_W - total_w) / 2
        # n lado a lado: cada uno ocupa polaroid + label + gap_polaroid_label
        # Total vertical por landmark = 130 + 50 + 8 = 188
        # Disponemos 620pt
        # Como es horizontal, no se acumula vertical. Usar 1 sola fila.
        for i in range(n):
            positions.append((start_x + i * (col_w + gap), 500))  # polaroid bot y=500
            label_positions.append(500 - gap_polaroid_label - label_h)

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
            # fit_image_in_box usa contain (escala para que QUEPA). Para landmarks con
            # imagenes pequeñas, queremos que la imagen llene el area.
            # Cambio a "cover" para que ocupe todo el polaroid.
            fit_image_in_box_cover(c, img_path, box["x"], box["y"], box["w"], box["h"])

        # Etiqueta
        label_w_local = col_w
        label_x = px
        label_y = label_positions[i]

        draw_paper_label(c, label_x, label_y, label_w_local, label_h, rotation=0,
                         color=COLOR_CREMA, has_tape=False)

        c.saveState()
        c.translate(label_x + label_w_local / 2, label_y + label_h / 2)

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
            c.circle(-label_w_local / 2 + 16, 0, 5, stroke=1, fill=1)
            c.setFont(SANS_REG, 6)
            c.setFillColor(COLOR_NEGRO_SUAVE)
            c.drawString(-label_w_local / 2 + 24, -2, custom_color["primary"].upper())

        c.restoreState()

    # Nota al pie
    c.setFont(SERIF_ITAL, 8.5)
    c.setFillColor(COLOR_MARRON)
    c.drawCentredString(PAGE_W / 2, 75,
                        "Cada lugar se imprime en su propio color de terreno especial")
    c.setFont(SANS_REG, 7)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    c.drawCentredString(PAGE_W / 2, 60,
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

    # Subtitulo debajo del header
    c.setFont(SCRIPT_REG, 24)
    c.setFillColor(COLOR_MORADO)
    c.drawCentredString(PAGE_W / 2, 715, "Colores Disponibles")

    c.setFont(SANS_REG, 8.5)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    c.drawCentredString(PAGE_W / 2, 695, "TODOS NUESTROS MODELOS ESTAN DISPONIBLES EN LOS SIGUIENTES ACABADOS")

    draw_thin_line(c, PAGE_W / 2 - 80, 680, PAGE_W / 2 + 80, 680,
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
    """Separador de categoria. La etiqueta va debajo del header."""
    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.45)

    draw_minimal_header(c)

    # Etiqueta principal centrada. Area util HEADER_BOTTOM(750) - FOOTER_TOP(60) = 690
    # label_h = 480. Top y = 720 (debajo header con margen 30). Bot y = 720-480 = 240.
    # 240 > FOOTER_TOP(60)+margen(90) = 150. OK.
    label_w = 460
    label_h = 480
    label_x = (PAGE_W - label_w) / 2
    label_y = 720 - label_h  # 240 (etiqueta top, va de 240 a 720)

    draw_paper_label(c, label_x, label_y, label_w, label_h,
                     rotation=0, color=COLOR_CREMA, has_tape=True, tape_pos="top")

    draw_washi_tape(c, label_x + 30, label_y + label_h - 6, 80, 12, angle=-8)

    c.saveState()

    # Texto centrado dentro de la etiqueta
    cy = label_y + label_h / 2

    c.setFont(SCRIPT_REG, 42)
    c.setFillColor(COLOR_NEGRO)
    cat_text = categoria
    if pdfmetrics.stringWidth(cat_text, SCRIPT_REG, 42) > label_w - 40:
        c.setFont(SCRIPT_REG, 34)
    c.drawCentredString(PAGE_W / 2, cy + 110, cat_text)

    draw_thin_line(c, PAGE_W / 2 - 50, cy + 75, PAGE_W / 2 + 50, cy + 75,
                   color=COLOR_NEGRO, width=0.6)

    c.setFont(SANS_REG, 12)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    sub = "Coleccion Regenerativa"
    c.drawCentredString(PAGE_W / 2, cy + 45, sub)

    c.setFont(SERIF_ITAL, 13)
    c.setFillColor(COLOR_MARRON)
    c.drawCentredString(PAGE_W / 2, cy - 40, "Diseno consciente · Impreso aqui")

    draw_isotipo_hoja(c, PAGE_W / 2, cy - 130, 26, color=COLOR_VERDE)

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

    # Polaroid centrado. Area util: HEADER_BOTTOM(750) - FOOTER_TOP(60) = 690.
    # 2 secciones: polaroid arriba + info label abajo.
    # Polaroid: 280pt de alto, info label: 200pt, gap 30pt, margen 60+60.
    # Total: 280+200+30+60+60 = 630. OK.
    pw, ph = 300, 280
    # Polaroid bot y: HEADER_BOTTOM - 30 (margen) = 720
    # Polaroid top y: 720 + ph = 1000 (fuera!). Hay que usar polaroid bot menor.
    # En realidad, ph=280, entonces polaroid top = polaroid bot + 280.
    # Si polaroid bot = 720, top = 1000. Necesito polaroid bot menor.
    # 750 (header bottom) - 280 (ph) = 470. Polaroid bot = 470. Top = 470+280=750. Justo.
    pw, ph = 300, 260
    py = HEADER_BOTTOM - 30 - ph  # 750-30-260 = 460
    # Polaroid: bot 460, top 720. Gap con header: 30pt.
    px = (PAGE_W - pw) / 2

    draw_product_card_scrapbook(c, px, py, pw, ph, prod, img_path,
                                 rot_photo=0, rot_label=0, max_desc_lines=4)

    # Info label centrado abajo (ancho completo)
    info_w = PAGE_W - 2 * MARGIN
    info_h = 200
    info_x = MARGIN
    info_y = FOOTER_TOP + 30  # 90

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
    sub_es = prod.get('subcategoria', '')
    dy = text_y - 25
    c.drawString(col2_x, dy, f"SKU: {sku}")
    cat_text = f"Categoria: {cat_es}"
    if sub_es:
        cat_text += f" / {sub_es}"
    # Wrap de la linea de categoria si es muy larga
    cat_lines = []
    if pdfmetrics.stringWidth(cat_text, SERIF_ITAL, 9) > 145:
        # Partir por subcategoria en su propia linea
        c.drawString(col2_x, dy - 15, f"Categoria: {cat_es}")
        if sub_es:
            c.drawString(col2_x, dy - 28, f"Tipo: {sub_es}")
            c.drawString(col2_x, dy - 41, f"Material: {prod.get('material', 'PLA')}")
        else:
            c.drawString(col2_x, dy - 28, f"Material: {prod.get('material', 'PLA')}")
    else:
        c.drawString(col2_x, dy - 15, cat_text)
        c.drawString(col2_x, dy - 30, f"Material: {prod.get('material', 'PLA')}")

    # Columna 3: Descripcion corta
    c.setFont(SANS_BOLD, 10)
    c.setFillColor(COLOR_MORADO)
    c.drawString(col3_x - 110, text_y, "NOTAS")
    c.setFont(SERIF_ITAL, 8.5)
    c.setFillColor(COLOR_MARRON)
    desc = prod["_display_desc"]
    # Wrap simple
    words = desc.split()
    lines = []
    current_line = ""
    max_w = 115
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
        c.drawString(col3_x - 110, ly, line)
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

    pw, ph = 200, 280
    n = min(len(elementos), 2)

    gap = (PAGE_W - n * pw) / (n + 1)
    # polaroid bot y = HEADER_BOTTOM - 30 = 720
    top_y = HEADER_BOTTOM - 30 - ph  # 720-280 = 440

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
    """Portrait: 2 productos apilados verticalmente.

    En coords reportlab (y crece hacia arriba):
    HEADER_BOTTOM=750, FOOTER_TOP=60.
    Polaroid va de y hasta y+ph. Etiqueta se calcula automaticamente por
    draw_product_card_scrapbook (8pt debajo del polaroid).
    """
    print(f"  Grid 1x2: {len(elementos)} productos (pág {page_num})")

    c.setFillColor(COLOR_MARFIL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_background_curves(c, color=COLOR_GRIS_LINEA, opacity=0.3)

    draw_minimal_header(c)

    pw = 320
    ph = 220

    # Layout: 2 bloques (polaroid + etiqueta 80pt = 300pt por bloque)
    # + 1 gap entre bloques = 30pt
    # Total: 2*300 + 30 = 630pt
    # Disponible: HEADER_BOTTOM(750) - FOOTER_TOP(60) = 690pt
    # Margen: 60pt (30 arriba, 30 abajo)

    # Bloque 1 (arriba): polaroid top y = HEADER_BOTTOM - 30 = 720
    # polaroid bot y = 720 - ph = 500
    p1_y = HEADER_BOTTOM - 30 - ph  # 500
    # Bloque 2 (abajo): polaroid top y = FOOTER_TOP + 30 + label_h + 30 = 200
    # polaroid bot y = 200 - ph = -20 (fuera!)
    # Ajusto: polaroid 2 bot = FOOTER_TOP + 30 + label_h = 170
    p2_y = FOOTER_TOP + 30 + 80  # 170
    # Si p2_y < p1_y - ph - 80 (etiqueta 1) - 30 (gap), se solapan
    # p1_y - ph = 280 (polaroid 1 top). Necesito polaroid 2 top > 280 + 80 + 30 = 390
    # p2_y = 170 < 390. MAL.
    # Reduzco ph.
    ph = 180
    p1_y = HEADER_BOTTOM - 30 - ph  # 540
    p2_y = FOOTER_TOP + 30 + 80  # 170
    # p1 top = 720, p1 bot = 540, p2 top = 350, p2 bot = 170
    # Etiqueta 1 top = 540-8-80 = 452, bot = 532. Gap polaroid1_bot-eta1_top = 540-532=8
    # Etiqueta 2 top = 170-8-80 = 82, bot = 162. Gap polaroid2_bot-eta2_top = 170-162=8
    # Gap entre etiqueta1 bot (532) y polaroid2 top (350): NO, polaroid2 top = 350, etiqueta1 bot = 532
    # Solapamiento: 532-350 = 182pt

    # CALCULO CORRECTO:
    # area_total = HEADER_BOTTOM - FOOTER_TOP - 2*gap_bloque_extremo = 750 - 60 - 60 = 630
    # 2 bloques de 300pt (polaroid+etiqueta+gap_interno) = 600pt
    # gap entre bloques = 30pt
    # Total = 630pt. EXACTO.

    # Coordenadas:
    # bloque 1 (top): polaroid_top y = HEADER_BOTTOM - margen_top = 720
    #   polaroid bot y = 720 - 180 = 540
    #   etiqueta top y = polaroid_bot - gap_polaroid_etiqueta - label_h = 540 - 8 - 80 = 452
    #   etiqueta bot y = 532
    # gap entre bloques = 30
    # bloque 2 (bot): etiqueta1 bot (532) + 30 (gap) = 562
    #   polaroid top y = etiqueta2 bot + gap_polaroid_etiqueta = ?
    # Voy de abajo hacia arriba:
    #   etiqueta 2 bot y = FOOTER_TOP + margen_bot = 90
    #   etiqueta 2 top y = 90 - 80 = 10
    #   polaroid 2 bot y = 10 + gap(8) = 18
    #   polaroid 2 top y = 18 + 180 = 198
    #   etiqueta 1 bot y = polaroid 2 top - 30 (gap bloques) = 168
    #   etiqueta 1 top y = 168 - 80 = 88
    #   polaroid 1 bot y = 88 - 8 (gap_polaroid_etiqueta) = 80
    #   polaroid 1 top y = 80 + 180 = 260
    # Demasiado bajo. ph=180 es mucho.

    # Recalculo con ph=160:
    # bloque 1: polaroid top = 720, bot = 560
    #   etiqueta top = 560-8-80 = 472, bot = 552
    # gap = 30
    # bloque 2: polaroid top = ?, bot = ?
    #   etiqueta bot = 552 - 30 = 522... espera, etiqueta1 bot esta ARRIBA de polaroid2 top
    #   El orden visual de arriba a abajo:
    #     polaroid 1 (top), gap, etiqueta 1, gap, polaroid 2, gap, etiqueta 2
    #   En coords reportlab (mayor y = mas arriba):
    #     polaroid_1_top > polaroid_1_bot > ... > polaroid_2_bot

    # Simplifico: layout vertical, 2 bloques
    # Cada bloque = polaroid (ph) + etiqueta (80) + gap_interno (8) = ph + 88
    # Gap entre bloques: 20
    # Total: 2*(ph+88) + 20 = 2*ph + 196
    # 2*ph + 196 = 690 - 60 (margenes) = 630
    # 2*ph = 434, ph = 217
    ph = 200  # un poco menos para tener margen

    # polaroid 1: top y = HEADER_BOTTOM - 30 = 720, bot y = 720-200 = 520
    p1_y = 720 - 200  # 520
    # etiqueta 1: top y = 520 - 8 - 80 = 432, bot y = 512
    # gap 20 entre etiqueta 1 bot (512) y polaroid 2 top
    # polaroid 2: top y = 512 - 20 = 492, bot y = 492-200 = 292
    p2_y = 492 - 200  # 292
    # etiqueta 2: top y = 292 - 8 - 80 = 204, bot y = 284
    # Verificar: etiqueta 2 bot (284) > FOOTER_TOP (60) + 30 margen = 90. OK.

    positions = [
        ((PAGE_W - pw) / 2, p1_y, -0.3, 0.2, 3),
        ((PAGE_W - pw) / 2, p2_y, 0.3, -0.2, -3),
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

    pw, ph = 340, 360
    n = min(len(elementos), 1)  # Solo 1 por pagina en portrait

    polaroid_x = (PAGE_W - pw) / 2
    polaroid_y = HEADER_BOTTOM - 30 - ph  # 750-30-360 = 360

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

    # Etiqueta principal. Area util HEADER_BOTTOM(750) - FOOTER_TOP(60) = 690
    # Margenes: 30 arriba, 30 abajo. label_h = 630.
    label_w = PAGE_W - 2 * MARGIN
    label_h = 630
    label_x = MARGIN
    label_y = HEADER_BOTTOM - 30 - label_h  # 750-30-630 = 90

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
    c.drawCentredString(PAGE_W / 2, 715, "Nuestro Compromiso")

    c.setFont(SANS_REG, 11)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    c.drawCentredString(PAGE_W / 2, 695, "CONTIGO Y CON EL PLANETA")

    draw_thin_line(c, PAGE_W / 2 - 50, 680, PAGE_W / 2 + 50, 680,
                   color=COLOR_NEGRO, width=0.5)

    # Box 1 - 10% conservacion (arriba)
    # Area: header_bottom(750) - 30 - titulo(40) = 680
    # Box 1: top y = 660, bot y = 460 (h=200)
    box1_x = MARGIN + 10
    box1_y = 460
    box1_w = PAGE_W - 2 * (MARGIN + 10)
    box1_h = 200

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

    # Box 2 - redes (abajo)
    # Box 1 bot = 460. Gap 30. Box 2 top = 430. Box 2 bot = 230.
    box2_x = MARGIN + 20
    box2_y = 230
    box2_w = PAGE_W - 2 * (MARGIN + 20)
    box2_h = 200

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
    draw_isotipo_hoja(c, PAGE_W / 2, 720, 50, color=COLOR_VERDE)

    c.setFont(SCRIPT_REG, 64)
    c.setFillColor(COLOR_MORADO)
    w = pdfmetrics.stringWidth("Yolitia", SCRIPT_REG, 64)
    c.drawString((PAGE_W - w) / 2, 645, "Yolitia")

    c.setFont(SANS_REG, 12)
    c.setFillColor(COLOR_NEGRO_SUAVE)
    sub = "UN PROYECTO CIRCULAR"
    w = pdfmetrics.stringWidth(sub, SANS_REG, 12)
    c.drawString((PAGE_W - w) / 2, 615, sub)

    # Manifesto ocupa casi toda la pagina
    label_w = PAGE_W - 2 * MARGIN
    label_h = 480
    label_x = MARGIN
    label_y = 500 - label_h  # 20 (etiqueta top), bot=500

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

    draw_footer(c, 0)
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
