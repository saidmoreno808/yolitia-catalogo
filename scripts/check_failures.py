import json

d = json.load(open('yolitia_catalog/data/download_failures.json', 'r', encoding='utf-8'))
print('IMAGENES FALLIDAS:')
print('-' * 80)
for f in d:
    fn = f["filename"]
    err = f["error"]
    url = f["url"][:80]
    print(f'  {fn:<35} {err:<15}')
    print(f'    URL: {url}')
    print()

productos = json.load(open('yolitia_catalog/data/yolitia_products_database.json', 'r', encoding='utf-8'))
sin_imagen = [p for p in productos["productos"] if not any(img.get("ruta_local") for img in p.get("imagenes", []))]
print(f'PRODUCTOS SIN IMAGEN LOCAL: {len(sin_imagen)}')
for p in sin_imagen:
    pid = p["id"]
    nombre = p["nombre_yolitia"][:40]
    print(f'  {pid} | {nombre}')
