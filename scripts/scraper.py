"""
Scraper para colección Yolitia en MakerWorld
Usa Selenium para bypass de Cloudflare
"""

import json
import os
import time
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


COLLECTION_URL = "https://makerworld.com/es/collections/10205491-yolitia-iniciousa"
BASE_URL = "https://makerworld.com"
DATA_DIR = Path(__file__).parent.parent / "data"
PROGRESS_FILE = DATA_DIR / "scraping_progress.json"
OUTPUT_FILE = DATA_DIR / "scraping_results.json"

RATE_LIMIT_DELAY = 1.5


def setup_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
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


def load_progress():
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "completed_models": [],
        "models_data": [],
        "last_updated": None
    }


def save_progress(progress):
    progress["last_updated"] = datetime.now().isoformat()
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def extract_collection_models(driver):
    models = []
    print("Cargando colección...")
    driver.get(COLLECTION_URL)
    
    if not wait_for_cloudflare(driver):
        print("ERROR: Cloudflare challenge no se resolvió")
        return models
    
    time.sleep(3)
    
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_pause = 2
    max_scrolls = 20
    scroll_count = 0
    
    while scroll_count < max_scrolls:
        driver.execute_script(f"window.scrollTo(0, {last_height});")
        time.sleep(scroll_pause)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        scroll_count += 1
        print(f"  Scroll {scroll_count}/{max_scrolls}")
    
    time.sleep(2)
    
    model_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/es/models/']")
    seen_urls = set()
    
    for link in model_links:
        href = link.get_attribute("href")
        if href and "/models/" in href and href not in seen_urls:
            seen_urls.add(href)
            try:
                name_el = link.find_element(By.CSS_SELECTOR, "span, div, p")
                name = name_el.text.strip()
            except:
                name = ""
            
            try:
                img_el = link.find_element(By.TAG_NAME, "img")
                thumbnail = img_el.get_attribute("src")
            except:
                thumbnail = None
            
            if name or thumbnail:
                models.append({
                    "url": href,
                    "nombre_preview": name,
                    "thumbnail": thumbnail
                })
    
    return models


def extract_model_details(driver, model_url):
    details = {
        "url": model_url,
        "nombre": "",
        "descripcion": "",
        "imagenes": [],
        "autor": "",
        "likes": "",
        "descargas": "",
        "categoria_inferida": ""
    }
    
    print(f"  Extrayendo: {model_url}")
    driver.get(model_url)
    
    if not wait_for_cloudflare(driver, timeout=20):
        print("  WARNING: Cloudflare timeout")
        return details
    
    time.sleep(2)
    
    try:
        title_selectors = [
            "h1",
            "[class*='title']",
            "[class*='Title']",
            "[data-testid*='title']"
        ]
        for selector in title_selectors:
            try:
                el = driver.find_element(By.CSS_SELECTOR, selector)
                if el.text.strip():
                    details["nombre"] = el.text.strip()
                    break
            except:
                continue
    except Exception as e:
        print(f"  Error nombre: {e}")
    
    try:
        desc_selectors = [
            "[class*='description']",
            "[class*='Description']",
            "[class*='desc']",
            "article",
            "[class*='content']"
        ]
        for selector in desc_selectors:
            try:
                el = driver.find_element(By.CSS_SELECTOR, selector)
                text = el.text.strip()
                if len(text) > 20:
                    details["descripcion"] = text[:500]
                    break
            except:
                continue
    except Exception as e:
        print(f"  Error descripción: {e}")
    
    try:
        img_elements = driver.find_elements(By.TAG_NAME, "img")
        seen_srcs = set()
        for img in img_elements:
            src = img.get_attribute("src")
            if src and src not in seen_srcs:
                if any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    if 'avatar' not in src.lower() and 'icon' not in src.lower() and 'logo' not in src.lower():
                        if 'makerworld' in src or 'cdn' in src or 'cloudfront' in src or src.startswith('http'):
                            seen_srcs.add(src)
                            details["imagenes"].append({
                                "url": src,
                                "alt": img.get_attribute("alt") or ""
                            })
    except Exception as e:
        print(f"  Error imágenes: {e}")
    
    try:
        author_selectors = [
            "[class*='author']",
            "[class*='Author']",
            "[class*='designer']",
            "a[href*='/users/']"
        ]
        for selector in author_selectors:
            try:
                el = driver.find_element(By.CSS_SELECTOR, selector)
                if el.text.strip():
                    details["autor"] = el.text.strip()
                    break
            except:
                continue
    except:
        pass
    
    return details


