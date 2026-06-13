"""
Genera la tarjeta YOLITIA con QR para el catálogo en línea.

Produce en output/:
  - yolitia_qr_card.pdf    Tarjeta A6 vertical (lista para imprimir)
  - yolitia_qr_card.png    Vista previa de la tarjeta (Pillow)
  - yolitia_qr.png         Solo el QR (alta resolución)

El QR apunta a CATALOG_URL (por defecto https://catalogo.yolitia.bio),
un subdominio estático (GitHub Pages) que descarga el PDF
catalogo-yolitia.pdf. El nombre del archivo PDF es estable, así que
el QR nunca cambia aunque actualices el catálogo.
"""
from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont
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

COLOR_MARFIL_CLARO = (250, 247, 239)
COLOR_NEGRO = (26, 22, 20)
COLOR_MORADO = (74, 68, 88)
COLOR_MARRON = (90, 74, 58)
COLOR_KRAFT = (217, 203, 168)
COLOR_LINEA = (201, 191, 169)

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


def _script_font(size: int) -> ImageFont.FreeTypeFont:
    for f in [WIN_FONTS / "PRISTINA.TTF", WIN_FONTS / "LCALLIG.TTF"]:
        if f.exists():
            return ImageFont.truetype(str(f), size)
    return _font(size, bold=True)


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


def build_card_png(url: str, size_px: int = 1400) -> Image.Image:
    w = int(size_px * 0.7)
    h = size_px
    img = Image.new("RGBA", (w, h), COLOR_MARFIL_CLARO + (255,))
    draw = ImageDraw.Draw(img)

    border = max(1, int(w * 0.005))
    draw.rectangle([border, border, w - border, h - border], outline=COLOR_KRAFT, width=2)

    cx = w / 2
    pad = int(w * 0.10)

    logo_path = ASSETS_DIR / "logo.png"
    if logo_path.exists():
        logo = Image.open(logo_path).convert("RGBA")
        logo_h = int(h * 0.13)
        logo_w = int(logo.size[0] * (logo_h / logo.size[1]))
        logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
        img.alpha_composite(logo, ((w - logo_w) // 2, pad))

    brand_font = _script_font(int(w * 0.090))
    brand_y = pad + int(h * 0.20)
    draw.text((cx, brand_y), "YOLITIA", font=brand_font, fill=COLOR_NEGRO, anchor="mm")

    tag_font = _font(int(w * 0.030))
    draw.text(
        (cx, brand_y + int(h * 0.055)),
        "— CATÁLOGO EN LÍNEA —",
        font=tag_font,
        fill=COLOR_MARRON,
        anchor="mm",
    )

    qr_size = int(min(w, h) * 0.46)
    qr_img = build_qr_png(url, size_px=qr_size * 2)
    qr_x = (w - qr_size) // 2
    qr_y_top = brand_y + int(h * 0.12)
    img.alpha_composite(qr_img.resize((qr_size, qr_size), Image.LANCZOS), (qr_x, qr_y_top))

    sep_y = qr_y_top + qr_size + int(h * 0.05)
    draw.line(
        [(pad + int(w * 0.10), sep_y), (w - pad - int(w * 0.10), sep_y)],
        fill=COLOR_LINEA,
        width=2,
    )

    line1_font = _script_font(int(w * 0.045))
    draw.text(
        (cx, sep_y + int(h * 0.05)),
        "Escanéame para",
        font=line1_font,
        fill=COLOR_NEGRO,
        anchor="mm",
    )
    draw.text(
        (cx, sep_y + int(h * 0.095)),
        "descargar el catálogo",
        font=line1_font,
        fill=COLOR_NEGRO,
        anchor="mm",
    )

    url_font = _font(int(w * 0.024))
    draw.text(
        (cx, h - pad + int(h * 0.02)),
        url,
        font=url_font,
        fill=COLOR_MARRON,
        anchor="mm",
    )
    return img


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
    script, sans, _ = register_fonts()
    page_w, page_h = A6
    c = canvas.Canvas(str(out_path), pagesize=A6)
    c.setTitle("YOLITIA · Catálogo en línea")
    c.setAuthor("YOLITIA")
    c.setSubject("Tarjeta con QR para descarga del catálogo")

    c.setFillColorRGB(*_rgb(COLOR_MARFIL_CLARO))
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)
    c.setStrokeColorRGB(*_rgb(COLOR_KRAFT))
    c.setLineWidth(0.6)
    c.rect(4, 4, page_w - 8, page_h - 8, fill=0, stroke=1)

    margin = 10 * mm
    cx = page_w / 2

    logo_path = ASSETS_DIR / "logo.png"
    if logo_path.exists():
        logo = Image.open(logo_path).convert("RGBA")
        logo_h = 16 * mm
        logo_w = logo.size[0] * (logo_h / logo.size[1])
        logo_tmp = _write_temp(logo, "logo.png")
        try:
            c.drawImage(str(logo_tmp), cx - logo_w / 2, page_h - margin - logo_h, width=logo_w, height=logo_h, mask="auto")
        finally:
            logo_tmp.unlink(missing_ok=True)

    c.setFillColorRGB(*_rgb(COLOR_NEGRO))
    c.setFont(script, 26)
    c.drawCentredString(cx, page_h - margin - 22 * mm, "YOLITIA")

    c.setFillColorRGB(*_rgb(COLOR_MARRON))
    c.setFont(sans, 7)
    c.drawCentredString(cx, page_h - margin - 27 * mm, "—  C A T Á L O G O   E N   L Í N E A  —")

    qr_size = 55 * mm
    qr_img = build_qr_png(url, size_px=900)
    qr_tmp = _write_temp(qr_img, "qr.png")
    try:
        qr_x = (page_w - qr_size) / 2
        qr_y = page_h / 2 - 8 * mm
        c.drawImage(str(qr_tmp), qr_x, qr_y, width=qr_size, height=qr_size, mask="auto")
    finally:
        qr_tmp.unlink(missing_ok=True)

    c.setStrokeColorRGB(*_rgb(COLOR_LINEA))
    c.setLineWidth(0.4)
    line_y = qr_y - 4 * mm
    c.line(margin + 4 * mm, line_y, page_w - margin - 4 * mm, line_y)

    c.setFillColorRGB(*_rgb(COLOR_NEGRO))
    c.setFont(script, 12)
    c.drawCentredString(cx, line_y - 5 * mm, "Escanéame para")
    c.drawCentredString(cx, line_y - 9 * mm, "descargar el catálogo")

    c.setFillColorRGB(*_rgb(COLOR_MARRON))
    c.setFont(sans, 6.5)
    c.drawCentredString(cx, margin + 2, url)

    c.showPage()
    c.save()


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
