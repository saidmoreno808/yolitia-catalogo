"""
Genera la tarjeta YOLITIA con QR para el catálogo en línea.

Produce en output/:
  - yolitia_qr_card.pdf    Tarjeta A6 vertical (lista para imprimir)
  - yolitia_qr_card.png    Vista previa de la tarjeta (Pillow)
  - yolitia_qr.png         Solo el QR (alta resolución)

El QR apunta a CATALOG_URL (por defecto https://catalogo.yolitia.bio),
un subdominio estático (GitHub Pages) que descarga el PDF.
"""
from __future__ import annotations

import argparse
import math
from io import BytesIO
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from reportlab.lib.pagesizes import A6
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / "assets" / "images"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_URL = "https://catalogo.yolitia.bio"

# Paleta
COLOR_MARFIL_CLARO = (250, 247, 239)
COLOR_MARFIL       = (245, 240, 230)
COLOR_CREMA        = (232, 220, 196)
COLOR_KRAFT        = (217, 203, 168)
COLOR_KRAFT_OSC    = (180, 162, 128)
COLOR_LINEA        = (201, 191, 169)
COLOR_NEGRO        = (26, 22, 20)
COLOR_NEGRO_SUAVE  = (45, 38, 32)
COLOR_MORADO       = (74, 68, 88)
COLOR_MORADO_CLARO = (118, 110, 138)
COLOR_VERDE        = (92, 110, 84)
COLOR_MARRON       = (90, 74, 58)

WIN_FONTS = Path("C:/Windows/Fonts")


def _font(size: int, bold: bool = False, italic: bool = False) -> ImageFont.FreeTypeFont:
    candidates = []
    if bold:
        candidates += [WIN_FONTS / "calibrib.ttf", WIN_FONTS / "BOD_B.TTF"]
    elif italic:
        candidates += [WIN_FONTS / "BOD_I.TTF", WIN_FONTS / "BOD_R.TTF"]
    else:
        candidates += [WIN_FONTS / "calibri.ttf", WIN_FONTS / "BOD_R.TTF"]
    for f in candidates:
        if f.exists():
            return ImageFont.truetype(str(f), size)
    return ImageFont.load_default()


def _script_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    if bold:
        candidates = [WIN_FONTS / "PRISTINA.TTF", WIN_FONTS / "LCALLIG.TTF", WIN_FONTS / "BOD_B.TTF"]
    else:
        candidates = [WIN_FONTS / "PRISTINA.TTF", WIN_FONTS / "LCALLIG.TTF"]
    for f in candidates:
        if f.exists():
            return ImageFont.truetype(str(f), size)
    return _font(size, bold=bold)