def infer_category(nombre, descripcion):
    text = f"{nombre} {descripcion}".lower()
    
    categories = {
        "Joyería & Accesorios": ["earring", "arete", "pendiente", "necklace", "collar", "bracelet", "pulsera", "ring", "anillo", "brooch", "broche", "jewelry", "joyería"],
        "Hogar & Decoración": ["pot", "maceta", "vase", "jarrón", "planter", "figure", "figura", "decorat", "decor", "home", "hogar", "lamp", "lámpara", "candle", "vela"],
        "Organización": ["organizer", "organizador", "holder", "soporte", "storage", "almacen", "box", "caja", "tray", "bandeja", "jewelry box", "joyero"],
        "Regalos & Coleccionables": ["keychain", "llavero", "figurine", "figurita", "collectible", "coleccionable", "gift", "regalo", "charm", "dije"],
        "Entretenimiento": ["fidget", "toy", "juguete", "game", "juego", "puzzle", "rompecabezas", "spinner", "clicker"]
    }
    
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in text:
                return cat
    
    return "Regalos & Coleccionables"


def main():
    print("=" * 60)
    print("SCRAPER YOLITIA - MakerWorld Collection")
    print("=" * 60)
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    progress = load_progress()
    completed_urls = set(progress["completed_models"])
    
    print(f"\nProgreso previo: {len(completed_urls)} modelos completados")
    
    driver = setup_driver(headless=True)
    
    try:
        print("\n[1/3] Extrayendo modelos de la colección...")
        models = extract_collection_models(driver)
        print(f"  Encontrados: {len(models)} modelos")
        
        if not models:
            print("\n  Intentando método alternativo (API interna)...")
            driver.get(COLLECTION_URL)
            wait_for_cloudflare(driver)
            time.sleep(5)
            
            page_source = driver.page_source
            model_urls = re.findall(r'href="(/es/models/[^"]+)"', page_source)
            model_urls = list(set(model_urls))
            
            for url_path in model_urls:
                full_url = urljoin(BASE_URL, url_path)
                if full_url not in [m["url"] for m in models]:
                    models.append({"url": full_url, "nombre_preview": "", "thumbnail": None})
            
            print(f"  Método alternativo: {len(models)} modelos")
        
        print(f"\n[2/3] Extrayendo detalles de cada modelo...")
        new_models = []
        
        for i, model in enumerate(models):
            url = model["url"]
            
            if url in completed_urls:
                print(f"  [{i+1}/{len(models)}] Ya completado: {url}")
                continue
            
            print(f"\n  [{i+1}/{len(models)}] Procesando...")
            details = extract_model_details(driver, url)
            details["categoria_inferida"] = infer_category(details["nombre"], details["descripcion"])
            details["thumbnail"] = model.get("thumbnail")
            details["nombre_preview"] = model.get("nombre_preview", "")
            
            new_models.append(details)
            progress["models_data"].append(details)
            progress["completed_models"].append(url)
            
            save_progress(progress)
            print(f"    Nombre: {details['nombre'][:50] or '(sin nombre)'}")
            print(f"    Imágenes: {len(details['imagenes'])}")
            print(f"    Categoría: {details['categoria_inferida']}")
            
            time.sleep(RATE_LIMIT_DELAY)
        
        print(f"\n[3/3] Guardando resultados...")
        
        all_models = progress["models_data"]
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "coleccion_url": COLLECTION_URL,
                "total_modelos": len(all_models),
                "fecha_scraping": datetime.now().isoformat(),
                "modelos": all_models
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'=' * 60}")
        print(f"RESUMEN:")
        print(f"  Total modelos: {len(all_models)}")
        print(f"  Nuevos este sesión: {len(new_models)}")
        total_images = sum(len(m.get("imagenes", [])) for m in all_models)
        print(f"  Total imágenes: {total_images}")
        print(f"  Archivo: {OUTPUT_FILE}")
        print(f"{'=' * 60}")
        
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
