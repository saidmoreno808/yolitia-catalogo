import json
import sqlite3
from pathlib import Path
from PIL import Image as PILImage

images_dir = Path('yolitia_catalog/assets/images/productos')
json_file = Path('yolitia_catalog/data/yolitia_products_database.json')
db_file = Path('yolitia_catalog/data/yolitia.db')

data = json.load(open(json_file, 'r', encoding='utf-8'))
productos = data['productos']

updated = 0
for p in productos:
    product_dir = images_dir / p['id']
    if not product_dir.exists():
        continue
    files = [f for f in product_dir.iterdir() if f.is_file()]
    if not files:
        continue
    for img in p.get('imagenes', []):
        filename = img['filename']
        for f in files:
            if f.name == filename:
                try:
                    pil = PILImage.open(str(f))
                    w, h = pil.size
                    pil.close()
                except Exception:
                    w, h = None, None
                pid = p['id']
                relative = 'assets/images/productos/' + pid + '/' + f.name
                img['ruta_local'] = relative
                img['tamano_kb'] = round(f.stat().st_size / 1024, 1)
                if w:
                    img['ancho'] = w
                    img['alto'] = h
                updated += 1

with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

conn = sqlite3.connect(str(db_file))
cursor = conn.cursor()
cursor.execute('DELETE FROM imagenes')
for p in productos:
    for img in p.get('imagenes', []):
        cursor.execute(
            'INSERT INTO imagenes (producto_id, url, filename, tipo, alt_text, titulo, posicion, es_principal, ruta_local, drive_url, ancho, alto, tamano_kb) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
            (p['id'], img['url'], img['filename'], img['tipo'],
             img.get('alt_text'), img.get('titulo'),
             img.get('posicion', 0), 1 if img.get('es_principal') else 0,
             img.get('ruta_local'), img.get('drive_url'),
             img.get('ancho'), img.get('alto'), img.get('tamano_kb'))
        )
conn.commit()
conn.close()

with_local = sum(1 for p in productos if any(img.get('ruta_local') for img in p.get('imagenes', [])))
print('Imagenes con ruta local actualizadas: ' + str(updated))
print('Productos con imagen: ' + str(with_local) + '/158')
print('JSON y SQLite actualizados.')
