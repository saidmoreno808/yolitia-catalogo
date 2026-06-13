"""
Extrae URLs + thumbnails como PARES de la colección MakerWorld.
Usa Selenium para renderizar y luego busca pares en el HTML.
"""

import json
import re
import time
from pathlib import Path
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


COLLECTION_URL = "https://makerworld.com/es/collections/10205491-yolitia-iniciousa"
BASE_URL = "https://makerworld.com"
DATA_DIR = Path(__file__).parent.parent / "data"
URLS_FILE = DATA_DIR / "collection_urls.json"


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


def extract_pairs_from_html(html):
    pairs = []
    
    pattern = r'href="(/es/models/(\d+)-[^"]+)"[^>]*>.*?(https://makerworld\.bblmw\.com/makerworld/model/[^"?\s]+)'
    matches = re.findall(pattern, html, re.DOTALL)
    
    for match in matches:
        url_path = match[0]
        model_num = match[1]
        thumb_url = match[2]
        full_url = BASE_URL + url_path
        pairs.append({
            "url": full_url,
            "model_id": model_num,
            "thumbnail": thumb_url
        })
    
    if len(pairs) < 50:
        pattern2 = r'(https://makerworld\.bblmw\.com/makerworld/model/[^"?\s]+).*?href="(/es/models/(\d+)-[^"]+)"'
        matches2 = re.findall(pattern2, html, re.DOTALL)
        for match in matches2:
            thumb_url = match[0]
            url_path = match[1]
            model_num = match[2]
            full_url = BASE_URL + url_path
            if not any(p["url"] == full_url for p in pairs):
                pairs.append({
                    "url": full_url,
                    "model_id": model_num,
                    "thumbnail": thumb_url
                })
    
    return pairs


def extract_via_dom(driver):
    pairs = []
    
    script = """
    const results = [];
    const cards = document.querySelectorAll('a[href*="/es/models/"]');
    cards.forEach(card => {
        const href = card.getAttribute('href');
        if (!href || !href.match(/\\/es\\/models\\/\\d+-/)) return;
        
        const img = card.querySelector('img');
        let thumbSrc = null;
        if (img) {
            thumbSrc = img.getAttribute('src') || img.getAttribute('data-src');
        }
        
        if (!thumbSrc) {
            const bgEl = card.querySelector('[style*="background"]');
            if (bgEl) {
                const style = bgEl.getAttribute('style');
                const match = style.match(/url\\(['"]?([^'")\\s]+)['"]?\\)/);
                if (match) thumbSrc = match[1];
            }
        }
        
        const modelMatch = href.match(/\\/es\\/models\\/(\\d+)-/);
        const modelId = modelMatch ? modelMatch[1] : null;
        
        results.push({
            url: 'https://makerworld.com' + href,
            model_id: modelId,
            thumbnail: thumbSrc
        });
    });
    
    const seen = new Set();
    return results.filter(r => {
        if (seen.has(r.url)) return false;
        seen.add(r.url);
        return true;
    });
    """
    
    results = driver.execute_script(script)
    return results if results else []


def main():
    print("=" * 60)
    print("EXTRACCIÓN DE PARES URL+THUMBNAIL - YOLITIA")
    print("=" * 60)
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    driver = setup_driver()
    
    try:
        print(f"\nCargando: {COLLECTION_URL}")
        driver.get(COLLECTION_URL)
        
        if not wait_for_cloudflare(driver):
            print("ERROR: Cloudflare no se resolvió")
            return
        
        time.sleep(3)
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        for scroll in range(25):
            driver.execute_script(f"window.scrollTo(0, {last_height});")
            time.sleep(1.5)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            print(f"  Scroll {scroll + 1}")
        
        time.sleep(3)
        
        print("\nMétodo 1: DOM extraction...")
        pairs = extract_via_dom(driver)
        print(f"  Pares encontrados: {len(pairs)}")
        
        if len(pairs) < 50:
            print("\nMétodo 2: Regex en HTML...")
            html = driver.page_source
            pairs_html = extract_pairs_from_html(html)
            print(f"  Pares encontrados: {len(pairs_html)}")
            
            existing_urls = {p["url"] for p in pairs}
            for p in pairs_html:
                if p["url"] not in existing_urls:
                    pairs.append(p)
                    existing_urls.add(p["url"])
            
            print(f"  Total combinado: {len(pairs)}")
        
        if len(pairs) < 50:
            print("\nMétodo 3: Todos los links + todos los thumbs (ordenados)...")
            html = driver.page_source
            
            all_urls = []
            for match in re.finditer(r'href="(/es/models/\d+-[^"]+)"', html):
                full_url = BASE_URL + match.group(1)
                if full_url not in [p["url"] for p in pairs]:
                    model_id = re.match(r'/es/models/(\d+)-', match.group(1))
                    all_urls.append({
                        "url": full_url,
                        "model_id": model_id.group(1) if model_id else None,
                        "thumbnail": None
                    })
            
            all_thumbs = []
            for match in re.finditer(r'(https://makerworld\.bblmw\.com/makerworld/model/[^"?\s]+)', html):
                all_thumbs.append(match.group(1))
            
            seen_urls = {p["url"] for p in pairs}
            for i, url_data in enumerate(all_urls):
                if url_data["url"] not in seen_urls:
                    if i < len(all_thumbs):
                        url_data["thumbnail"] = all_thumbs[i]
                    pairs.append(url_data)
                    seen_urls.add(url_data["url"])
            
            print(f"  Total con método 3: {len(pairs)}")
        
        pairs_with_thumbs = sum(1 for p in pairs if p.get("thumbnail"))
        print(f"\n{'=' * 60}")
        print(f"RESULTADO:")
        print(f"  Total pares: {len(pairs)}")
        print(f"  Con thumbnail: {pairs_with_thumbs}")
        print(f"  Sin thumbnail: {len(pairs) - pairs_with_thumbs}")
        
        output = {
            "collection_url": COLLECTION_URL,
            "total_urls": len(pairs),
            "total_with_thumbnails": pairs_with_thumbs,
            "fecha_extraccion": datetime.now().isoformat(),
            "models": pairs
        }
        
        with open(URLS_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\nGuardado: {URLS_FILE}")
        
        print(f"\nPRIMEROS 10 PARES:")
        for p in pairs[:10]:
            has_thumb = "✓" if p.get("thumbnail") else "✗"
            slug = p["url"].split("/")[-1][:50]
            print(f"  [{has_thumb}] {slug}")
        
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
