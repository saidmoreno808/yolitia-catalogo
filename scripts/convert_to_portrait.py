"""
Convierte un PDF apaisado (landscape) a formato vertical (portrait),
manteniendo el contenido original sin editar.

Cada pagina original se inserta escalada y centrada dentro de una pagina
A4 vertical, conservando la proporcion y la calidad vectorial del contenido.

Uso:
    python scripts/convert_to_portrait.py
"""
from __future__ import annotations

from pathlib import Path

import fitz

BASE_DIR = Path(__file__).parent.parent
INPUT_PDF = BASE_DIR / "output" / "catalogo_yolitia_v8.pdf"
OUTPUT_PDF = BASE_DIR / "output" / "catalogo_yolitia_vfinal.pdf"

# A4 en puntos (1 pulgada = 72 pts)
A4_WIDTH = 595.27
A4_HEIGHT = 841.89


def convert_landscape_to_portrait(
    src_path: Path,
    dst_path: Path,
) -> None:
    src_doc = fitz.open(str(src_path))
    dst_doc = fitz.open()

    for src_page in src_doc:
        src_rect = src_page.rect

        # Crear pagina destino en A4 vertical
        dst_page = dst_doc.new_page(width=A4_WIDTH, height=A4_HEIGHT)

        # Calcular escala para que el contenido landscape quepa en el ancho
        scale = A4_WIDTH / src_rect.width
        scaled_h = src_rect.height * scale

        # Centrar verticalmente dejando margen arriba y abajo
        y_offset = (A4_HEIGHT - scaled_h) / 2

        # Rectangulo destino donde se insertara la pagina original
        target_rect = fitz.Rect(
            0,
            y_offset,
            A4_WIDTH,
            y_offset + scaled_h,
        )

        # Insertar la pagina original escalada y centrada (conserva vectorial)
        dst_page.show_pdf_page(
            target_rect,
            src_doc,
            src_page.number,
            keep_proportion=True,
        )

    # Copiar metadatos y actualizar titulo
    metadata = src_doc.metadata
    metadata["title"] = "Catalogo Yolitia - Version Final (Vertical)"
    dst_doc.set_metadata(metadata)

    page_count = len(src_doc)
    dst_doc.save(str(dst_path), deflate=True, garbage=4)
    src_doc.close()
    dst_doc.close()

    print(f"OK: {dst_path}")
    print(f"    Paginas: {page_count}")
    print(f"    Orientacion: A4 vertical (portrait)")


if __name__ == "__main__":
    if not INPUT_PDF.exists():
        raise SystemExit(f"No existe el PDF fuente: {INPUT_PDF}")

    dst_path = OUTPUT_PDF
    convert_landscape_to_portrait(INPUT_PDF, dst_path)
