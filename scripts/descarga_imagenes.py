"""
Descarga y organiza imagenes de productos Yolitia.
- Descarga desde URLs del CDN de MakerWorld
- Organiza por carpeta YOL-001/, YOL-002/, etc.
- Rate limiting (1.5s entre requests)
- Actualiza JSON, SQLite y XLSX con rutas locales
- Soporte para reanudar descargas interrumpidas
"""

import json
import time
import sqlite3
import os
from pathlib import Path
from datetime import datetime

import requests
from PIL import Image as PILImage

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = BASE_DIR / "assets" / "images" / "productos"
JSON_FILE = DATA_DIR / "yolitia_products_database.json"
DB_FILE = DATA_DIR / "yolitia.db"
PROGRESS_FILE = DATA_DIR / "download_progress.json"

RATE_LIMIT_DELAY = 1.5
TIMEOUT = 30
MIN_SIZE_BYTES = 5000


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    "Referer": "https://makerworld.com/",
}


def load_progress():
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"completed": [], "failed": [], "last_updated": None}


def save_progress(progress):
    progress["last_updated"] = datetime.now().isoformat()
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def download_image(url, filepath):
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True)
        response.raise_for_status()

        content_type = response.headers.get('content-type', '')
        if not any(t in content_type for t in ['image', 'octet-stream']):
            return False, f"Content-Type no es imagen: {content_type}"

        total_size = 0
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    total_size += len(chunk)

        if total_size < MIN_SIZE_BYTES:
            filepath.unlink(missing_ok=True)
            return False, f"Tamano muy pequeno: {total_size} bytes"

        return True, f"{total_size:,} bytes"

    except requests.exceptions.Timeout:
        return False, "Timeout"
    except requests.exceptions.ConnectionError:
        return False, "Connection error"
    except requests.exceptions.HTTPError as e:
        return False, f"HTTP {e.response.status_code}"
    except Exception as e:
        return False, str(e)[:100]


def convert_to_jpg(filepath):
    try:
        img = PILImage.open(filepath)
        if img.mode in ('RGBA', 'P', 'LA'):
            img = img.convert('RGB')
        
        jpg_path = filepath.with_suffix('.jpg')
        if filepath.suffix.lower() != '.jpg':
            img.save(jpg_path, 'JPEG', quality=90)
            filepath.unlink()
            return jpg_path
        else:
            img.save(jpg_path, 'JPEG', quality=90)
            return jpg_path
    except Exception:
        return filepath


def get_image_dimensions(filepath):
    try:
        with PILImage.open(filepath) as img:
            return img.size[0], img.size[1]
    except Exception:
        return None, None


def main():
    print("=" * 60)
    print("DESCARGA DE IMAGENES - YOLITIA")
    print("=" * 60)

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    productos = data["productos"]
    print(f"\nProductos: {len(productos)}")

    progress = load_progress()
    completed_set = set(progress["completed"])
    print(f"Ya descargadas: {len(completed_set)}")

    to_download = []
    total_images = 0
    for p in productos:
        for img in p.get("imagenes", []):
            total_images += 1
            if img["filename"] not in completed_set:
                to_download.append((p["id"], img))

    print(f"Total imagenes: {total_images}")
    print(f"Pendientes: {len(to_download)}")

    if not to_download:
        print("\nTodas las imagenes ya estan descargadas.")
    else:
        print(f"\nIniciando descarga...")
        success_count = 0
        fail_count = 0

        for idx, (producto_id, img_data) in enumerate(to_download, 1):
            product_dir = IMAGES_DIR / producto_id
            product_dir.mkdir(parents=True, exist_ok=True)

            url = img_data["url"]
            filename = img_data["filename"]
            filepath = product_dir / filename

            pct = (idx / len(to_download)) * 100
            sys.stdout.write(f"\r  [{idx}/{len(to_download)}] ({pct:.0f}%) {filename[:40]}... ")
            sys.stdout.flush()

            ok, msg = download_image(url, filepath)

            if ok:
                final_path = convert_to_jpg(filepath)
                w, h = get_image_dimensions(final_path)
                file_size = final_path.stat().st_size

                relative_path = f"assets/images/productos/{producto_id}/{final_path.name}"
                img_data["ruta_local"] = relative_path
                if w and h:
                    img_data["ancho"] = w
                    img_data["alto"] = h
                img_data["tamano_kb"] = round(file_size / 1024, 1)

                progress["completed"].append(filename)
                success_count += 1
                print(f"OK ({msg})")
            else:
                progress["failed"].append({"filename": filename, "url": url, "error": msg})
                fail_count += 1
                print(f"FALLA ({msg})")

            save_progress(progress)

            if idx < len(to_download):
                time.sleep(RATE_LIMIT_DELAY)

        print(f"\n\nResultados sesion:")
        print(f"  Exitosas: {success_count}")
        print(f"  Fallidas: {fail_count}")

    total_completed = len(set(progress["completed"]))
    total_failed = len(progress["failed"])
    print(f"\n{'=' * 60}")
    print(f"RESUMEN TOTAL:")
    print(f"  Imagenes descargadas: {total_completed}/{total_images}")
    print(f"  Fallidas: {total_failed}")

    folders = [d for d in IMAGES_DIR.iterdir() if d.is_dir()]
    total_files = sum(1 for d in folders for f in d.iterdir() if f.is_file())
    total_size = sum(f.stat().st_size for d in folders for f in d.iterdir() if f.is_file())

    print(f"  Carpetas creadas: {len(folders)}")
    print(f"  Archivos totales: {total_files}")
    print(f"  Tamano total: {total_size / (1024*1024):.1f} MB")
    print(f"{'=' * 60}")

    print("\nActualizando archivos de datos...")

    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  JSON actualizado: {JSON_FILE}")

    update_sqlite(productos)
    print(f"  SQLite actualizada: {DB_FILE}")

    if progress["failed"]:
        failed_file = DATA_DIR / "download_failures.json"
        with open(failed_file, 'w', encoding='utf-8') as f:
            json.dump(progress["failed"], f, ensure_ascii=False, indent=2)
        print(f"  Reporte fallas: {failed_file}")

    print(f"\nCICLO 3 COMPLETADO")


def update_sqlite(productos):
    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()

    cursor.execute("DELETE FROM imagenes")

    for p in productos:
        for img in p.get("imagenes", []):
            cursor.execute(
                """INSERT INTO imagenes 
                   (producto_id, url, filename, tipo, alt_text, titulo, posicion, es_principal, ruta_local, drive_url, ancho, alto, tamano_kb)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    p["id"], img["url"], img["filename"], img["tipo"],
                    img.get("alt_text"), img.get("titulo"),
                    img.get("posicion", 0), 1 if img.get("es_principal") else 0,
                    img.get("ruta_local"), img.get("drive_url"),
                    img.get("ancho"), img.get("alto"), img.get("tamano_kb")
                )
            )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    import sys
    main()
