"""
Reintenta descargar imagenes fallidas con URLs alternativas.
"""

import json
import re
import time
import requests
from pathlib import Path
from PIL import Image as PILImage

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = BASE_DIR / "assets" / "images" / "productos"
JSON_FILE = DATA_DIR / "yolitia_products_database.json"
DB_FILE = DATA_DIR / "yolitia.db"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://makerworld.com/",
    "Origin": "https://makerworld.com",
    "Sec-Fetch-Dest": "image",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "cross-site",
}


def try_download(url, filepath):
    try:
        response = requests.get(url, headers=HEADERS, timeout=30, stream=True)
        response.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        size = filepath.stat().st_size
        if size < 5000:
            filepath.unlink(missing_ok=True)
            return False, f"Too small: {size}"
        return True, f"{size:,} bytes"
    except Exception as e:
        return False, str(e)[:80]


def main():
    failures = json.load(open(DATA_DIR / "download_failures.json", 'r', encoding='utf-8'))
    data = json.load(open(JSON_FILE, 'r', encoding='utf-8'))
    productos = data["productos"]

    print(f"Reintentando {len(failures)} imagenes fallidas...")
    print()

    recovered = 0
    still_failed = 0

    for fail in failures:
        filename = fail["filename"]
        original_url = fail["url"]
        producto_id = filename.split("_")[0]

        product_dir = IMAGES_DIR / producto_id
        product_dir.mkdir(parents=True, exist_ok=True)
        filepath = product_dir / filename

        alt_url = re.sub(r'\?x-oss-process=.*$', '', original_url)

        print(f"  {filename}")
        print(f"    URL alt: {alt_url[:70]}...")

        ok, msg = try_download(alt_url, filepath)

        if ok:
            img = PILImage.open(filepath)
            if img.mode in ('RGBA', 'P', 'LA'):
                img = img.convert('RGB')
            jpg_path = filepath.with_suffix('.jpg')
            img.save(jpg_path, 'JPEG', quality=90)
            if filepath.suffix != '.jpg':
                filepath.unlink()
            final_path = jpg_path

            w, h = img.size
            file_size = final_path.stat().st_size
            relative_path = f"assets/images/productos/{producto_id}/{final_path.name}"

            for p in productos:
                if p["id"] == producto_id:
                    for img_data in p.get("imagenes", []):
                        if img_data["filename"] == filename:
                            img_data["ruta_local"] = relative_path
                            img_data["ancho"] = w
                            img_data["alto"] = h
                            img_data["tamano_kb"] = round(file_size / 1024, 1)

            recovered += 1
            print(f"    RECUPERADA ({msg})")
        else:
            still_failed += 1
            print(f"    FALLA: {msg}")

        time.sleep(2)

    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    import sqlite3
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

    print(f"\n{'=' * 60}")
    print(f"RESULTADO REINTENTO:")
    print(f"  Recuperadas: {recovered}")
    print(f"  Ainda fallidas: {still_failed}")
    print(f"  Total final: {150 + recovered}/158")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