def build_qr_png(url: str, size_px: int = 1024) -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1A1614", back_color="#FAF7EF").convert("RGBA")
    img = img.resize((size_px, size_px), Image.NEAREST)
    return img


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def build_card_png(url: str, size_px: int = 1800) -> Image.Image:
    """Tarjeta A6 vertical (relacion 1:1.414) con composicion rica."""
    # A6 portrait aspect: 105 x 148 mm
    w = int(size_px * (105 / 148))
    h = size_px
    img = Image.new("RGBA", (w, h), COLOR_MARFIL_CLARO + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # === Fondo con vignette sutil y manchas decorativas ===
    _paint_background_decor(draw, w, h)

    # === Marco decorativo exterior ===
    margin_outer = int(w * 0.04)
    draw.rectangle(
        [margin_outer, margin_outer, w - margin_outer, h - margin_outer],
        outline=COLOR_KRAFT_OSC, width=2,
    )
    margin_inner = margin_outer + int(w * 0.018)
    draw.rectangle(
        [margin_inner, margin_inner, w - margin_inner, h - margin_inner],
        outline=COLOR_LINEA, width=1,
    )

    # Esquinas decorativas (pétalos pequeños)
    for cx, cy, rot in [
        (margin_outer, margin_outer, 0),
        (w - margin_outer, margin_outer, 90),
        (w - margin_outer, h - margin_outer, 180),
        (margin_outer, h - margin_outer, 270),
    ]:
        _draw_corner_fleuron(draw, cx, cy, rot, COLOR_MORADO, int(w * 0.022))

    # === Banda superior con logo y nombre ===
    cx = w / 2
    top = margin_inner

    # Logo mas grande
    logo = Image.open(ASSETS_DIR / "logo.png").convert("RGBA")
    logo_h = int(h * 0.14)
    logo_w = int(logo.size[0] * (logo_h / logo.size[1]))
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
    logo_y = top + int(h * 0.025)
    img.alpha_composite(logo, ((w - logo_w) // 2, logo_y))

    # Nombre de marca
    brand_y = logo_y + logo_h + int(h * 0.035)
    brand_font = _script_font(int(w * 0.130), bold=True)
    draw.text((cx, brand_y), "YOLITIA", font=brand_font, fill=COLOR_NEGRO, anchor="mm")

    # Linea ornamental bajo el nombre
    orn_y = brand_y + int(h * 0.045)
    _draw_ornamental_line(draw, cx, orn_y, w * 0.45, COLOR_MORADO)

    # Subtitulo
    sub_font = _font(int(w * 0.032), bold=True)
    draw.text(
        (cx, orn_y + int(h * 0.030)),
        "CATÁLOGO EN LÍNEA",
        font=sub_font,
        fill=COLOR_MORADO,
        anchor="mm",
    )

    # === Marco del QR con esquinas acentuadas ===
    qr_size = int(min(w, h) * 0.46)
    qr_margin_x = (w - qr_size) // 2
    qr_margin_y = int(h * 0.41)
    qr_panel_pad = int(w * 0.025)
    qr_panel_rect = (
        qr_margin_x - qr_panel_pad,
        qr_margin_y - qr_panel_pad,
        qr_margin_x + qr_size + qr_panel_pad,
        qr_margin_y + qr_size + qr_panel_pad,
    )
    # Sombra suave del panel
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.rectangle(qr_panel_rect, fill=(0, 0, 0, 28))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    img.alpha_composite(shadow, (0, 4))
    # Panel
    draw.rectangle(qr_panel_rect, fill=COLOR_MARFIL, outline=COLOR_KRAFT_OSC, width=2)

    # Esquinas acentuadas del panel
    for x, y, dx, dy in [
        (qr_panel_rect[0], qr_panel_rect[1], 1, 1),
        (qr_panel_rect[2], qr_panel_rect[1], -1, 1),
        (qr_panel_rect[2], qr_panel_rect[3], -1, -1),
        (qr_panel_rect[0], qr_panel_rect[3], 1, -1),
    ]:
        L = int(w * 0.025)
        draw.line([(x, y), (x + dx * L, y)], fill=COLOR_MORADO, width=3)
        draw.line([(x, y), (x, y + dy * L)], fill=COLOR_MORADO, width=3)

    # QR
    qr_img = build_qr_png(url, size_px=qr_size * 2)
    qr_img = qr_img.resize((qr_size, qr_size), Image.LANCZOS)
    img.alpha_composite(qr_img, (qr_margin_x, qr_margin_y))

    # === Bloque de texto bajo el QR ===
    txt_y = qr_panel_rect[3] + int(h * 0.035)

    line1_font = _script_font(int(w * 0.055), bold=True)
    draw.text((cx, txt_y), "Escanéame para", font=line1_font, fill=COLOR_NEGRO, anchor="mm")
    draw.text(
        (cx, txt_y + int(h * 0.035)),
        "descargar el catálogo",
        font=line1_font,
        fill=COLOR_NEGRO,
        anchor="mm",
    )

    # Etiqueta "Edición 2026" con lineas a los lados
    badge_y = txt_y + int(h * 0.095)
    badge_font = _font(int(w * 0.022), bold=True)
    bw = int(w * 0.32)
    draw.line([(cx - bw, badge_y), (cx - int(w * 0.06), badge_y)], fill=COLOR_KRAFT_OSC, width=1)
    draw.line([(cx + int(w * 0.06), badge_y), (cx + bw, badge_y)], fill=COLOR_KRAFT_OSC, width=1)
    draw.text(
        (cx, badge_y - 1),
        "EDICIÓN 2026",
        font=badge_font,
        fill=COLOR_MARRON,
        anchor="mm",
    )

    # === Footer ===
    footer_y = h - margin_inner - int(h * 0.045)
    url_font = _font(int(w * 0.022))
    url_text = url
    url_bbox = draw.textbbox((0, 0), url_text, font=url_font)
    url_w = url_bbox[2] - url_bbox[0]
    url_cx = cx
    icon_size = int(w * 0.028)
    gap = int(w * 0.018)

    # Icono PDF a la izquierda de la URL
    pdf_x = url_cx - url_w // 2 - gap - icon_size // 2
    _draw_pdf_icon(draw, pdf_x, footer_y, icon_size, COLOR_MORADO, COLOR_MARFIL_CLARO)

    # Texto URL
    draw.text((url_cx, footer_y), url_text, font=url_font, fill=COLOR_MORADO, anchor="mm")

    # Icono link a la derecha
    link_x = url_cx + url_w // 2 + gap + icon_size // 2
    _draw_link_icon(draw, link_x, footer_y, icon_size, COLOR_MORADO)

    # Sellos decorativos pequeños (pie)
    seals_y = h - margin_inner - int(h * 0.090)
    seal_font = _font(int(w * 0.017), bold=True)
    for offset, label, mark in [
        (-int(w * 0.22), "PLA BIODEGRADABLE", "leaf"),
        (int(w * 0.22), "HECHO EN MÉXICO", "star"),
    ]:
        x = cx + offset
        # Marca pequeña
        if mark == "leaf":
            _draw_leaf_icon(draw, x - int(w * 0.085), seals_y, int(w * 0.018), COLOR_VERDE)
        else:
            _draw_star_icon(draw, x - int(w * 0.085), seals_y, int(w * 0.018), COLOR_VERDE)
        draw.text((x + int(w * 0.005), seals_y), label, font=seal_font, fill=COLOR_VERDE, anchor="lm")

    return img


def _paint_background_decor(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
    """Fondo: marfil solido + ruido sutil de papel + vignette muy tenue."""
    import random
    rng = random.Random(7)

    # Vignette muy tenue en los bordes
    edge = (180, 162, 128)
    edge_alpha = 14
    for x in range(0, w, 3):
        d = min(x, w - x) / w
        a = int(edge_alpha * (1 - d) ** 4)
        if a > 0:
            draw.line([(x, 0), (x, 4)], fill=(*edge, a))
            draw.line([(x, h - 4), (x, h)], fill=(*edge, a))
    for y in range(0, h, 3):
        d = min(y, h - y) / h
        a = int(edge_alpha * (1 - d) ** 4)
        if a > 0:
            draw.line([(0, y), (4, y)], fill=(*edge, a))
            draw.line([(w - 4, y), (w, y)], fill=(*edge, a))

    # Grano de papel (puntos finos)
    paper_color = (180, 162, 128)
    n = 500
    for _ in range(n):
        x = rng.randint(0, w)
        y = rng.randint(0, h)
        r = rng.choice([0, 0, 0, 0, 1, 1, 2])
        a = rng.randint(6, 16)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(*paper_color, a))

    # Fibras largas muy sutiles
    for _ in range(40):
        x1 = rng.randint(0, w)
        y1 = rng.randint(0, h)
        ang = rng.uniform(0, math.pi)
        ln = rng.randint(15, 50)
        x2 = x1 + math.cos(ang) * ln
        y2 = y1 + math.sin(ang) * ln
        draw.line([(x1, y1), (x2, y2)], fill=(*paper_color, rng.randint(6, 12)), width=1)


def _draw_ornamental_line(draw: ImageDraw.ImageDraw, cx: float, y: float, half_w: float, color) -> None:
    # Linea central
    draw.line([(cx - half_w, y), (cx + half_w, y)], fill=color, width=2)
    # Diamante al centro
    s = half_w * 0.045
    draw.polygon(
        [(cx, y - s), (cx + s, y), (cx, y + s), (cx - s, y)],
        fill=color,
    )
    # Pequeños circulos a los lados
    for sign in (-1, 1):
        x = cx + sign * half_w * 0.85
        draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=color)


def _draw_pdf_icon(draw: ImageDraw.ImageDraw, cx: float, cy: float, size: int, color, fill) -> None:
    """Mini icono de PDF (documento con esquina doblada y texto PDF)."""
    s = size
    fold = s * 0.28
    # Poligono del documento con esquina doblada
    pts = [
        (cx - s * 0.45, cy - s * 0.55),
        (cx + s * 0.45 - fold, cy - s * 0.55),
        (cx + s * 0.45, cy - s * 0.55 + fold),
        (cx + s * 0.45, cy + s * 0.55),
        (cx - s * 0.45, cy + s * 0.55),
    ]
    draw.polygon(pts, outline=color, fill=fill, width=2)
    # Linea diagonal de la esquina doblada
    draw.line(
        [(cx + s * 0.45 - fold, cy - s * 0.55), (cx + s * 0.45 - fold, cy - s * 0.55 + fold),
         (cx + s * 0.45, cy - s * 0.55 + fold)],
        fill=color, width=2,
    )
    # Texto PDF
    fnt = _font(int(s * 0.40), bold=True)
    draw.text((cx, cy + s * 0.12), "PDF", font=fnt, fill=color, anchor="mm")


def _draw_link_icon(draw: ImageDraw.ImageDraw, cx: float, cy: float, size: int, color) -> None:
    """Mini icono de enlace (dos eslabones)."""
    s = size
    r = s * 0.22
    # Anillo izquierdo
    draw.rounded_rectangle(
        [cx - s * 0.45, cy - r, cx - s * 0.05, cy + r],
        radius=r, outline=color, width=2,
    )
    # Anillo derecho
    draw.rounded_rectangle(
        [cx + s * 0.05, cy - r, cx + s * 0.45, cy + r],
        radius=r, outline=color, width=2,
    )


def _draw_leaf_icon(draw: ImageDraw.ImageDraw, cx: float, cy: float, size: int, color) -> None:
    """Mini icono de hoja (PLA biodegradable): forma de gota/hoja."""
    s = size
    # Gota/hoja apuntando arriba
    pts = [
        (cx, cy - s),
        (cx + s * 0.7, cy - s * 0.1),
        (cx + s * 0.4, cy + s * 0.7),
        (cx, cy + s * 0.85),
        (cx - s * 0.4, cy + s * 0.7),
        (cx - s * 0.7, cy - s * 0.1),
    ]
    draw.polygon(pts, fill=color)
    # Nervadura central
    draw.line([(cx, cy - s * 0.85), (cx, cy + s * 0.7)], fill=COLOR_MARFIL, width=1)


def _draw_star_icon(draw: ImageDraw.ImageDraw, cx: float, cy: float, size: int, color) -> None:
    """Estrella de 5 puntas."""
    s = size
    pts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        r = s if i % 2 == 0 else s * 0.42
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    draw.polygon(pts, fill=color)


def _draw_corner_fleuron(draw: ImageDraw.ImageDraw, x: float, y: float, angle_deg: float, color, size: int) -> None:
    """Pequeño ornamento en forma de pétalo/corazón en las esquinas."""
    s = size
    rad = math.radians(angle_deg)

    def rot(px: float, py: float) -> tuple[float, float]:
        return (x + px * math.cos(rad) - py * math.sin(rad), y + px * math.sin(rad) + py * math.cos(rad))

    # Tres pétalos formando un trebol pequeño
    petals = [
        [(0, 0), (s * 0.7, -s * 0.2), (s * 0.55, s * 0.4)],
        [(0, 0), (-s * 0.2, -s * 0.7), (s * 0.4, -s * 0.55)],
        [(0, 0), (-s * 0.7, s * 0.2), (-s * 0.4, s * 0.55)],
    ]
    for p in petals:
        pts = [rot(*pt) for pt in p]
        draw.polygon(pts, fill=color)
    # Centro
    c = rot(0, 0)
    draw.ellipse([c[0] - s * 0.12, c[1] - s * 0.12, c[0] + s * 0.12, c[1] + s * 0.12], fill=color)


def register_fonts() -> tuple[str, str, str]:
    try:
        pdfmetrics.registerFont(TTFont("YolitiaScript", str(WIN_FONTS / "PRISTINA.TTF")))
    except Exception:
        pdfmetrics.registerFont(TTFont("YolitiaScript", str(WIN_FONTS / "LCALLIG.TTF")))
    pdfmetrics.registerFont(TTFont("YolitiaSans", str(WIN_FONTS / "calibri.ttf")))
    pdfmetrics.registerFont(TTFont("YolitiaSansB", str(WIN_FONTS / "calibrib.ttf")))
    return "YolitiaScript", "YolitiaSans", "YolitiaSansB"


def _rgb(c: tuple[int, int, int]) -> tuple[float, float, float]:
    return (c[0] / 255, c[1] / 255, c[2] / 255)


def _write_temp(img: Image.Image, name: str) -> Path:
    tmp = OUTPUT_DIR / f".__tmp_{name}"
    img.save(tmp, format="PNG")
    return tmp


def build_card_pdf(url: str, out_path: Path) -> None:
    """Renderiza la tarjeta como PDF A6 vectorial a partir de la PNG en alta resolución."""
    card = build_card_png(url, size_px=2400)
    tmp = _write_temp(card, "card.png")
    try:
        page_w, page_h = A6
        c = canvas.Canvas(str(out_path), pagesize=A6)
        c.setTitle("YOLITIA · Catálogo en línea")
        c.setAuthor("YOLITIA")
        c.setSubject("Tarjeta con QR para descarga del catálogo")
        c.drawImage(str(tmp), 0, 0, width=page_w, height=page_h, mask="auto")
        c.showPage()
        c.save()
    finally:
        tmp.unlink(missing_ok=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=DEFAULT_URL)
    args = ap.parse_args()

    url = args.url
    print(f"URL: {url}")

    qr_png = OUTPUT_DIR / "yolitia_qr.png"
    build_qr_png(url, size_px=1024).save(qr_png, format="PNG", optimize=True)
    print(f"OK -> {qr_png}")

    card_pdf = OUTPUT_DIR / "yolitia_qr_card.pdf"
    build_card_pdf(url, card_pdf)
    print(f"OK -> {card_pdf}")

    card_png = OUTPUT_DIR / "yolitia_qr_card.png"
    build_card_png(url, size_px=1400).save(card_png, format="PNG", optimize=True)
    print(f"OK -> {card_png}")


if __name__ == "__main__":
    main()
