"""
Normaliza el logo YOLITIA a RGBA con fondo transparente.
Toma la versión original (paleta o con fondo blanco) y produce:
  - assets/images/logo.png  (RGBA, fondo transparente, máximo 1024px)
  - assets/images/logo_dark.png  (RGBA, versión en color morado para fondos claros)
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).parent.parent
SRC = ROOT.parent / "yolitia corazonblanco.png"
OUT_DIR = ROOT / "assets" / "images"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_rgba(path: Path) -> Image.Image:
    im = Image.open(path)
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    return im


def trim_transparent(im: Image.Image, padding: int = 32) -> Image.Image:
    bbox = im.getbbox()
    if not bbox:
        return im
    left, upper, right, lower = bbox
    w, h = im.size
    left = max(0, left - padding)
    upper = max(0, upper - padding)
    right = min(w, right + padding)
    lower = min(h, lower + padding)
    return im.crop((left, upper, right, lower))


def recolor_white_to(im: Image.Image, target=(74, 68, 88, 255)) -> Image.Image:
    """Reemplaza pixels blancos (o casi blancos) por un color sólido con alpha total."""
    px = im.load()
    w, h = im.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    opx = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 10:
                continue
            if r > 220 and g > 220 and b > 220:
                opx[x, y] = target
            elif a > 0:
                opx[x, y] = (r, g, b, a)
    return out


def main() -> None:
    im = load_rgba(SRC)
    im = trim_transparent(im, padding=24)
    im = recolor_white_to(im, target=(74, 68, 88, 255))

    if max(im.size) > 1024:
        ratio = 1024 / max(im.size)
        im = im.resize((int(im.size[0] * ratio), int(im.size[1] * ratio)), Image.LANCZOS)

    out_logo = OUT_DIR / "logo.png"
    im.save(out_logo, format="PNG", optimize=True)
    print(f"OK -> {out_logo}  size={im.size}")

    out_white = ROOT / "assets" / "images" / "logo_white.png"
    white_im = recolor_white_to(load_rgba(SRC), target=(255, 255, 255, 255))
    white_im = trim_transparent(white_im, padding=24)
    if max(white_im.size) > 1024:
        ratio = 1024 / max(white_im.size)
        white_im = white_im.resize((int(white_im.size[0] * ratio), int(white_im.size[1] * ratio)), Image.LANCZOS)
    white_im.save(out_white, format="PNG", optimize=True)
    print(f"OK -> {out_white}  size={white_im.size}")


if __name__ == "__main__":
    main()
