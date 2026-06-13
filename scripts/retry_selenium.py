"""
Obtiene URLs frescas para las 8 imagenes fallidas usando Selenium.
"""

import json
import re
import time
import requests
from pathlib import Path
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from PIL import Image as PILImage


BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = BASE_DIR / "assets" / "images" / "productos"
JSON_FILE = DATA_DIR / "yolitia_products_database.json"
DB_FILE = DATA_DIR / "yolitia.db"

FAILED_IDS = {
    "YOL-001": "617061-fender-stratocaster-key-hanger-guitar-key-holder",
    "YOL-048": "1132655-spray-paint-can-fidget",
    "YOL-063": "467451-print-in-place-fidget-toggle-switch",
    "YOL-064": "1496019-customizable-baseball-bat",
    "YOL-103": "1864468-mini-baseball-glove-keychain",
    "YOL-115": "1276383-plyometric-box-storage-crossfit",
    "YOL-117": "1492864-ultimate-koozie-v2",
    "YOL-130": "1352373-gym-bro-kettlebell-keychain",
}


def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


def wait_for_cloudflare(driver, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            challenge = driver.find_elements(By.ID, "challenge-running")
            if not challenge:
                time.sleep(2)
                return True
        except:
            pass
        time.sleep(1)
    return False


def get_fresh_thumbnail(driver, model_slug):
    url = f"https://makerworld.com/es/models/{model_slug}"
    driver.get(url)
    wait_for_cloudflare(driver, timeout=20)
    time.sleep(2)

    script = """
    const imgs = document.querySelectorAll('img');
    const results = [];
    imgs.forEach(img => {
        const src = img.getAttribute('src') || img.getAttribute('data-src');
        if (src && src.includes('makerworld.bblmw.com') && src.includes('/model/')) {
            results.push(src);
        }
    });
    return results;
    """
    urls = driver.execute_script(script)
    return urls[0] if urls else None


def download_image(url, filepath):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "image/*,*/*;q=0.8",
        "Referer": "https://makerworld.com/",
    }
    try:
        r = requests.get(url, headers=headers, timeout=30, stream=True)
        r.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        size = filepath.stat().st_size
        if size < 5000:
            filepath.unlink(missing_ok=True)
            return False, f"Small: {size}"
        return True, f"{size:,} bytes"
    except Exception as e:
        return False, str(e)[:80]


def main():
    print("=" * 60)
    print("OBTENER URLs FRESCAS - 8 IMAGENES FALLIDAS")
    print("=" * 60)

    data = json.load(open(JSON_FILE, 'r', encoding='utf-8'))
    productos = data["productos"]

    driver = setup_driver()
    recovered = 0

    try:
        for producto_id, model_slug in FAILED_IDS.items():
            print(f"\n  {producto_id}: {model_slug[:50]}...")

            fresh_url = get_fresh_thumbnail(driver, model_slug)

            if not fresh_url:
                print(f"    No se encontro URL fresca")
                continue

            clean_url = re.sub(r'x-oss-process=image/resize,w_\d+', 'x-oss-process=image/resize,w_1200', fresh_url)
            clean_url = re.sub(r'format,webp', 'format,jpg', clean_url)
            clean_url = re.sub(r'\.gif\?', '.jpg?', clean_url)

            print(f"    URL fresca: {clean_url[:70]}...")

            product_dir = IMAGES_DIR / producto_id
            product_dir.mkdir(parents=True, exist_ok=True)
            filename = f"{producto_id}_principal_01.jpg"
            filepath = product_dir / filename

            ok, msg = download_image(clean_url, filepath)

            if ok:
                img = PILImage.open(filepath)
                if img.mode in ('RGBA', 'P', 'LA'):
                    img = img.convert('RGB')
                jpg_path = filepath.with_suffix('.jpg')
                img.save(jpg_path, 'JPEG', quality=90)
                if filepath.suffix != '.jpg':
                    filepath.unlink()

                w, h = img.size
                file_size = jpg_path.stat().st_size
                relative_path = f"assets/images/productos/{producto_id}/{jpg_path.name}"

                for p in productos:
                    if p["id"] == producto_id:
                        for img_data in p.get("imagenes", []):
                            if img_data["filename"] == filename:
                                img_data["ruta_local"] = relative_path
                                img_data["ancho"] = w
                                img_data["alto"] = h
                                img_data["tamano_kb"] = round(file_size / 1024, 1)
                                img_data["url"] = clean_url

                recovered += 1
                print(f"    RECUPERADA ({msg})")
            else:
                print(f"    FALLA: {msg}")

            time.sleep(2)

    finally:
        driver.quit()

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

    total_with_images = sum(1 for p in productos if any(img.get("ruta_local") for img in p.get("imagenes", [])))

    print(f"\n{'=' * 60}")
    print(f"RESULTADO FINAL:")
    print(f"  Recuperadas con Selenium: {recovered}/8")
    print(f"  Total con imagen: {total_with_images}/158")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
